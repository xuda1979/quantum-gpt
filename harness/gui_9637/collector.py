#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"
OUTPUTS = REPO / "outputs"


def collect_goal():
    out = []
    p = STATE / "GOAL.json"
    if not p.exists():
        return [("Goal file", "missing")]
    try:
        g = json.loads(p.read_text())
    except Exception:
        return [("Goal file", "unreadable")]
    out.append(("Goal objective", str(g.get("objective", "N/A"))[:200]))
    out.append(("Goal model", g.get("model", "N/A")))
    out.append(("Goal target pass", g.get("target_pass", "N/A")))
    out.append(("Goal status", g.get("status", "N/A")))
    out.append(("Goal created (UTC)", g.get("created_utc", "N/A")))
    for i, c in enumerate(g.get("done_criteria", [])):
        out.append((f"Done criterion {i + 1}", str(c)[:120]))
    return out


_KIND_LABELS = {
    "reaped": "workers reaped",
    "card_ghost_rearmed": "ghost card re-armed",
    "stale_lock_cleaned": "stale lock cleaned",
    "launchd_installed": "launchd daemon installed",
    "dispatched": "card dispatched to worker",
    "card_added": "new card added",
    "card_requeued": "card requeued",
    "card_purged": "card purged",
    "card_superseded": "card superseded",
    "card_auto_retired": "card auto-retired",
    "auto_retire_high_bounce": "high-bounce auto-retire",
    "auto_requeue_zero_bounce": "zero-bounce requeue",
    "auto_training_queued": "auto training queued",
    "auto_plan": "auto plan generated",
    "ghost_heartbeat": "ghost heartbeat",
    "gate_skip": "gate skipped",
    "gate_bounced": "card bounced by gate",
    "spawn_failed_env": "spawn failed (env)",
    "spawn_error": "spawn error",
    "env_blocked_requeued": "env-blocked requeued",
    "dep_edge_dropped": "dependency edge dropped",
    "dead_dep_escalated": "dead dependency escalated",
    "dep_blocker_requeued": "dependency blocker requeued",
    "measured_eval_truth": "eval truth measured",
    "box_exec_dead": "box exec detected dead",
    "training_alarm_training_unmeasurable": "training state unmeasurable",
    "training_alarm_log_stale": "training log stale",
    "training_watch_error": "training watch error",
    "trainer_no_checkpoints": "trainer produced no checkpoints",
    "heal_halt_detected": "loop halt detected",
    "guardian_restarted_by_heal": "guardian restarted by auto-heal",
    "report_errors_present": "report errors present",
    "stale_running_cleaned": "stale running card cleaned",
    "auto_cleanup_stale_running": "stale running auto-cleaned",
    "c9133_window_rearm_spawned": "ASI2 window sentinel rearmed",
}


def _friendly_event_kind(kind):
    kind = str(kind)
    if kind in _KIND_LABELS:
        return _KIND_LABELS[kind]
    stripped = re.sub(r"^c[0-9]+_?", "", kind)
    words = stripped.replace("_", " ").strip()
    return words if words else kind


def collect_events():
    out = []
    p = STATE / "EVENTS.jsonl"
    if not p.exists():
        return [("Events file", "missing")]
    kinds = Counter()
    recent = []
    total = 0
    try:
        for line in p.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            total += 1
            kinds[ev.get("kind", "?")] += 1
            recent.append(ev)
    except Exception:
        return [("Events file", "unreadable")]
    out.append(("Total events recorded", total))
    out.append(("Distinct event kinds", len(kinds)))
    for kind, c in kinds.most_common():
        out.append((f"Event kind - {_friendly_event_kind(kind)}", c))
    for i, (kind, c) in enumerate(kinds.most_common(5)):
        out.append((f"Top event kind #{i + 1} - {_friendly_event_kind(kind)}", c))
    skip = {"ts", "kind"}
    for ev in recent[-8:]:
        k = ev.get("kind", "?")
        card = ev.get("card", ev.get("lane", ""))
        ts = ev.get("ts", "?")
        payload = json.dumps({k2: v2 for k2, v2 in ev.items() if k2 not in skip})
        out.append((f"Latest event - {_friendly_event_kind(k)} ({card} {ts})", payload[:120]))
    return out


def collect_queue():
    out = []
    p = STATE / "QUEUE.json"
    if not p.exists():
        return [("Queue file", "missing")]
    try:
        q = json.loads(p.read_text())
        cards = q.get("cards", [])
    except Exception:
        return [("Queue file", "unreadable")]
    out.append(("Total cards in queue", len(cards)))
    out.append(("Queue sequence number", q.get("seq", "N/A")))
    st = Counter(c.get("status", "?") for c in cards)
    ln = Counter(c.get("lane", "?") for c in cards)
    for s, c in st.most_common():
        out.append((f"Cards with status - {s}", c))
    for lane, c in ln.most_common():
        out.append((f"Cards on lane - {lane}", c))
    bounces = Counter(c.get("bounce_count", 0) for c in cards)
    for b, c in bounces.most_common(8):
        out.append((f"Cards bounced {b} times", c))
    interesting = [
        c
        for c in cards
        if c.get("status") in ("running", "ready") or (c.get("bounce_count") or 0) >= 1
    ]
    interesting.sort(key=lambda c: -(c.get("bounce_count") or 0))
    for c in interesting[:40]:
        cid = c.get("id", "?")
        out.append((f"Card {cid} - status", c.get("status", "?")))
        out.append((f"Card {cid} - lane", c.get("lane", "?")))
        out.append((f"Card {cid} - bounce count", c.get("bounce_count", 0)))
        out.append((f"Card {cid} - title", str(c.get("title", ""))[:90]))
        out.append((f"Card {cid} - created (UTC)", c.get("created_utc", "N/A")))
        if c.get("claimed_utc"):
            out.append((f"Card {cid} - claimed (UTC)", c.get("claimed_utc")))
    return out


def collect_fleet():
    out = []
    p = STATE / "FLEET.json"
    if not p.exists():
        return [("Fleet file", "missing")]
    try:
        agents = json.loads(p.read_text()).get("agents", [])
    except Exception:
        return [("Fleet file", "unreadable")]
    out.append(("Agents in fleet", len(agents)))
    for a in agents:
        pid = a.get("pid", "?")
        out.append((f"Agent pid {pid} - card", a.get("card", "?")))
        out.append((f"Agent pid {pid} - lane", a.get("lane", "?")))
        out.append((f"Agent pid {pid} - status", a.get("status", "?")))
        out.append((f"Agent pid {pid} - started (UTC)", a.get("started_utc", "N/A")))
        out.append((f"Agent pid {pid} - deadline (UTC)", a.get("deadline_utc", "N/A")))
        out.append((f"Agent pid {pid} - budget (min)", a.get("budget_min", "N/A")))
    return out


def collect_ops():
    out = []
    p = STATE / "OPS.json"
    if not p.exists():
        return [("Ops file", "missing")]
    try:
        o = json.loads(p.read_text())
    except Exception:
        return [("Ops file", "unreadable")]
    out.append(("Consecutive spawn failures", o.get("consecutive_spawn_failures", "N/A")))
    out.append(("Spawn backoff until (UTC)", o.get("backoff_until_utc") or "none"))
    out.append(("Stagnation fired", o.get("stagnation_fired", "N/A")))
    out.append(("Trainer no-checkpoint ticks", o.get("trainer_no_checkpoint_ticks", "N/A")))
    out.append(("Zero dispatch streak", o.get("zero_dispatch_streak", "N/A")))
    out.append(("Box exec dead - ASI1", o.get("box_exec_dead_ASI1", "N/A")))
    out.append(("Box exec dead - ASI2", o.get("box_exec_dead_ASI2", "N/A")))
    out.append(("Box exec dead - ASI3", o.get("box_exec_dead_ASI3", "N/A")))
    out.append(("Last eval truth (measure)", o.get("tw_last_eval_truth", "N/A")))
    for card, info in (o.get("spawn_failures_by_card") or {}).items():
        if isinstance(info, dict):
            out.append((f"Spawn failures - card {card}", info.get("consecutive", 0)))
            out.append((f"Spawn backoff - card {card}", info.get("backoff_until_utc") or "none"))
    tw = o.get("training_watch_fired")
    if isinstance(tw, dict):
        for k, v in tw.items():
            out.append((f"Training watch - {k}", v))
    return out


def _flatten_json(obj, prefix, out, seen=None):
    if seen is None:
        seen = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = k if not prefix else prefix + " - " + k
            if key in seen:
                continue
            seen.add(key)
            if isinstance(v, (dict, list)):
                _flatten_json(v, key, out, seen)
            else:
                out.append((key, v))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]"
            if key in seen:
                continue
            seen.add(key)
            if isinstance(v, (dict, list)):
                _flatten_json(v, key, out, seen)
            else:
                out.append((key, v))


def collect_training():
    out = []
    p = STATE / "probes" / "train.json"
    if p.exists():
        try:
            t = json.loads(p.read_text())
        except Exception:
            t = None
        if t:
            out.append(("Training status (probe)", t.get("status", "N/A")))
            proc = t.get("process", {})
            if isinstance(proc, dict):
                out.append(("Training process alive", proc.get("alive", "N/A")))
                out.append(("Training process list", proc.get("processes", "N/A")))
            step = t.get("step", {})
            if isinstance(step, dict):
                out.append(("Latest training step dir", step.get("latest_step_dir", "N/A")))
            out.append(("Training probe timestamp", t.get("ts", "N/A")))
    p = STATE / "probes" / "trainer.json"
    if p.exists():
        try:
            t = json.loads(p.read_text())
        except Exception:
            t = None
        if t:
            out.append(("Trainer self-report status", t.get("status", "N/A")))
            out.append(("Trainer summary", str(t.get("summary", "N/A"))[:160]))
            out.append(("Trainer probe timestamp", t.get("ts", "N/A")))
            lv = t.get("liveness")
            if isinstance(lv, dict):
                for k, v in list(lv.items())[:4]:
                    out.append((f"Trainer liveness - {k}", v))
    p = STATE / "probes" / "train_fire.json"
    if p.exists():
        try:
            _flatten_json(json.loads(p.read_text()), "Train-fire", out)
        except Exception:
            pass
    for name in (
        "asi3_train_fire_state.json",
        "resume_training.json",
        "auto_launch.json",
        "checkpoint_publisher.json",
        "self_resume_guardian.json",
        "loop_state.json",
    ):
        fp = STATE / name
        if fp.exists():
            try:
                _flatten_json(
                    json.loads(fp.read_text()),
                    name.replace(".json", "").replace("_", " ").title(),
                    out,
                )
            except Exception:
                pass
    p = STATE / "BEST_CHECKPOINT.json"
    if p.exists():
        try:
            b = json.loads(p.read_text())
        except Exception:
            b = None
        if isinstance(b, dict):
            for k, v in b.items():
                out.append((f"Best checkpoint - {k}", v))
    p = STATE / "training_source_of_truth.json"
    if p.exists():
        try:
            _flatten_json(json.loads(p.read_text()), "Training source of truth", out)
        except Exception:
            pass
    return out


def _box_probe_items(name):
    out = []
    p = STATE / "probes" / (f"{name}.json")
    if not p.exists():
        return [(f"Box {name.upper()} probe", "missing")]
    try:
        obj = json.loads(p.read_text())
    except Exception:
        return [(f"Box {name.upper()} probe", "unreadable")]
    box = name.upper()
    out.append((f"Box {box} - health status", obj.get("status", "N/A")))
    out.append((f"Box {box} - summary", str(obj.get("summary", "N/A"))[:120]))
    out.append((f"Box {box} - probe timestamp", obj.get("ts", "N/A")))
    tr = obj.get("transport")
    if isinstance(tr, dict):
        out.append((f"Box {box} - transport status", tr.get("status", "N/A")))
        ev = tr.get("evidence")
        if isinstance(ev, dict):
            out.append((f"Box {box} - startup state", ev.get("startupState", "N/A")))
            out.append((f"Box {box} - ready", ev.get("ready", "N/A")))
            out.append((f"Box {box} - uptime (s)", ev.get("uptime_s", "N/A")))
            out.append((f"Box {box} - busy", ev.get("busy", "N/A")))
            out.append((f"Box {box} - busy age (ms)", ev.get("busyAgeMs", "N/A")))
            out.append((f"Box {box} - pending requests", ev.get("pendingRequestCount", "N/A")))
            out.append((f"Box {box} - last command started", ev.get("lastCommandStartedAt", "N/A")))
            out.append(
                (f"Box {box} - last command completed", ev.get("lastCommandCompletedAt", "N/A"))
            )
            out.append((f"Box {box} - command queue", ev.get("commandQueue", "N/A")))
            out.append((f"Box {box} - command queue depth", ev.get("commandQueueDepth", "N/A")))
    lv = obj.get("liveness")
    if isinstance(lv, dict):
        for k, v in list(lv.items())[:3]:
            out.append((f"Box {box} - liveness {k}", v))
    return out


def collect_system():
    out = []
    for name in ("asi1", "asi2", "asi3"):
        out.extend(_box_probe_items(name))
    for lp in ("launchd-com.quantumgpt.qgh-tick.log", "launchd-com.quantumgpt.qgh-heal.log"):
        fp = STATE / lp
        out.append((f"Launchd daemon {lp}", "present" if fp.exists() else "missing"))
        if fp.exists():
            out.append((f"Launchd daemon {lp} - size (bytes)", fp.stat().st_size))
            out.append(
                (
                    f"Launchd daemon {lp} - last modified (s ago)",
                    int(time.time() - fp.stat().st_mtime),
                )
            )
    p = STATE / "c9124_daemon_pid_state.json"
    if p.exists():
        try:
            _flatten_json(json.loads(p.read_text()), "Daemon pid state", out)
        except Exception:
            pass
    return out


def _friendly_verdict_tag(path):
    """Derive a human-readable display tag from a verdict file path.
    Turns 'STATE/C-9072/c9072_canary_verdict.json' -> 'C-9072' and
    'outputs/c9030_base_verdict_blocked_20260919T002404Z.json' -> 'C-9030'."""
    parent = Path(path).parent.name
    m = re.search(r"C-(\d+)", str(parent))
    if m:
        return "C-" + m.group(1)
    m = re.search(r"c(\d+)", Path(path).name)
    if m:
        return "C-" + m.group(1)
    stem = re.sub(r"(?:_base|_adapter|_canary|_transport)?_verdict.*$", "", Path(path).stem)
    words = re.sub(r"^c\d+_?", "", stem).replace("_", " ").strip()
    return words or Path(path).name


def collect_verdicts():
    out = []
    vpaths = []
    for root in (OUTPUTS, STATE):
        if not root.exists():
            continue
        for p in root.rglob("*verdict*.json"):
            vpaths.append(p)
    vpaths = sorted(set(vpaths))
    out.append(("Verdict files found", len(vpaths)))
    seen_any = False
    for p in vpaths:
        try:
            v = json.loads(p.read_text())
        except Exception:
            out.append((f"Verdict {p.name} - unreadable", "yes"))
            continue
        if not isinstance(v, dict):
            continue
        seen_any = True
        tag = _friendly_verdict_tag(p)
        out.append((f"Verdict {tag} - pass adapter", v.get("pass_adapter", "N/A")))
        out.append((f"Verdict {tag} - pass base", v.get("pass_base", "N/A")))
        out.append((f"Verdict {tag} - beats base", v.get("beats_base", "N/A")))
        out.append((f"Verdict {tag} - composite adapter", v.get("composite_adapter", "N/A")))
        out.append((f"Verdict {tag} - composite base", v.get("composite_base", "N/A")))
        out.append((f"Verdict {tag} - rubric adapter", v.get("rubric_adapter", "N/A")))
        out.append((f"Verdict {tag} - rubric base", v.get("rubric_base", "N/A")))
        out.append((f"Verdict {tag} - superseded", v.get("superseded", "N/A")))
        out.append((f"Verdict {tag} - stale reason", str(v.get("stale_reason", "N/A"))[:100]))
        for i, g in enumerate(v.get("gains") or []):
            out.append((f"Verdict {tag} - adapter gain #{i + 1}", str(g)))
        for i, loss in enumerate(v.get("losses") or []):
            out.append((f"Verdict {tag} - adapter loss #{i + 1}", str(loss)))
        bc = v.get("by_category") or []
        for cat in bc[:10]:
            prefix = "Verdict {} - category {}".format(tag, cat.get("category", "?"))
            out.append((prefix + " adapter pass", cat.get("adapter_pass", "N/A")))
            out.append((prefix + " base pass", cat.get("base_pass", "N/A")))
            out.append((prefix + " adapter rubric", cat.get("adapter_rubric", "N/A")))
            out.append((prefix + " base rubric", cat.get("base_rubric", "N/A")))
        bt = v.get("by_task_wins") or []
        for i, t in enumerate(bt):
            out.append((f"Verdict {tag} - task win #{i + 1}", str(t)))
        per = v.get("per_task") or v.get("results") or v.get("tasks")
        if isinstance(per, dict):
            for tid, tv in per.items():
                out.append((f"Verdict {tag} - task {tid}", tv))
    if not seen_any:
        out.append(("Verdict detail", "none found"))
    return out


def collect_unit_tests():
    out = []
    tdir = REPO / "harness" / "tests"
    ntest = 0
    if tdir.exists():
        ntest = len(list(tdir.glob("test_*.py")))
    out.append(("Unit test files present", ntest))
    out.append(("Unit test source - harness/tests", "present" if tdir.exists() else "missing"))
    ns = 0
    for k in ("c0012_smoke", "c0012_smoke2"):
        if (REPO / "tmp" / k).exists():
            ns += 1
    out.append(("Smoke test dirs found", ns))
    for root in (REPO / "tmp", STATE / "tmp"):
        if not root.exists():
            continue
        for p in root.rglob("*smoke*"):
            if p.is_dir():
                continue
            try:
                friendly = re.sub(r"^c\d+_?", "", p.stem).replace("_", " ").strip()
                out.append(("Smoke artifact - %s" % (friendly or p.stem), p.stat().st_size))
            except Exception:
                pass
    return out


def collect_md_ledgers():
    out = []
    p = STATE / "STATUS.md"
    if p.exists():
        txt = p.read_text(errors="replace")
        ticks = [int(m.group(1)) for m in re.finditer(r"tick#(\d+)", txt)]
        if ticks:
            out.append(("Highest STATUS.md tick seen", max(ticks)))
            out.append(("Total tick mentions in STATUS.md", len(ticks)))
        out.append(("STATUS.md size (bytes)", p.stat().st_size))
    for name, label in (
        ("REPORT.md", "Detailed report"),
        ("DASHBOARD.md", "Dashboard"),
        ("STATUS.md", "Status log"),
    ):
        path = (REPO if name in ("REPORT.md", "DASHBOARD.md") else STATE) / name
        if path.exists():
            out.append((f"{label} present", "yes"))
            out.append((f"{label} size (bytes)", path.stat().st_size))
            out.append((f"{label} last modified (s ago)", int(time.time() - path.stat().st_mtime)))
    return out


def collect_all():
    items = []
    items += [("Section", "Goal")]
    items += collect_goal()
    items += [("Section", "Queue / Fleet")]
    items += collect_queue() + collect_fleet()
    items += [("Section", "Training")]
    items += collect_training()
    items += [("Section", "System Testing")]
    items += collect_system()
    items += [("Section", "Evaluation")]
    items += collect_verdicts()
    items += [("Section", "Unit Testing")]
    items += collect_unit_tests()
    items += [("Section", "Errors / Events")]
    items += collect_events()
    items += [("Section", "Operations")]
    items += collect_ops()
    items += [("Section", "Ledgers")]
    items += collect_md_ledgers()
    seen = set()
    dedup = []
    for label, value in items:
        if label == "Section":
            dedup.append((label, value))
            continue
        if label in seen:
            continue
        seen.add(label)
        dedup.append((label, value))
    return dedup


def split_sections(items):
    sections = []
    current = None
    for label, value in items:
        if label == "Section":
            current = value
            sections.append({"name": value, "items": []})
        elif current:
            sections[-1]["items"].append((label, value))
    return sections


if __name__ == "__main__":
    import sys

    items = collect_all()
    secs = split_sections(items)
    total = sum(len(s["items"]) for s in secs)
    print(f"TOTAL DATA ITEMS: {total}")
    for s in secs:
        print(f"  {s['name']}: {len(s['items'])} items")
    if "--sample" in sys.argv:
        for s in secs:
            print(f"=== {s['name']} ({len(s['items'])} items) ===")
            for _i, (label, value) in enumerate(s["items"][:4]):
                print(f"  {label} = {value}")
