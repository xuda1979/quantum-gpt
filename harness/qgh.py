#!/usr/bin/env python3
"""qgh — QG Goal Harness CLI. The manager is a PROGRAM, not a session.

Usage:
  qgh init                       create/update durable state (idempotent)
  qgh goal                       show the goal + done criteria
  qgh seed                       seed the objective critical path (idempotent)
  qgh card add --title T --lane L --why W --accept A [--accept A2 ...]
                [--budget N] [--priority P] [--gate G] [--dep C-XXXX]
  qgh queue                      render the priority queue
  qgh fleet                      render live agents
  qgh dispatch [--lane L]        spawn workers for top ready cards (per WIP limits)
  qgh reap                       harvest finished/dead/overrun workers
  qgh tick                       THE MANAGER TICK: reconcile + dispatch + standup
  qgh standup                    render a fresh standup from structured state
  qgh done-check                 exit 0 iff goal achieved (fail-closed verdict)
  qgh install-cron               idempotent crontab self-install (never-expiring)
  qgh watch [--interval S]       foreground tick loop
  qgh heal                       reinstall cron, kill wedged ticks, force tick

Design contract (user directive 2026-09-16):
  NEVER-STOP:   cron re-arms itself; fleet reconciles idempotently; only
                done-check (goal achieved) retires the loop.
  PRIORITY:     every card names its goal edge; claim = top-of-queue; hard
                timeboxes; overrun = stop + decompose, never extend.
  SMALL CTX:    briefs <=80 lines; agents reply in a strict RESULT contract.
  NO MESS:      mechanical gates (tdd/review/eval-failclosed/sha-verified);
                no evidence = bounced, never accepted.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_lib as H  # noqa: E402
from harness_lib import (  # noqa: E402
    BACKOFF_PATH_KEY,
    LANES,
    WIP_LIMITS,
    add_card,
    age_min,
    append_line,
    backoff_active,
    check_gate,
    claim_card,
    compose_brief,
    event,
    find_card,
    goal_done,
    harvest_log,
    kill_pid,
    load_fleet,
    load_goal,
    load_json,
    load_ops,
    load_queue,
    new_card,
    note_spawn_result,
    now_iso,
    pid_alive,
    ready_cards,
    release_card,
    render_standup,
    requeue_card,
    rotate_log,
    running_count,
    save_fleet,
    save_json,
    save_ops,
    save_queue,
    scan_verdicts,
)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Testability seam: integration tests run against an isolated state dir.
STATE = os.environ.get("QGH_STATE_DIR") or os.path.join(REPO, "harness", "state")
QGH = os.path.join(REPO, "harness", "qgh.py")
CLAUDE = os.environ.get("QGH_CLAUDE", "/Users/daxu/homebrew/bin/claude")
CRON_MARK = "qgh.py tick"
MAX_LIVE_AGENTS = 6
TICK_LOCK = os.path.join(STATE, "locks", "tick.lock")
TICK_STALE_SEC = 1800  # a tick holding the lock >30min is wedged -> break it
# A successful tick appends to STATUS.md; a CRASHING tick still touches
# tick.log (the launchd stdout redirect catches the traceback) but NOT
# STATUS.md. So STATUS.md mtime is the true "loop is making progress"
# signal, not tick.log. If no successful tick in this window, the loop is
# effectively halted (measured 2026-09-18: 19h halt where tick.log looked
# fresh but STATUS.md was stale) -> heal must detect and force recovery.
SUCCESS_STALE_SEC = 2400  # 40 min = 4 missed 10-min ticks => halted
API_ERROR_SIGNATURES = (
    "API Error: Unable to connect to API",
    "Not logged in",
    "Please run /login",
    "Connection error",
    "rate limit",
)


# ----------------------------------------------------------------------------- helpers


def self_spawn(args_list, timeout=None):
    """Run qgh as a subprocess, propagating the state-dir seam."""
    env = dict(os.environ)
    env.setdefault("QGH_STATE_DIR", STATE)
    return subprocess.run(
        [sys.executable, QGH] + args_list, capture_output=True, text=True, env=env, timeout=timeout
    )


def acquire_lock(path, stale_sec=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        if stale_sec is not None:
            try:
                if time.time() - os.path.getmtime(path) > stale_sec:
                    append_line(
                        os.path.join(STATE, "tick.log"),
                        f"{now_iso()} WARN breaking stale tick lock\n",
                    )
                    kill_pid(int(load_json(path + "/pid", 0) or 0))
                    _rmtree(path)
                else:
                    return None
            except (OSError, ValueError):
                _rmtree(path)
        else:
            return None
    try:
        os.mkdir(path)
    except OSError:
        return None
    with open(path + "/pid", "w") as f:
        f.write(str(os.getpid()))
    return path


def _rmtree(path):
    import shutil

    shutil.rmtree(path, ignore_errors=True)


def release_lock(path):
    if path and os.path.exists(path):
        _rmtree(path)


def default_goal():
    return {
        "objective": (
            "LoRA adapter on Qwen3.8-27B that passes 18/18 on the frozen "
            "18-task quantum holdout, fail-closed verified (adapter-applied "
            "+ probe-differs, candidates differ from base), and beats base."
        ),
        "model": "Qwen3.8-27B",
        "target_pass": "18/18",
        "status": "OPEN",
        "created_utc": now_iso(),
        "done_criteria": [
            "verdict file with pass_adapter == 18/18 and beats_base true",
            "eval leg fail-closed: adapter-applied + adapter-probe-differs markers",
            "verdict reconfirmed by an independent second leg",
        ],
    }


# ----------------------------------------------------------------------------- commands
def cmd_init(_args):
    os.makedirs(STATE, exist_ok=True)
    for sub in ("briefs", "agents", "probes", "standup", "locks"):
        os.makedirs(os.path.join(STATE, sub), exist_ok=True)
    goal_path = os.path.join(STATE, "GOAL.json")
    if not os.path.exists(goal_path):
        save_json(goal_path, default_goal())
        event(STATE, "goal_created", {"objective": default_goal()["objective"]})
    for name, default in (("QUEUE.json", {"cards": [], "seq": 0}), ("FLEET.json", {"agents": []})):
        p = os.path.join(STATE, name)
        if not os.path.exists(p):
            save_json(p, default)
    if not os.path.exists(os.path.join(STATE, "EVENTS.jsonl")):
        append_line(os.path.join(STATE, "EVENTS.jsonl"), "")
    print(f"harness state ready at {STATE}")


def cmd_goal(_args):
    goal = load_goal(STATE)
    print(json.dumps(goal, indent=1, ensure_ascii=False))


def cmd_seed(_args):
    """Seed the objective critical path. Idempotent by (id-key) title prefix."""
    queue = load_queue(STATE)
    titles = {c["title"] for c in queue["cards"]}

    def seed(title, lane, why, acc, **kw):
        if title not in titles:
            add_card(queue, new_card(title, lane, why, acc, **kw))
            return 1
        return 0

    n = 0
    n += seed(
        "Assess current run + box state; file follow-up cards",
        "planner",
        "a stale picture of training/eval state blocks every correct next card",
        [
            "probe ASI1/2/3 daemon health + running trainer + newest checkpoints",
            "identify newest adapter not yet fail-closed eval'd",
            "file cards: eval-newest-adapter, keep-training-healthy, mine-failures",
        ],
        priority=0,
        budget_min=20,
    )
    n += seed(
        "Fail-closed re-eval of newest adapter checkpoint (post qiskit fix)",
        "evaluator",
        "B-225: pre-fix verdicts are untrustworthy on the pass component; the "
        "18/18 verdict chain must start from trustworthy measurements",
        [
            "run the 18-task holdout leg with 3 parallel task slices on ASI2",
            "leg log shows adapter-applied AND adapter-probe-differs markers",
            "candidates not byte-identical to base (spot-check 3)",
            "write outputs/verdict_<step>.json with per-task pass + composite",
        ],
        priority=0,
        budget_min=90,
        gates=["eval-failclosed"],
    )
    n += seed(
        "Keep ASI3 trainer healthy (alive, finite loss, checkpoint cadence)",
        "trainer-ops",
        "training is the adapter generator; a dead/starved trainer blocks the goal",
        [
            "trainer process alive + step markers advancing",
            "loss/reward finite; zero-change alarm absent",
            "crash -> evidence captured -> TDD fix card filed -> gated relaunch",
        ],
        priority=1,
        budget_min=20,
    )
    n += seed(
        "Mine failing holdout tasks into concrete repair/data cards",
        "data-miner",
        "base=1/18 and best adapter=3/18: 15 tasks fail; each failing task is a "
        "work item on the critical path to 18/18",
        [
            "parse latest verdict + candidate outputs",
            "per failing task: failure class (syntax/api/algorithm/harness)",
            "file 1-3 cards: repair prompt, SFT data, reward shaping, or harness fix",
        ],
        priority=1,
        budget_min=30,
    )
    save_queue(STATE, queue)
    event(STATE, "seed", {"added": n})
    print(f"seeded {n} new cards")


def cmd_card(args):
    queue = load_queue(STATE)
    card = new_card(
        title=args.title,
        lane=args.lane,
        why=args.why,
        acceptance=args.accept or ["complete the card as titled"],
        budget_min=args.budget,
        gates=args.gate,
        deps=args.dep,
        priority=args.priority,
    )
    add_card(queue, card)
    save_queue(STATE, queue)
    event(
        STATE,
        "card_added",
        {
            "id": card["id"],
            "title": card["title"],
            "lane": card["lane"],
            "priority": card["priority"],
        },
    )
    print(card["id"])


def cmd_card_requeue(args):
    """C-0032: explicit bounced->ready requeue; the dep-deadlock exit."""
    queue = load_queue(STATE)
    requeued, refused = [], []
    for cid in args.ids:
        ok, reason = requeue_card(queue, cid)
        if ok:
            requeued.append(cid)
            card = find_card(queue, cid)
            event(
                STATE,
                "card_requeued",
                dict(card=cid, bounce_count=card.get("bounce_count", 0), by="manual"),
            )
            print(f"REQUEUED {cid} {reason}")
        else:
            refused.append(f"{cid}: {reason}")
    save_queue(STATE, queue)
    for r in refused:
        print("REFUSED " + r)
    print(f"requeued {len(requeued)} card(s), refused {len(refused)}")
    if refused:
        sys.exit(1)  # fail closed: a refusal must never look like success


def cmd_queue(_args):
    queue = load_queue(STATE)
    rows = sorted(queue["cards"], key=lambda c: (c["priority"], c["created_utc"]))
    print(f"{'id':<6} {'P':<3} {'lane':<16} {'status':<8} {'title':<52} budget")
    for c in rows:
        print(
            f"{c['id']:<6} P{c['priority']:<2} {c['lane']:<16} {c['status']:<8} "
            f"{c['title'][:52]:<52} {c['budget_min']}m"
        )


def cmd_fleet(_args):
    fleet = load_fleet(STATE)
    for a in fleet["agents"]:
        if a.get("status") != "running":
            continue
        left = age_min(a.get("deadline_utc"))
        print(
            f"{a.get('pid'):<8} {a.get('card'):<7} {a.get('lane'):<16} "
            f"alive={pid_alive(a.get('pid'))!s:<5} "
            f"age={age_min(a.get('started_utc'))!s:<6} "
            f"left={(-left) if left is not None else '?'}"
        )


# ----------------------------------------------------------------------------- dispatch
WORKER_ENV_FILES = (
    "/Users/daxu/.codex/secrets/huanxin.env",
    "/Users/daxu/.claude-mcp-cron/claude_headless.env",
)


def worker_command():
    """bash: source credential files, then exec claude (pid stays the worker's)."""
    srcs = " ".join(f'[ -f "{f}" ] && source "{f}";' for f in WORKER_ENV_FILES)
    return ["/bin/bash", "-c", f"{srcs} exec '{CLAUDE}' --print"]


def dispatch_target_ok(queue, card, lanes=None, claim_in_progress=False):
    """Fail-closed preflight for dispatch: refuse when the target card is
    missing from the queue, resolves to a DIFFERENT card (duplicate-id
    collision, the C-0021 incident), is not claimable (dead/closed/running),
    is lane-mismatched, or is claimed_by a live pid."""
    resolved = find_card(queue, card.get("id"))
    if resolved is None:
        return False, f"card missing from queue: {card.get('id')}"
    if resolved is not card:
        return False, (
            f"duplicate card id {card.get('id')}: resolves to a different card "
            f"(status={resolved.get('status')}, claimed_by={resolved.get('claimed_by')})"
        )
    if sum(1 for c in queue["cards"] if c.get("id") == card.get("id")) > 1:
        # an ambiguous id can deliver two workers onto one card (C-0021)
        return False, f"duplicate card id {card.get('id')}: id is ambiguous in queue"
    if claim_in_progress and card.get("claimed_by") == "dispatching":
        pass  # our own claim, stamped by cmd_dispatch while holding this lock
    elif card.get("status") != "ready":
        return False, f"card status is {card.get('status')!r}, not ready: {card.get('id')}"
    if lanes is not None and card.get("lane") not in lanes:
        return False, f"lane mismatch: {card.get('lane')!r} not in {sorted(lanes)}"
    claimed_by = card.get("claimed_by")
    if claimed_by and pid_alive(claimed_by):
        return False, f"card claimed by live pid {claimed_by}: {card.get('id')}"
    return True, "ok"


def planner_topup_needed(queue, min_ready=2):
    """Idle top-up gate for _reap: mint a planner card only when the queue is
    GENUINELY idle. The <2 trigger counts CLAIMABLE cards only (ready_cards:
    unclaimed + deps satisfied). A saturated board -- few claimable cards but
    ready cards dep-blocked on a RUNNING dep -- is work in flight, not
    idleness, and must NOT mint (the C-0021 measured bug: three planner cards
    minted in 30 min while C-0010/C-0015/C-0016 waited on running deps). A
    blocker that is terminally dead will never unblock the board: that IS a
    management failure and must mint."""
    if len(ready_cards(queue)) >= min_ready:
        return False
    for c in queue["cards"]:
        if c["status"] != "ready":
            continue
        for dep_id in c["deps"]:
            dep = find_card(queue, dep_id)
            if dep is not None and dep["status"] == "running":
                return False
    return True


def spawn_worker(goal, queue, card, dep_results):
    """Spawn one headless claude worker for a card. Returns fleet entry or None.

    Fail-closed and atomic: the target is re-validated under the dispatch
    lock, the brief file must exist and be non-empty BEFORE spawn, and
    claimed_by=<pid> is durably saved to QUEUE.json in the same code path as
    the spawn -- a crash after spawn can never leave the card re-dispatchable.
    """
    lock = os.path.join(STATE, "locks", "agent-{}.lock".format(card["id"]))
    if acquire_lock(lock) is None:
        return None  # already dispatched
    ok, why = dispatch_target_ok(queue, card, claim_in_progress=True)
    if not ok:
        release_lock(lock)
        try:
            event(STATE, "dispatch_refused", {"card": card.get("id"), "why": why[:200]})
        except Exception:
            pass
        return None
    brief = compose_brief(goal, card, dep_results)
    brief_path = os.path.join(STATE, "briefs", "{}.md".format(card["id"]))
    with open(brief_path, "w", encoding="utf-8") as f:
        f.write(brief)
    if not (os.path.exists(brief_path) and os.path.getsize(brief_path) > 0):
        raise RuntimeError(f"brief write failed for {card['id']}")
    log_path = os.path.join(STATE, "agents", "{}.log".format(card["id"]))
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n===== dispatch {now_iso()} =====\n")
    card["claimed_by"] = "pending"
    # Minimal deterministic env: workers get credentials from the sourced files,
    # never from whatever session happened to run the tick.
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/local/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
    }
    proc = subprocess.Popen(
        worker_command(),
        stdin=open(brief_path),
        stdout=open(log_path, "a", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        cwd=REPO,
        env=env,
        start_new_session=True,
    )
    # Deadline derives from THIS process's clock, never from the card dict:
    # a lost-update race must not resurrect a stale (past) deadline that the
    # reaper would read as overrun and use to kill a healthy worker.
    deadline_utc = (
        datetime.now(timezone.utc) + timedelta(minutes=int(card["budget_min"]))
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    pid = proc.pid
    card["claimed_by"] = str(pid)
    # Atomic claim: the claimed_by=<pid> stamp hits disk HERE, in the spawn
    # code path -- not at the end of cmd_dispatch, which a crash can miss.
    save_queue(STATE, queue)
    try:
        event(
            STATE,
            "dispatched",
            {
                "card": card["id"],
                "lane": card["lane"],
                "pid": pid,
                "budget_min": card["budget_min"],
            },
        )
    except Exception:
        pass  # telemetry must never unwind a completed spawn
    entry = {
        "pid": pid,
        "lstart": H.process_lstart(pid),
        "card": card["id"],
        "lane": card["lane"],
        "brief": brief_path,
        "log": log_path,
        "started_utc": now_iso(),
        "deadline_utc": deadline_utc,
        "budget_min": card["budget_min"],
        "status": "running",
    }
    event(
        STATE,
        "dispatched",
        {"card": card["id"], "lane": card["lane"], "pid": pid, "budget_min": card["budget_min"]},
    )
    return entry


BOX_BOUND_LANES = ("evaluator", "trainer-ops", "deploy-integrity")
TRANSPORT_WEDGE_MARK = "exec_wedged"
# A box probe older than this is treated as stale at dispatch-decision time
# and re-measured live. Below the measured normal probe agent cadence; chosen
# well above a transient probe hiccup so a healthy agent's probes are never
# re-measured (the live /health is cheap, but we only pay it when stale).
PROBE_STALE_S = 3600


def _box_probe_age_s(state_dir):
    """Age (seconds) of the on-disk asi3 probe, or None if missing/illegible."""
    try:
        data = load_json(os.path.join(state_dir, "probes", "asi3.json"))
        ts = data.get("ts")
        if not ts:
            return None
        t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - t).total_seconds()
    except Exception:
        return None


def _refresh_box_probe_best_effort(state_dir):
    """Re-measure the box daemon probes (asi1/asi2/asi3) from live /health.

    A dead probe AGENT leaves a STALE 'exec_wedged' asi3 probe on disk; without
    a live re-measure the transport gate would hold box-bound lanes forever
    (measured outage 2026-09-17: 5h+ stall while asi3 had rebooted and asi1/2
    were healthy). This does a read-only, health-only probe of each daemon —
    no exec echo, never raises — and re-writes the probe files so the gate and
    the standup both see current reality. On refresh failure the existing file
    is left untouched (fail-safe: stale wedge evidence still holds)."""
    try:
        import resource_probes as RP
        from harness_lib import now_iso, save_json

        out_dir = os.path.join(state_dir, "probes")
        os.makedirs(out_dir, exist_ok=True)
        for name, port in RP.DAEMON_PORTS.items():
            p = RP.probe_daemon(name, port)  # health-only, read-only
            rec = {"ts": now_iso(), "status": p.get("status"), "summary": p.get("summary")}
            if "liveness" in p:
                rec["liveness"] = p["liveness"]
            save_json(os.path.join(out_dir, f"{name}.json"), rec)
    except Exception:
        pass  # probe refresh must never break dispatch


def transport_wedged(state_dir=None):
    """True iff asi3 is CURRENTLY exec-wedged. Fail-open for MISSING probes
    (never dispatched against an unmeasured box anyway). A STALE probe is
    re-measured live before deciding, so a dead probe agent cannot hold box
    lanes forever after the box has actually recovered; if the box is still
    wedged, the fresh probe says so and the gate still holds (fail-safe)."""
    sd = state_dir or STATE
    age = _box_probe_age_s(sd)
    # Refresh ONLY when a probe file EXISTS and is stale — so a dead probe
    # agent's stale wedge evidence is re-measured live (the fixed case). A
    # MISSING probe is left untouched and fails open (original behavior: no
    # refresh, no side effect, never dispatch against an unmeasured box
    # either way). Refresh helper never raises, but the gate is safety
    # critical and must never crash dispatch: on any raise fall back to the
    # on-disk file (a stale wedged probe then keeps the gate held).
    if age is not None and age > PROBE_STALE_S:
        try:
            _refresh_box_probe_best_effort(sd)
        except Exception:
            pass
    p = os.path.join(sd, "probes", "asi3.json")
    data = load_json(p)
    if not data:
        return False
    if "exec_wedged" in str(data.get("summary", "")):
        return True
    return False


def cmd_dispatch(args):
    goal = load_goal(STATE)
    queue = load_queue(STATE)
    fleet = load_fleet(STATE)
    ops = load_ops(STATE)
    if backoff_active(ops):
        print(f"dispatch skipped: API backoff until {ops.get(BACKOFF_PATH_KEY)}")
        return
    wedged = transport_wedged()
    if wedged and not args.lane:
        print("dispatch note: exec transport wedged - box-bound lanes held")
    elif wedged:
        pass  # explicit lane request overrides the gate (operator escape hatch)
    live = [a for a in fleet["agents"] if a.get("status") == "running" and pid_alive(a.get("pid"))]
    n_spawned = 0
    lanes = args.lane.split(",") if args.lane else None
    # GLOBAL-priority dispatch: repeatedly take the highest-priority ready card
    # whose lane has a free WIP slot. Lane order must never beat priority.
    while len(live) < MAX_LIVE_AGENTS:
        lane_live = {}
        for a in live:
            lane_live[a.get("lane")] = lane_live.get(a.get("lane"), 0) + 1
        candidates = [
            c
            for c in ready_cards(queue)
            if (lanes is None or c["lane"] in lanes)
            and lane_live.get(c["lane"], 0) < WIP_LIMITS.get(c["lane"], 1)
            and not (wedged and c["lane"] in BOX_BOUND_LANES and (args.lane is None))
        ]
        if not candidates:
            break
        card = candidates[0]
        ok, why = dispatch_target_ok(queue, card, lanes=lanes)
        if not ok:
            # fail closed: never claim or spawn against a bad target
            event(STATE, "dispatch_refused", {"card": card.get("id"), "why": why[:200]})
            break
        deps = [
            (d["id"], d["title"], d.get("result"))
            for d in (find_card(queue, x) for x in card["deps"])
            if d
        ]
        claimed = claim_card(queue, card["id"], "dispatching")
        if claimed is None:
            break
        try:
            entry = spawn_worker(goal, queue, card, deps)
        except Exception as exc:  # spawn must never crash the tick
            entry = None
            event(STATE, "spawn_error", {"card": card["id"], "err": str(exc)[:200]})
        if entry is None:
            # lock race or refused target: spawn_worker raises only BEFORE the
            # durable spawn, so no worker can be running -- revert is safe
            card["status"] = "ready"
            card["claimed_by"] = None
            break
        fleet["agents"].append(entry)
        live.append(entry)
        n_spawned += 1
    if n_spawned:
        ops = load_ops(STATE)
        if ops.get("consecutive_spawn_failures"):
            note_spawn_result(STATE, ops, ok=True)
            save_ops(STATE, ops)
    save_queue(STATE, queue)
    save_fleet(STATE, fleet)
    print(f"dispatched {n_spawned} workers")


# ----------------------------------------------------------------------------- reap
def cmd_reap(_args):
    _reap()


def _reap():
    queue = load_queue(STATE)
    fleet = load_fleet(STATE)
    goal = load_goal(STATE)
    reaped = 0
    for a in fleet["agents"]:
        if a.get("status") != "running":
            continue
        card = find_card(queue, a.get("card"))
        alive = pid_alive(a.get("pid"))
        # PID-REUSE GUARD: a recorded lstart that no longer matches means the
        # original worker is gone and an unrelated process owns the pid.
        # Treat as DEAD (harvest only) -- never kill the new owner.
        recorded_lstart = a.get("lstart")
        if alive and recorded_lstart:
            current = H.process_lstart(a.get("pid"))
            if current != recorded_lstart:
                event(STATE, "pid_reuse_detected", {"card": a.get("card"), "pid": a.get("pid")})
                alive = False  # harvest path; kill branches are skipped
        # Corrupt-deadline guard: deadline predating the entry's own start is
        # a lost-update artifact -- recompute from start + budget, never use it.
        if a.get("deadline_utc") and a.get("started_utc"):
            if a["deadline_utc"] < a["started_utc"]:
                budget = int(a.get("budget_min") or (card["budget_min"] if card else 30))
                base = datetime.strptime(a["started_utc"], "%Y-%m-%dT%H:%M:%SZ")
                fixed = (base + timedelta(minutes=budget)).strftime("%Y-%m-%dT%H:%M:%SZ")
                event(
                    STATE,
                    "corrupt_deadline_fixed",
                    {"card": a.get("card"), "was": a["deadline_utc"], "now": fixed},
                )
                a["deadline_utc"] = fixed
                save_fleet(STATE, fleet)
        over = (age_min(a.get("deadline_utc")) or 0) >= 0
        # STALL check FIRST: an alive, not-overdue worker with a stale heartbeat
        # must not be skipped by the alive-and-not-over continue below (the
        # "working != alive" trap: --print buffers output; only the heartbeat
        # proves progress).
        hb_path = os.path.join(STATE, "agents", "{}.progress".format(a.get("card")))
        stalled = False
        if alive and os.path.exists(hb_path):
            hb_age = time.time() - os.path.getmtime(hb_path)
            if hb_age > H.STALL_MIN * 60:
                kill_pid(a["pid"])
                alive = False
                stalled = True
        if alive and not over:
            continue
        reaped += 1
        outcome = "stalled-killed" if stalled else None
        verdict, tail = harvest_log(a.get("log"))
        try:
            text = open(a.get("log"), encoding="utf-8", errors="replace").read()
        except (OSError, TypeError):
            text = ""
        # ENVIRONMENTAL = pid DEAD + produced NOTHING (spawn/credential/API
        # failure) -> never burns the card's bounce budget. A worker that was
        # ALIVE past its deadline with no output is a HUNG worker, not an API
        # outage: it takes the normal bounce path and never trips backoff.
        body = [ln for ln in tail if not ln.startswith("===== dispatch")]
        # API-down signature: claude prints an API error as its final output —
        # non-empty body but still an outage, never a card fault.
        api_error = verdict is None and any(sig in text for sig in API_ERROR_SIGNATURES)
        environmental = (
            (not alive and verdict is None and len(body) == 0) or api_error
        ) and not stalled
        if outcome is None:
            if not alive:
                outcome = "dead"
            elif over:
                kill_pid(a["pid"])
                outcome = "overrun-killed"
            else:
                outcome = "harvested"
        ops = load_ops(STATE)
        if environmental:
            note_spawn_result(STATE, ops, ok=False)
            save_ops(STATE, ops)
            event(
                STATE,
                "spawn_failed_env",
                {
                    "card": a.get("card"),
                    "consecutive": ops.get("consecutive_spawn_failures"),
                    "backoff_until": ops.get(BACKOFF_PATH_KEY),
                },
            )
        if verdict == "DONE":
            ok, reason = True, "RESULT DONE"
            for gate in card["gates"] if card else []:
                ok, reason = check_gate(
                    gate, "\n".join(tail) + " " + str(card and card.get("result"))
                )
                # gate evidence must be in the log tail, not a claim
                ok2, reason2 = check_gate(gate, "\n".join(tail))
                if not ok2:
                    ok, reason = False, reason2
                    break
            if card:
                release_card(
                    card,
                    "done" if ok else "bounced",
                    tail[-1] if tail else "",
                    None if ok else reason,
                )
                if not ok:
                    event(STATE, "gate_bounced", {"card": card["id"], "reason": reason})
        elif verdict == "BLOCKED":
            if card:
                release_card(card, "bounced", tail[-1] if tail else "", "worker blocked")
        elif verdict == "PARTIAL" and over:
            if card:
                release_card(
                    card,
                    "bounced",
                    tail[-1] if tail else "",
                    "partial at deadline; decompose next time",
                )
        elif environmental:
            if card:
                # re-arm WITHOUT a bounce strike (not the card's fault)
                card["status"] = "ready"
                card["claimed_by"] = None
                card["claimed_utc"] = None
                card["deadline_utc"] = None
        else:
            # no RESULT contract -> fail closed; card re-arms (max 2) then dies
            if card:
                # C-9048: truthful reason, quotes the literal RESULT contract;
                # a PARTIAL verdict present at reap must not be reported as
                # "no RESULT verdict".
                reason = H.bounce_reason(verdict, outcome, over)
                release_card(card, "bounced", (tail[-1] if tail else ""), reason)
        if not environmental:
            ops = load_ops(STATE)
            if ops.get("consecutive_spawn_failures"):
                note_spawn_result(STATE, ops, ok=True)
                save_ops(STATE, ops)
        event(
            STATE,
            "reaped",
            {"card": a.get("card"), "lane": a.get("lane"), "outcome": outcome, "verdict": verdict},
        )
        a["status"] = "stopped"
        if os.path.exists(os.path.join(STATE, "locks", "agent-{}.lock".format(a.get("card")))):
            _rmtree(os.path.join(STATE, "locks", "agent-{}.lock".format(a.get("card"))))
    # C-9014: re-arm running cards with no live fleet entry (ghosts from
    # event-log recovery or lost fleet rows) -- AFTER the harvest loop so
    # just-reaped agents are already stopped and never double-counted.
    for _ghost_id in H.rearm_ghost_running_cards(queue, fleet):
        event(STATE, "card_ghost_rearmed", {"card": _ghost_id})
    # dead cards that exhausted retries
    for c in queue["cards"]:
        if (
            c["status"] == "ready"
            and c.get("bounce_count", 0) > 2
            and not c.get("requeued_utc")  # C-0032: an explicit requeue survives
        ):
            c["status"] = "dead"
            event(STATE, "card_dead", {"card": c["id"], "title": c["title"]})
    save_queue(STATE, queue)
    save_fleet(STATE, fleet)
    # duplicate-id repair FIRST (a single duplicate refused by the preflight
    # must never hold the whole dispatch hostage), then dep-blocker self-heal
    _dedup_card_ids()
    # dep-blocker self-heal (re-queue env-bounced blockers, escalate dead ones),
    # then re-read the queue before the top-up decision
    _reconcile_dep_blockers()
    queue = load_queue(STATE)
    # planner top-up: only when the queue is GENUINELY idle -- the <2 trigger
    # counts CLAIMABLE cards and a saturated board (dep-blocked on running
    # deps) must not mint (C-0021)
    if planner_topup_needed(queue) and running_count(queue, "planner") == 0:
        _auto_plan(goal)
    return reaped


ENV_BOUNCE_SIGNATURES = (
    "api error",
    "not logged in",
    "transport",
    "exec",
    "connection",
    "rate limit",
    "no exec path",
    "daemon",
    "booting",
    "backoff",
    "timeout",
)


def _bounce_was_environmental(card):
    reason = ((card.get("bounce_reason") or "") + " " + (card.get("result") or "")).lower()
    return any(sig in reason for sig in ENV_BOUNCE_SIGNATURES)


def _dedup_card_ids():
    """Repair duplicate card ids (concurrent card-add race): keep the running
    one, else the oldest; re-id the rest and repoint dependent cards' deps."""
    queue = load_queue(STATE)
    from collections import Counter

    ids = Counter(c["id"] for c in queue["cards"])
    dup_ids = {i for i, n in ids.items() if n > 1}
    if not dup_ids:
        return False
    maxnum = max(
        [
            int(c["id"][2:])
            for c in queue["cards"]
            if c["id"].startswith("C-") and c["id"][2:].isdigit()
        ]
        or [0]
    )
    for cid in dup_ids:
        entries = [c for c in queue["cards"] if c["id"] == cid]
        entries.sort(key=lambda c: (c["status"] != "running", c["created_utc"]))
        for extra in entries[1:]:
            maxnum += 1
            old, fresh = extra["id"], f"C-{maxnum:04d}"
            extra["id"] = fresh
            for c in queue["cards"]:
                c["deps"] = [fresh if d == old else d for d in c.get("deps", [])]
            event(
                STATE,
                "duplicate_id_repaired",
                {"was": old, "now": fresh, "title": extra["title"][:80]},
            )
    queue["seq"] = max(maxnum, queue.get("seq", 0))
    save_queue(STATE, queue)
    return True


def _reconcile_dep_blockers():
    """Self-heal dep livelock: ready cards blocked on TERMINAL (bounced/dead)
    deps. Environmental bounces re-arm the blocker (strikes reset -- they were
    never the card's fault); genuinely dead blockers trigger a planner mint to
    re-decompose. Runs every tick before the planner top-up check."""
    queue = load_queue(STATE)
    changed = False
    dead_blockers = []
    for c in queue["cards"]:
        if c["status"] != "ready":
            continue
        for dep_id in c["deps"]:
            dep = find_card(queue, dep_id)
            if dep is None or dep["status"] not in ("bounced", "dead"):
                continue
            if dep["status"] == "bounced" and _bounce_was_environmental(dep):
                dep["status"] = "ready"
                dep["bounce_count"] = 0
                dep["claimed_by"] = None
                dep["claimed_utc"] = None
                dep["deadline_utc"] = None
                changed = True
                event(STATE, "dep_blocker_requeued", {"blocker": dep["id"], "unblocks": c["id"]})
            elif dep["id"] not in dead_blockers:
                dead_blockers.append(dep["id"])
    if changed:
        save_queue(STATE, queue)
    if dead_blockers:
        _auto_plan(load_goal(STATE))
        event(STATE, "dead_dep_escalated", {"blockers": dead_blockers})
    return changed, dead_blockers


def _auto_plan(goal):
    queue = load_queue(STATE)
    # idempotency guard: never mint a second identical planner card while one
    # is already ready/running (the C-0044/45/46 duplicate-mint class)
    for c in queue["cards"]:
        if (
            c["lane"] == "planner"
            and c["status"] in ("ready", "running")
            and c["title"].startswith("Queue nearly empty")
        ):
            event(STATE, "auto_plan_skipped", {"existing": c["id"]})
            return
    card = new_card(
        "Queue nearly empty: decompose next objective steps",
        "planner",
        "the harness must never idle: empty queue = management failure",
        [
            "read harness/state/GOAL.json + latest standup + EVENTS.jsonl tail (200)",
            "inspect current run/eval state (fast commands only)",
            "add 2-5 concrete cards with qgh card add (each: why+acceptance+budget)",
            "priority 0 = blocks the objective now; 1 = core path; 2 = quality",
        ],
        priority=0,
        budget_min=20,
    )
    add_card(queue, card)
    save_queue(STATE, queue)
    event(STATE, "auto_plan", {"card": card["id"]})


# ----------------------------------------------------------------------------- tick
def cmd_tick(_args):
    lock = acquire_lock(TICK_LOCK, stale_sec=TICK_STALE_SEC)
    if lock is None:
        print("tick skipped: another tick live")
        return
    try:
        goal = load_goal(STATE)
        if goal.get("status") == "DONE":
            print("GOAL ACHIEVED — loop retired")
            return
        reaped = _reap()
        # fail-closed scheduler self-checks: cron AND launchd (belt + braces)
        for heal_cmd in ("install-cron", "install-launchd"):
            try:
                self_spawn([heal_cmd], timeout=30)
            except subprocess.SubprocessError:
                pass
        rotate_log(os.path.join(STATE, "tick.log"))
        # dispatch (skip only if this very process is the wedged-tick killer)
        r = self_spawn(["dispatch"], timeout=300)
        dispatch_note = (r.stdout or "").strip()
        # standup
        queue = load_queue(STATE)
        fleet = load_fleet(STATE)
        tick_no = _next_standup_no()
        verdicts = scan_verdicts(REPO)
        refresh_trainer_probe()  # C-0074: trainer row from live file evidence
        probes = _probe_results()
        text = render_standup(goal, queue, fleet, tick_no, verdicts, probes, state_dir=STATE)
        path = os.path.join(STATE, "standup", f"standup-{tick_no}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        append_line(
            os.path.join(STATE, "STATUS.md"),
            f"- {now_iso()} tick#{tick_no} reaped={reaped} {dispatch_note}\n",
        )
        # goal check
        done, vfile = goal_done(goal, verdicts)
        if done:
            goal["status"] = "DONE"
            goal["achieved_utc"] = now_iso()
            goal["achieved_verdict"] = vfile
            save_json(os.path.join(STATE, "GOAL.json"), goal)
            event(STATE, "GOAL_ACHIEVED", {"verdict": vfile})
        print(f"tick #{tick_no} done (reaped={reaped}, {dispatch_note})")
    finally:
        release_lock(lock)


def _tick_floor(state_dir=None):
    """C-9007: highest tick# ever recorded in STATUS.md (durable history).

    The tick counter is file-derived (standup-*.md); the 2026-09-17 recovery
    recreated that dir empty and the counter fell 127 -> 1 (STATUS.md
    18:40:01Z -> 18:40:27Z), reusing pre-reset numbers that durable card
    text references. STATUS.md survives standup-dir wipes, so its max tick#
    floors the counter: a wipe can never reset tick numbering backwards.
    """
    sd = state_dir or STATE
    mx = 0
    try:
        with open(os.path.join(sd, "STATUS.md")) as f:
            for line in f:
                i = line.find("tick#")
                if i < 0:
                    continue
                digits = ""
                for ch in line[i + len("tick#") :]:
                    if ch.isdigit():
                        digits += ch
                    else:
                        break
                if digits:
                    mx = max(mx, int(digits))
    except OSError:
        pass
    return mx


def _next_standup_no(state_dir=None):
    sd = state_dir or STATE
    d = os.path.join(sd, "standup")
    os.makedirs(d, exist_ok=True)
    nums = []
    for name in os.listdir(d):
        if name.startswith("standup-") and name.endswith(".md"):
            try:
                nums.append(int(name[len("standup-") : -3]))
            except ValueError:
                pass
    # prune: keep last 30
    nums.sort()
    for old in nums[:-30]:
        try:
            os.remove(os.path.join(d, f"standup-{old}.md"))
        except OSError:
            pass
    file_next = (nums[-1] + 1) if nums else 1
    # C-9007: never tick backwards past durable history (see _tick_floor)
    return max(file_next, _tick_floor(sd) + 1)


def refresh_trainer_probe(state_dir=None, outputs_dir=None):
    """C-0074: refresh probes/trainer.json from live run-dir file evidence.

    The no-exec trainer instrument: newest run dir under outputs/ (read-time
    resolution), its eval_results.jsonl step ladder + freshness/proc state.
    Never raises -- on failure the existing record goes stale honestly
    (_probe_results renders STALE past 30 min).
    """
    try:
        import resource_probes

        sd = state_dir or STATE
        od = outputs_dir or os.path.join(REPO, "outputs")
        p = resource_probes.probe_trainer_files(od)
        save_json(
            os.path.join(sd, "probes", "trainer.json"),
            dict(
                ts=now_iso(),
                status=p.get("status"),
                summary=p.get("summary"),
                liveness=p.get("liveness"),
            ),
        )
        return p
    except Exception:
        return None


def _probe_results():
    """Read box-probe result files (written by probe agents), fail-stale-closed."""
    probes = {}
    d = os.path.join(STATE, "probes")
    for name in ("asi1", "asi2", "asi3", "trainer"):
        p = os.path.join(d, f"{name}.json")
        data = load_json(p)
        if not data:
            probes[name] = "NO PROBE YET (spawning one)"
            continue
        age = age_min(data.get("ts"))
        if age is None or age > 30:
            probes[name] = f"STALE ({age} min)"
        else:
            probes[name] = data.get("summary", "?")
    return probes


def cmd_metrics(_args):
    from harness_lib import compute_metrics

    print(json.dumps(compute_metrics(STATE), indent=1))


def cmd_standup(_args):
    refresh_trainer_probe()  # C-0074: trainer row from live file evidence
    goal = load_goal(STATE)
    queue = load_queue(STATE)
    fleet = load_fleet(STATE)
    text = render_standup(
        goal, queue, fleet, 0, scan_verdicts(REPO), _probe_results(), state_dir=STATE
    )
    print(text)


def cmd_done_check(_args):
    goal = load_goal(STATE)
    verdicts = scan_verdicts(REPO)
    done, vfile = goal_done(goal, verdicts)
    if done:
        print(f"GOAL ACHIEVED via {vfile}")
        sys.exit(0)
    print(
        "NOT DONE — best recent verdicts: %s"
        % [(v.get("_file"), v.get("pass_adapter")) for v in verdicts[:3]]
    )
    sys.exit(1)


# ----------------------------------------------------------------------------- never-stop
def cmd_install_cron(_args):
    line = "*/10 * * * * cd {} && /usr/bin/python3 {} tick >> {} 2>&1".format(
        REPO,
        QGH,
        os.path.join(STATE, "tick.log"),
    )
    try:
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        cur = cur.stdout if cur.returncode == 0 else ""
    except OSError:
        cur = ""
    if CRON_MARK in cur and QGH in cur:
        print("cron already installed")
        return
    lines = [ln for ln in cur.splitlines() if CRON_MARK not in ln]
    lines.append(line)
    p = subprocess.run(
        ["crontab", "-"], input="\n".join(lines) + "\n", capture_output=True, text=True
    )
    if p.returncode == 0:
        event(STATE, "cron_installed", {"line": line})
        print(f"cron installed: {line}")
    else:
        print(f"cron install FAILED: {p.stderr}")


LAUNCHD_LABEL_TICK = "com.quantumgpt.qgh-tick"
LAUNCHD_LABEL_HEAL = "com.quantumgpt.qgh-heal"

PLIST_TMPL = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>%(label)s</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>%(qgh)s</string>
    <string>%(arg)s</string>
  </array>
  <key>StartInterval</key><integer>%(seconds)d</integer>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>%(log)s</string>
  <key>StandardErrorPath</key><string>%(log)s</string>
  <key>Nice</key><integer>5</integer>
</dict>
</plist>
"""


def _launchd_installed(label):
    p = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
    if not os.path.exists(p):
        return False
    try:
        r = subprocess.run(
            [f"gui/{os.getuid()}/{label}"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return True  # file present; don't flap on probe failure


def cmd_install_launchd(_args):
    """Second, independent scheduler: survives crontab rewrites AND reboots."""
    ok_all = True
    for label, seconds, arg in (
        (LAUNCHD_LABEL_TICK, 600, "tick"),
        (LAUNCHD_LABEL_HEAL, 1800, "heal"),
    ):
        log = os.path.join(STATE, f"launchd-{label}.log")
        plist = PLIST_TMPL % {
            "label": label,
            "qgh": QGH,
            "arg": arg,
            "seconds": seconds,
            "log": log,
        }
        plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{label}.plist")
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)
        try:
            with open(plist_path, "w", encoding="utf-8") as f:
                f.write(plist)
        except OSError as exc:
            print(f"launchd plist write FAILED {label}: {exc}")
            ok_all = False
            continue
        if not _launchd_installed(label):
            loaded = False
            for cmd in (
                ["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path],
                ["launchctl", "load", "-w", plist_path],
            ):
                try:
                    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    loaded = r.returncode == 0
                except (OSError, subprocess.SubprocessError):
                    loaded = False
                if loaded:
                    break
            if not loaded:
                print(f"launchctl load FAILED for {label} (manual: launchctl load -w {plist_path})")
                ok_all = False
        event(STATE, "launchd_installed", {"label": label, "seconds": seconds})
    print("launchd schedulers %s" % ("installed" if ok_all else "PARTIALLY INSTALLED"))


def cmd_doctor(_args):
    """One-command 'is the loop alive' report."""
    import time as _t

    goal = load_goal(STATE)
    print(
        "GOAL: {} | status={}".format(goal.get("objective", "?")[:80], goal.get("status", "OPEN"))
    )
    ops = load_ops(STATE)
    print(
        "API backoff: {} (consecutive spawn failures: {})".format(
            ops.get(BACKOFF_PATH_KEY) or "none", ops.get("consecutive_spawn_failures", 0)
        )
    )
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=20)
        cron_ok = CRON_MARK in r.stdout and QGH in r.stdout
    except (OSError, subprocess.SubprocessError):
        cron_ok = False
    print("cron line: %s" % ("INSTALLED" if cron_ok else "MISSING (tick self-heals)"))
    tick_log = os.path.join(STATE, "tick.log")
    if os.path.exists(tick_log):
        age = _t.time() - os.path.getmtime(tick_log)
        print("last tick: {} (age {:.0f}s)".format("RECENT" if age < 1800 else "STALE", age))
    else:
        print("last tick: NEVER")
    # TRUE health signal: STATUS.md is only appended on a successful tick
    # (a crashing tick still touches tick.log via the launchd redirect, so
    # tick.log alone is a false-positive 'RECENT'). Report last success.
    succ_age = _last_success_age_s()
    if succ_age is None:
        print("last success: NEVER")
    else:
        print(
            "last success: {} (age {:.0f}s)".format(
                "RECENT" if succ_age < SUCCESS_STALE_SEC else "HALTED", succ_age
            )
        )
    ld = os.path.expanduser(f"~/Library/LaunchAgents/{LAUNCHD_LABEL_TICK}.plist")
    print("launchd: %s" % ("INSTALLED" if os.path.exists(ld) else "MISSING"))
    queue = load_queue(STATE)
    ready = ready_cards(queue)
    print(f"queue: {len(ready)} ready / {len(queue['cards'])} total cards")
    fleet = load_fleet(STATE)
    live = [a for a in fleet["agents"] if a.get("status") == "running" and pid_alive(a.get("pid"))]
    print(f"fleet: {len(live)} live workers")
    verdicts = scan_verdicts(REPO)
    done, vfile = goal_done(goal, verdicts)
    print("goal: %s" % (f"ACHIEVED via {vfile}" if done else "OPEN"))


def cmd_watch(args):
    interval = args.interval
    while True:
        self_spawn(["tick"])
        time.sleep(interval)


def _last_success_age_s():
    """Age (s) since the last SUCCESSFUL tick, via STATUS.md mtime.

    A crashing tick touches tick.log (launchd stderr/stdout redirect) but
    never appends to STATUS.md (that happens only after reap+dispatch). So
    STATUS.md is the only reliable 'loop is progressing' signal. Returns
    None if STATUS.md does not exist."""
    p = os.path.join(STATE, "STATUS.md")
    if not os.path.exists(p):
        return None
    try:
        return time.time() - os.path.getmtime(p)
    except OSError:
        return None


def cmd_heal(_args):
    # Self-monitoring heal: detect a true tick HALT (no successful tick in
    # SUCCESS_STALE_SEC — e.g. every tick crashing in reap) and force recovery,
    # not just a wedged tick lock. The 2026-09-18 19h halt had a fresh tick.log
    # (crashes wrote tracebacks) but a stale STATUS.md, so the old heal — which
    # only broke a tick lock — never noticed the loop was dead.
    succ_age = _last_success_age_s()
    halted = succ_age is not None and succ_age > SUCCESS_STALE_SEC
    if halted:
        event(STATE, "heal_halt_detected", {"last_success_age_s": int(succ_age)})
    # break wedged tick lock
    if os.path.exists(TICK_LOCK):
        pid = load_json(TICK_LOCK + "/pid", 0) or 0
        if pid and pid_alive(pid):
            age = time.time() - os.path.getmtime(TICK_LOCK)
            if age > TICK_STALE_SEC:
                kill_pid(pid)
        _rmtree(TICK_LOCK)
    self_spawn(["install-cron"])
    # on a detected halt, clear zombie fleet BEFORE the tick so the fresh tick
    # can dispatch (zombies count against WIP and block new workers). Then tick.
    if halted:
        try:
            _reap()
        except Exception as exc:
            event(STATE, "heal_reap_failed", {"why": str(exc)[:200]})
    self_spawn(["tick"])


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(prog="qgh")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in (
        "init",
        "goal",
        "seed",
        "queue",
        "fleet",
        "reap",
        "tick",
        "standup",
        "done-check",
        "install-cron",
        "install-launchd",
        "doctor",
        "metrics",
        "heal",
    ):
        s = sub.add_parser(name.replace("-", "_") if False else name)
        s.set_defaults(func=globals()["cmd_" + name.replace("-", "_")])

    p = sub.add_parser("card")
    cp = p.add_subparsers(dest="sub", required=True)
    ca = cp.add_parser("add")
    ca.add_argument("--title", required=True)
    ca.add_argument("--lane", required=True, choices=LANES)
    ca.add_argument("--why", required=True)
    ca.add_argument("--accept", action="append")
    ca.add_argument("--budget", type=int, default=25)
    ca.add_argument("--priority", type=int, default=1)
    ca.add_argument(
        "--gate", action="append", choices=["tdd", "review", "eval-failclosed", "sha-verified"]
    )
    ca.add_argument("--dep", action="append")
    ca.set_defaults(func=cmd_card)
    cr = cp.add_parser("requeue")
    cr.add_argument("ids", nargs="+", metavar="C-XXXX")
    cr.set_defaults(func=cmd_card_requeue)

    p = sub.add_parser("dispatch")
    p.add_argument("--lane", default=None)
    p.set_defaults(func=cmd_dispatch)

    p = sub.add_parser("watch")
    p.add_argument("--interval", type=int, default=600)
    p.set_defaults(func=cmd_watch)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
