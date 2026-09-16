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
        "card": card["id"],
        "lane": card["lane"],
        "brief": brief_path,
        "log": log_path,
        "started_utc": now_iso(),
        "deadline_utc": card["deadline_utc"],
        "status": "running",
    }
    event(
        STATE,
        "dispatched",
        {"card": card["id"], "lane": card["lane"], "pid": pid, "budget_min": card["budget_min"]},
    )
    return entry


def cmd_dispatch(args):
    goal = load_goal(STATE)
    queue = load_queue(STATE)
    fleet = load_fleet(STATE)
    ops = load_ops(STATE)
    if backoff_active(ops):
        print(f"dispatch skipped: API backoff until {ops.get(BACKOFF_PATH_KEY)}")
        return
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
        # ENVIRONMENTAL = pid DEAD + produced NOTHING (spawn/credential/API
        # failure) -> never burns the card's bounce budget. A worker that was
        # ALIVE past its deadline with no output is a HUNG worker, not an API
        # outage: it takes the normal bounce path and never trips backoff.
        body = [ln for ln in tail if not ln.startswith("===== dispatch")]
        environmental = (
            not alive and verdict is None and len(body) == 0 and not stalled
        )  # a stalled worker ran and hung: NOT an outage
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
                reason = (
                    f"no RESULT verdict ({outcome})"
                    if outcome != "stalled-killed"
                    else f"stalled: heartbeat stale >{H.STALL_MIN} min"
                )
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
    # dead cards that exhausted retries
    for c in queue["cards"]:
        if c["status"] == "ready" and c.get("bounce_count", 0) > 2:
            c["status"] = "dead"
            event(STATE, "card_dead", {"card": c["id"], "title": c["title"]})
    save_queue(STATE, queue)
    save_fleet(STATE, fleet)
    # planner top-up: only when the queue is GENUINELY idle -- the <2 trigger
    # counts CLAIMABLE cards and a saturated board (dep-blocked on running
    # deps) must not mint (C-0021)
    if planner_topup_needed(queue) and running_count(queue, "planner") == 0:
        _auto_plan(goal)
    return reaped


def _auto_plan(goal):
    queue = load_queue(STATE)
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


def _next_standup_no():
    d = os.path.join(STATE, "standup")
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
    return (nums[-1] + 1) if nums else 1


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


def cmd_heal(_args):
    # break wedged tick lock, reinstall cron, tick now
    if os.path.exists(TICK_LOCK):
        pid = load_json(TICK_LOCK + "/pid", 0) or 0
        if pid and pid_alive(pid):
            age = time.time() - os.path.getmtime(TICK_LOCK)
            if age > TICK_STALE_SEC:
                kill_pid(pid)
        _rmtree(TICK_LOCK)
    self_spawn(["install-cron"])
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
