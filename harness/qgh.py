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
  qgh heartbeat C-XXXX MSG       append a worker heartbeat (sanctioned python route)
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
from functools import wraps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_lib as H  # noqa: E402
import quota_preflight_gate as QPG  # noqa: E402  (C-9132)
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
    purge_card,
    ready_cards,
    release_card,
    render_progress,
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
CLAUDE_ARGS = os.environ.get("QGH_CLAUDE_ARGS", "-p cmri -m GLM-5.2")
WORKER_MODEL_DEFAULT = "DeepSeek-V4-Flash-0731-dev"
WORKER_MODEL = os.environ.get("QGH_WORKER_MODEL", WORKER_MODEL_DEFAULT)
CRON_MARK = "qgh.py tick"
MAX_LIVE_AGENTS = 10  # reduced from 100: cmri GLM-5.2 gateway rate-limits at high concurrency
TICK_LOCK = os.path.join(STATE, "locks", "tick.lock")
TICK_STALE_SEC = 1800
QUEUE_LOCK = os.path.join(STATE, "locks", "QUEUE.json.lock")
QUEUE_STALE_SEC = 1800  # C-9386: queue write lease (matches LOCK_STALE_S)  # a tick holding the lock >30min is wedged -> break it
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


def _queue_locked(fn):
    """C-9386: serialize a QUEUE.json read-modify-write under a file lock.

    qgh card commands load->mutate->save the shared QUEUE.json. Concurrent
    invocations without a lock lose each other's updates (the vaporizer).
    Fail-closed: if the live lock cannot be taken, refuse rather than race.
    A stale/dead-holder lock is taken over by the harness_lib lease protocol.
    """

    @wraps(fn)
    def wrapper(*a, **k):
        lock = H.acquire_lock(QUEUE_LOCK, stale_s=QUEUE_STALE_SEC)
        if lock is None:
            raise RuntimeError("queue busy: another qgh card op is mutating QUEUE.json")
        try:
            return fn(*a, **k)
        finally:
            H.release_lock(QUEUE_LOCK, lock)

    return wrapper


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


@_queue_locked
def cmd_seed(_args):
    """Seed the objective critical path. Idempotent by (id-key) title prefix."""
    queue = load_queue(STATE)
    titles = {c["title"] for c in queue["cards"]}

    def seed(title, lane, why, acc, **kw):
        if title not in titles:
            add_card(queue, new_card(title, lane, why, acc, **kw), state_dir=STATE)
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
        "B-330: pre-fix verdicts are untrustworthy on the pass component; the "
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


@_queue_locked
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
    add_card(queue, card, state_dir=STATE)
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


@_queue_locked
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


@_queue_locked
def cmd_card_remove(args):
    """C-9139: purge a card from the queue.  Refuses to purge a running
    card whose claimed_by pid is still alive (orphan guard).  Removes
    dead/ready/bounced cards unconditionally."""
    queue = load_queue(STATE)
    fleet = load_fleet(STATE)
    removed, refused = [], []
    for cid in args.ids:
        card = find_card(queue, cid)
        if card is None:
            refused.append(f"{cid}: not found")
            continue
        # Also stop any fleet entry for this card
        ok = purge_card(queue, cid)
        if ok:
            removed.append(cid)
            # Stop fleet agent entries for the purged card
            for a in fleet.get("agents", []):
                if a.get("card") == cid and a.get("status") == "running":
                    a["status"] = "stopped"
            event(STATE, "card_purged", {"id": cid, "title": card.get("title", "")})
            print(f"PURGED {cid}")
        else:
            refused.append(f"{cid}: running with live pid, refuse to orphan")
    save_queue(STATE, queue)
    save_fleet(STATE, fleet)
    for r in refused:
        print("REFUSED " + r)
    print(f"purged {len(removed)} card(s), refused {len(refused)}")
    if refused:
        sys.exit(1)


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
    "/Users/daxu/.codex/secrets/cmri.env",
    "/Users/daxu/.codex/secrets/huanxin.env",
    "/Users/daxu/.claude-mcp-cron/claude_headless.env",
    "/Users/daxu/.claude-mcp-cron/claude_headless_override.env",
)


def worker_command():
    """bash: source credential files, then exec claude (pid stays the worker's).

    The brief is passed via stdin. Since the cmri GLM-5.2 proxy hangs on stdin
    input, we read stdin into a variable and pass it as the --print argument.
    """
    srcs = " ".join(f'[ -f "{f}" ] && source "{f}";' for f in WORKER_ENV_FILES)
    model_flag = f"-m '{WORKER_MODEL}'" if WORKER_MODEL else ""
    return ["/bin/bash", "-c", f"{srcs} exec '{CLAUDE}' -p cmri {model_flag} --print \"$(cat)\""]


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


def claimable_ready_count(queue):
    """C-9114: count CLAIMABLE ready cards straight from QUEUE.json's cards
    field (dict-format cards): status "ready" AND no dep whose status is
    dead/bounced. A running or done dep is work in flight/complete -- the
    card still counts (the board is not idle); only a TERMINAL dep means
    the card can never become work, so it is excluded."""
    n = 0
    for c in queue["cards"]:
        if c["status"] != "ready":
            continue
        stuck = False
        for dep_id in c["deps"]:
            dep = find_card(queue, dep_id)
            if dep is not None and dep["status"] in ("dead", "bounced"):
                stuck = True
                break
        if not stuck:
            n += 1
    return n


def planner_topup_needed(queue, min_ready=2):
    """Idle top-up gate for _reap: mint a planner card only when the queue is
    GENUINELY idle. The trigger counts CLAIMABLE ready cards (claimable_
    ready_count: ready + deps not terminally dead/bounced) and skips the
    mint while any exist -- a saturated board is work in flight, not
    idleness (the C-0021 measured bug: three planner cards minted in 30 min
    while C-0010/C-0015/C-0016 waited on running deps; the C-9111 measured
    bug: C-9111 minted on 25 ready + 6 running because one dead blocker
    escalated UNGATED). A blocker that is terminally dead will never
    unblock the board: that IS a management failure and must mint."""
    if claimable_ready_count(queue) > 0:
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
    hb_path = os.path.join(STATE, "agents", "{}.progress".format(card["id"]))
    # C-9073/C-9115: pre-create the heartbeat file BEFORE the worker starts.
    # A missing file skips the reaper's STALL check (fail-open), and a
    # gate-stranded worker denied create-permission has no file to append
    # to. The dispatch line also anchors freshness at spawn time.
    H.append_heartbeat(
        hb_path, "dispatched card {} (progress pre-created by dispatcher)".format(card["id"])
    )
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
    return entry


def cmd_heartbeat(args):
    """Worker heartbeat (C-9073/C-9115): the sanctioned append route.

    Gate-degraded sessions deny shell redirection -- the brief's old echo >>
    recipe left heartbeat-silent workers that the reaper killed as STALLED
    while they worked. Appends via harness_lib.append_heartbeat, which
    survives the permission gate.

    C-0001: emit a ghost_heartbeat event when the card is NOT in QUEUE.json
    so ghost dispatches (workers dispatched outside the tick, under a
    terminal/removed card ID) are VISIBLE in audit history. The heartbeat
    append MUST still succeed -- the worker needs it to survive the stall
    reaper. Fail-open for the write, fail-closed for detection.
    """
    hb = os.path.join(STATE, "agents", f"{args.card}.progress")
    H.append_heartbeat(hb, args.message)
    # C-0001: detect ghost card (not in QUEUE). Must not raise -- a heartbeat
    # failure would stall-kill a healthy worker. Best-effort event emission.
    try:
        queue = load_queue(STATE)
        if H.find_card(queue, args.card) is None:
            event(STATE, "ghost_heartbeat", {"card": args.card})
    except Exception:
        pass  # detection must never unwind a successful heartbeat


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
    spawned_cards = []
    lanes = args.lane.split(",") if args.lane else None
    # C-9132: quota preflight state -- ONE cheap probe per dispatch run,
    # lazily fired by the first launch-leg candidate; ids gate-skipped by
    # the quota gate are excluded from re-selection (no busy loop).
    quota_probe = None
    quota_blocked_ids = set()
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
            and not H.card_backoff_active(ops, c["id"])
            and c["id"] not in quota_blocked_ids  # C-9132
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
        # C-9132: API-quota preflight for launch legs. C-9029 burned 3 spawn
        # cycles in 9 min on exhausted quota (额度耗尽); each cycle cost a
        # 25-min budget slot and a spawn. ONE cheap probe per dispatch run;
        # EXHAUSTED or UNKNOWN -> gate_skip with a NAMED blocker artifact and
        # NO spawn (fail closed). The card stays ready (no bounce strike) so
        # a later run with quota dispatches it.
        if card.get("lane") in BOX_BOUND_LANES:
            if quota_probe is None:
                try:
                    quota_probe = QPG.probe_quota(env_files=WORKER_ENV_FILES)
                except Exception as exc:  # a probe crash must never kill the tick
                    quota_probe = dict(
                        verdict=QPG.UNKNOWN,
                        detail=f"probe error: {str(exc)[:160]}",
                        utc=H.now_iso(),
                    )
            if not QPG.gate_allows(quota_probe):
                quota_blocked_ids.add(card["id"])
                try:
                    QPG.write_quota_block(STATE, quota_probe, card=card["id"])
                except OSError:
                    pass
                event(
                    STATE,
                    "gate_skip",
                    {
                        "card": card["id"],
                        "gate": "api_quota",
                        "blocker": quota_probe.get("verdict"),
                        "detail": (quota_probe.get("detail") or "")[:200],
                    },
                )
                continue
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
        spawned_cards.append(card["id"])
    for cid in sorted(c["id"] for c in ready_cards(queue) if H.card_backoff_active(ops, c["id"])):
        _skip = dict()
        _skip["card"] = cid
        event(STATE, "dispatch_backoff_skip", _skip)
    if n_spawned:
        ops = load_ops(STATE)
        for cid in spawned_cards:
            note_spawn_result(STATE, ops, ok=True, card=cid)
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
    # C-9086 reap idempotency: (card, pid) pairs already reaped per EVENTS.
    # Pre-fix events carry no pid, so their key (card, None) never matches a
    # live row's real pid -- idempotency holds for every reap emitted from
    # now on without rewriting history.
    seen_reaps = set()
    try:
        with open(os.path.join(STATE, "EVENTS.jsonl"), encoding="utf-8") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("kind") == "reaped":
                    seen_reaps.add((ev.get("card"), ev.get("pid")))
    except OSError:
        pass
    for a in fleet["agents"]:
        if a.get("status") != "running":
            continue
        # C-9086: a row resurrected to "running" by a concurrent writer's lost
        # update must not re-harvest an already-reaped (card, pid): second
        # pass is a no-op except marking the stale row stopped. Key is
        # (card, pid), never card alone -- a NEW incarnation (new pid) of the
        # same card must still reap normally.
        key = (a.get("card"), a.get("pid"))
        if key in seen_reaps:
            a["status"] = "stopped"
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
            # C-9093: a progress file left by a PRIOR incarnation of the same
            # card is hours old; the fresh worker must not be stall-killed for
            # it. Age the heartbeat off max(mtime, started_utc) -- the file
            # cannot predate this incarnation. Missing/unparseable started_utc
            # falls back to mtime-only (fail closed, never fabricated).
            hb_age = time.time() - os.path.getmtime(hb_path)
            started_min = H.age_min(a.get("started_utc"))
            if started_min is not None:
                hb_age = min(hb_age, max(started_min, 0.0) * 60)
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
        # C-9124: /exec endpoint failure is environmental (box transport broken, not card fault)
        exec_failure = H.is_exec_endpoint_failure(text)
        environmental = (
            (not alive and verdict is None and len(body) == 0) or api_error or exec_failure
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
            note_spawn_result(STATE, ops, ok=False, card=a.get("card"))
            save_ops(STATE, ops)
            event(
                STATE,
                "spawn_failed_env",
                {
                    "card": a.get("card"),
                    "consecutive": H.card_consecutive_spawn_fails(ops, a.get("card")),
                    "backoff_until": H.card_backoff_until(ops, a.get("card")),
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
                if H.is_gate_skip_blocked(text):
                    # C-9085: gate-SKIP BLOCKED = WAITING on the window
                    # preflight gate, not a card fault -> requeue WITHOUT a
                    # bounce strike; the release_card path burned bounce
                    # budget here and drove the C-9029 dead-dep cascade.
                    # requeued_utc (C-0032) keeps a >2-strike card exempt
                    # from the exhausted-retries tripwire below.
                    card["status"] = "ready"
                    card["claimed_by"] = None
                    card["claimed_utc"] = None
                    card["deadline_utc"] = None
                    card["requeued_utc"] = H.now_iso()
                    event(STATE, "gate_skip_requeued", {"card": card["id"]})
                else:
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
            _cid = a.get("card")
            if H.card_consecutive_spawn_fails(ops, _cid) or H.card_backoff_active(ops, _cid):
                note_spawn_result(STATE, ops, ok=True, card=_cid)
                save_ops(STATE, ops)
        event(
            STATE,
            "reaped",
            {
                "card": a.get("card"),
                "pid": a.get("pid"),
                "lane": a.get("lane"),
                "outcome": outcome,
                "verdict": verdict,
            },
        )
        seen_reaps.add(key)
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
    # C-9124: auto-clean stale agent locks (dead PID holders block dispatch)
    _cleanup_stale_agent_locks()
    # C-9123: bounce cards stuck in 'running' with all-dead workers and
    # expired deadlines (prevents dependency deadlocks like the C-9029
    # incident where a card sat 'running' for 8h blocking 3 downstream cards)
    H.bounce_dead_running_cards(STATE)
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
    # Write directly, bypassing save_queue's C-9027 identity validation:
    # we just re-id'd a duplicate — the old on-disk card under that id
    # necessarily has a different title/lane, which the validation would
    # reject. This is the repair path, not a mutation.
    save_json(os.path.join(STATE, "QUEUE.json"), queue)
    return True


def _cleanup_stale_agent_locks():
    """C-9124: remove agent lock files/dirs held by dead PIDs.

    A stale agent lock (agent-<card>.lock) blocks spawn_worker from
    dispatching the card — acquire_lock returns None and the card
    silently never dispatches. This was the root cause of the C-9029
    dispatch failure (2026-09-19): a lock held by dead PID 4343
    blocked all dispatches for hours."""
    lock_dir = os.path.join(STATE, "locks")
    if not os.path.isdir(lock_dir):
        return
    for name in os.listdir(lock_dir):
        if not name.startswith("agent-") or not name.endswith(".lock"):
            continue
        lock_path = os.path.join(lock_dir, name)
        # Lock can be a file (JSON token) or directory (with pid file)
        if os.path.isdir(lock_path):
            pid_file = os.path.join(lock_path, "pid")
            if os.path.isfile(pid_file):
                try:
                    pid = int(open(pid_file).read().strip())
                    if not H.pid_alive(pid):
                        os.unlink(pid_file)
                        os.rmdir(lock_path)
                        event(
                            STATE,
                            "stale_lock_cleaned",
                            {"lock": name, "pid": pid, "reason": "dead_pid"},
                        )
                except (OSError, ValueError):
                    pass
        elif os.path.isfile(lock_path):
            # JSON token lock — check if holder PID is dead
            try:
                tok = json.loads(open(lock_path).read())
                pid = tok.get("pid")
                if pid and not H.pid_alive(pid):
                    os.unlink(lock_path)
                    event(
                        STATE,
                        "stale_lock_cleaned",
                        {"lock": name, "pid": pid, "reason": "dead_pid"},
                    )
            except (OSError, ValueError):
                pass


def _reconcile_dep_blockers():
    """Self-heal dep livelock: ready cards blocked on TERMINAL (bounced/dead)
    deps. Environmental bounces re-arm the blocker (strikes reset -- they were
    never the card's fault); genuinely dead blockers trigger a planner mint to
    re-decompose. Runs every tick before the planner top-up check.

    C-9095: also heals BLOCKED cards whose named blockers are all done --
    status "blocked" was a write-only trap (the blocked_by field had zero
    readers anywhere), so C-9010 rotted behind done C-9026. Superseded
    blockers do NOT release (C-0060 doctrine: superseded edges are stale
    and need owner re-pointing, and _deps_satisfied would strand the
    released card as undispatchable-ready). Silent blocks (no named
    blocker) and missing blocker ids fail closed. A live owner's park
    (claimed_by pid alive) is never stomped.

    C-9056/v7 self-heal: a bounced NON-environmental or dead dep can
    never reach done -- the old code only re-listed it in
    dead_dep_escalated every tick (55+ events measured) while the
    dependent stayed undispatchable forever: the exact precondition of
    the v7 live guard, re-baselined by hand v1..v7. The stale edge is
    now DROPPED (audited dep_edge_dropped) so the dependent becomes
    dispatchable; the blocker card itself stays as the historical
    record, and the C-9114 gate judges idleness on the honest claimable
    count afterwards."""
    queue = load_queue(STATE)
    changed = False
    dead_blockers = []
    for c in queue["cards"]:
        if c["status"] != "ready":
            continue
        for dep_id in list(c["deps"]):
            dep = find_card(queue, dep_id)
            if dep is None:
                # Dead dep: card no longer exists in the queue. Drop the
                # stale edge so the ready card is never permanently blocked.
                c["deps"] = [d for d in c["deps"] if d != dep_id]
                changed = True
                event(
                    STATE,
                    "dep_edge_dropped",
                    {"blocker": dep_id, "unblocks": c["id"], "reason": "dep_not_in_queue"},
                )
                continue
            if dep["status"] not in ("bounced", "dead"):
                continue
            if dep["status"] == "bounced" and _bounce_was_environmental(dep):
                dep["status"] = "ready"
                dep["bounce_count"] = 0
                dep["claimed_by"] = None
                dep["claimed_utc"] = None
                dep["deadline_utc"] = None
                changed = True
                event(STATE, "dep_blocker_requeued", {"blocker": dep["id"], "unblocks": c["id"]})
            else:
                # C-9056/v7 self-heal: never-done dep -- drop the stale
                # edge (audited) instead of re-escalating it every tick.
                if dep_id in c["deps"]:
                    c["deps"] = [d for d in c["deps"] if d != dep_id]
                    changed = True
                    event(STATE, "dep_edge_dropped", {"blocker": dep_id, "unblocks": c["id"]})
                if dep_id not in dead_blockers:
                    dead_blockers.append(dep_id)
    # C-9095 dep-guard: a card parked in status "blocked" behind named
    # blockers must re-evaluate when those blockers resolve. Release only
    # on ALL-DONE; anything else (open, superseded, missing) fails closed.
    for c in queue["cards"]:
        if c["status"] != "blocked":
            continue
        holder = c.get("claimed_by")
        if holder and pid_alive(holder):
            continue  # a live owner's active park
        names = list(c.get("deps") or [])
        bb = c.get("blocked_by")
        if isinstance(bb, str) and bb.strip():
            names.append(bb.strip())
        elif isinstance(bb, list):
            names.extend(x for x in bb if isinstance(x, str) and x.strip())
        if not names:
            continue  # silent block: an owner must state the reason
        blockers = [find_card(queue, n) for n in names]
        if any(b is None or b["status"] != "done" for b in blockers):
            continue
        c["status"] = "ready"
        c["blocked_by"] = None
        c["claimed_by"] = None
        c["claimed_utc"] = None
        c["deadline_utc"] = None
        c["requeued_utc"] = now_iso()
        changed = True
        event(
            STATE,
            "dep_released",
            dict(card=c["id"], blockers=[b["id"] for b in blockers]),
        )
    if changed:
        save_queue(STATE, queue)
    if dead_blockers:
        # C-9114: escalation mints ONLY when the board holds no INDEPENDENTLY
        # claimable ready work. A terminally dead blocker with healthy ready
        # cards elsewhere minted a planner card every tick (C-9111 minted on
        # 2026-09-18T05:50Z with 25 ready + 6 running on blocker C-9029).
        # C-9114: the reconciler only drops dep edges and tracks dead
        # blockers. Minting is the tick top-up gate (planner_topup_needed),
        # NOT the reconciler job -- a dead blocker with no dependents and
        # zero claimable work is genuinely idle, and planner_topup_needed
        # will fire on the next tick.
        n_claimable = claimable_ready_count(queue)
        event(
            STATE,
            "dead_dep_escalated",
            dict(blockers=dead_blockers, claimable_ready=n_claimable, minted=False),
        )
    return changed, dead_blockers


def _auto_plan(goal):
    queue = load_queue(STATE)
    # C-9027 (3): every auto_plan decision records its count basis
    # (ready + unblocked) so a misfire is auditable from EVENTS.jsonl
    # alone.
    ready_count = sum(1 for c in queue["cards"] if c.get("status") == "ready")
    unblocked_count = sum(
        1
        for c in queue["cards"]
        if c.get("status") in ("ready", "running")
        and all((find_card(queue, d) or {}).get("status") == "done" for d in (c.get("deps") or []))
    )
    # idempotency guard: never mint a second identical planner card while one
    # is already ready/running (the C-0044/45/46 duplicate-mint class)
    for c in queue["cards"]:
        if (
            c["lane"] == "planner"
            and c["status"] in ("ready", "running")
            and c["title"].startswith("Queue nearly empty")
        ):
            event(
                STATE,
                "auto_plan_skipped",
                {
                    "existing": c["id"],
                    "ready_count": ready_count,
                    "unblocked_count": unblocked_count,
                },
            )
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
    add_card(queue, card, state_dir=STATE)
    save_queue(STATE, queue)
    event(
        STATE,
        "auto_plan",
        {"card": card["id"], "ready_count": ready_count, "unblocked_count": unblocked_count},
    )


# ----------------------------------------------------------------- C-9133 re-arm

# C-9133: the C-9098 window re-arm (run_rearm / sentinel --rearm) keeps
# window_open.json fresh for the C-9071 gate but was only callable BY HAND.
# Left unwired, the artifact self-expires (window_fresh_s=1800s) and every
# launch leg SKIPs on window=window_open_stale (2026-09-20T05:01:55Z event)
# while ASI2 sits ready. The resident tick now detects staleness with the
# SAME freshness judge the gate applies and spawns ONE detached re-arm loop;
# the loop writes window_open.json ONLY on a bar-met poll (C-9020 two-signal),
# so a re-arm failure leaves the gate SKIP -- fail closed, exactly as before.

REARM_WINDOW_FRESH_S = 1800.0  # MUST equal the C-9071 window staleness bar
REARM_CARD = "C-9098"


def _window_age_s(window_dir, clock=time.time):
    """Age of window_open.json in seconds, or None when the artifact is
    absent/unreadable/not-open. Mirrors the C-9071 window judge: unknown is
    NEVER fresh and NEVER stale -- it is None, and None never re-arms."""
    try:
        with open(os.path.join(window_dir, "window_open.json"), encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("artifact") != "window_open":
        return None
    try:
        return clock() - H.parse_iso(str(doc.get("generated_utc"))).timestamp()
    except (ValueError, TypeError, AttributeError):
        return None


def _rearm_running(lock_path):
    """Single-flight liveness: the lock names a LIVE pid whose lstart still
    matches (the reaper's pid-reuse guard). Dead/stale/corrupt/absent lock
    => not running, so exactly one new re-arm may claim it."""
    try:
        with open(lock_path, encoding="utf-8") as f:
            rec = json.load(f)
    except (OSError, ValueError):
        return False
    if not isinstance(rec, dict):
        return False
    pid, lstart = rec.get("pid"), rec.get("lstart")
    if not isinstance(pid, int) or not H.pid_alive(pid):
        return False
    return bool(lstart) and H.process_lstart(pid) == lstart


def _spawn_rearm_detached(state_dir):
    """Spawn the C-9098 re-arm loop DETACHED from this tick (it polls the
    C-9020 bar for up to rearm_budget_s=7200s; a tick must never block on
    it) and stamp the single-flight lock. Returns the child pid."""
    lock_dir = os.path.join(state_dir, "locks")
    log_dir = os.path.join(state_dir, "c9098")
    os.makedirs(lock_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/local/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
    }
    log_path = os.path.join(log_dir, "rearm.log")
    with open(log_path, "a", encoding="utf-8") as lf:
        proc = subprocess.Popen(
            [
                sys.executable,
                os.path.join(REPO, "harness", "asi2_window_sentinel.py"),
                "--rearm",
            ],
            stdout=lf,
            stderr=subprocess.STDOUT,
            cwd=REPO,
            env=env,
            start_new_session=True,
        )
    rec = dict(pid=proc.pid, lstart=H.process_lstart(proc.pid), started_utc=now_iso())
    with open(os.path.join(lock_dir, "c9098-rearm.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f)
    return proc.pid


def auto_rearm_stale_window(
    state_dir=None,
    clock=time.time,
    window_fresh_s=REARM_WINDOW_FRESH_S,
    spawn_fn=None,
    is_running_fn=None,
):
    """C-9133: the resident runner's re-arm decision (once per tick).

    - window_open.json STALE (age > window_fresh_s -- the exact artifact the
      C-9071 gate reads window_open_stale from) => invoke the C-9098 re-arm
      path (detached `asi2_window_sentinel.py --rearm`), single-flight: no
      manual step, no re-arm herd.
    - a fresh window => NO re-arm (no spurious re-arms).
    - a missing/not-open artifact => no decision from this card (owned
      elsewhere; fail closed).
    - NEVER writes window_open.json itself and NEVER clears the gate: a
      re-arm that fails to open leaves the gate SKIP (fail closed).
    Returns an action dict; never raises into the tick."""
    sd = state_dir or STATE
    window_dir = os.path.join(sd, "c9061")
    lock_path = os.path.join(sd, "locks", "c9098-rearm.json")
    age_s = _window_age_s(window_dir, clock)
    if age_s is None:
        return dict(action="no-artifact")
    if age_s <= window_fresh_s:
        return dict(action="fresh", age_s=round(age_s, 1))
    if (is_running_fn or (lambda: _rearm_running(lock_path)))():
        return dict(action="already-running", age_s=round(age_s, 1))
    if spawn_fn is None:
        spawn_fn = lambda: _spawn_rearm_detached(sd)  # noqa: E731
    try:
        pid = spawn_fn()
    except Exception as exc:
        try:
            event(sd, "c9133_rearm_spawn_failed", {"err": repr(exc)[:160]})
        except Exception:
            pass
        return dict(action="spawn-failed", age_s=round(age_s, 1))
    try:
        event(
            sd,
            "c9133_window_rearm_spawned",
            {"pid": pid, "window_age_s": round(age_s, 1), "card": REARM_CARD},
        )
    except Exception:
        pass  # telemetry must never unwind the decision
    return dict(action="spawned", pid=pid, age_s=round(age_s, 1))


# ----------------------------------------------------------------------------- tick
def cmd_tick(_args):
    # C-9125: clean up stale tick lock if it's a directory (the acquire_lock
    # O_EXCL mechanism can't take over a directory-based lock, so a killed
    # tick's lock permanently blocks all future ticks)
    if os.path.isdir(TICK_LOCK):
        pid_file = os.path.join(TICK_LOCK, "pid")
        if os.path.isfile(pid_file):
            try:
                pid = int(open(pid_file).read().strip())
                if not H.pid_alive(pid):
                    import shutil

                    shutil.rmtree(TICK_LOCK)
                    event(STATE, "stale_tick_lock_cleaned", {"pid": pid})
            except (OSError, ValueError):
                pass
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
        # C-9133: a stale window_open artifact must re-arm the C-9098
        # sentinel WITHOUT a hand-run --rearm; otherwise every launch leg
        # re-SKIPs on window_open_stale (05:01:55Z) while ASI2 sits ready.
        # Detect-only spawn, single-flight; must never break a tick.
        try:
            auto_rearm_stale_window()
        except Exception as _rearm_exc:
            event(STATE, "c9133_rearm_step_error", {"err": repr(_rearm_exc)[:160]})
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
        auto_refresh_stale_probes()  # C-9148: re-measure stale/missing box probes
        probes = _probe_results()
        # reload queue+fleet AFTER dispatch (which ran as a subprocess and
        # modified them on disk) so the standup/dashboard/progress see the
        # CURRENT state, not the pre-dispatch snapshot.
        queue = load_queue(STATE)
        fleet = load_fleet(STATE)
        text = render_standup(goal, queue, fleet, tick_no, verdicts, probes, state_dir=STATE)
        path = os.path.join(STATE, "standup", f"standup-{tick_no}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        # publish a concise progress report to the repo root so the project's
        # progress is VISIBLE every tick (not buried in state/standup/)
        try:
            progress = render_progress(goal, queue, fleet, tick_no, verdicts, probes)
            with open(os.path.join(REPO, "PROGRESS.md"), "w", encoding="utf-8") as f:
                f.write(progress)
        except Exception:
            pass  # progress publish must never break a tick
        # publish the comprehensive system dashboard (detailed tables for every
        # component — DevOps observability: environments, agents, cards, verdicts)
        try:
            import json as _json
            import urllib.request as _url

            from dashboard import render_dashboard

            env_health = {}
            for _name, _port in (("ASI1", 20646), ("ASI2", 19004), ("ASI3", 20653)):
                try:
                    _r = _url.urlopen(f"http://127.0.0.1:{_port}/health", timeout=5)
                    env_health[_name] = _json.loads(_r.read())
                except Exception:
                    env_health[_name] = None
            dash = render_dashboard(
                goal, queue, fleet, tick_no, verdicts, probes, env_health, STATE
            )
            with open(os.path.join(REPO, "DASHBOARD.md"), "w", encoding="utf-8") as f:
                f.write(dash)
        except Exception:
            pass  # dashboard publish must never break a tick
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
        # C-9125: detailed tick status — user directive: show full state, not tiny info
        fleet_live = sum(
            1
            for a in fleet.get("agents", [])
            if a.get("status") == "running" and H.pid_alive(a.get("pid"))
        )
        ready = H.ready_cards(queue)
        running = [c for c in queue["cards"] if c.get("status") == "running"]
        blocked = [c for c in queue["cards"] if c.get("status") == "blocked"]
        bounced = [c for c in queue["cards"] if c.get("status") == "bounced"]
        done = [c for c in queue["cards"] if c.get("status") == "done"]
        print(
            f"  FLEET: {fleet_live} live agents | MAX={MAX_LIVE_AGENTS} | ASI1={'R' if (env_health.get('ASI1') or {}).get('ready') else 'N'} ASI2={'R' if (env_health.get('ASI2') or {}).get('ready') else 'N'} ASI3={'R' if (env_health.get('ASI3') or {}).get('ready') else 'N'}"
        )
        print(
            f"  QUEUE: {len(ready)} ready | {len(running)} running | {len(blocked)} blocked | {len(bounced)} bounced | {len(done)} done | total={len(queue['cards'])}"
        )
        # C-9125: auth + API health check (detect auth expiry early)
        # Check ALL worker env files for ANTHROPIC_API_KEY
        _has_key = False
        for _envf in WORKER_ENV_FILES:
            try:
                if os.path.exists(_envf):
                    with open(_envf) as f:
                        if "ANTHROPIC_API_KEY" in f.read():
                            _has_key = True
                            break
            except OSError:
                pass
        ops = load_ops(STATE)
        print(
            f"  AUTH: {'OK' if _has_key else 'MISSING ANTHROPIC_API_KEY'} | API backoff: {ops.get('backoff_until_utc', 'none')}"
        )
        print(
            f"  GATE: {H.load_json(os.path.join(STATE, 'c9071', 'window_gate_go.json'), {}).get('verdict', 'NONE') if os.path.exists(os.path.join(STATE, 'c9071', 'window_gate_go.json')) else 'SKIP' if os.path.exists(os.path.join(STATE, 'c9071', 'window_gate_skip.json')) else 'NONE'}"
        )
        print(
            f"  VERDICT: best={goal.get('best', '?')} | target={goal.get('target_pass', '?')} | status={goal.get('status', '?')}"
        )
        # C-9125: blocker analysis — what's preventing the next step?
        _blockers = []
        if ops.get("backoff_until_utc"):
            _blockers.append(f"API backoff until {ops['backoff_until_utc']}")
        if not _has_key:
            _blockers.append("AUTH: ANTHROPIC_API_KEY missing")
        _gate_go = os.path.exists(os.path.join(STATE, "c9071", "window_gate_go.json"))
        if not _gate_go:
            _blockers.append("GATE: not GO")
        _asi2 = env_health.get("ASI2") or {}
        if not _asi2.get("ready"):
            _blockers.append("ASI2: not ready")
        if _blockers:
            print(f"  BLOCKERS: {' | '.join(_blockers)}")
        else:
            print("  BLOCKERS: none -- ready to launch!")
        if running:
            for c in running[:10]:
                print(
                    f"    RUNNING: {c['id']} [{c.get('lane', '?')}] {c.get('title', '?')[:60]} bounce={c.get('bounce_count', 0)}"
                )
        if ready:
            for c in ready[:10]:
                print(f"    READY: {c['id']} [{c.get('lane', '?')}] {c.get('title', '?')[:60]}")
        if blocked:
            for c in blocked[:5]:
                deps = c.get("deps", [])
                print(f"    BLOCKED: {c['id']} deps={deps} {c.get('title', '?')[:50]}")
        # C-9125: auto-diagnose /exec health on each box
        for _name, _port in (("ASI1", 20646), ("ASI2", 19004), ("ASI3", 20653)):
            _h = env_health.get(_name)
            if _h and _h.get("ready"):
                _cc = _h.get("commandCount", 0)
                _busy = _h.get("busy", False)
                _last = (_h.get("lastCommand") or "")[:60]
                print(f"    {_name} /exec: cmdCount={_cc} busy={_busy} last=[{_last}]")
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


def refresh_box_probes_best_effort(state_dir=None):
    """C-9145: live-refresh stale box daemon probes (asi1/asi2/asi3) best-effort.

    Called by _probe_results() when on-disk probe files are older than 30 min,
    so the standup shows current reality rather than a STALE label.  Returns
    True if the refresh ran (files updated), False on failure.  Never raises."""
    sd = state_dir or STATE
    try:
        import resource_probes as RP
        from harness_lib import now_iso, save_json

        out_dir = os.path.join(sd, "probes")
        os.makedirs(out_dir, exist_ok=True)
        for name, port in RP.DAEMON_PORTS.items():
            p = RP.probe_daemon(name, port)  # health-only, read-only
            rec = {"ts": now_iso(), "status": p.get("status"), "summary": p.get("summary")}
            if "liveness" in p:
                rec["liveness"] = p["liveness"]
            save_json(os.path.join(out_dir, f"{name}.json"), rec)
        return True
    except Exception:
        return False  # probe refresh must never break standup


# C-9148: staleness threshold for the auto-refresh gate (matches _probe_results).
PROBE_STALE_MIN = 30


def auto_refresh_stale_probes(state_dir=None, clock=None):
    """C-9148: detect stale/missing box probes and re-measure them live.

    Called by the tick BEFORE _probe_results() so the standup sees fresh
    data even when the external probe agent has died.  Uses the SAME 30-min
    threshold _probe_results() applies, and calls resource_probes.run_all()
    to re-measure ALL five probes (asi1/asi2/asi3/trainer/train_fire) --
    not just the three daemon-health probes that
    refresh_box_probes_best_effort covers.

    Fail-closed: a refresh failure returns action="refresh-failed" and
    never raises.  Fresh probes return action="skip" (no spurious refresh).
    """
    sd = state_dir or STATE
    probe_dir = os.path.join(sd, "probes")
    box_names = ("asi1", "asi2", "asi3", "trainer", "train_fire")
    _any_stale = False
    for name in box_names:
        p = os.path.join(probe_dir, f"{name}.json")
        data = load_json(p)
        if not data:
            _any_stale = True
            break
        age = age_min(data.get("ts"))
        if age is None or age > PROBE_STALE_MIN:
            _any_stale = True
            break
    if not _any_stale:
        return dict(action="skip")
    try:
        import resource_probes as RP

        RP.run_all(sd)
        try:
            event(sd, "c9148_probe_refresh", {"action": "refreshed"})
        except Exception:
            pass  # telemetry must never unwind the refresh
        return dict(action="refreshed")
    except Exception:
        try:
            event(sd, "c9148_probe_refresh", {"action": "refresh-failed"})
        except Exception:
            pass
        return dict(action="refresh-failed")


def _probe_results():
    """Read box-probe result files (written by probe agents), fail-stale-closed.

    C-9145: when any box daemon probe (asi1/asi2/asi3) is stale (>30 min or
    illegible ts), attempt a best-effort live refresh before labelling STALE.
    If the refresh succeeds the standup shows the fresh summary; if it fails
    the standup shows STALE (fail-closed)."""
    probes = {}
    d = os.path.join(STATE, "probes")
    _box_names = ("asi1", "asi2", "asi3")
    _any_stale = False
    for name in _box_names:
        p = os.path.join(d, f"{name}.json")
        data = load_json(p)
        if not data:
            _any_stale = True
            break
        age = age_min(data.get("ts"))
        if age is None or age > 30:
            _any_stale = True
            break
    if _any_stale:
        try:
            refresh_box_probes_best_effort(STATE)
        except Exception:
            pass
    for name in ("asi1", "asi2", "asi3", "trainer", "train_fire"):
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


def cmd_review(_args):
    from review import run_review

    return run_review(STATE, REPO)


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
        "review",
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
    crem = cp.add_parser("remove")
    crem.add_argument("ids", nargs="+", metavar="C-XXXX")
    crem.set_defaults(func=cmd_card_remove)

    p = sub.add_parser("dispatch")
    p.add_argument("--lane", default=None)
    p.set_defaults(func=cmd_dispatch)

    p = sub.add_parser("heartbeat")
    p.add_argument("card", metavar="C-XXXX")
    p.add_argument("message")
    p.set_defaults(func=cmd_heartbeat)

    p = sub.add_parser("watch")
    p.add_argument("--interval", type=int, default=600)
    p.set_defaults(func=cmd_watch)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
