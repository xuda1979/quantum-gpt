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
    "planner": 1,
    "evaluator": 2,
    "trainer-ops": 1,
    "fixer": 2,
    "reviewer": 2,
    "qa-steward": 1,
    "data-miner": 1,
    "deploy-integrity": 1,
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


RESULT_RE = re.compile(r"^RESULT:\s*(DONE|PARTIAL|BLOCKED)\b", re.MULTILINE)


def harvest_log(log_path):
    """Parse a worker log for the RESULT contract. Returns (verdict, tail_lines).

    Fail-closed: no RESULT line -> verdict None (never guess done).
    """
    if not os.path.exists(log_path):
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


def goal_done(goal, verdicts):
    """18/18 achieved = a fail-closed verdict shows 18/18 + beats_base.

    Fail-closed: absent/bad evidence -> False (loop keeps running).
    """
    target = goal.get("target_pass", "18/18")
    for v in verdicts:
        pa = str(v.get("pass_adapter", ""))
        bb = v.get("beats_base")
        markers_ok = v.get("adapter_applied_marker") is not False
        if pa == target and bb is True and markers_ok:
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
            L.append(
                "- {}: pass_adapter={} beats_base={} (base {})".format(
                    v.get("_file"), v.get("pass_adapter"), v.get("beats_base"), v.get("pass_base")
                )
            )
    if probes:
        L.append("")
        L.append("### RESOURCES")
        for name, p in probes.items():
            L.append(f"- {name}: {p}")
    return "\n".join(L)
