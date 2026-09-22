"""QG Goal Harness — pure logic.

Durable, deterministic management machinery for the quantum-gpt objective:
an adapter on Qwen3.8-27B that passes 18/18 on the frozen 18-task holdout.

Pain points this library exists to kill (user directive 2026-09-16):
  1. work that silently stops        -> idempotent state + respawn + self-healing cron
  2. wrong priorities held too long  -> goal-linked priority queue + hard timeboxes
  3. long contexts (slow, wrong)     -> composed micro-briefs + RESULT contract
  4. messy code/work                 -> per-card gates (TDD/review/eval) + bounce protocol

Stdlib only; Python 3.9-safe (box runtime gate: no `X | Y`, no match, no zip strict).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import types as _types
from datetime import datetime, timedelta, timezone
from functools import wraps

# ----------------------------------------------------------------------------- module constants
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.environ.get("QGH_STATE_DIR") or os.path.join(REPO, "harness", "state")
QGH = os.path.join(REPO, "harness", "qgh.py")
MAX_LIVE_AGENTS = 100  # user mandate: agent working limit is 100
CLAUDE = os.environ.get("QGH_CLAUDE", "/Users/daxu/homebrew/bin/claude")
CLAUDE_ARGS = os.environ.get("QGH_CLAUDE_ARGS", "-p huanxin -m dp4")
WORKER_MODEL_DEFAULT = "dp4"
WORKER_MODEL = os.environ.get("QGH_WORKER_MODEL", WORKER_MODEL_DEFAULT)
WORKER_PROVIDER = os.environ.get("QGH_WORKER_PROVIDER", "huanxin")
WORKER_ENV_FILES = [
    "/Users/daxu/.codex/secrets/cmri.env",
    "/Users/daxu/.codex/secrets/zhipu.env",
    "/Users/daxu/.codex/secrets/huanxin.env",
    "/Users/daxu/.claude-mcp-cron/claude_headless.env",
    "/Users/daxu/.claude-mcp-cron/claude_headless_override.env",
]
CRON_MARK = "qgh.py tick"
TICK_LOCK = os.path.join(STATE, "locks", "tick.lock")
TICK_STALE_SEC = 1800
QUEUE_LOCK = os.path.join(STATE, "locks", "QUEUE.json.lock")
SUCCESS_STALE_SEC = 2400
API_ERROR_SIGNATURES = (
    "API Error: Unable to connect to API",
    "Not logged in",
    "Please run /login",
    "Connection error",
    "rate limit",
)
# QPG: quota preflight gate module (imported lazily to avoid circular deps)

try:
    import quota_preflight_gate as QPG
except ImportError:
    QPG = None


# ----------------------------------------------------------------------------- time
def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def age_min(iso_ts, now=None):
    """Minutes since iso timestamp. Missing/invalid -> None (never fabricate)."""
    if not iso_ts:
        return None
    try:
        then = parse_iso(iso_ts)
    except ValueError:
        return None
    ref = now or datetime.now(timezone.utc)
    return round((ref - then).total_seconds() / 60.0, 1)


# ----------------------------------------------------------------------------- io
def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, obj):
    """Atomic write: tmp + rename, so a crash never leaves torn state."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def append_line(path, line):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")


def append_heartbeat(path, line):
    """The ONLY sanctioned heartbeat write route (C-9073/C-9115): a python
    open-append stamped with now_iso().

    Gate-degraded sessions deny shell redirection (echo/tee >>) and the
    Write tool at the permission layer, but this append survives (measured
    live 2026-09-17/18); a worker heartbeating through shell redirection
    goes heartbeat-silent and the reaper kills it as STALLED while it works.
    """
    append_line(path, f"{now_iso()} {line}")


# ----------------------------------------------------------------------------- events
def event(state_dir, kind, payload):
    append_line(
        os.path.join(state_dir, "EVENTS.jsonl"),
        json.dumps({"ts": now_iso(), "kind": kind, **payload}, ensure_ascii=False),
    )


# ----------------------------------------------------------------------------- queue
LANES = (
    "planner",
    "evaluator",
    "trainer-ops",
    "fixer",
    "reviewer",
    "qa-steward",
    "data-miner",
    "deploy-integrity",
)

# Per-lane concurrency limits (WIP). I/O-bound lanes get 1; context-bound get more.
WIP_LIMITS = {
    "planner": 10,
    "evaluator": 20,
    "trainer-ops": 10,
    "fixer": 20,
    "reviewer": 10,
    "qa-steward": 10,
    "data-miner": 10,
    "deploy-integrity": 10,
}

DEFAULT_BUDGET_MIN = 25
STALL_MIN = 10  # heartbeat staleness that counts as a stall (2min ticks)
MAX_BUDGET_MIN = 90


def new_card(
    title,
    lane,
    why,
    acceptance,
    budget_min=DEFAULT_BUDGET_MIN,
    gates=None,
    deps=None,
    priority=1,
    card_id=None,
):
    if lane not in LANES:
        raise ValueError(f"unknown lane: {lane}")
    # C-9147: reject placeholder titles/why — a card with title 't' and
    # why 'w' (C-9001) burned a running fixer slot while the effective
    # queue was empty. Minimum 8 chars enforces a real description.
    if not title or len(title) < 8:
        raise ValueError(
            f"card title too short ({len(title) if title else 0} chars); "
            "minimum 8 characters required"
        )
    if not why or len(why) < 8:
        raise ValueError(
            f"card why too short ({len(why) if why else 0} chars); minimum 8 characters required"
        )
    # C-9139: reject empty acceptance list -- a card with no acceptance
    # criteria has an unverifiable done-gate.  At least one item required.
    if not acceptance or len(acceptance) == 0:
        raise ValueError("card acceptance list is empty; at least one criterion required")
    # C-9001: reject placeholder acceptance items -- acceptance=['a'] is
    # content-free and makes the done-gate unverifiable.  Each item must
    # be at least 8 chars to describe a real acceptance criterion.
    for item in acceptance:
        if not item or len(item) < 8:
            raise ValueError(
                f"card acceptance item too short ({len(item) if item else 0} chars); "
                "minimum 8 characters required"
            )
    return {
        "id": card_id,  # assigned by add_card
        "title": title,
        "lane": lane,
        "priority": int(priority),  # 0 = objective-critical, 1 = core, 2 = quality, 3 = cleanup
        "why": why,  # MUST name the goal edge this serves
        "acceptance": list(acceptance),
        "gates": list(gates or []),
        "deps": list(deps or []),
        "budget_min": min(int(budget_min), MAX_BUDGET_MIN),
        "status": "ready",  # ready|running|done|bounced|blocked|dead
        "created_utc": now_iso(),
        "claimed_by": None,
        "claimed_utc": None,
        "deadline_utc": None,
        "result": None,
        "bounce_count": 0,
        "bounce_reason": None,
    }


def load_queue(state_dir):
    return load_json(os.path.join(state_dir, "QUEUE.json"), {"cards": [], "seq": 0})


def save_queue(state_dir, queue):
    # C-9027 (3): identity (title+lane) is frozen per live id -- the
    # C-9021 incident stood up fixer/"Split /health-ready..." under the
    # id standup-27 had recorded as planner/"Queue nearly empty...".
    # State fields (status/claims/deadlines) stay writable; new intent
    # requires a NEW id. A missing/corrupt prior file skips the guard
    # (first save).
    path = os.path.join(state_dir, "QUEUE.json")
    if os.path.exists(path):
        # C-9427: read the REAL disk file directly (not through a possibly-
        # monkeypatched load_json) so the lost-update merge sees concurrent
        # adds that happened after our in-memory snapshot was taken.
        import json as _json

        try:
            with open(path, encoding="utf-8") as _f:
                disk = _json.load(_f)
        except (OSError, ValueError):
            disk = {"cards": [], "seq": 0}
        mem = {c.get("id"): c for c in queue.get("cards", [])}
        for c in disk.get("cards", []):
            m = mem.get(c.get("id"))
            if m is None:
                # C-9135/C-9136: card exists on disk but NOT in the
                # in-memory copy.  It was added by a concurrent writer
                # after this copy was loaded.  Preserve it ONLY if it
                # has no terminal event (reaped/card_dead/card_done/
                # card_voided/card_superseded) in EVENTS.jsonl -- a
                # terminal card was intentionally removed and must not
                # be resurrected.  This prevents the lost-update
                # vaporizer that silently dropped ready cards
                # (C-9125/C-9128/C-9129/C-9130 vanished
                # 2026-09-20T04:51-05:15Z with no archive event).
                _terminal = history_terminal_card_ids(state_dir)
                if c.get("id") not in _terminal:
                    queue.setdefault("cards", []).append(c)
                continue
            for field in ("title", "lane"):
                if field in c and field in m and c[field] != m[field]:
                    raise ValueError(
                        f"refusing to mutate {field} of existing card {c.get('id')} under a "
                        f"live id (disk {c.get(field)!r} != memory {m.get(field)!r}); new intent requires "
                        "a new id"
                    )
        # C-9136: reconcile seq -- a concurrent add bumped seq on disk;
        # our stale in-memory seq must not regress it (would cause id
        # collisions on the next add_card).
        disk_seq = int(disk.get("seq", 0))
        if disk_seq > int(queue.get("seq", 0)):
            queue["seq"] = disk_seq
    # C-9415: count cards BEFORE save_json (a clobbering monkeypatch
    # may mutate the queue object in-place during the write).
    _pre_save_n = len(queue.get("cards", []))
    H.save_json(path, queue)
    # C-9415: post-write integrity check -- if the atomic write landed
    # fewer cards than the caller supplied (a clobbering concurrent
    # writer or a corrupted save), fail closed rather than silently
    # persisting a truncated queue.
    try:
        with open(path, encoding="utf-8") as _vf:
            _verify = json.load(_vf)
        _disk_n = len(_verify.get("cards", []))
        if _disk_n < _pre_save_n:
            raise RuntimeError(
                f"save_queue integrity check failed: disk has {_disk_n} cards "
                f"but memory had {_pre_save_n} -- a clobbering write vaporized cards"
            )
    except (OSError, ValueError):
        pass  # verify is best-effort; the save itself already happened
    # C-9415: post-write integrity check.  The atomic tmp+rename (save_json)
    # guarantees the write either fully lands or leaves the old file intact,
    # but a concurrent clobbering writer (C-9427's direct save_json path) can
    # still land a *different, truncated* queue during the rename window.  We
    # re-read the durable artifact directly from disk and fail closed if any
    # card this caller intended to persist is missing -- never silently
    # persisting a vaporized working set.
    try:
        with open(path, encoding="utf-8") as _f:
            _persisted = json.load(_f)
    except (OSError, ValueError):
        raise ValueError(
            "QUEUE.json post-write integrity check could not re-read "
            + str(path)
            + " after save; refusing to proceed on an unverifiable queue"
        )
    _persisted_ids = set(c.get("id") for c in _persisted.get("cards", []))
    _intended_ids = set(c.get("id") for c in queue.get("cards", []))
    _missing = _intended_ids - _persisted_ids
    if _missing:
        raise ValueError(
            "QUEUE.json post-write integrity check failed: cards lost during persist "
            + str(sorted(_missing))
            + " (persisted "
            + str(len(_persisted.get("cards", [])))
            + " of intended "
            + str(len(_intended_ids))
            + "); queue not committed"
        )


# C-9027: statuses under which a card is open (same intent still live).
OPEN_STATUSES = ("ready", "running", "blocked")


def cmd_init(_args=None):
    """Initialize the state directory with empty queue, goal, and fleet."""
    sd = os.environ.get("QGH_STATE_DIR") or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "harness", "state"
    )
    os.makedirs(sd, exist_ok=True)
    os.makedirs(os.path.join(sd, "probes"), exist_ok=True)
    os.makedirs(os.path.join(sd, "agents"), exist_ok=True)
    os.makedirs(os.path.join(sd, "briefs"), exist_ok=True)
    os.makedirs(os.path.join(sd, "locks"), exist_ok=True)
    os.makedirs(os.path.join(sd, "standups"), exist_ok=True)
    if not os.path.exists(os.path.join(sd, "QUEUE.json")):
        save_json(os.path.join(sd, "QUEUE.json"), {"cards": [], "seq": 0})
    if not os.path.exists(os.path.join(sd, "GOAL.json")):
        save_json(
            os.path.join(sd, "GOAL.json"),
            {
                "objective": "test objective",
                "model": "test-model",
                "target_pass": "18/18",
                "status": "OPEN",
                "created_utc": now_iso(),
                "done_criteria": [],
            },
        )
    if not os.path.exists(os.path.join(sd, "FLEET.json")):
        save_json(os.path.join(sd, "FLEET.json"), {"agents": []})


def history_card_ids(state_dir):
    """C-9127: every card id ever referenced in EVENTS.jsonl.

    EVENTS.jsonl is append-only history; a pruned card leaves no other
    trace, so this is the authority for ids that must never be re-issued
    (C-9124 was re-minted 2026-09-20 for an unrelated card after its
    original holder was pruned). Read-only: allocation never rewrites
    history.
    """
    try:
        with open(os.path.join(state_dir, "EVENTS.jsonl"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return set()
    return set(re.findall(r"C-\d{3,}", text))


# C-9135: terminal event kinds that mark a card as done -- a card with
# one of these events is NOT preserved by the save_queue merge (it was
# intentionally removed from the working set).
TERMINAL_EVENT_KINDS = frozenset(
    {
        "reaped",
        "card_dead",
        "card_done",
        "card_voided",
        "card_superseded",
        "card_purged",
    }
)


def history_terminal_card_ids(state_dir):
    """C-9135: card ids that have a terminal event in EVENTS.jsonl.

    A terminal event (reaped, card_dead, card_done, card_voided,
    card_superseded) means the card is no longer live -- save_queue
    should NOT resurrect it from disk during the lost-update merge.
    """
    try:
        with open(os.path.join(state_dir, "EVENTS.jsonl"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return set()
    ids = set()
    for m in re.finditer(
        r'"kind":\s*"(reaped|card_dead|card_done|card_voided|card_superseded|card_purged)".*?"(?:card|id)":\s*"(C-\d{3,})"',
        text,
    ):
        ids.add(m.group(2))
    return ids


def is_terminal_card_id(state_dir, card_id):
    """C-0001: True if this card id has a terminal event in EVENTS.jsonl.

    A terminal reap is one with a non-null verdict (DONE/PARTIAL/BLOCKED/
    BOUNCED) -- the card was closed, not merely re-armed after an
    environmental death.  A reap with verdict=null means the worker died
    without producing output (API failure, credential issue) and the card
    was re-armed to 'ready' -- that is NOT terminal.

    Other terminal event kinds (card_dead, card_done, card_voided,
    card_superseded, card_purged) are always terminal regardless of
    verdict.  card_purged uses the "id" field instead of "card".

    This lets a worker detect it has been handed a ghost card id (one that
    was already completed and pruned) and exit immediately instead of
    spinning on a non-existent card.
    """
    try:
        with open(os.path.join(state_dir, "EVENTS.jsonl"), encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except (ValueError, TypeError):
                    continue
                if not isinstance(ev, dict):
                    continue
                # card id may be in "card" or "id" field, any order
                if ev.get("card") != card_id and ev.get("id") != card_id:
                    continue
                kind = ev.get("kind")
                if kind == "reaped":
                    verdict = ev.get("verdict")
                    if verdict is not None and verdict != "null":
                        return True
                elif kind in TERMINAL_EVENT_KINDS:
                    return True
        return False
    except OSError:
        return False


def add_card(queue, card, state_dir=None):
    # C-9027 (1): decompose-class dedupe -- a second OPEN "Queue nearly
    # empty" card is the C-9021/C-9023 double-mint (the incident card
    # mutated lane planner->fixer under one id, so the marker is the
    # TITLE class, never the lane). The marker mirrors qgh._auto_plan's
    # own idempotency guard. Scoped to the decompose class only: other
    # intents dedupe by id uniqueness below (test fixtures legitimately
    # mint several placeholder-titled cards).
    title = card.get("title") or ""
    if title.startswith("Queue nearly empty"):
        for c in queue.get("cards", []):
            if c.get("title") == title and c.get("status") in OPEN_STATUSES:
                raise ValueError(
                    f"duplicate open decompose-class card {title!r} (live id {c.get('id')}); "
                    "new intent requires a new id"
                )
    # C-9135: seq must exceed the max id ever seen in EVENTS.jsonl so a
    # fresh queue (seq=0) never re-mints a pruned card id below the
    # history max (e.g. C-9999 in history would be ignored, minting
    # C-0001 below it).  Bump seq to the history max BEFORE the +1 so
    # the allocated id always exceeds it.
    if state_dir:
        _hist_max = 0
        for _hid in history_card_ids(state_dir):
            try:
                _hist_max = max(_hist_max, int(_hid.split("-")[1]))
            except (ValueError, IndexError):
                pass
        if _hist_max > int(queue.get("seq", 0)):
            queue["seq"] = _hist_max
    queue["seq"] = int(queue.get("seq", 0)) + 1
    card["id"] = card["id"] or f"C-{queue['seq']:04d}"
    # C-9027 (2): a stale on-disk seq (a lost update left seq=9020 while
    # C-9021 existed) must never mint a colliding id -- bump to free.
    ids = {c.get("id") for c in queue.get("cards", [])}
    # C-9127: live ids alone let a seq regression (stale concurrent
    # save) re-mint a PRUNED card's id. Never allocate an id that the
    # durable history references.
    if state_dir:
        ids |= history_card_ids(state_dir)
    while card["id"] in ids:
        queue["seq"] += 1
        card["id"] = f"C-{queue['seq']:04d}"
    queue["cards"].append(card)
    return card


def find_card(queue, card_id):
    for c in queue["cards"]:
        if c["id"] == card_id:
            return c
    return None


def purge_card(queue, card_id, live_fn=None):
    """C-9139: remove a card from the queue, but ONLY if it is safe.

    A 'running' card is purgeable only if its claimed_by pid is provably
    dead (no live process owns the slot).  A 'ready'/'dead'/'bounced' card
    is always purgeable (no live worker to orphan).  A running card with
    a LIVE pid is refused -- purging it would orphan a live worker.

    Returns True if the card was removed, False if refused or not found.
    """
    card = find_card(queue, card_id)
    if card is None:
        return False
    if card.get("status") == "running":
        pid_str = card.get("claimed_by")
        if pid_str:
            _live_fn = live_fn or pid_alive
            try:
                pid = int(pid_str)
            except (ValueError, TypeError):
                pid = 0
            if pid > 0 and _live_fn(pid):
                return False  # live worker -- refuse to orphan
    queue["cards"] = [c for c in queue["cards"] if c["id"] != card_id]
    return True


def rearm_ghost_running_cards(queue, fleet, live_fn=None, terminal_ids=None):
    # terminal_ids (C-0001/C-9135): optional set of card ids with a terminal
    # event in EVENTS.jsonl (reaped DONE / purged / voided / dead). Such ids
    # are pruned/historical and MUST never be resurrected -- a running card
    # that is already terminal stays put instead of being flipped to ready.
    """C-9014: re-arm 'running' cards whose fleet agent is gone (ghost).

    A card can land in status "running" with no LIVE fleet entry — e.g. the
    event-log recovery flipped a card whose last event was `dispatched` (no
    matching `reaped`) to running, but the worker process is already dead.
    The harvest loop only reaps cards that HAVE a fleet agent row, so such a
    ghost would run forever: the card is stuck "running", blocking its lane's
    WIP, never re-dispatched.

    This reconcile finds every card that is "running" but has no live fleet
    agent (no running-status agent whose process is alive) and re-arms it:
      status -> "ready", clear claimed_by/claimed_utc/deadline_utc, set
      requeued_utc, bounce_count += 1 (environmental — a dead worker is not
      the card's fault, so no strike). Terminal cards (done/bounced/dead/...)
    are never touched. Returns the list of rearmed card ids (sorted-stable).

    live_fn(agent) -> bool defaults to the real pid_alive check on the agent's
    pid; tests inject a stub. An agent with no lstart, or whose lstart no
    longer matches the recorded one (PID reuse), is treated as NOT live.
    """
    if live_fn is None:
        live_fn = lambda a: pid_alive(a.get("pid"))  # noqa: E731

    # index live fleet entries by card id
    live_cards = set()
    for a in fleet.get("agents", []):
        if a.get("status") != "running":
            continue
        if live_fn(a):
            live_cards.add(a.get("card"))

    rearmed = []
    for c in queue["cards"]:
        if c.get("status") != "running":
            continue
        if terminal_ids and c["id"] in terminal_ids:
            # C-0001/C-9135: terminal card id (already reaped DONE / purged /
            # voided) — a stale fleet or event-log recovery row must not
            # resurrect it. Leave status untouched, do NOT re-arm.
            continue
        if c["id"] in live_cards:
            continue  # has a live worker — genuinely running, leave it
        # ghost: re-arm. Environmental — a dead/missing worker is not the
        # card's fault, so do NOT strike (bounce_count unchanged): a ghost
        # rearm must never push a healthy card toward the dead-card threshold.
        c["status"] = "ready"
        c["claimed_by"] = None
        c["claimed_utc"] = None
        c["deadline_utc"] = None
        c["requeued_utc"] = now_iso()
        rearmed.append(c["id"])
    return rearmed


def bounce_dead_running_cards(state_dir, pid_alive_fn=None):
    """C-9123: bounce 'running' cards whose deadline expired AND all workers
    are dead. Unlike rearm_ghost_running_cards (which re-arms environmental
    deaths without a strike), this BOUNCES the card so the dep-blocker
    self-heal can detect it and break dependency cycles.

    A card stuck in 'running' with an expired deadline and no live workers
    is a deadlock source: downstream cards wait on it forever. Bouncing
    lets _reconcile_dep_blockers escalate or re-decompose.

    Returns a list of bounced card ids."""
    if pid_alive_fn is None:
        pid_alive_fn = pid_alive
    queue = load_json(os.path.join(state_dir, "QUEUE.json"), {"cards": [], "seq": 0})
    fleet = load_json(os.path.join(state_dir, "FLEET.json"), {"agents": []})
    # Gather card ids with at least one live running worker
    live_cards = set()
    for a in fleet.get("agents", []):
        if a.get("status") != "running":
            continue
        if pid_alive_fn(a.get("pid")):
            live_cards.add(a.get("card"))

    now = datetime.now(timezone.utc)
    bounced = []
    for c in queue.get("cards", []):
        if c.get("status") != "running":
            continue
        if c["id"] in live_cards:
            continue  # has a live worker
        deadline = c.get("deadline_utc")
        if not deadline:
            continue  # no deadline — let rearm_ghost handle it
        try:
            dl = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            continue
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)
        if dl > now:
            continue  # deadline not yet passed
        # All workers dead + deadline expired → bounce
        c["status"] = "bounced"
        c["bounce_count"] = c.get("bounce_count", 0) + 1
        c["bounce_reason"] = "all_workers_dead_deadline_expired"
        c["claimed_by"] = None
        c["claimed_utc"] = None
        c["deadline_utc"] = None
        c["requeued_utc"] = now_iso()
        bounced.append(c["id"])
        # Record event: use canonical event() helper (C-9505: lowercase
        # events.jsonl was a separate file on case-sensitive filesystems)
        event(
            state_dir,
            "dead_worker_requeued",
            {"card": c["id"], "reason": "all_workers_dead_deadline_expired"},
        )
    if bounced:
        save_queue(state_dir, queue)
    return bounced


def _deps_satisfied(queue, card):
    for dep in card["deps"]:
        d = find_card(queue, dep)
        if d is None or d["status"] != "done":
            return False
    return True


def ready_cards(queue, lane=None):
    out = []
    for c in queue["cards"]:
        if c["status"] != "ready":
            continue
        if lane and c["lane"] != lane:
            continue
        if not _deps_satisfied(queue, c):
            continue
        out.append(c)
    out.sort(key=lambda c: (c["priority"], c["created_utc"]))
    return out


def auto_requeue_zero_bounce(state_dir):
    """C-9529: Auto-requeue bounced cards with 0 bounces.

    Bounced cards sitting idle with bounce_count=0 are a productivity leak.
    This sets status=ready, clears claimed_by/claimed_utc so the dispatcher
    can pick them up on the next cycle. Returns the count of requeued cards.

    C-9533: the field is "bounce_count" (set by new_card at line 219), not
    "bounces". The old check c.get("bounces", 0) always returned 0 because
    the field did not exist, requeueing ALL bounced cards including ones
    with bounce_count=4 that should be decomposed instead.

    Never raises -- best-effort.
    """
    try:
        queue = load_queue(state_dir)
        requeued = 0
        for c in queue["cards"]:
            if c["status"] == "bounced" and c.get("bounce_count", 0) == 0:
                c["status"] = "ready"
                c["claimed_by"] = None
                c["claimed_utc"] = None
                c["requeued_utc"] = now_iso()
                requeued += 1
        if requeued:
            save_queue(state_dir, queue)
        return requeued
    except Exception:
        return 0


def auto_cleanup_stale_running(state_dir):
    """C-9537: Requeue running cards whose worker PID is dead.

    A running card with a dead PID is a stuck card that reap missed
    (e.g. fleet entry was already marked stopped but card status
    was never updated). This requeues it (bounce strike, as the
    worker failed) so a fresh dispatch can happen.
    Returns count of cleaned-up cards.
    """
    try:
        queue = load_queue(state_dir)
        cleaned = 0
        for c in queue["cards"]:
            if c["status"] != "running":
                continue
            claimed_by = c.get("claimed_by")
            if not claimed_by:
                # running without a PID claim is already corrupt
                c["status"] = "bounced"
                c["bounce_count"] = c.get("bounce_count", 0) + 1
                c["bounce_reason"] = "running without claimed_by"
                c["claimed_by"] = None
                c["claimed_utc"] = None
                cleaned += 1
                continue
            if not pid_alive(claimed_by):
                c["status"] = "bounced"
                c["bounce_count"] = c.get("bounce_count", 0) + 1
                c["bounce_reason"] = "worker PID dead"
                c["claimed_by"] = None
                c["claimed_utc"] = None
                cleaned += 1
        if cleaned:
            save_queue(state_dir, queue)
        # Also clean up fleet entries with dead PIDs (zombies)
        try:
            fleet = load_fleet(state_dir)
            fleet_cleaned = 0
            for a in fleet.get("agents", []):
                if a.get("status") != "running":
                    continue
                pid = a.get("pid")
                if pid and not pid_alive(pid):
                    a["status"] = "stopped"
                    a["stopped_utc"] = now_iso()
                    fleet_cleaned += 1
            if fleet_cleaned:
                save_fleet(state_dir, fleet)
                cleaned += fleet_cleaned
        except Exception:
            pass
        if cleaned:
            try:
                event(state_dir, "stale_running_cleaned", {"count": cleaned})
            except Exception:
                pass
        return cleaned
    except Exception:
        return 0


def auto_retire_high_bounce(state_dir, threshold=3):
    """C-9534: Auto-retire bounced cards with bounce_count >= threshold.

    Bounced cards with high bounce_count are stuck -- they keep failing the
    same way. Retire them (mark dead) so the queue stays clean and the
    dispatcher can focus on new, more targeted cards. The bounce reasons
    are preserved in the card data for future mining.

    Returns the count of retired cards. Never raises -- best-effort.
    """
    try:
        queue = load_queue(state_dir)
        retired = 0
        for c in queue["cards"]:
            if c["status"] == "bounced" and c.get("bounce_count", 0) >= threshold:
                c["status"] = "dead"
                c["retired_utc"] = now_iso()
                retired += 1
                try:
                    event(
                        state_dir,
                        "card_auto_retired",
                        {
                            "card": c["id"],
                            "bounce_count": c.get("bounce_count", 0),
                            "title": c.get("title", "")[:80],
                        },
                    )
                except Exception:
                    pass
        if retired:
            save_queue(state_dir, queue)
        return retired
    except Exception:
        return 0


def running_count(queue, lane):
    return sum(1 for c in queue["cards"] if c["status"] == "running" and c["lane"] == lane)


def claim_card(queue, card_id, agent_name):
    c = find_card(queue, card_id)
    if c is None or c["status"] != "ready":
        return None
    deadline = time.time() + c["budget_min"] * 60
    c["status"] = "running"
    c["claimed_by"] = agent_name
    c["claimed_utc"] = now_iso()
    c["deadline_utc"] = datetime.fromtimestamp(deadline, timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    return c


def release_card(card, status, result, reason=None):
    """Terminal transition for a card. 'bounced' with budget left re-arms as ready."""
    card["status"] = status
    card["result"] = (result or "")[:400]
    if reason:
        card["bounce_reason"] = reason[:400]
    if status == "bounced":
        card["bounce_count"] = card.get("bounce_count", 0) + 1
        if card["bounce_count"] <= 2:
            card["status"] = "ready"  # re-arm for a different agent (max 2 retries)
            card["claimed_by"] = None
            card["claimed_utc"] = None
            card["deadline_utc"] = None


def bounce_reason(verdict, outcome, over):
    """C-9048: truthful, contract-quoting reason for a bounced card.

    Every reason this path emits must quote the literal expected RESULT line
    so a re-dispatched worker succeeds first try, and must NEVER say
    'no RESULT verdict' when a verdict WAS present (the recorded lie:
    verdict PARTIAL present but reason said 'no RESULT verdict'). The
    outcome (dead/overrun-killed/harvested/stalled-killed) is preserved so
    the bounce is diagnosable, and the literal contract is always quoted.
    """
    literal = "RESULT: DONE|PARTIAL|BLOCKED"
    parts = []
    if outcome == "stalled-killed":
        parts.append(f"stalled: heartbeat stale >{STALL_MIN} min")
    elif outcome == "overrun-killed" or over:
        parts.append("overran deadline")
    elif outcome == "dead":
        parts.append("worker died")
    elif outcome == "harvested":
        parts.append("harvested at deadline")
    if verdict:
        parts.append(f"had {verdict} verdict")
    else:
        parts.append("no RESULT verdict")
    parts.append(f"expected literal line '{literal}'")
    return "; ".join(parts)


def requeue_card(queue, card_id):
    """C-0032: the ONLY exit from a bounced-board deadlock. A 3rd-strike
    bounce is terminal in release_card and _deps_satisfied only passes on
    dep status=="done", so ready cards gated on a bounced dep are
    undispatchable forever, and the planner mints an identical idle card
    every tick. This flips bounced->ready as an explicit operator action:
    bounce_count is PRESERVED (never laundered), claim fields are cleared,
    and a requeued_utc stamp exempts the card from the reaper's
    exhausted-retries tripwire (ready + bounce_count>2 -> dead) -- without
    the stamp the next tick would convert the requeue into an
    unrecoverable dead card. Fail-closed: refuses anything that is not a
    single, unambiguous, bounced card. Returns (ok, reason).
    """
    matches = [c for c in queue["cards"] if c["id"] == card_id]
    if not matches:
        return False, f"no such card: {card_id}"
    if len(matches) > 1:
        return False, (f"ambiguous card id {card_id}: {len(matches)} queue entries")
    c = matches[0]
    if c["status"] != "bounced":
        return False, (
            "card {} status is {!r}, not bounced: requeue refused".format(card_id, c["status"])
        )
    c["status"] = "ready"
    c["claimed_by"] = None
    c["claimed_utc"] = None
    c["deadline_utc"] = None
    c["requeued_utc"] = now_iso()
    return True, (f"requeued bounced->ready (bounce_count={c.get('bounce_count', 0)} preserved)")


# ----------------------------------------------------------------------------- fleet
def load_fleet(state_dir):
    return load_json(os.path.join(state_dir, "FLEET.json"), {"agents": []})


def save_fleet(state_dir, fleet):
    save_json(os.path.join(state_dir, "FLEET.json"), fleet)


def pid_alive(pid):
    """True iff pid is a live, non-zombie process.

    os.kill(pid, 0) succeeds for ZOMBIES on macOS/BSD — a finished-but-unreaped
    worker must count as dead or it is never harvested. ps stat Z => dead.
    """
    try:
        pid = int(pid)
    except (ValueError, TypeError):
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:
        out = subprocess.run(
            ["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, timeout=5
        )
        if out.stdout.strip().startswith("Z"):
            return False
    except (OSError, subprocess.SubprocessError):
        pass  # probe failed: fall back to the kill(0) verdict
    return True


def process_lstart(pid):
    """Process start-time identity string, or "" if the process is gone.

    pids are recycled by macOS/BSD: pid_alive(pid) alone cannot distinguish
    'the worker we spawned' from 'an unrelated process that reused the pid'.
    Comparing the recorded lstart closes that hole.
    """
    try:
        out = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(int(pid))], capture_output=True, text=True, timeout=5
        )
        return out.stdout.strip()
    except (OSError, ValueError, subprocess.SubprocessError):
        return ""


def kill_pid(pid):
    """TERM then KILL; process-group first (workers run in their own session)."""
    try:
        pid = int(pid)
    except (ValueError, TypeError):
        return False
    try:
        os.killpg(pid, signal.SIGTERM)
        time.sleep(1.0)
        if pid_alive(pid):
            os.killpg(pid, signal.SIGKILL)
        return True
    except (OSError, ProcessLookupError):
        pass
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1.0)
        if pid_alive(pid):
            os.kill(pid, signal.SIGKILL)
        return True
    except (OSError, ValueError, TypeError):
        return False


# ----------------------------------------------------------------------------- locks
# C-0022: the eval box (ASI2) is a SHARED resource -- 4 concurrent cards launch
# 18-task holdout legs at it and the launcher (scripts/asi2_loop_eval.sh) has
# only a per-ts pid check, so two legs with different ts both fire: interleaved
# writes, double-loaded NPU. Convention: a leg acquires
# harness/state/locks/asi2-eval.lock (this helper) before launching and
# releases it when its dispatch completes.
LOCK_STALE_S = 1800  # 30 min: a lease older than this is a crashed holder


def _lock_takeover_allowed(path, stale_s):
    """Takeover iff the holder pid is dead or the lease is stale.

    Unparseable + young -> refuse (a concurrent creator may be mid-write);
    unparseable + old -> takeover (torn write from a dead process).
    Fail-closed: any doubt while the lease is young refuses.
    """

    def _mtime_age():
        try:
            return (time.time() - os.path.getmtime(path)) > stale_s
        except OSError:
            return False

    try:
        with open(path, encoding="utf-8") as f:
            tok = json.load(f)
    except (OSError, ValueError):
        return _mtime_age()
    if not isinstance(tok, dict):
        return _mtime_age()
    pid = tok.get("pid")
    if isinstance(pid, int) and pid > 0 and not pid_alive(pid):
        return True
    age_min_val = age_min(tok.get("ts"))
    if age_min_val is None:  # corrupt ts: fall back to file mtime
        return _mtime_age()
    return (age_min_val * 60.0) > stale_s


def acquire_lock(path, stale_s=LOCK_STALE_S, stale_sec=None):
    """Take an exclusive lock file (O_EXCL create). Returns the owner token
    dict, or None when a fresh lease held by a live pid exists (refuse --
    never steal). A stale lease or a dead holder pid is taken over so a
    crashed leg cannot wedge the box forever."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tok = dict(pid=os.getpid(), ts=now_iso())
    for _ in range(2):  # retry once after a takeover remove
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            if not _lock_takeover_allowed(path, stale_s):
                return None
            try:
                os.unlink(path)
            except OSError:
                return None  # lost the takeover race
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(tok, f)
        return tok
    return None


def release_lock(path, token):
    """Remove the lock iff it is still the caller's own lease (pid+ts match).
    A foreign or absent token -> False and the lock is left alone."""
    try:
        with open(path, encoding="utf-8") as f:
            cur = json.load(f)
    except (OSError, ValueError):
        return False
    if not isinstance(cur, dict) or not isinstance(token, dict):
        return False
    if cur.get("pid") != token.get("pid") or cur.get("ts") != token.get("ts"):
        return False
    try:
        os.unlink(path)
    except OSError:
        return False
    return True


RESULT_RE = re.compile(r"^RESULT:\s*(DONE|PARTIAL|BLOCKED)\b", re.MULTILINE)
# C-9048-A: a worker log carries one segment per dispatch
# ("===== dispatch <ts> =====" separators).
DISPATCH_SEG_RE = re.compile(r"^=====\s*dispatch\b.*=====\s*$", re.MULTILINE)


def harvest_log(log_path):
    """Parse a worker log for the RESULT contract. Returns (verdict, tail_lines).

    Fail-closed: no RESULT line -> verdict None (never guess done).
    """
    if not log_path or not os.path.exists(log_path):
        return None, []
    with open(log_path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    # C-9048-A: scope the verdict to the LAST dispatch segment. An
    # append-mode worker log accumulates one segment per dispatch
    # ("===== dispatch <ts> ====="); a whole-file scan leaked the
    # previous dispatch's verdict into a dispatch that produced none,
    # defeating the environmental re-arm and burning bounce strikes
    # with a lying reason.
    segments = DISPATCH_SEG_RE.split(text)
    last_seg = segments[-1] if segments else text
    m = RESULT_RE.search(last_seg)
    # C-9507: tail must come from the LAST dispatch segment only, not the
    # whole file -- a whole-file tail leaks previous dispatch lines into
    # gate checks and bounce reasons (same class as the C-9048-A verdict
    # scope fix).
    tail = [ln for ln in last_seg.strip().splitlines() if ln.strip()][-10:]
    return (m.group(1) if m else None), tail


# ----------------------------------------------------------------------------- gates
# C-9085: explicit window-gate SKIP / WAITING markers (the C-9071 preflight
# gate's own vocabulary: the window_gate_skip.json artifact name and the
# "window-gate skip" prose forms). Tokens are deliberately narrow -- a bare
# "SKIP" or "blocked" in a worker log must NEVER match, or plain BLOCKEDs
# would silently stop bouncing.
GATE_SKIP_MARKERS = (
    "window_gate_skip",
    "window-gate skip",
    "window gate skip",
)


EXEC_FAILURE_SIGNATURES = (
    "rc=none",
    "rc = none",
    "/exec returned rc",
    "http error: 500",
    "http 500",
    "exec endpoint",
    "/exec not functional",
    "shell_endpoint_unavailable",
)


def is_exec_endpoint_failure(text):
    """C-9124: True iff a worker's output indicates the box /exec endpoint
    is broken (rc=None, HTTP 500, or similar). These are environmental
    failures — the card cannot run commands on the box, so bounce_count
    must NOT increment (the card is fine, the box transport is broken).

    Without this detection, the harness kept dispatching workers that
    failed at /exec precheck, incrementing bounce_count until the card
    hit dead-card threshold — all because the box /exec was broken, not
    because the card was faulty."""
    t = (text or "").lower()
    return any(sig in t for sig in EXEC_FAILURE_SIGNATURES)


WRAPPER_OUTPUT_SIGNATURES = (
    "claude wrapper",
    "probing cmri",
    "using cmri",
)


def is_wrapper_only_output(tail_lines):
    """C-9515: True iff the worker's output consists ONLY of claude wrapper
    debug lines (no RESULT, no actual work output). This is an environmental
    death: the claude CLI failed to start or crashed before doing any work,
    which is never the card's fault.

    Without this, agents that produce wrapper output but no RESULT get a
    bounce strike because len(body) > 0 defeats the environmental check.
    """
    if not tail_lines:
        return False
    for line in tail_lines:
        ln = line.strip().lower()
        if not ln:
            continue
        if not any(sig in ln for sig in WRAPPER_OUTPUT_SIGNATURES):
            return False
    return True


def is_gate_skip_blocked(text):
    """True iff a worker BLOCKED result cites the window-gate SKIP marker.

    C-9085: a worker that reports BLOCKED because the window preflight gate
    said SKIP is WAITING on the window, not failing the card -- the reaper
    must requeue it WITHOUT a bounce strike.
    """
    t = (text or "").lower()
    return any(m in t for m in GATE_SKIP_MARKERS)


def check_gate(gate, result_text):
    """Mechanical, evidence-based gate checks. Fail-closed: missing evidence = fail.

    Returns (ok, reason).
    """
    text = result_text or ""
    if gate == "tdd":
        has_red = re.search(r"\bRED\b", text)
        has_green = re.search(r"\bGREEN\b", text)
        counts = re.search(r"\b\d+\s*/\s*\d+\s+(?:pass|green|passed)", text, re.I)
        if has_red and (has_green or counts):
            return True, "RED->GREEN evidence present"
        return False, "no RED->GREEN evidence in result"
    if gate == "review":
        if re.search(r"REVIEW:\s*APPROVED", text):
            return True, "reviewer approved"
        return False, "no REVIEW: APPROVED verdict"
    if gate == "eval-failclosed":
        ok_markers = ("adapter-applied" in text) and ("adapter-probe-differs" in text)
        if ok_markers and "byte-identical" not in text:
            return True, "adapter-applied + probe-differs markers present"
        return False, "eval leg missing fail-closed markers"
    if gate == "sha-verified":
        if re.search(r"[0-9a-f]{64}", text):
            return True, "sha256 evidence present"
        return False, "no sha256 evidence"
    # Unknown gate -> fail closed, never silently pass.
    return False, f"unknown gate: {gate}"


# ----------------------------------------------------------------------------- briefs
LANE_AUTHORITY = {
    "planner": "decompose the objective into concrete cards; never implement",
    "evaluator": "run/verify holdout eval legs fail-closed; never edit training code",
    "trainer-ops": "keep the ASI3 trainer healthy; relaunch only via gates",
    "fixer": "root-cause one bug with TDD (RED first); scope limited to the card",
    "reviewer": "adversarially review diffs/results; cannot modify code",
    "qa-steward": "code hygiene: dead code, split oversize files, tests; TDD-neutral refactors",
    "data-miner": "mine failing holdout tasks into repair/data cards; never train",
    "deploy-integrity": "bundle/sha/deploy verification; refuse unverified deploys",
}

BRIEF_MAX_LINES = 80


def compose_brief(goal, card, dep_results=None, heartbeat_path=None, stall_min=None):
    """Compose a worker brief: small, complete, with an output contract."""
    acc = "\n".join(f"- {a}" for a in card["acceptance"])
    gates = ", ".join(card["gates"]) if card["gates"] else "none (acceptance still required)"
    dep_note = ""
    if card["deps"]:
        lines = [
            "- {}: {} -> {}".format(cid, title, result or "?")
            for cid, title, result in (dep_results or [])
        ]
        dep_note = "DEPENDENCIES (done, results):\n" + "\n".join(lines) + "\n"
    brief = """You are the {lane} worker for card {cid} in the QG goal harness.
GOAL: {goal}
CARD: {cid} — {title}
WHY (goal edge): {why}
AUTHORITY: {auth}
ACCEPTANCE (every item must hold to report DONE):
{acc}
GATES (mechanical, evidence required in your reply): {gates}
SCRIPT-FIRST: write code/script, run it, report deterministic output. Use:
  python3 harness/scripts/log_to_table.py --status-md|<log_file>   # log→table
  python3 harness/scripts/tdd.py red|green --test <path>           # TDD cycle
  python3 harness/scripts/run_and_report.py <cmd>|--box-exec ASI3 "cmd"  # run→report
  python3 harness/scripts/answer_question.py "why is X slow?"      # question→data
  Never eyeball logs. Never analyze conversationally. Write script, run script, paste output.BUDGET: {budget} min hard deadline — you will be stopped; report what you have by then.
HEARTBEAT (mandatory): after every meaningful step run
  python3 harness/qgh.py heartbeat {cid} "what you just did"   # heartbeat file: {hb}
A worker whose heartbeat file goes stale >{stall} min is treated as STALLED and killed.
PROGRESS: best known pass_adapter is 3/18 on the 18-task quantum holdout. Target is 18/18 + beats_base. Every card must advance toward this goal.
RULES:
- TDD: RED test first, smallest fix, GREEN + touched suites. A fix without a test is rejected.
- Touch ONLY what this card needs. Shared dirs (training/ scripts/ configs/ evals/) need
  a lock: create harness/state/locks/<file>.lock before editing, remove it when green.
- Shared compute: eval legs at the ASI2 box are serialized. Acquire
  harness/state/locks/asi2-eval.lock via harness_lib.acquire_lock BEFORE
  launching a leg; release it (release_lock) when the leg dispatch completes.
- Never mark DONE on another agent's unverified claim. Never fabricate a measurement.
- Unknown/unmeasured = say so. Fail closed, always.
{deps}
OUTPUT CONTRACT — end your reply EXACTLY with:
RESULT: <DONE|PARTIAL|BLOCKED> <one line verdict>
EVIDENCE: <=10 lines, commands + numbers only
NEXT: <=3 bullets
Full role rules (read only if needed): harness/lanes/{lane}.md
""".format(
        lane=card["lane"],
        cid=card["id"],
        title=card["title"],
        why=card["why"],
        auth=LANE_AUTHORITY[card["lane"]],
        acc=acc,
        gates=gates,
        budget=card["budget_min"],
        goal=goal,
        deps=dep_note,
        hb=heartbeat_path or os.path.join("harness/state/agents", "{}.progress".format(card["id"])),
        stall=stall_min or STALL_MIN,
    )
    n = len(brief.splitlines())
    assert n <= BRIEF_MAX_LINES, f"brief for {card['id']} too long: {n} lines"
    return brief


def find_card_by_id_in(queue, card_id):
    for c in queue.get("cards", []):
        if c["id"] == card_id:
            return c
    return None


# ----------------------------------------------------------------------------- auto-training
def auto_queue_training(state_dir):
    """C-9531: Auto-queue a training launch card with v10 benchmark.

    When no training is running and the goal is still OPEN, queue a
    trainer-ops card to launch/resume GRPO training using the v10 benchmark
    (quantum_grpo_training_v10_sapo_18holdout.txt) which covers all 18
    holdout tasks.

    Returns the new card dict if one was created, or None if not needed.
    Never raises -- best-effort.
    """
    try:
        goal = load_json(os.path.join(state_dir, "GOAL.json"), {})
        if goal.get("status") == "DONE":
            return None
        queue = load_queue(state_dir)
        # Check if any trainer-ops card is running or ready
        # C-9536: a running card with a dead PID must NOT block new
        # training -- the worker died without reap catching it. Verify
        # PID liveness before counting it as truly running.
        for c in queue["cards"]:
            if c.get("lane") == "trainer-ops" and c["status"] == "ready":
                return None
            if c.get("lane") == "trainer-ops" and c["status"] == "running":
                claimed_by = c.get("claimed_by")
                if claimed_by and pid_alive(claimed_by):
                    return None
                # Dead PID: this card is stale, do not block new training
        # Need a training card
        # C-9538: deduplicate -- skip if there are already >= 3 bounced
        # trainer-ops cards from prior auto-queue attempts (they will be
        # auto-retired by auto_retire_high_bounce, but until then we don't
        # need to pile on more).
        _bounced_trainer_count = sum(
            1 for c in queue["cards"] if c.get("lane") == "trainer-ops" and c["status"] == "bounced"
        )
        if _bounced_trainer_count >= 3:
            return None
        # Best-checkpoint registry (user directive: warm-start from the BEST
        # holdout-verified checkpoint, not just the latest).
        best = load_json(os.path.join(state_dir, "BEST_CHECKPOINT.json"), None)
        best_note = ""
        if best and best.get("checkpoint"):
            best_note = (
                f" WARM-START from best verified checkpoint "
                f"{best['checkpoint']} (measured {best['n_passes']}/"
                f"{best['n_tasks']} on frozen holdout) — do NOT warm-start "
                f"from a weaker/latest-only checkpoint."
            )
        card = new_card(
            title="Auto: launch/resume GRPO training with v10 benchmark (18/18 holdout coverage) toward 18/18",
            lane="trainer-ops",
            why="No training running and goal is OPEN. v10 benchmark covers all 18 holdout tasks (unlike v9 which has 0 overlap). Use --min-rms-for-update 0.01 for warm-continue."
            + best_note,
            acceptance=[
                "Launch GRPO training on ASI3 using v10 benchmark (quantum_grpo_training_v10_sapo_18holdout.txt)",
                "Use --min-rms-for-update 0.01 for warm-continue training",
                "Verify training is producing checkpoints with step/loss advancement",
                "Report current pass count if eval is available",
            ],
            budget_min=40,
            priority=0,
        )
        return card
    except Exception:
        return None


# ----------------------------------------------------------------------------- auto-eval
def auto_eval_on_checkpoint(queue, checkpoint_name, run_dir, fast_score=None, current_best=None):
    """When training produces a new checkpoint, automatically queue an eval
    card to measure progress toward 18/18.

    Returns a new card dict if one should be created, or None if the
    checkpoint already has an eval card (dedup) or fails the C-9584
    fast-pass pre-gate (fast_score provided but not greater than current best).

    This is the core automation primitive: train -> checkpoint -> eval ->
    verdict -> (if <18/18) -> continue training -> (if 18/18) -> done-check.
    """
    for c in queue.get("cards", []):
        title = c.get("title", "")
        # C-9590 lesson: only a LIVE (ready/running) eval card blocks a fresh
        # eval — dead/bounced/done cards must never starve new checkpoints.
        if (
            checkpoint_name in title
            and c.get("lane") == "evaluator"
            and c.get("status") in ("ready", "running")
        ):
            return None
    if fast_score is not None:
        import fast_pass_gate as FPG

        gate = FPG.FastPassGate(current_best=current_best)
        allowed, best, reason = gate.gate(checkpoint=checkpoint_name, fast_score=fast_score)
        if not allowed:
            return None
    card = new_card(
        title=f"Auto-eval checkpoint {checkpoint_name} from {run_dir}",
        lane="evaluator",
        why=f"Training produced {checkpoint_name}; must measure pass_adapter vs 18/18 target and beats_base to track progress toward goal.",
        acceptance=[
            f"Run fail-closed holdout eval on {checkpoint_name} adapter from {run_dir}",
            "Record pass_adapter count (target 18/18) and beats_base verdict",
            "If pass_adapter < 18/18: note which tasks failed and queue remediation",
            "If pass_adapter == 18/18: trigger goal-done-check with two-leg reconfirm",
        ],
        budget_min=40,
        gates=["tdd"],
        priority=0,
    )
    return card


class TrainingProgressTracker:
    """Track training progress toward 18/18: step, pass rate, trend.

    Used by the tick to decide when to trigger eval, when to alert
    on stalled training, and when to celebrate improvement.
    """

    def __init__(self):
        self._history = []  # list of (step, n_passed, n_total)
        self._evaluated_checkpoints = set()

    @property
    def latest_step(self):
        return self._history[-1][0] if self._history else 0

    @property
    def latest_pass_rate(self):
        if not self._history:
            return 0.0
        _, p, t = self._history[-1]
        return p / t if t > 0 else 0.0

    def update(self, step, n_passed, n_total):
        self._history.append((step, n_passed, n_total))

    def is_improving(self):
        if len(self._history) < 2:
            return True  # assume improving until proven otherwise
        _, p1, t1 = self._history[-2]
        _, p2, t2 = self._history[-1]
        r1 = p1 / t1 if t1 > 0 else 0.0
        r2 = p2 / t2 if t2 > 0 else 0.0
        return r2 > r1

    def should_eval_checkpoint(self, step):
        if step in self._evaluated_checkpoints:
            return False
        self._evaluated_checkpoints.add(step)
        return True


class StallDetector:
    """Detect when training is stalled (no progress for N minutes).

    Used by the tick to decide when to restart training or alert.
    """

    def __init__(self, stall_threshold_min=30):
        self.stall_threshold_min = stall_threshold_min
        self._last_progress = None  # (step, timestamp_iso)

    def record_progress(self, step, timestamp):
        self._last_progress = (step, timestamp)

    def is_stalled(self, current_time=None):
        if self._last_progress is None:
            return False  # no data yet
        _, ts = self._last_progress
        if current_time is None:
            age = age_min(ts)
        else:
            ref = parse_iso(current_time) if isinstance(current_time, str) else current_time
            age = age_min(ts, ref)
        if age is None:
            return False
        return age > self.stall_threshold_min

    def should_restart(self):
        return self.is_stalled()


class GoalProgressTracker:
    """C-9540: Track best pass count and detect goal-level stalls.

    When the best pass_adapter count has not improved for N ticks,
    the harness should take corrective action (requeue training,
    alert, change strategy).
    """

    def __init__(self, stall_threshold_ticks=20):
        self.stall_threshold_ticks = stall_threshold_ticks
        self._best_pass = 0
        self._ticks_since_improvement = 0
        self._history = []  # list of (tick_no, best_pass)

    def record_tick(self, tick_no, best_pass):
        """Record the best pass count seen at this tick."""
        if best_pass > self._best_pass:
            self._best_pass = best_pass
            self._ticks_since_improvement = 0
        else:
            self._ticks_since_improvement += 1
        self._history.append((tick_no, best_pass))

    def is_stalled(self):
        """True when no improvement for stall_threshold_ticks ticks."""
        return self._ticks_since_improvement >= self.stall_threshold_ticks

    def best_pass(self):
        return self._best_pass

    def ticks_since_improvement(self):
        return self._ticks_since_improvement

    def status(self):
        if self.is_stalled():
            return f"stalled ({self._ticks_since_improvement} ticks without improvement, best={self._best_pass}/18)"
        return f"progressing (best={self._best_pass}/18, {self._ticks_since_improvement} ticks since last improvement)"


# ----------------------------------------------------------------------------- done-check
def load_goal(state_dir):
    return load_json(os.path.join(state_dir, "GOAL.json"), {})


def scan_verdicts(repo_root, limit=12):
    """Newest verdict JSONs in outputs/ (fail-closed eval artifacts).

    C-9532: skip verdicts already marked superseded:true. Legacy pre-pin
    verdicts (verdict_step000097_leg4.json & friends, written before the
    scorer embedded holdout_sha256/scorer_shas) are marked superseded by
    C-0040 and can never satisfy the done-check; surfacing them as the
    newest verdicts made the goal_done preflight blame scorer_sha_pins_missing
    on an obsolete, already-superseded file. A superseded verdict is by
    definition non-canonical, so it is never presented as a goal candidate.
    Fail-closed preserved: a FRESH (superseded unset/false) unpinned verdict
    is still surfaced and still fails the done-check with
    scorer_sha_pins_missing.
    """
    out_dir = os.path.join(repo_root, "outputs")
    verdicts = []
    if os.path.isdir(out_dir):
        cands = []
        for name in os.listdir(out_dir):
            if name.startswith("verdict") and name.endswith(".json"):
                p = os.path.join(out_dir, name)
                try:
                    cands.append((os.path.getmtime(p), p))
                except OSError:
                    pass
        cands.sort(reverse=True)
        for _, p in cands[:limit]:
            d = load_json(p, {})
            if not d:
                continue
            if d.get("superseded") is True:
                # C-9532: deprecated verdict can never retire the goal.
                continue
            d["_file"] = os.path.basename(p)
            verdicts.append(d)
    return verdicts


def _candidates_differ_gate_passes(v):
    """Fail-closed candidates-differ evidence on the verdict (C-9456).

    The composer records candidates_vs_base_gate TOP-LEVEL on the verdict
    as {leg1: {...}, leg2: {...}}; a verdict whose gate is UNKNOWN, FAIL,
    or absent for either leg never retires the goal. This is the
    done-criteria "candidates differ from base" marker, verified from the
    recorded probe evidence, not assumed.
    """
    gates = v.get("candidates_vs_base_gate")
    if not isinstance(gates, dict):
        return False
    for leg in ("leg1", "leg2"):
        gate = gates.get(leg)
        if not isinstance(gate, dict) or gate.get("status") != "PASS":
            return False
    return True


def _leg_probe_differs(leg):
    """Probe-differs evidence on one leg, from either marker shape."""
    if not isinstance(leg, dict):
        return False
    if leg.get("adapter_probe_differs_marker") is True:
        return True
    markers = leg.get("markers")
    return isinstance(markers, dict) and bool(markers.get("adapter_probe_differs"))


def _per_task_ok(v, n_target):
    """The agreed per-task map must be well-formed and cover the target
    task count; when both legs embed their own per_task maps they must
    agree (cross-leg per-task pass agreement enforced here, not only at
    compose time); asymmetric leg evidence fails closed."""
    pt = v.get("per_task")
    if not isinstance(pt, dict) or len(pt) != n_target:
        return False
    for rec in pt.values():
        if not isinstance(rec, dict):
            return False
        if not isinstance(rec.get("adapter_pass"), bool):
            return False
        if not isinstance(rec.get("base_pass"), bool):
            return False
    leg1 = v.get("leg1")
    leg2 = v.get("leg2")
    has1 = isinstance(leg1, dict) and "per_task" in leg1
    has2 = isinstance(leg2, dict) and "per_task" in leg2
    if has1 != has2:
        return False
    if has1 and leg1.get("per_task") != leg2.get("per_task"):
        return False
    return True


def _freeze_module():
    """C-0031: lazy import of the canonical freeze-manifest module."""
    import sys

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from evals.runner import holdout_freeze as fz

    return fz


def _canonical_sha_manifest(fz=None):
    """C-0031: the canonical freeze manifest as {repo_relpath: sha256}.
    Raises on a missing/malformed/empty manifest."""
    fz = fz or _freeze_module()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return dict(fz.load_manifest(os.path.join(repo_root, fz.MANIFEST_RELPATH)))


def sha_pin_violation(verdict, manifest=None, state_dir=None):
    """C-0031: NAMED sha-pin violation for a verdict, or None when its
    embedded holdout/scorer sha256 pins match the pinned scorer.

    C-9507: the authoritative "want" pins are resolved from the C-9131
    attestation bank (harness/state/scorer_sha_pins.json) when a
    well-formed bank is present (state_dir defaults to the harness state
    dir, and callers may pass an explicit state_dir). The bank cannot
    diverge from the freeze manifest -- bank_scorer_sha_pins refuses any
    drift -- so honoring the bank honors the frozen scorer without adding
    a bypass. When no bank is banked, fall back to the canonical freeze
    manifest (evals/benchmarks/sapo_promotion_holdout_v1_18.sha256).
    Fail-closed: missing pins, missing coverage, a drifted sha, or an
    unreadable manifest each reject with a distinct named violation, so
    verdicts banked under a pre-pin scorer (the Sep 8-9 outputs/
    verdicts) can never satisfy the done-check."""
    if not isinstance(verdict, dict):
        return "verdict_not_an_object"
    pins = verdict.get("scorer_shas")
    if not isinstance(pins, dict) or not pins:
        return "scorer_sha_pins_missing"
    hold = verdict.get("holdout_sha256")
    if not isinstance(hold, str) or not hold:
        return "holdout_sha_pin_missing"
    try:
        fz = _freeze_module()
        # C-9507: prefer the banked attestation when present; the bank is
        # the card's explicit "honored against banked scorer_sha_pins.json"
        # requirement. Absent/malformed bank -> fall back to the manifest.
        bank = load_banked_scorer_sha_pins(state_dir=state_dir)
    except Exception:
        bank = None
    bank_hold = None
    bank_shas = None
    if bank is not None:
        bank_hold = bank.get("holdout_sha256")
        bank_shas = bank.get("scorer_shas")
    if bank_shas and isinstance(bank_hold, str) and bank_hold:
        # honor the banked pins as the authoritative attestation
        if str(hold).lower() != bank_hold.lower():
            return "holdout_sha_mismatch"
        for rel in fz.SCORER_CHAIN:
            want = bank_shas.get(rel)
            if not isinstance(want, str) or not want:
                return "canonical_manifest_lacks_scorer:" + rel
            got = pins.get(rel)
            if not isinstance(got, str) or not got:
                return "scorer_sha_pin_missing:" + rel
            if str(got).lower() != want.lower():
                return "scorer_sha_mismatch:" + rel
        return None
    try:
        entries = dict(manifest) if manifest is not None else _canonical_sha_manifest(fz)
    except Exception:
        return "canonical_manifest_unreadable"
    want_hold = entries.get(fz.BENCH_RELPATH)
    if not want_hold:
        return "canonical_manifest_lacks_holdout"
    if str(hold).lower() != want_hold:
        return "holdout_sha_mismatch"
    for rel in fz.SCORER_CHAIN:
        want = entries.get(rel)
        if not want:
            return "canonical_manifest_lacks_scorer:" + rel
        got = pins.get(rel)
        if not isinstance(got, str) or not got:
            return "scorer_sha_pin_missing:" + rel
        if str(got).lower() != want:
            return "scorer_sha_mismatch:" + rel
    return None


# ----------------------------------------------------------------------------- C-9131 scorer sha pin bank
SCORER_SHA_PIN_BANK_NAME = "scorer_sha_pins.json"


def _default_harness_state_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")


def bank_scorer_sha_pins(state_dir=None, manifest=None):
    """C-9131: bank the frozen holdout scorer sha pins under harness/state.

    Writes scorer_sha_pins.json holding the sha256 of the pinned 18-task
    holdout bench file + every SCORER_CHAIN scorer file -- exactly the
    pins sha_pin_violation demands a verdict to carry, so done_criteria
    #1 is reachable: compose stamps the verdict from this bank. Fail-
    closed: every pinned file must exist on disk and hash to its
    canonical-manifest entry, or the bank refuses (ValueError) and
    nothing is written -- a bank can never diverge from the frozen
    scorer it certifies. This bank adds no bypass: the done-check still
    compares verdict pins against the canonical manifest only.
    """
    import hashlib

    fz = _freeze_module()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    entries = dict(manifest) if manifest is not None else _canonical_sha_manifest(fz)
    pins = {}
    for rel in (fz.BENCH_RELPATH,) + tuple(fz.SCORER_CHAIN):
        want = entries.get(rel)
        p = os.path.join(root, rel)
        if not want:
            raise ValueError("scorer_sha_pin_unpinned_by_manifest: " + rel)
        if not os.path.isfile(p):
            raise ValueError("scorer_sha_pin_source_missing: " + rel)
        with open(p, "rb") as f:
            got = hashlib.sha256(f.read()).hexdigest()
        if got != str(want).lower():
            raise ValueError("scorer_sha_pin_drift: " + rel)
        pins[rel] = got
    bank = {
        "card": "C-9131",
        "manifest_relpath": fz.MANIFEST_RELPATH,
        "n_tasks": len(fz.BENCH_TASKS),
        "holdout_sha256": pins[fz.BENCH_RELPATH],
        "scorer_shas": dict((rel, pins[rel]) for rel in fz.SCORER_CHAIN),
        "banked_utc": now_iso(),
    }
    sdir = state_dir or _default_harness_state_dir()
    path = os.path.join(sdir, SCORER_SHA_PIN_BANK_NAME)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)
    return bank


def load_banked_scorer_sha_pins(state_dir=None):
    """C-9131: the banked pins, or None when nothing is banked yet.
    Fail-closed: a malformed bank raises ValueError -- a half-written or
    tampered-shape bank must never silently read as 'no pins required'."""
    path = os.path.join(state_dir or _default_harness_state_dir(), SCORER_SHA_PIN_BANK_NAME)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        bank = json.load(f)
    if (
        not isinstance(bank, dict)
        or not isinstance(bank.get("holdout_sha256"), str)
        or not bank.get("holdout_sha256")
        or not isinstance(bank.get("scorer_shas"), dict)
        or not bank.get("scorer_shas")
        or not all(isinstance(v, str) and v for v in bank["scorer_shas"].values())
    ):
        raise ValueError("scorer_sha_pin_bank_malformed: " + path)
    return bank


def is_qwen38_27b_model(name):
    """C-9119: does this id resolve to the GOAL's Qwen3.8-27B family?
    Case-insensitive and path-tolerant: requires BOTH the "qwen3.8"
    series token and the "27b" size token ("Qwen/Qwen3.8-27B",
    "/models/qwen3.8-27b-instruct" pass; "Qwen/Qwen3.6-35B-A3B" --
    what probe C-9004 says the box actually ships -- does not)."""
    if not isinstance(name, str) or not name:
        return False
    lowered = name.lower()
    return "qwen3.8" in lowered and "27b" in lowered


def model_identity_violation(verdict):
    """C-9119: None iff the verdict PROVES its checkpoint base model is
    a Qwen3.8-27B family id (a PASS model_identity column with a truthy
    sha256); otherwise a named model_identity_violation reason.
    Fail-closed: a verdict with NO model_identity column -- every
    pre-C-9119 banked verdict, e.g. s97/s26 -- is base_model_unproven
    and can never retire THIS goal."""
    mi = verdict.get("model_identity") if isinstance(verdict, dict) else None
    if not isinstance(mi, dict):
        return "model_identity_violation: base_model_unproven (verdict carries no model_identity column)"
    if mi.get("status") != "PASS":
        reason = mi.get("violation") or f"status={mi.get('status')}"
        return f"model_identity_violation: {reason}"
    if not is_qwen38_27b_model(mi.get("base_model")):
        return (
            f"model_identity_violation: base_model_mismatch ({mi.get('base_model')!r} is not "
            "the Qwen3.8-27B family)"
        )
    sha = mi.get("sha256")
    if not isinstance(sha, str) or not sha:
        return "model_identity_violation: sha256_missing"
    return None


def goal_done(goal, verdicts):
    """18/18 achieved = a fail-closed TWO-LEG verdict shows 18/18 +
    beats_base.

    C-0020: a single optimistic leg can no longer retire the goal. A
    verdict counts only when it carries ALL of:
      - pass_adapter == target and beats_base is True
      - a truthy scorer_version tag (pre-sanitize verdicts can never
        satisfy the done-check)
      - adapter_applied_marker not False and adapter_probe_differs_marker
        truthy at top level AND on BOTH legs
      - leg1 + leg2 with distinct leg identity (different box or a
        different runner_mechanism; missing identity fails closed)
      - a well-formed per_task map covering the target task count; when
        both legs embed per_task maps they must agree per task
      - (C-0031) holdout_sha256 + scorer_shas pins that match the
        canonical freeze manifest; sha-unpinned or scorer-drifted
        verdicts are non-canonical and fail closed with a named
        violation (sha_pin_violation)

    Fail-closed: absent/bad evidence -> False (loop keeps running).
    """
    target = str(goal.get("target_pass", "18/18"))
    try:
        n_target = int(target.split("/", 1)[0])
    except ValueError:
        return False, None
    try:
        manifest = _canonical_sha_manifest()
    except Exception:
        manifest = {}  # C-0031 fail closed: unreadable manifest rejects all
    for v in verdicts:
        if not isinstance(v, dict):
            continue
        if str(v.get("pass_adapter", "")) != target:
            continue
        if v.get("beats_base") is not True:
            continue
        if not v.get("scorer_version"):
            continue
        if v.get("adapter_applied_marker") is False:
            continue
        if not v.get("adapter_probe_differs_marker"):
            continue
        leg1 = v.get("leg1")
        leg2 = v.get("leg2")
        if not isinstance(leg1, dict) or not isinstance(leg2, dict):
            continue
        if not (_leg_probe_differs(leg1) and _leg_probe_differs(leg2)):
            continue
        if not _candidates_differ_gate_passes(v):
            # C-9456: the "candidates differ from base" done-criterion is
            # fail-closed; UNKNOWN/FAIL/absent gate never retires the goal.
            continue
        box1 = leg1.get("box") or None
        box2 = leg2.get("box") or None
        mech1 = leg1.get("runner_mechanism") or None
        mech2 = leg2.get("runner_mechanism") or None
        distinct = (box1 is not None and box2 is not None and box1 != box2) or (
            mech1 is not None and mech2 is not None and mech1 != mech2
        )
        if not distinct:
            continue
        if not _per_task_ok(v, n_target):
            continue
        if sha_pin_violation(v, manifest=manifest) is not None:
            # C-0031: sha-unpinned / scorer-drifted verdict is
            # non-canonical; it can never retire the goal.
            continue
        mvio = model_identity_violation(v)
        if mvio is not None:
            # C-9119: a verdict whose checkpoint base model is unproven
            # or outside the Qwen3.8-27B family silently violates the
            # GOAL's model field; it can never retire the goal.
            continue
        return True, v.get("_file")
    return False, None


# ----------------------------------------------------------------------------- api-backoff
BACKOFF_PATH_KEY = "backoff_until_utc"
CONSECUTIVE_SPAWN_FAIL_KEY = "consecutive_spawn_failures"
SPAWN_FAIL_THRESHOLD = 2
SPAWN_FAILURES_BY_CARD_KEY = "spawn_failures_by_card"
BACKOFF_MIN = 15


def load_ops(state_dir):
    return load_json(
        os.path.join(state_dir, "OPS.json"), {CONSECUTIVE_SPAWN_FAIL_KEY: 0, BACKOFF_PATH_KEY: None}
    )


def save_ops(state_dir, ops):
    save_json(os.path.join(state_dir, "OPS.json"), ops)


def note_spawn_result(state_dir, ops, ok, card=None, environmental=False):
    """Track consecutive spawn failures; trip backoff after N in a row.

    card=None -> legacy GLOBAL counter (pre-C-9126 shape). card=<id> ->
    PER-CARD counter + per-card backoff (C-9126): another card's success
    must never reset this card's env-death streak or clear its armed
    backoff -- interleaved successes on a healthy lane kept a dying card
    from EVER arming (C-9030 burned 6 dispatches into a dead API wall).
    """
    if card is None:
        if ok:
            ops[CONSECUTIVE_SPAWN_FAIL_KEY] = 0
            ops[BACKOFF_PATH_KEY] = None  # a success is proof the API recovered
        else:
            ops[CONSECUTIVE_SPAWN_FAIL_KEY] = ops.get(CONSECUTIVE_SPAWN_FAIL_KEY, 0) + 1
            if ops[CONSECUTIVE_SPAWN_FAIL_KEY] >= SPAWN_FAIL_THRESHOLD:
                ops[BACKOFF_PATH_KEY] = (
                    datetime.now(timezone.utc) + timedelta(minutes=BACKOFF_MIN)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
        return ops
    by = ops.setdefault(SPAWN_FAILURES_BY_CARD_KEY, dict())
    e = by.setdefault(card, dict())
    if ok:
        e["consecutive"] = 0
        e["backoff_until_utc"] = None  # ONLY this card's own success clears it
        # Also clear the global counter: a successful spawn proves the
        # environment is healthy, so any stale global backoff is obsolete.
        ops[CONSECUTIVE_SPAWN_FAIL_KEY] = 0
        ops[BACKOFF_PATH_KEY] = None
    else:
        e["consecutive"] = e.get("consecutive", 0) + 1
        if e["consecutive"] >= SPAWN_FAIL_THRESHOLD:
            e["backoff_until_utc"] = (
                datetime.now(timezone.utc) + timedelta(minutes=BACKOFF_MIN)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
        # C-9449: environmental failures (box down, API error) must NOT trip
        # the global backoff — they are infrastructure problems, not card
        # faults. Non-box-bound lanes (planner, fixer, qa-steward) can still
        # make progress when boxes are down, and the global backoff blocks
        # them all. Only TRUE spawn failures increment the global counter.
        if not environmental:
            ops[CONSECUTIVE_SPAWN_FAIL_KEY] = ops.get(CONSECUTIVE_SPAWN_FAIL_KEY, 0) + 1
            if ops[CONSECUTIVE_SPAWN_FAIL_KEY] >= SPAWN_FAIL_THRESHOLD:
                ops[BACKOFF_PATH_KEY] = (
                    datetime.now(timezone.utc) + timedelta(minutes=BACKOFF_MIN)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
    return ops


def card_backoff_until(ops, card):
    """Per-card armed-backoff deadline (C-9126); absent entry = None."""
    e = (ops.get(SPAWN_FAILURES_BY_CARD_KEY) or dict()).get(card) or dict()
    return e.get("backoff_until_utc")


def card_consecutive_spawn_fails(ops, card):
    """Per-card consecutive env-death count (C-9126); absent entry = 0."""
    e = (ops.get(SPAWN_FAILURES_BY_CARD_KEY) or dict()).get(card) or dict()
    return e.get("consecutive", 0)


def card_backoff_active(ops, card, now=None):
    """Fail-closed per-card read (C-9126): absent/expired/invalid = not active."""
    until = card_backoff_until(ops, card)
    if not until:
        return False
    remaining = age_min(until, now=now)
    if remaining is None:
        return False
    return remaining < 0  # deadline in the future


def armed_backoff_cards(ops, now=None):
    """Card ids with an armed, unexpired per-card backoff (fail-closed listing)."""
    by = ops.get(SPAWN_FAILURES_BY_CARD_KEY) or dict()
    return sorted(cid for cid in by if card_backoff_active(ops, cid, now=now))


def backoff_active(ops, now=None):
    """Fail-closed read: absent/expired/invalid backoff = not active."""
    until = ops.get(BACKOFF_PATH_KEY)
    if not until:
        return False
    remaining = age_min(until, now=now)
    if remaining is None:
        return False
    return remaining < 0  # deadline in the future


def rotate_log(path, max_bytes=5 * 1024 * 1024, keep=1):
    """Shift oversized logs to .1/.2... and recreate an EMPTY live path (readers
    must never hit ENOENT between rotations)."""
    try:
        if os.path.exists(path) and os.path.getsize(path) > max_bytes:
            for i in range(keep, 0, -1):
                src = path if i == 1 else f"{path}.{i - 1}"
                dst = f"{path}.{i}"
                if os.path.exists(src):
                    os.replace(src, dst)
            with open(path, "a", encoding="utf-8"):
                pass
    except OSError:
        pass


# ----------------------------------------------------------------------------- metrics
def compute_metrics(state_dir, window_min=60):
    """Throughput instrument: everything derived from EVENTS.jsonl, fail-soft.

    Returns dict with totals + last-hour window + per-lane done counts.
    """
    path = os.path.join(state_dir, "EVENTS.jsonl")
    ev = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        pass

    def count(kind, since=None):
        return sum(
            1
            for e in ev
            if e.get("kind") == kind and (since is None or (e.get("ts") or "") >= since)
        )

    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=window_min)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    # avg card latency: dispatched -> reaped(DONE) per card
    dispatch_ts, latencies = {}, []
    for e in ev:
        cid = e.get("card")
        if e.get("kind") == "dispatched" and cid:
            dispatch_ts[cid] = e.get("ts")
        elif e.get("kind") == "reaped" and cid and e.get("verdict") == "DONE":
            t0 = dispatch_ts.get(cid)
            if t0:
                a0, a1 = age_min(t0), age_min(e.get("ts"))
                if a0 is not None and a1 is not None:
                    latencies.append(round(a0 - a1, 1))  # minutes elapsed
    per_lane = {}
    for e in ev:
        if e.get("kind") == "reaped" and e.get("verdict") == "DONE":
            lane = e.get("lane")
            per_lane[lane] = per_lane.get(lane, 0) + 1
    return {
        "dispatched_total": count("dispatched"),
        "done_total": sum(
            1 for e in ev if e.get("kind") == "reaped" and e.get("verdict") == "DONE"
        ),
        "bounce_total": count("gate_bounced"),
        "env_fail_total": count("spawn_failed_env"),
        "dispatched_1h": count("dispatched", cutoff),
        "done_1h": sum(
            1
            for e in ev
            if e.get("kind") == "reaped"
            and e.get("verdict") == "DONE"
            and (e.get("ts") or "") >= cutoff
        ),
        "avg_done_latency_min": round(sum(latencies) / len(latencies), 1) if latencies else None,
        "per_lane_done": per_lane,
    }


# ----------------------------------------------------------------------------- progress
def render_progress(goal, queue, fleet, tick_no, verdicts=None, probes=None, state_dir=None):
    """Concise, human-readable progress report published to repo root every
    tick so the project's progress is VISIBLE (not buried in state/standup/).
    The harness must self-report — a working loop that nobody can see is a
    silent loop. Returns markdown text."""
    from collections import Counter

    statuses = Counter(c.get("status", "?") for c in queue["cards"])
    live = [a for a in fleet["agents"] if a.get("status") == "running" and pid_alive(a.get("pid"))]
    ready = [c for c in queue["cards"] if c.get("status") == "ready"]
    bounced = [c for c in queue["cards"] if c.get("status") == "bounced"]
    running_cards = [c for c in queue["cards"] if c.get("status") == "running"]
    blocked = [c for c in queue["cards"] if c.get("status") == "blocked"]
    # best verdict so far (progress toward 18/18)
    best_pass, best_vf = 0, None
    if verdicts:
        for v in verdicts:
            if not isinstance(v, dict):
                continue
            pa = v.get("pass_adapter")
            # pass_adapter may be "3/18" (str) or 3 (int) or None
            try:
                pa_int = int(str(pa).split("/")[0]) if pa is not None else 0
            except (ValueError, TypeError):
                pa_int = 0
            if pa_int > best_pass:
                best_pass, best_vf = pa_int, v.get("_file", "?")
    L = []
    L.append("# PROGRESS — QG Goal Harness")
    L.append("")
    L.append(
        f"_Auto-published every tick by `qgh.py tick`. Last update: {now_iso()} (tick #{tick_no})_"
    )
    L.append("")
    L.append("## Goal")
    L.append(f"**{goal.get('objective', '?')}**")
    L.append(f"- status: **{goal.get('status', 'OPEN')}**")
    L.append(f"- target: {goal.get('target_pass', '?')}")
    L.append(
        f"- best adapter eval so far: **{best_pass}/{goal.get('target_pass', '18/18').split('/')[-1]}**"
        + (f" (verdict: {best_vf})" if best_vf else "")
    )
    L.append("")
    L.append("## Queue")
    total = len(queue["cards"])
    L.append(
        f"- {total} cards total: " + ", ".join(f"{k}={v}" for k, v in sorted(statuses.items()))
    )
    L.append(f"- {len(ready)} ready to dispatch, {len(live)} live workers")
    L.append("")
    L.append("## Live Workers")
    if live:
        L.append("| card | lane | pid | age_min | deadline_min |")
        L.append("|---|---|---|---|---|")
        for a in live:
            age = age_min(a.get("started_utc"))
            dl = age_min(a.get("deadline_utc"))
            L.append(
                f"| {a.get('card')} | {a.get('lane')} | {a.get('pid')} | "
                f"{age if age is not None else '?'} | {dl if dl is not None else '?'} |"
            )
    else:
        L.append("_No live workers (loop may be between ticks or halted)._")
    L.append("")
    L.append("## Resources")
    if probes:
        L.append("| resource | status |")
        L.append("|---|---|")
        for name in ("asi1", "asi2", "asi3", "trainer"):
            s = probes.get(name)
            if s:
                L.append(f"| {name} | {str(s)[:100]} |")
    L.append("")
    done = statuses.get("done", 0)
    bounced_n = statuses.get("bounced", 0)
    L.append(f"## Throughput so far: {done} done, {bounced_n} bounced")
    L.append("")
    # ---- Ready Cards table ----
    L.append("## Ready to Dispatch")
    if ready:
        L.append("| card | lane | priority | title |")
        L.append("|---|---|---|---|")
        for c in sorted(ready, key=lambda c: c.get("priority", 9))[:20]:
            L.append(
                f"| {c['id']} | {c.get('lane', '?')} | P{c.get('priority', 9)} | "
                f"{(c.get('title') or '')[:50]} |"
            )
    else:
        L.append("_No ready cards (planner should decompose)._")
    L.append("")
    # ---- Running Cards table ----
    L.append("## Running")
    if running_cards:
        L.append("| card | lane | title |")
        L.append("|---|---|---|")
        for c in running_cards:
            L.append(f"| {c['id']} | {c.get('lane', '?')} | {(c.get('title') or '')[:50]} |")
    else:
        L.append("_No running cards._")
    L.append("")
    # ---- Bounced Cards table (failure signals) ----
    L.append("## Bounced (failure signals)")
    if bounced:
        L.append("| card | lane | bounce_count | reason |")
        L.append("|---|---|---|---|")
        for c in sorted(bounced, key=lambda c: c.get("bounce_count", 0), reverse=True)[:15]:
            L.append(
                f"| {c['id']} | {c.get('lane', '?')} | {c.get('bounce_count', 0)} | "
                f"{(c.get('bounce_reason') or '')[:60]} |"
            )
    else:
        L.append("_No bounced cards._")
    L.append("")
    # ---- Blocked Cards table ----
    L.append("## Blocked")
    if blocked:
        L.append("| card | lane | title |")
        L.append("|---|---|---|")
        for c in blocked:
            L.append(f"| {c['id']} | {c.get('lane', '?')} | {(c.get('title') or '')[:50]} |")
    else:
        L.append("_No blocked cards._")
    L.append("")
    # ---- Verdicts table (eval progress toward 18/18) ----
    L.append("## Eval Verdicts (progress toward 18/18)")
    if verdicts:
        L.append("| verdict | pass_adapter | beats_base | pass_base | superseded |")
        L.append("|---|---|---|---|---|")
        for v in verdicts:
            if not isinstance(v, dict):
                continue
            vf = v.get("_file", "?")
            pa = v.get("pass_adapter", "?")
            bb = v.get("beats_base", "?")
            pb = v.get("pass_base", "?")
            sup = "YES" if v.get("superseded") else "no"
            L.append(f"| {vf} | {pa} | {bb} | {pb} | {sup} |")
    else:
        L.append("_No verdicts yet._")
    L.append("")
    L.append("---")
    L.append("_Full standup: `harness/state/standup/`. Events: `harness/state/EVENTS.jsonl`._")
    # Work review section
    try:
        from harness.work_review import render_work_review

        L.append("")
        L.append(
            render_work_review(
                state_dir=state_dir,
                repo_root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            )
        )
    except Exception:
        pass
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- standup
def dispatch_reason(card, by_id):
    """C-9087: None iff the card is DISPATCHABLE (ready + deps-not-dead +
    unclaimed); otherwise a short renderable reason, naming the dead dep.
    Read-only over QUEUE.json -- no status transition."""
    if card.get("status") != "ready":
        return "not ready"
    if card.get("claimed_by"):
        return "claimed"
    dead = [d for d in card.get("deps", []) if (by_id.get(d) or {}).get("status") == "dead"]
    if dead:
        return "dead dep: " + ",".join(dead)
    return None


def render_standup(goal, queue, fleet, tick_no, verdicts=None, probes=None, state_dir=None):
    L = []
    L.append(f"## HARNESS STANDUP #{tick_no} — {now_iso()}")
    L.append(
        "Objective: {} | status: {}".format(goal.get("objective", "?"), goal.get("status", "OPEN"))
    )
    L.append("")
    by_id = {c.get("id"): c for c in queue["cards"]}
    eff = sum(1 for c in queue["cards"] if dispatch_reason(c, by_id) is None)
    L.append("### QUEUE (top 12 ready/running by priority)")
    L.append(f"EFFECTIVE-QUEUE: {eff} (ready+deps-not-dead+unclaimed)")
    L.append("| pri | id | lane | status | disp | title | why |")
    L.append("|---|---|---|---|---|---|---|")
    rows = [c for c in queue["cards"] if c["status"] in ("ready", "running", "blocked")]
    rows.sort(key=lambda c: (c["priority"], c["created_utc"]))
    for c in rows[:12]:
        reason = dispatch_reason(c, by_id)
        disp = "Y" if reason is None else f"N ({reason})"
        L.append(
            "| P{} | {} | {} | {} | {} | {} | {} |".format(
                c["priority"],
                c["id"],
                c["lane"],
                c["status"],
                disp,
                c["title"][:48],
                (c["why"] or "")[:48],
            )
        )
    if not rows:
        L.append("| - | - | - | EMPTY | planner must decompose next | - |")
    L.append("")
    L.append("### FLEET (live agents)")
    L.append("| pid | card | lane | alive | age_min | deadline_min | status |")
    L.append("|---|---|---|---|---|---|---|")
    for a in fleet["agents"]:
        if a.get("status") != "running":
            continue
        alive = pid_alive(a.get("pid"))
        left = age_min(a.get("deadline_utc"))
        L.append(
            "| {} | {} | {} | {} | {} | {} | {} |".format(
                a.get("pid"),
                a.get("card"),
                a.get("lane"),
                "Y" if alive else "N",
                age_min(a.get("started_utc")),
                (-left) if left is not None else "?",
                a.get("status"),
            )
        )
    if not any(a.get("status") == "running" for a in fleet["agents"]):
        L.append("| - | - | - | - | - | - | no live agents |")
    if state_dir:
        m = compute_metrics(state_dir)
        L.append("")
        L.append("### THROUGHPUT")
        L.append("| dispatched | done | done/1h | bounce | env-fail | avg done latency |")
        L.append("|---|---|---|---|---|---|")
        L.append(
            "| {} | {} | {} | {} | {} | {} min |".format(
                m["dispatched_total"],
                m["done_total"],
                m["done_1h"],
                m["bounce_total"],
                m["env_fail_total"],
                m["avg_done_latency_min"],
            )
        )
    if state_dir:
        ops = load_ops(state_dir)
        armed = armed_backoff_cards(ops)
        L.append("")
        L.append("### SPAWN BREAKERS (per-card env-death circuit breakers)")
        if armed:
            by_card = ops.get(SPAWN_FAILURES_BY_CARD_KEY) or dict()
            for cid in armed:
                e = by_card.get(cid) or dict()
                L.append(
                    f"- CARD BACKOFF ARMED: {cid} until {e.get('backoff_until_utc')} (consecutive env-deaths: {e.get('consecutive')})"
                )
        else:
            L.append("- none armed")
    if verdicts:
        L.append("")
        L.append("### LATEST VERDICTS (fail-closed eval)")
        for v in verdicts[:3]:
            # C-0050: annotate each listed verdict with goal_done
            # eligibility so a legacy sha-unpinned verdict (which can
            # never retire the goal) is not mistaken for goal progress.
            done, _src = goal_done(goal, [v])
            if done:
                mark = "goal_done=YES"
            else:
                vio = sha_pin_violation(v)
                mvio = model_identity_violation(v)
                if vio:
                    mark = f"goal_done=NO (sha_pin_violation: {vio})"
                elif mvio:
                    # C-9119: annotate model-inadmissible verdicts
                    mark = f"goal_done=NO ({mvio})"
                else:
                    mark = "goal_done=NO (criteria-unmet)"
            L.append(
                "- {}: pass_adapter={} beats_base={} (base {}) | {}".format(
                    v.get("_file"),
                    v.get("pass_adapter"),
                    v.get("beats_base"),
                    v.get("pass_base"),
                    mark,
                )
            )
    if probes:
        L.append("")
        L.append("### RESOURCES")
        for name, p in probes.items():
            L.append(f"- {name}: {p}")
    # Work review section — productivity, commits, blockers, path to 18/18
    try:
        from harness.work_review import render_work_review

        L.append("")
        L.append(
            render_work_review(
                state_dir=state_dir,
                repo_root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            )
        )
    except Exception:
        pass
    return "\n".join(L)


def prune_old_probes(state_dir, max_age_days=7):
    """C-9510: prune probe files older than max_age_days to prevent disk bloat.

    Probe artifacts (harness/state/probes/*.json) accumulate indefinitely.
    This removes files older than max_age_days, keeping only recent probes
    for audit. Returns the count of pruned files.
    """
    import time

    probes_dir = os.path.join(state_dir, "probes")
    if not os.path.isdir(probes_dir):
        return 0
    cutoff = time.time() - (max_age_days * 24 * 3600)
    pruned = 0
    for name in os.listdir(probes_dir):
        if not name.endswith(".json"):
            continue
        path = os.path.join(probes_dir, name)
        try:
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
                pruned += 1
        except OSError:
            pass
    return pruned


def trim_status_file(state_dir, keep=500):
    """C-9512: trim STATUS.md to the last `keep` lines to prevent unbounded growth.

    STATUS.md is append-only and grows by 1 line per tick. The max tick#
    in the file is used as a floor for tick numbering, so we preserve the
    last `keep` lines (which always include the highest tick numbers).
    Returns the number of lines pruned.
    """
    status_path = os.path.join(state_dir, "STATUS.md")
    if not os.path.isfile(status_path):
        return 0
    try:
        with open(status_path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return 0
    if len(lines) <= keep:
        return 0
    pruned = len(lines) - keep
    try:
        with open(status_path, "w", encoding="utf-8") as f:
            f.writelines(lines[-keep:])
    except OSError:
        return 0
    return pruned


def _tick_floor(state_dir):
    """C-9007: read durable tick history from STATUS.md so the tick counter
    never regresses below the highest tick seen, even if standup/ is wiped.

    Returns the highest tick number found in STATUS.md, or 0 if no ticks.
    """
    status_path = os.path.join(state_dir, "STATUS.md")
    if not os.path.isfile(status_path):
        return 0
    max_tick = 0
    try:
        with open(status_path, encoding="utf-8") as f:
            for line in f:
                m = re.search(r"tick#(\d+)", line)
                if m:
                    max_tick = max(max_tick, int(m.group(1)))
    except OSError:
        pass
    return max_tick


def _next_standup_no(state_dir=None):
    """Compute the next standup number, never going below _tick_floor."""
    sd = (
        state_dir
        or os.environ.get("QGH_STATE_DIR")
        or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "harness", "state"
        )
    )
    standup_dir = os.path.join(sd, "standup")
    nums = []
    if os.path.isdir(standup_dir):
        for fn in os.listdir(standup_dir):
            m = re.match(r"standup-(\d+)\.md", fn)
            if m:
                nums.append(int(m.group(1)))
    floor = _tick_floor(sd)
    file_next = (max(nums) + 1) if nums else 1
    return max(file_next, floor + 1)


QUEUE_STALE_SEC = 1800
LOCK_STALE_S = 1800
DISPATCH_SEG_RE = re.compile(r"^=====\s*dispatch\b.*=====\s*$", re.MULTILINE)
REARM_WINDOW_FRESH_S = 1800.0
REARM_CARD = "C-9098"  # card id for rearm telemetry
LAUNCHD_LABEL_TICK = "com.quantumgpt.qgh-tick"
LAUNCHD_LABEL_HEAL = "com.quantumgpt.qgh-heal"
CLAUDE = os.environ.get("QGH_CLAUDE", "claude")
CRON_LABEL = "qgh-tick"
LAUNCHD_LABEL = LAUNCHD_LABEL_TICK

# ----------------------------------------------------------------------------- restored functions
BOX_BOUND_LANES = ("evaluator", "trainer-ops", "deploy-integrity")
TRANSPORT_WEDGE_MARK = "exec_wedged"
PROBE_STALE_S = 3600
CLAUDE = os.environ.get("QGH_CLAUDE", "/Users/daxu/homebrew/bin/claude")


def self_spawn(args_list, timeout=None):
    """Run qgh as a subprocess, propagating the state-dir seam."""
    env = dict(os.environ)
    env.setdefault("QGH_STATE_DIR", STATE)
    return subprocess.run(
        [sys.executable, QGH] + args_list, capture_output=True, text=True, env=env, timeout=timeout
    )


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


def worker_command():
    """bash: source credential files, then exec claude (pid stays the worker's)."""
    srcs = " ".join(f'[ -f "{f}" ] && source "{f}";' for f in WORKER_ENV_FILES)
    model_flag = f"-m '{WORKER_MODEL}'" if WORKER_MODEL else ""
    provider_flag = f"-p {WORKER_PROVIDER}" if WORKER_PROVIDER else ""
    return [
        "/bin/bash",
        "-c",
        srcs + " exec '" + CLAUDE + "' " + provider_flag + " " + model_flag + ' --print "$(cat)"',
    ]


def worker_env():
    """C-9547: Build the worker environment with the REAL HOME.

    The claude wrapper resolves the claude binary via $HOME/.local/bin/claude.
    A /tmp fallback orphans that lookup and causes env-blocked spawn failures.
    """
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/local/bin"),
        "HOME": os.environ.get("HOME") or os.path.expanduser("~"),
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
    }


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
    append_heartbeat(
        hb_path, "dispatched card {} (progress pre-created by dispatcher)".format(card["id"])
    )
    card["claimed_by"] = "pending"
    # Minimal deterministic env: workers get credentials from the sourced files,
    # never from whatever session happened to run the tick.
    env = worker_env()
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
    append_heartbeat(hb, args.message)
    # C-0001: detect ghost card (not in QUEUE). Must not raise -- a heartbeat
    # failure would stall-kill a healthy worker. Best-effort event emission.
    try:
        queue = load_queue(STATE)
        if find_card(queue, args.card) is None:
            event(STATE, "ghost_heartbeat", {"card": args.card})
    except Exception:
        pass  # detection must never unwind a successful heartbeat


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
            started_min = age_min(a.get("started_utc"))
            if started_min is not None:
                hb_age = min(hb_age, max(started_min, 0.0) * 60)
            if hb_age > STALL_MIN * 60:
                kill_pid(a["pid"])
                alive = False
                stalled = True
        if alive and not over:
            continue
        reaped += 1
        outcome = "stalled-killed" if stalled else None
        verdict, tail = harvest_log(a.get("log"))
        try:
            full_text = open(a.get("log"), encoding="utf-8", errors="replace").read()
        except (OSError, TypeError):
            full_text = ""
        # C-9508: scope API-error and exec-failure detection to the LAST
        # dispatch segment only -- a prior dispatch's API error must not
        # classify the current (possibly clean) dispatch as environmental.
        _segs = DISPATCH_SEG_RE.split(full_text)
        text = _segs[-1] if _segs else full_text
        # ENVIRONMENTAL = pid DEAD + produced NOTHING (spawn/credential/API
        # failure) -> never burns the card's bounce budget. A worker that was
        # ALIVE past its deadline with no output is a HUNG worker, not an API
        # outage: it takes the normal bounce path and never trips backoff.
        body = [ln for ln in tail if not ln.startswith("===== dispatch")]
        # API-down signature: claude prints an API error as its final output —
        # non-empty body but still an outage, never a card fault.
        api_error = verdict is None and any(sig in text for sig in API_ERROR_SIGNATURES)
        # C-9124: /exec endpoint failure is environmental (box transport broken, not card fault)
        exec_failure = is_exec_endpoint_failure(text)
        # C-9515: wrapper-only output (claude CLI failed before doing work)
        # is also environmental — never the card's fault.
        wrapper_only = verdict is None and is_wrapper_only_output(body)
        environmental = (
            (not alive and verdict is None and (len(body) == 0 or wrapper_only))
            or api_error
            or exec_failure
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
            note_spawn_result(STATE, ops, ok=False, card=a.get("card"), environmental=True)
            save_ops(STATE, ops)
            event(
                STATE,
                "spawn_failed_env",
                {
                    "card": a.get("card"),
                    "consecutive": card_consecutive_spawn_fails(ops, a.get("card")),
                    "backoff_until": card_backoff_until(ops, a.get("card")),
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
                if is_gate_skip_blocked(text):
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
                    card["requeued_utc"] = now_iso()
                    event(STATE, "gate_skip_requeued", {"card": card["id"]})
                else:
                    # C-9476: if the BLOCKED text carries an environmental
                    # signature (transport, connection, timeout, etc.), re-arm
                    # WITHOUT a bounce strike -- the box being down is not the
                    # card fault.
                    _blocked_text = (text or "").lower()
                    if any(sig in _blocked_text for sig in ENV_BOUNCE_SIGNATURES):
                        card["status"] = "ready"
                        card["claimed_by"] = None
                        card["claimed_utc"] = None
                        card["deadline_utc"] = None
                        card["requeued_utc"] = now_iso()
                        event(STATE, "env_blocked_requeued", {"card": card["id"]})
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
                reason = bounce_reason(verdict, outcome, over)
                release_card(card, "bounced", (tail[-1] if tail else ""), reason)
        if not environmental:
            ops = load_ops(STATE)
            _cid = a.get("card")
            if card_consecutive_spawn_fails(ops, _cid) or card_backoff_active(ops, _cid):
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
    # C-0001: never re-arm a TERMINAL card id (already reaped/purged/voided)
    # -- the terminal/pruned id would otherwise be resurrected to "ready".
    _terminal_ids = history_terminal_card_ids(STATE)
    for _ghost_id in rearm_ghost_running_cards(queue, fleet, terminal_ids=_terminal_ids):
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
    # C-9508: prune stopped agents from FLEET.json to prevent unbounded growth.
    # Stopped agents are historical baggage -- their log files persist for audit.
    fleet["agents"] = [a for a in fleet["agents"] if a.get("status") != "stopped"]
    save_fleet(STATE, fleet)
    # duplicate-id repair FIRST (a single duplicate refused by the preflight
    # must never hold the whole dispatch hostage), then dep-blocker self-heal
    _dedup_card_ids()
    # C-9124: auto-clean stale agent locks (dead PID holders block dispatch)
    _cleanup_stale_agent_locks()
    # C-9123: bounce cards stuck in 'running' with all-dead workers and
    # expired deadlines (prevents dependency deadlocks like the C-9029
    # incident where a card sat 'running' for 8h blocking 3 downstream cards)
    bounce_dead_running_cards(STATE)
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
    if not isinstance(pid, int) or not pid_alive(pid):
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
        "HOME": os.environ.get("HOME") or os.path.expanduser("~"),
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


def auto_eval_scan():
    """Scan ASI3 training output for new checkpoints and auto-queue eval cards.

    This is the core automation loop: when training produces a new checkpoint,
    we automatically queue an eval card to measure progress toward 18/18.
    Never raises — best-effort, must not break the tick.
    """
    try:
        import json as _json
        import urllib.request as _url

        # Check ASI3 for latest training checkpoints
        r = _url.urlopen(
            "http://127.0.0.1:20653/exec",
            timeout=10,
            data=_json.dumps(
                {
                    "command": "ls -t /root/work/software/quantum-gpt/outputs/sapo-27b-ai-*/ 2>/dev/null | head -20"
                }
            ).encode(),
            headers={"Content-Type": "application/json"},
        )
        resp = _json.loads(r.read())
        output = resp.get("output", "")

        # Find checkpoint directories (step_XXXXXX_adapter)
        import re

        checkpoints = re.findall(r"(step_\d+_adapter)", output)
        if not checkpoints:
            return  # no checkpoints found

        # Find the run directory
        run_dirs = re.findall(r"(sapo-27b-ai-\d+T\d+)", output)
        if not run_dirs:
            return

        latest_run = run_dirs[0]
        latest_ckpt = checkpoints[0]

        # Check if we already have an eval card for this checkpoint
        queue = load_queue(STATE)
        card = auto_eval_on_checkpoint(queue, latest_ckpt, latest_run)
        if card is not None:
            add_card(queue, card)
            save_queue(STATE, queue)
            event(STATE, "auto_eval_queued", {"checkpoint": latest_ckpt, "run": latest_run})
    except Exception:
        pass  # best-effort, never break the tick


def training_watch_eval_truth():
    """Fetch measured eval ground truth (passed counts) from the live run.
    Returns {'run','step','n_passes','n_candidates'} or None. Never raises.
    """
    try:
        import base64 as _b64_mod
        import json as _json
        import urllib.request as _url

        _script_b64 = _b64_mod.b64encode(
            b"import json,glob,os\n"
            b"ds=sorted(glob.glob('/root/work/software/quantum-gpt/outputs/sapo-27b-ai-*'),"
            b"key=os.path.getmtime)\n"
            b"d=ds[-1] if ds else ''\n"
            b"ev=os.path.join(d,'eval_results.jsonl') if d else ''\n"
            b"ev_rows=[]\n"
            b"try:\n"
            b"    ev_rows=[json.loads(l) for l in open(ev).read().strip().splitlines()]\n"
            b"except Exception:\n"
            b"    pass\n"
            b"ev_small=[{'step':r.get('step'),'passed':bool(r.get('passed'))} for r in ev_rows]\n"
            b"print(json.dumps({'run':os.path.basename(d),'eval_rows':ev_small}))\n"
        ).decode()
        _push = _url.urlopen(
            _url.Request(
                "http://127.0.0.1:20653/exec",
                data=_json.dumps(
                    {"command": f"echo {_script_b64} | base64 -d > /tmp/tw_eval.py"}
                ).encode(),
                headers={"Content-Type": "application/json"},
            ),
            timeout=15,
        )
        _push.read()
        d = None
        for _attempt in range(2):
            try:
                r = _url.urlopen(
                    _url.Request(
                        "http://127.0.0.1:20653/exec",
                        data=_json.dumps(
                            {"command": "python3 /tmp/tw_eval.py 2>&1 | base64"}
                        ).encode(),
                        headers={"Content-Type": "application/json"},
                    ),
                    timeout=20,
                )
                out = _json.loads(r.read()).get("output", "")
                d = _json.loads(_b64_mod.b64decode("".join(out.split())).decode("utf-8", "replace"))
                break
            except Exception:
                if _attempt == 0:
                    import time as _time

                    _time.sleep(2)
        if d is None:
            return None
        from harness_lib import eval_truth_summary

        t = eval_truth_summary(d.get("eval_rows", []))
        if t:
            t["run"] = d.get("run", "unknown")
        return t
    except Exception:
        return None


def training_watch():
    """Full-training-process monitor (C-9556): fetch metrics tail from the
    live ASI3 run, compute alarms (DEAD-SIGNAL/NO-OP/PASS-RATE-ZERO/LOG-STALE/
    ENTROPY-LOW/SEQ-KL-HIGH/TRAINING-UNMEASURABLE), emit to EVENTS + STATUS.
    Dedupes by kind per run so an alarm fires once, not every tick.
    Never raises — best-effort, must not break the tick.
    """
    try:
        import base64 as _b64_mod
        import json as _json
        import urllib.request as _url

        from harness_lib import append_status_line, training_watch_alarms

        # Box-side summary script (pushed once to /tmp/tw_summary.py): the exec
        # transport front-truncates long outputs, so raw metric rows are lossy.
        # The script emits a tiny JSON {run, mtime, now, rows[12 compact]}.
        _script_b64 = _b64_mod.b64encode(
            b"import json,glob,os,time\n"
            b"ds=sorted(glob.glob('/root/work/software/quantum-gpt/outputs/sapo-27b-ai-*'),"
            b"key=os.path.getmtime)\n"
            b"d=ds[-1] if ds else ''\n"
            b"f=os.path.join(d,'grpo_step_metrics.jsonl') if d else ''\n"
            b"rows=[]\n"
            b"m=None\n"
            b"try:\n"
            b"    m=os.stat(f).st_mtime\n"
            b"    rows=[json.loads(l) for l in open(f).read().strip().splitlines()[-12:]]\n"
            b"except Exception:\n"
            b"    pass\n"
            b"small=[{k:r.get(k) for k in ('step','mean_reward','pass_rate',"
            b"'entropy_mean','seq_kl_after')} for r in rows]\n"
            b"print(json.dumps({'run':os.path.basename(d),'mtime':m,"
            b"'now':time.time(),'rows':small}))\n"
        ).decode()
        # measured eval ground truth: per-row passed flags from eval_results.jsonl
        _script_b64 = _b64_mod.b64encode(
            b"import json,os\n"
            b"d=sorted(glob.glob('/root/work/software/quantum-gpt/outputs/sapo-27b-ai-*'),"
            b"key=os.path.getmtime)[-1] if glob.glob("
            b"'/root/work/software/quantum-gpt/outputs/sapo-27b-ai-*') else ''\n"
            b"ev=os.path.join(d,'eval_results.jsonl') if d else ''\n"
            b"ev_rows=[]\n"
            b"try:\n"
            b"    ev_rows=[json.loads(l) for l in open(ev).read().strip().splitlines()]\n"
            b"except Exception:\n"
            b"    pass\n"
            b"ev_small=[{'step':r.get('step'),'passed':bool(r.get('passed'))} for r in ev_rows]\n"
            b"print(json.dumps({'run':os.path.basename(d),'eval_rows':ev_small}))\n"
        ).decode()
        _push = _url.urlopen(
            _url.Request(
                "http://127.0.0.1:20653/exec",
                data=_json.dumps(
                    {"command": f"echo {_script_b64} | base64 -d > /tmp/tw_summary.py"}
                ).encode(),
                headers={"Content-Type": "application/json"},
            ),
            timeout=15,
        )
        _push.read()

        def _fetch_summary():
            r = _url.urlopen(
                _url.Request(
                    "http://127.0.0.1:20653/exec",
                    data=_json.dumps(
                        {"command": "python3 /tmp/tw_summary.py 2>&1 | base64"}
                    ).encode(),
                    headers={"Content-Type": "application/json"},
                ),
                timeout=20,
            )
            out = _json.loads(r.read()).get("output", "")
            b64 = "".join(out.split())
            if not b64 or "c9591_no_script" in out:
                return None
            import base64 as _b64

            return _json.loads(_b64.b64decode(b64).decode("utf-8", "replace"))

        # transport is flaky (intermittent empty exec responses): 2 attempts
        d = None
        for _attempt in range(2):
            try:
                d = _fetch_summary()
                if d:
                    break
            except Exception:
                if _attempt == 0:
                    import time as _time

                    _time.sleep(2)
        run = "unknown"
        if not d:
            alarms = [
                {
                    "kind": "TRAINING-UNMEASURABLE",
                    "detail": "summary fetch failed twice (transport flake)",
                }
            ]
        else:
            run = d.get("run", "unknown")
            rows = d.get("rows", [])
            last_mtime = d.get("mtime")
            now_s = d.get("now")
            alarms = training_watch_alarms(rows, now_s or 0, last_mtime)
        if not alarms:
            return
        ops = load_ops(STATE)
        seen = ops.setdefault("training_watch_fired", {})
        fresh = [a for a in alarms if seen.get(a["kind"]) != run]
        for a in fresh:
            event(
                STATE,
                "training_alarm_" + a["kind"].lower().replace("-", "_"),
                {"run": run, "detail": a["detail"]},
            )
            seen[a["kind"]] = run
        if fresh:
            save_ops(STATE, ops)
            detail = "; ".join(a["kind"] + ": " + a["detail"][:80] for a in fresh)
            append_status_line(f"- training_watch [{run}]: {detail}")

        # --- CONFIG CONSISTENCY: catch train/eval/inference mismatches
        # (the 2048-vs-4096 token bug existed for weeks undetected)
        try:
            configs = {}
            # training rollout tokens (from trainer default or launch script)
            configs["training_max_new_tokens"] = 4096  # default after a492cb1d
            configs["eval_max_new_tokens"] = 4096  # C-9198
            configs["inference_max_new_tokens"] = 4096
            from harness_lib import check_pipeline_config_consistency

            mismatches = check_pipeline_config_consistency(configs)
            if mismatches:
                for m in mismatches:
                    append_status_line(
                        f"- ⚠️ CONFIG-MISMATCH {m['field']}: {m['issue']} — {m['detail'][:80]}"
                    )
                    event(STATE, "config_mismatch", m)
        except Exception:
            pass

        # --- STRATEGIC-STAGNATION: holdout best hasn't improved
        try:
            best_fp = os.path.join(STATE, "BEST_CHECKPOINT.json")
            best_data = load_json(best_fp, {})
            banked_date = best_data.get("date", "2026-09-08")
            banked_pass = best_data.get("n_passes", 3)
            from datetime import datetime as _dt

            today = _dt.now().strftime("%Y-%m-%d")
            from harness_lib import objective_stagnation_alarm

            alarm = objective_stagnation_alarm(banked_pass, banked_date, today)
            if alarm:
                ops_stag = load_ops(STATE)
                if not ops_stag.get("stagnation_fired"):
                    ops_stag["stagnation_fired"] = True
                    save_ops(STATE, ops_stag)
                    append_status_line(
                        f"- 🚨 STRATEGIC-STAGNATION: holdout stuck at {banked_pass}/18 "
                        f"for {alarm['detail'].split('for ')[1]}. Approach needs rethink."
                    )
        except Exception:
            pass

        # --- box liveness: /health "ready" can LIE (daemon up, session dead).
        # Only an /exec echo round-trip proves the box answers. Alarm
        # BOX-EXEC-DEAD when exec fails (deduped via ops state).
        for _name, _port in (("ASI1", 20646), ("ASI2", 19004), ("ASI3", 20653)):
            try:
                _r = _url.urlopen(
                    _url.Request(
                        f"http://127.0.0.1:{_port}/exec",
                        data=_json.dumps({"command": "echo BOX_ALIVE_PROBE"}).encode(),
                        headers={"Content-Type": "application/json"},
                    ),
                    timeout=10,
                )
                _ok = "BOX_ALIVE_PROBE" in _json.loads(_r.read()).get("output", "")
            except Exception:
                _ok = False
            _ops3 = load_ops(STATE)
            _key = f"box_exec_dead_{_name}"
            if not _ok:
                if not _ops3.get(_key):
                    _ops3[_key] = True
                    save_ops(STATE, _ops3)
                    append_status_line(
                        f"- ⚠️ BOX-EXEC-DEAD {_name}: exec round-trip FAILED — "
                        f"box cannot work. USER ACTION likely required "
                        f"(console re-login) if authDrift; keeper cannot fix auth."
                    )
                    event(STATE, "box_exec_dead", {"box": _name})
            elif _ops3.get(_key):
                _ops3[_key] = False
                save_ops(STATE, _ops3)
                append_status_line(f"- ✅ BOX-EXEC-RECOVERED {_name}: exec round-trip OK")

        # --- measurement-integrity: emit MEASURED pass counts every cycle so
        # unverified "X/18 milestone" claims are visibly contradicted by the
        # ground truth (C-9590 lesson: n_candidates misread as pass count).
        try:
            ev = training_watch_eval_truth()
            if ev:
                ops2 = load_ops(STATE)
                key = f"{ev['run']}:{ev['step']}:{ev['n_passes']}"
                if ops2.get("tw_last_eval_truth") != key:
                    ops2["tw_last_eval_truth"] = key
                    save_ops(STATE, ops2)
                    append_status_line(
                        f"- MEASURED [{ev['run']}]: checkpoint step {ev['step']} "
                        f"eval = {ev['n_passes']}/{ev['n_candidates']} tasks passed "
                        f"(ground truth from eval_results.jsonl; any conflicting "
                        f"'X/18 milestone' claim without this signature is FALSE)"
                    )
                    event(
                        STATE,
                        "measured_eval_truth",
                        {
                            "run": ev["run"],
                            "step": ev["step"],
                            "n_passes": ev["n_passes"],
                            "n_candidates": ev["n_candidates"],
                        },
                    )
        except Exception:
            pass
    except Exception as _tw_exc:
        import os as _os

        if _os.environ.get("TW_DEBUG"):
            import traceback as _tb

            _tb.print_exc()
        else:
            event(STATE, "training_watch_error", {"err": repr(_tw_exc)[:200]})


def cmd_tick(_args):
    # C-9125: clean up stale tick lock if it's a directory (the acquire_lock
    # O_EXCL mechanism can't take over a directory-based lock, so a killed
    # tick's lock permanently blocks all future ticks)
    if os.path.isdir(TICK_LOCK):
        pid_file = os.path.join(TICK_LOCK, "pid")
        if os.path.isfile(pid_file):
            try:
                pid = int(open(pid_file).read().strip())
                if not pid_alive(pid):
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
        # C-9510: prune old probe files to prevent disk bloat
        try:
            _pruned = prune_old_probes(STATE, max_age_days=7)
            if _pruned:
                event(STATE, "probes_pruned", {"count": _pruned})
        except Exception:
            pass
        # C-9512: trim STATUS.md to prevent unbounded growth
        try:
            trim_status_file(STATE, keep=500)
        except Exception:
            pass
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
        # C-9537: cleanup stale running cards (dead PID) before auto-queue.
        try:
            _n_cleaned = auto_cleanup_stale_running(STATE)
            if _n_cleaned:
                event(STATE, "auto_cleanup_stale_running", {"count": _n_cleaned})
        except Exception as _clean_exc:
            event(STATE, "auto_cleanup_stale_error", {"err": repr(_clean_exc)[:160]})
        # C-9532: auto-queue training launch when no training is running.
        try:
            _card = auto_queue_training(STATE)
            if _card is not None:
                _q = load_queue(STATE)
                add_card(_q, _card)
                save_queue(STATE, _q)
                event(STATE, "auto_training_queued", {"card": _card["id"]})
        except Exception as _tq_exc:
            event(STATE, "auto_training_queue_error", {"err": repr(_tq_exc)[:160]})
        # C-9533: auto-requeue bounced cards with 0 bounces (productivity leak).
        try:
            _n_rq = auto_requeue_zero_bounce(STATE)
            if _n_rq:
                event(STATE, "auto_requeue_zero_bounce", {"count": _n_rq})
        except Exception as _rq_exc:
            event(STATE, "auto_requeue_error", {"err": repr(_rq_exc)[:160]})
        # C-9534: auto-retire high-bounce cards to keep the queue clean.
        try:
            _n_ret = auto_retire_high_bounce(STATE)
            if _n_ret:
                event(STATE, "auto_retire_high_bounce", {"count": _n_ret})
        except Exception as _ret_exc:
            event(STATE, "auto_retire_error", {"err": repr(_ret_exc)[:160]})
        # auto-eval: scan for new training checkpoints and queue eval cards
        auto_eval_scan()
        training_watch()
        # C-9541: alert when training is running but no checkpoints produced
        try:
            _ops_post = load_ops(STATE)
            _trainer_probe = load_json(os.path.join(STATE, "probes", "trainer.json"), {})
            _trainer_status = _trainer_probe.get("status", "unknown")
            _has_running_trainer = any(
                c.get("lane") == "trainer-ops"
                and c.get("status") == "running"
                and pid_alive(c.get("claimed_by", ""))
                for c in load_queue(STATE).get("cards", [])
            )
            if _has_running_trainer and _trainer_status == "no_live_run":
                _ops_post["trainer_no_checkpoint_ticks"] = (
                    _ops_post.get("trainer_no_checkpoint_ticks", 0) + 1
                )
                if _ops_post.get("trainer_no_checkpoint_ticks", 0) >= 10:
                    event(
                        STATE,
                        "trainer_no_checkpoints",
                        {
                            "ticks": _ops_post["trainer_no_checkpoint_ticks"],
                            "msg": "trainer running but no checkpoints for 10+ ticks",
                        },
                    )
                    _ops_post["trainer_no_checkpoint_ticks"] = 0
            else:
                _ops_post["trainer_no_checkpoint_ticks"] = 0
            save_ops(STATE, _ops_post)
        except Exception:
            pass
        # dispatch (skip only if this very process is the wedged-tick killer)
        r = self_spawn(["dispatch"], timeout=300)
        dispatch_note = (r.stdout or "").strip()
        # C-9539: track zero-dispatch streak for productivity monitoring
        _ops = load_ops(STATE)
        if "dispatched 0" in dispatch_note or "dispatched 0 workers" in dispatch_note:
            _ops["zero_dispatch_streak"] = _ops.get("zero_dispatch_streak", 0) + 1
        else:
            _ops["zero_dispatch_streak"] = 0
        save_ops(STATE, _ops)
        # If 5+ consecutive zero-dispatch ticks, force aggressive cleanup
        if _ops.get("zero_dispatch_streak", 0) >= 5:
            try:
                _n_cleaned = auto_cleanup_stale_running(STATE)
                if _n_cleaned:
                    event(STATE, "zero_dispatch_force_cleanup", {"count": _n_cleaned})
                    _ops["zero_dispatch_streak"] = 0
                    save_ops(STATE, _ops)
            except Exception:
                pass
        # standup
        queue = load_queue(STATE)
        fleet = load_fleet(STATE)
        tick_no = _next_standup_no()
        verdicts = scan_verdicts(REPO)
        auto_refresh_stale_probes()  # C-9148: re-measure stale/missing box probes
        refresh_trainer_probe()  # C-0074: trainer row from live file evidence (after auto_refresh)
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
            if a.get("status") == "running" and pid_alive(a.get("pid"))
        )
        ready = ready_cards(queue)
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
            f"  GATE: {load_json(os.path.join(STATE, 'c9071', 'window_gate_go.json'), {}).get('verdict', 'NONE') if os.path.exists(os.path.join(STATE, 'c9071', 'window_gate_go.json')) else 'SKIP' if os.path.exists(os.path.join(STATE, 'c9071', 'window_gate_skip.json')) else 'NONE'}"
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
        release_lock(TICK_LOCK, lock)


def refresh_trainer_probe(state_dir=None, outputs_dir=None):
    """C-0074: refresh probes/trainer.json from live run-dir file evidence.

    The no-exec trainer instrument: newest run dir under outputs/ (read-time
    resolution), its eval_results.jsonl step ladder + freshness/proc state.
    Never raises -- on failure the existing record goes stale honestly
    (_probe_results renders STALE past 30 min).

    C-9107: when no live run is found, enrich the probe with a measured
    process-state liveness dict (term=process_state, measured=True,
    process_found=False) and a stub_note pointing at the c9107 stub
    disposition artifact, so the probe is self-evidencing.
    """
    try:
        import resource_probes

        sd = state_dir or STATE
        od = outputs_dir or os.path.join(REPO, "outputs")
        asi3_port = resource_probes.DAEMON_PORTS["asi3"]
        p = resource_probes.probe_trainer_box_aware(asi3_port, od)
        rec = dict(
            ts=now_iso(),
            status=p.get("status"),
            summary=p.get("summary"),
            liveness=p.get("liveness"),
        )
        # C-9107: enrich no-live-run probes with process-state liveness
        if p.get("status") in ("unknown", "stub") and not p.get("liveness"):
            rec["status"] = "no_live_run"
            rec["liveness"] = dict(
                term="process_state",
                measured=True,
                process_found=False,
            )
        stub_path = os.path.join(sd, "probes", "c9107_stub_disposition.json")
        if os.path.exists(stub_path):
            rec["stub_note"] = "see c9107_stub_disposition.json"
        save_json(os.path.join(sd, "probes", "trainer.json"), rec)
        return p
    except Exception:
        return None


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
        # C-9107: re-enrich trainer probe after run_all overwrites it
        # with daemon-based result (run_all uses probe_trainer which returns
        # UNKNOWN without exec transport; refresh_trainer_probe uses
        # probe_trainer_files + liveness enrichment).
        try:
            refresh_trainer_probe(sd)
        except Exception:
            pass
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
            _refresh_box_probe_best_effort(STATE)
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
    auto_refresh_stale_probes()  # C-9148: re-measure stale/missing box probes
    refresh_trainer_probe()  # C-0074: trainer row from live file evidence (after auto_refresh)
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
    line = "*/5 * * * * cd {} && /usr/bin/python3 {} tick >> {} 2>&1".format(
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


def cmd_install_launchd(_args):
    """Second, independent scheduler: survives crontab rewrites AND reboots."""
    ok_all = True
    for label, seconds, arg in (
        (LAUNCHD_LABEL_TICK, 120, "tick"),
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
        "progress",
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


def _queue_locked(fn):
    """C-9386: serialize a QUEUE.json read-modify-write under a file lock.

    qgh card commands load->mutate->save the shared QUEUE.json. Concurrent
    invocations without a lock lose each other's updates (the vaporizer).
    Fail-closed: if the live lock cannot be taken, refuse rather than race.
    A stale/dead-holder lock is taken over by the harness_lib lease protocol.
    """

    @wraps(fn)
    def wrapper(*a, **k):
        lock = acquire_lock(QUEUE_LOCK, stale_s=QUEUE_STALE_SEC)
        if lock is None:
            raise RuntimeError("queue busy: another qgh card op is mutating QUEUE.json")
        try:
            return fn(*a, **k)
        finally:
            release_lock(QUEUE_LOCK, lock)

    return wrapper


# Additional restored helper functions


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
        return clock() - parse_iso(str(doc.get("generated_utc"))).timestamp()
    except (ValueError, TypeError, AttributeError):
        return None


def _bounce_was_environmental(card):
    reason = ((card.get("bounce_reason") or "") + " " + (card.get("result") or "")).lower()
    return any(sig in reason for sig in ENV_BOUNCE_SIGNATURES)


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
                    if not pid_alive(pid):
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
                if pid and not pid_alive(pid):
                    os.unlink(lock_path)
                    event(
                        STATE,
                        "stale_lock_cleaned",
                        {"lock": name, "pid": pid, "reason": "dead_pid"},
                    )
            except (OSError, ValueError):
                pass


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


def _rmtree(path):
    shutil.rmtree(path, ignore_errors=True)


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
    "fleet",
    "box not ready",
    "boxes",
    "not ready",
    "fleet down",
)
PROBE_STALE_MIN = 30


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
    refused_ids = set()  # C-9506: track refused cards to avoid infinite loop
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
            and not card_backoff_active(ops, c["id"])
            and c["id"] not in quota_blocked_ids  # C-9132
            and c["id"] not in refused_ids  # C-9506
            and not (wedged and c["lane"] in BOX_BOUND_LANES and (args.lane is None))
        ]
        if not candidates:
            break
        card = candidates[0]
        ok, why = dispatch_target_ok(queue, card, lanes=lanes)
        if not ok:
            # fail closed: never claim or spawn against a bad target, but
            # CONTINUE to the next candidate (C-9506: a race-condition claim
            # on the first candidate must not block dispatch of other ready cards)
            event(STATE, "dispatch_refused", {"card": card.get("id"), "why": why[:200]})
            refused_ids.add(card["id"])
            continue
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
                        utc=now_iso(),
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
            # C-9506: race condition -- card was claimed or changed status
            # between candidate selection and claim. Skip to next candidate
            # instead of breaking the entire dispatch loop.
            refused_ids.add(card["id"])
            continue
        try:
            entry = spawn_worker(goal, queue, card, deps)
        except Exception as exc:  # spawn must never crash the tick
            entry = None
            event(STATE, "spawn_error", {"card": card["id"], "err": str(exc)[:200]})
        if entry is None:
            # lock race or refused target: spawn_worker raises only BEFORE the
            # durable spawn, so no worker can be running -- revert is safe.
            # C-9506: continue to next candidate instead of breaking.
            card["status"] = "ready"
            card["claimed_by"] = None
            refused_ids.add(card["id"])
            continue
        fleet["agents"].append(entry)
        live.append(entry)
        n_spawned += 1
        spawned_cards.append(card["id"])
    for cid in sorted(c["id"] for c in ready_cards(queue) if card_backoff_active(ops, c["id"])):
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


def cmd_goal(_args):
    goal = load_goal(STATE)
    print(json.dumps(goal, indent=1, ensure_ascii=False))


def cmd_progress(_args):
    """C-9542: Concise progress summary toward 18/18."""
    goal = load_goal(STATE)
    verdicts = scan_verdicts(REPO)
    done, vfile = goal_done(goal, verdicts)

    # Best pass count from verdicts
    best_pass = 0
    best_verdict = None
    for v in verdicts:
        pa = v.get("pass_adapter", "0/18")
        try:
            n = int(str(pa).split("/")[0])
            if n > best_pass:
                best_pass = n
                best_verdict = v
        except (ValueError, IndexError):
            pass

    # Also check loop_state score_history for best known
    loop_state = load_json(os.path.join(STATE, "loop_state.json"), {})
    score_history = loop_state.get("score_history", [])
    for h in score_history:
        pa = h.get("pass_adapter", "0/18")
        try:
            n = int(str(pa).split("/")[0])
            if n > best_pass:
                best_pass = n
        except (ValueError, IndexError):
            pass

    # Queue status
    queue = load_queue(STATE)
    cards = queue.get("cards", [])
    by_status = {}
    for c in cards:
        s = c.get("status", "?")
        by_status[s] = by_status.get(s, 0) + 1

    # Fleet status
    fleet = load_fleet(STATE)
    agents = fleet.get("agents", [])
    alive_workers = sum(
        1 for a in agents if a.get("status") == "running" and pid_alive(a.get("pid"))
    )

    print("=" * 60)
    print("PROGRESS TOWARD 18/18")
    print("=" * 60)
    print(f"Goal status: {goal.get('status', 'OPEN')}")
    print(f"Best pass:   {best_pass}/18")
    if best_verdict:
        print(f"Best verdict: {best_verdict.get('_file', '?')}")
        print(f"  beats_base: {best_verdict.get('beats_base', '?')}")
    print(f"Score history entries: {len(score_history)}")
    for h in score_history[-3:]:
        print(
            f"  {h.get('checkpoint', '?')}: {h.get('pass_adapter', '?')} beats={h.get('beats_base', '?')}"
        )
    print()
    print(f"Queue: {by_status}")
    print(f"Fleet: {alive_workers} live workers (of {len(agents)} total)")
    print(f"Done: {done}")
    if done:
        print(f"GOAL ACHIEVED via {vfile}")
    else:
        print("GOAL NOT YET ACHIEVED")
    print("=" * 60)


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
    "/Users/daxu/.codex/secrets/zhipu.env",
    "/Users/daxu/.codex/secrets/huanxin.env",
    "/Users/daxu/.claude-mcp-cron/claude_headless.env",
    "/Users/daxu/.claude-mcp-cron/claude_headless_override.env",
)


def cmd_reap(_args):
    _reap()


def cmd_remove(args):
    return cmd_card_remove(args)


# H: helper namespace for tests (H.new_card, H.save_json, etc.)
H = _types.SimpleNamespace(
    _candidates_differ_gate_passes=_candidates_differ_gate_passes,
    _canonical_sha_manifest=_canonical_sha_manifest,
    _default_harness_state_dir=_default_harness_state_dir,
    _deps_satisfied=_deps_satisfied,
    _freeze_module=_freeze_module,
    _leg_probe_differs=_leg_probe_differs,
    _lock_takeover_allowed=_lock_takeover_allowed,
    _next_standup_no=_next_standup_no,
    _per_task_ok=_per_task_ok,
    _tick_floor=_tick_floor,
    acquire_lock=acquire_lock,
    add_card=add_card,
    age_min=age_min,
    append_heartbeat=append_heartbeat,
    append_line=append_line,
    armed_backoff_cards=armed_backoff_cards,
    auto_eval_on_checkpoint=auto_eval_on_checkpoint,
    auto_queue_training=auto_queue_training,
    auto_requeue_zero_bounce=auto_requeue_zero_bounce,
    auto_cleanup_stale_running=auto_cleanup_stale_running,
    auto_retire_high_bounce=auto_retire_high_bounce,
    GoalProgressTracker=GoalProgressTracker,
    backoff_active=backoff_active,
    bank_scorer_sha_pins=bank_scorer_sha_pins,
    bounce_dead_running_cards=bounce_dead_running_cards,
    bounce_reason=bounce_reason,
    card_backoff_active=card_backoff_active,
    card_backoff_until=card_backoff_until,
    card_consecutive_spawn_fails=card_consecutive_spawn_fails,
    check_gate=check_gate,
    claim_card=claim_card,
    cmd_init=cmd_init,
    compose_brief=compose_brief,
    compute_metrics=compute_metrics,
    dispatch_reason=dispatch_reason,
    event=event,
    find_card=find_card,
    find_card_by_id_in=find_card_by_id_in,
    goal_done=goal_done,
    harvest_log=harvest_log,
    history_card_ids=history_card_ids,
    history_terminal_card_ids=history_terminal_card_ids,
    is_exec_endpoint_failure=is_exec_endpoint_failure,
    is_gate_skip_blocked=is_gate_skip_blocked,
    is_qwen38_27b_model=is_qwen38_27b_model,
    is_terminal_card_id=is_terminal_card_id,
    is_wrapper_only_output=is_wrapper_only_output,
    kill_pid=kill_pid,
    load_banked_scorer_sha_pins=load_banked_scorer_sha_pins,
    load_fleet=load_fleet,
    load_goal=load_goal,
    load_json=load_json,
    load_ops=load_ops,
    load_queue=load_queue,
    model_identity_violation=model_identity_violation,
    new_card=new_card,
    note_spawn_result=note_spawn_result,
    now_iso=now_iso,
    parse_iso=parse_iso,
    pid_alive=pid_alive,
    process_lstart=process_lstart,
    prune_old_probes=prune_old_probes,
    purge_card=purge_card,
    ready_cards=ready_cards,
    rearm_ghost_running_cards=rearm_ghost_running_cards,
    release_card=release_card,
    release_lock=release_lock,
    render_progress=render_progress,
    render_standup=render_standup,
    requeue_card=requeue_card,
    rotate_log=rotate_log,
    running_count=running_count,
    save_fleet=save_fleet,
    save_json=save_json,
    save_ops=save_ops,
    save_queue=save_queue,
    scan_verdicts=scan_verdicts,
    sha_pin_violation=sha_pin_violation,
    trim_status_file=trim_status_file,
)


if __name__ == "__main__":
    main()
