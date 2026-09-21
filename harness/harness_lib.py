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

import json
import os
import re
import signal
import subprocess
import time
from datetime import datetime, timedelta, timezone


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
    save_json(path, queue)
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


def is_past_deadline(card, now=None):
    """C-9532: Check if a card is past its deadline_utc."""
    deadline = card.get("deadline_utc")
    if not deadline:
        return False
    try:
        dt = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        return current > dt
    except (ValueError, TypeError):
        return False


def auto_requeue_zero_bounce(state_dir):
    """C-9529: Auto-requeue bounced cards with 0 bounces.

    Bounced cards sitting idle with bounce_count=0 are a productivity leak.
    This sets status=ready, clears claimed_by/claimed_utc so the dispatcher
    can pick them up on the next cycle. Returns the count of requeued cards.

    C-9533: the field is "bounce_count" (set by new_card), not "bounces".
    The old check c.get("bounces", 0) always returned 0 because the field
    did not exist, requeueing ALL bounced cards including high-bounce ones.

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


def acquire_lock(path, stale_s=LOCK_STALE_S):
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
BUDGET: {budget} min hard deadline — you will be stopped; report what you have by then.
HEARTBEAT (mandatory): after every meaningful step run
  python3 harness/qgh.py heartbeat {cid} "what you just did"   # heartbeat file: {hb}
A worker whose heartbeat file goes stale >{stall} min is treated as STALLED and killed.
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
        for c in queue["cards"]:
            if c.get("lane") == "trainer-ops" and c["status"] in ("running", "ready"):
                return None
        # Need a training card
        card = new_card(
            title="Auto: launch/resume GRPO training with v10 benchmark (18/18 holdout coverage) toward 18/18",
            lane="trainer-ops",
            why="No training running and goal is OPEN. v10 benchmark covers all 18 holdout tasks (unlike v9 which has 0 overlap). Use --min-rms-for-update 0.01 for warm-continue.",
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
def auto_eval_on_checkpoint(queue, checkpoint_name, run_dir):
    """When training produces a new checkpoint, automatically queue an eval
    card to measure progress toward 18/18.

    Returns a new card dict if one should be created, or None if an eval
    card for this checkpoint already exists (dedup).

    This is the core automation primitive: train -> checkpoint -> eval ->
    verdict -> (if <18/18) -> continue training -> (if 18/18) -> done-check.
    """
    for c in queue.get("cards", []):
        title = c.get("title", "")
        if checkpoint_name in title and c.get("lane") == "evaluator":
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
    """C-9540: Track best pass count and detect goal-level stalls."""

    def __init__(self, stall_threshold_ticks=20):
        self.stall_threshold_ticks = stall_threshold_ticks
        self._best_pass = 0
        self._ticks_since_improvement = 0
        self._history = []

    def record_tick(self, tick_no, best_pass):
        if best_pass > self._best_pass:
            self._best_pass = best_pass
            self._ticks_since_improvement = 0
        else:
            self._ticks_since_improvement += 1
        self._history.append((tick_no, best_pass))

    def is_stalled(self):
        return self._ticks_since_improvement >= self.stall_threshold_ticks

    def best_pass(self):
        return self._best_pass

    def ticks_since_improvement(self):
        return self._ticks_since_improvement

    def status(self):
        if self.is_stalled():
            return f"stalled ({self._ticks_since_improvement} ticks, best={self._best_pass}/18)"
        return (
            f"progressing (best={self._best_pass}/18, {self._ticks_since_improvement} since last)"
        )


def recompute_goal_done_preflight(goal, verdicts):
    """C-9545: Recompute goal_done preflight checks, return violation report."""
    violations = []
    target = goal.get("target_pass", "18/18")
    best_pass = "0/18"
    best_verdict = None
    for v in verdicts:
        pa = v.get("pass_adapter", "0/18")
        try:
            n = int(str(pa).split("/")[0])
            bn = int(str(best_pass).split("/")[0])
            if n > bn:
                best_pass = pa
                best_verdict = v
        except (ValueError, IndexError):
            pass
    if best_verdict is None:
        violations.append({"violation_type": "no_verdict", "detail": "no verdicts found"})
        return {
            "total_violations": len(violations),
            "violations": violations,
            "pass_adapter": best_pass,
        }
    v = best_verdict
    if str(v.get("pass_adapter", "")) != target:
        violations.append(
            {
                "violation_type": "pass_adapter_mismatch",
                "detail": "got " + str(v.get("pass_adapter")) + ", need " + target,
            }
        )
    if not v.get("beats_base"):
        violations.append(
            {"violation_type": "beats_base_false", "detail": "beats_base is not true"}
        )
    if not v.get("scorer_version"):
        violations.append(
            {"violation_type": "scorer_version_missing", "detail": "no scorer_version tag"}
        )
    if v.get("adapter_applied_marker") is not True:
        violations.append(
            {
                "violation_type": "adapter_applied_marker_false",
                "detail": "adapter_applied_marker is not True",
            }
        )
    if not v.get("adapter_probe_differs_marker"):
        violations.append(
            {
                "violation_type": "probe_differs_marker_missing",
                "detail": "adapter_probe_differs_marker absent or false",
            }
        )
    leg1 = v.get("leg1")
    leg2 = v.get("leg2")
    if not isinstance(leg1, dict) or not isinstance(leg2, dict):
        violations.append(
            {"violation_type": "missing_legs", "detail": "need both leg1 and leg2 as dicts"}
        )
    else:
        for leg_name, leg in [("leg1", leg1), ("leg2", leg2)]:
            if not _leg_probe_differs(leg):
                violations.append(
                    {
                        "violation_type": "probe_differs_" + leg_name,
                        "detail": leg_name + " missing adapter_probe_differs",
                    }
                )
    return {
        "total_violations": len(violations),
        "violations": violations,
        "pass_adapter": best_pass,
    }


def apply_goal_done_transition(state_dir, goal, verdicts):
    """C-9545: Apply the goal_done transition if preflight passes."""
    pf = recompute_goal_done_preflight(goal, verdicts)
    if pf["total_violations"] > 0:
        return False
    goal = dict(goal)
    goal["status"] = "DONE"
    from datetime import datetime, timezone

    # Find the winning verdict file
    verdict_sha = None
    target = goal.get("target_pass", "18/18")
    for v in verdicts:
        if str(v.get("pass_adapter", "")) == target and v.get("beats_base"):
            verdict_sha = v.get("_file")
            break
    goal["achieved"] = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict_sha": verdict_sha,
    }
    save_json(os.path.join(state_dir, "GOAL.json"), goal)
    return True


# ----------------------------------------------------------------------------- done-check
def load_goal(state_dir):
    return load_json(os.path.join(state_dir, "GOAL.json"), {})


def scan_verdicts(repo_root, limit=12):
    """Newest verdict JSONs in outputs/ (fail-closed eval artifacts)."""
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
            if d:
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
