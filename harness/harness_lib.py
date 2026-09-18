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
    "planner": 2,
    "evaluator": 3,
    "trainer-ops": 2,
    "fixer": 3,
    "reviewer": 2,
    "qa-steward": 2,
    "data-miner": 2,
    "deploy-integrity": 2,
}

DEFAULT_BUDGET_MIN = 25
STALL_MIN = 20  # heartbeat staleness that counts as a stall
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
    save_json(os.path.join(state_dir, "QUEUE.json"), queue)


def add_card(queue, card):
    queue["seq"] = queue.get("seq", 0) + 1
    card["id"] = card["id"] or f"C-{queue['seq']:04d}"
    queue["cards"].append(card)
    return card


def find_card(queue, card_id):
    for c in queue["cards"]:
        if c["id"] == card_id:
            return c
    return None


def rearm_ghost_running_cards(queue, fleet, live_fn=None):
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
        parts.append("stalled: heartbeat stale >20 min")
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


def harvest_log(log_path):
    """Parse a worker log for the RESULT contract. Returns (verdict, tail_lines).

    Fail-closed: no RESULT line -> verdict None (never guess done).
    """
    if not log_path or not os.path.exists(log_path):
        return None, []
    with open(log_path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    m = RESULT_RE.search(text)
    tail = [ln for ln in text.strip().splitlines() if ln.strip()][-10:]
    return (m.group(1) if m else None), tail


# ----------------------------------------------------------------------------- gates
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
  echo "$(date -u +%FT%TZ) <one line of progress>" >> {hb}
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


def sha_pin_violation(verdict, manifest=None):
    """C-0031: NAMED sha-pin violation for a verdict, or None when its
    embedded holdout/scorer sha256 pins match the canonical freeze
    manifest (evals/benchmarks/sapo_promotion_holdout_v1_18.sha256).
    Fail-closed: missing pins, missing manifest coverage, a drifted sha,
    or an unreadable manifest each reject with a distinct named
    violation, so verdicts banked under a pre-pin scorer (the Sep 8-9
    outputs/ verdicts) can never satisfy the done-check."""
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
        return True, v.get("_file")
    return False, None


# ----------------------------------------------------------------------------- api-backoff
BACKOFF_PATH_KEY = "backoff_until_utc"
CONSECUTIVE_SPAWN_FAIL_KEY = "consecutive_spawn_failures"
SPAWN_FAIL_THRESHOLD = 2
BACKOFF_MIN = 15


def load_ops(state_dir):
    return load_json(
        os.path.join(state_dir, "OPS.json"), {CONSECUTIVE_SPAWN_FAIL_KEY: 0, BACKOFF_PATH_KEY: None}
    )


def save_ops(state_dir, ops):
    save_json(os.path.join(state_dir, "OPS.json"), ops)


def note_spawn_result(state_dir, ops, ok):
    """Track consecutive spawn failures; trip backoff after N in a row."""
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
        "done_total": count("reaped")
        and sum(1 for e in ev if e.get("kind") == "reaped" and e.get("verdict") == "DONE"),
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
def render_progress(goal, queue, fleet, tick_no, verdicts=None, probes=None):
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
        f"- best adapter eval so far: **{best_pass}/18**"
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
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- standup
def render_standup(goal, queue, fleet, tick_no, verdicts=None, probes=None, state_dir=None):
    L = []
    L.append(f"## HARNESS STANDUP #{tick_no} — {now_iso()}")
    L.append(
        "Objective: {} | status: {}".format(goal.get("objective", "?"), goal.get("status", "OPEN"))
    )
    L.append("")
    L.append("### QUEUE (top 12 ready/running by priority)")
    L.append("| pri | id | lane | status | title | why |")
    L.append("|---|---|---|---|---|---|")
    rows = [c for c in queue["cards"] if c["status"] in ("ready", "running", "blocked")]
    rows.sort(key=lambda c: (c["priority"], c["created_utc"]))
    for c in rows[:12]:
        L.append(
            "| P{} | {} | {} | {} | {} | {} |".format(
                c["priority"],
                c["id"],
                c["lane"],
                c["status"],
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
                if vio:
                    mark = f"goal_done=NO (sha_pin_violation: {vio})"
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
    return "\n".join(L)
