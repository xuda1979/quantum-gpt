#!/usr/bin/env python3
"""detailed_report.py — the harness's own detailed, regular information layer.

Mandate (user, 2026-09-23): the harness MUST deliver detailed information
regularly via scripts it runs itself — not via a human or ad-hoc agent session
walking ps, /tmp files, and box execs. Today's spawn_error 'why'/'acceptance'
KeyErrors starved ALL worker spawns for hours and were only discovered by
manual digging through a 6000-line EVENTS.jsonl. Never again.

Design:
  - Source of truth: the LEDGERS (EVENTS.jsonl, QUEUE.json, STATUS.md,
    DASHBOARD.md, fleet, crontab, claude-mcp-cron jobs) — never ad-hoc
    scraping of live processes except a cheap ps for audit.
  - Fail-closed per section: UNREADABLE, never silent.
  - Event-kind aggregation over a time window (default last hour): counts
    per kind + exact payloads for ERROR-class kinds (spawn_error,
    dispatch_refused, box_exec_dead, training_watch_error, ...) so systemic
    bugs surface on the FIRST report after they start, not hours later.
  - Emit: markdown (default), --json for agents.
  - Called by `qgh.py tick` every N ticks (REGULAR) and on demand via
    `qgh.py report`. Publishes to harness/state/REPORT.md + appends a
    one-line digest to harness/state/STATUS.md.

Usage:
  python3 harness/scripts/detailed_report.py              # md to stdout
  python3 harness/scripts/detailed_report.py --json      # json to stdout
  python3 harness/scripts/detailed_report.py --window-hours 1
"""

from __future__ import annotations

import calendar
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"

# Error-class event kinds: exact payloads are ALWAYS included in the report,
# not just counts. Anything matching *_error, *_dead, *_failed also qualifies.
ERROR_KINDS = {
    "spawn_error",
    "dispatch_refused",
    "box_exec_dead",
    "training_watch_error",
    "auto_training_queue_error",
    "guardian_restart_failed",
    "heal_reap_failed",
    "config_mismatch",
    "card_dead",
    "gate_bounced",
    "env_blocked_requeued",
    "pid_reuse_detected",
    "ghost_heartbeat",
    "dep_blocker_requeued",
    # C-9631: concurrent reap/dispatch lock contention + ghost-rearm respawn
    # loop signatures. A live claimed_by with a rearm = duplicate worker; a
    # burst of card_ghost_rearmed + dispatched on one card = respawn loop.
    "reap_lock_refused",
    "dispatch_lock_refused",
    "card_ghost_rearmed",
}
ERROR_RE = re.compile(r"(_error|_dead|_failed)$")


def _read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return default if default is not None else "UNREADABLE"


def _age(path, now):
    try:
        return int(now - Path(path).stat().st_mtime)
    except OSError:
        return None


def _now_iso(now=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now or time.time()))


def _latest_standup():
    """Newest standup-*.md by mtime, or None (counts as MISSING)."""
    try:
        return max((STATE / "standup").glob("standup-*.md"), key=lambda p: p.stat().st_mtime)
    except (OSError, ValueError):
        return None


def _parse_ts(ts):
    """Parse harness UTC ISO ts to epoch; None if unparseable.

    time.mktime would interpret a UTC stamp as LOCAL time (8h shift on this
    box) and silently empty the aggregation window — the exact class of
    silent bug this script exists to prevent. Use calendar.timegm."""
    try:
        return calendar.timegm(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
    except Exception:
        return None


def collect_events(window_hours):
    """Aggregate EVENTS.jsonl by kind over the window. Fail-closed."""
    path = STATE / "EVENTS.jsonl"
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return "UNREADABLE"
    now = time.time()
    cutoff = now - window_hours * 3600
    counts = Counter()
    errors = []  # [(ts, kind, payload_str)] for error-class kinds
    samples = {}  # kind -> most recent non-error payload
    dispatched_by_card = {}  # C-9631 respawn-loop detector
    rearmed_by_card = {}
    in_window = 0
    total = len(lines)
    for ln in lines:
        try:
            ev = json.loads(ln)
        except Exception:
            counts["<unparseable>"] += 1
            continue
        ts = _parse_ts(ev.get("ts", ""))
        if ts is None or ts < cutoff:
            continue
        in_window += 1
        kind = ev.get("kind", "?")
        counts[kind] += 1
        detail = {k: v for k, v in ev.items() if k not in ("ts", "kind")}
        detail_s = json.dumps(detail, ensure_ascii=False)
        if kind in ERROR_KINDS or ERROR_RE.search(kind or ""):
            errors.append((ev.get("ts", "?"), kind, detail_s[:200]))
        else:
            samples[kind] = (ev.get("ts", "?"), detail_s[:120])
        # C-9631 respawn-loop detector inputs: per-card dispatched/rearmed tallies
        _card = detail.get("card") or detail.get("id")
        if isinstance(_card, str):
            if kind == "dispatched":
                dispatched_by_card[_card] = dispatched_by_card.get(_card, 0) + 1
            elif kind == "card_ghost_rearmed":
                rearmed_by_card[_card] = rearmed_by_card.get(_card, 0) + 1
    respawn_loops = [
        {"card": c, "dispatched": dispatched_by_card[c], "ghost_rearmed": rearmed_by_card[c]}
        for c in rearmed_by_card
        if rearmed_by_card[c] >= 2 and dispatched_by_card.get(c, 0) >= 3
    ]
    return {
        "total_lines": total,
        "in_window": in_window,
        "window_hours": window_hours,
        "counts": dict(counts.most_common()),
        "errors": errors[-40:],  # cap; newest last
        "samples": samples,
        "respawn_loops": sorted(respawn_loops, key=lambda r: -r["dispatched"]),
    }


def collect_queue_schema():
    """Schema audit: required fields missing on dispatchable cards.

    This is the check that would have flagged the 'why'/'acceptance' KeyErrors
    BEFORE they starved spawns: a card missing compose_brief's required keys
    is a spawn_error waiting to happen.
    """
    q = _read_json(STATE / "QUEUE.json", default={})
    cards = q.get("cards", []) if isinstance(q, dict) else q
    if not isinstance(cards, list):
        return "UNREADABLE"
    required = ("id", "lane", "title", "why", "budget_min", "deps", "gates", "acceptance")
    dispatchable = [
        c for c in cards if isinstance(c, dict) and c.get("status") in ("ready", "running")
    ]
    missing = {}
    for c in dispatchable:
        for f in required:
            if f not in c or c.get(f) in (None, ""):
                missing.setdefault(f, []).append(c.get("id", "?"))
    return {
        "total_cards": len(cards),
        "dispatchable": len(dispatchable),
        "missing_fields": {k: v[:12] for k, v in sorted(missing.items())},
        "ok": not missing,
    }


def collect_freshness(now):
    """Ledger freshness: every file the harness is expected to update
    regularly, with age verdicts (OK/STALE/MISSING)."""

    def verdict(age, ok_s=1800, stale_s=3600):
        if age is None:
            return "MISSING"
        return "OK" if age <= ok_s else ("STALE" if age <= stale_s else "CRITICAL")

    files = {
        "EVENTS.jsonl": STATE / "EVENTS.jsonl",
        "STATUS.md": STATE / "STATUS.md",
        "tick.log": STATE / "tick.log",
        "QUEUE.json": STATE / "QUEUE.json",
        "DASHBOARD.md": REPO / "DASHBOARD.md",
        "PROGRESS.md": REPO / "PROGRESS.md",
        "standup-latest": _latest_standup(),
        "FLEET.json": STATE / "FLEET.json",
    }
    out = {}
    for name, p in files.items():
        if p is None:
            out[name] = {"age_s": None, "verdict": "MISSING"}
            continue
        age = _age(p, now)
        out[name] = {"age_s": age, "verdict": verdict(age)}
    return out


def collect_scheduler(now):
    """Cron table + claude-mcp-cron jobs with firing evidence."""
    try:
        ct = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        ct = "UNREADABLE"
    jobs = []
    jobs_root = Path.home() / ".claude-mcp-cron" / "jobs"
    if jobs_root.is_dir():
        for d in sorted(jobs_root.iterdir()):
            if not d.is_dir():
                continue
            log = d / "log.txt"
            last_firing = None
            failing = None
            if log.exists():
                try:
                    tail = log.read_text(errors="replace").splitlines()[-6:]
                    for ln in reversed(tail):
                        if "firing job" in ln:
                            m = re.search(r"\[(\S+)\] firing job", ln)
                            last_firing = m.group(1) if m else "?"
                            break
                    failing = "Not logged in" in "\n".join(tail)
                except OSError:
                    pass
            jobs.append(
                {
                    "job": d.name,
                    "last_firing": last_firing,
                    "failing": failing,
                    "log_age_s": _age(log, now),
                }
            )
    return {
        "crontab": ct.strip().splitlines() if ct != "UNREADABLE" else "UNREADABLE",
        "mcp_cron_jobs": jobs,
    }


def collect_goal():
    """GOAL.json + BEST_CHECKPOINT.json — what we're all here for."""
    g = _read_json(STATE / "GOAL.json")
    if g is None:
        return "UNREADABLE"
    best = _read_json(STATE / "BEST_CHECKPOINT.json") or {}
    return {
        "objective": g.get("objective"),
        "target_pass": g.get("target_pass"),
        "status": g.get("status"),
        "created_utc": g.get("created_utc"),
        "best_checkpoint": best.get("checkpoint"),
        "best_n_passes": best.get("n_passes"),
        "best_n_tasks": best.get("n_tasks"),
        "best_beats_base": best.get("beats_base"),
        "best_caveat": best.get("caveat"),
        "best_updated": best.get("updated"),
    }


def collect_training(now):
    """Whole training picture: TSoT + resume state + probes.

    This is the section that answers 'is training actually running, on which
    run, and how far along' — from ledgers, without box execs.
    """
    tsot = _read_json(STATE / "training_source_of_truth.json")
    resume = _read_json(STATE / "resume_training.json")
    t_probe = _read_json(STATE / "probes" / "train.json") or {}
    trainer = _read_json(STATE / "probes" / "trainer.json") or {}
    fire = _read_json(STATE / "probes" / "train_fire.json") or {}

    def _age_of(p):
        a = _age(STATE / p, now)
        return a if isinstance(a, int) else 999999

    return {
        "tsot_card": (tsot or {}).get("card"),
        "engine": ((tsot or {}).get("authoritative_engine") or {}).get("engine"),
        "run_name": ((tsot or {}).get("authoritative_engine") or {}).get("run_name"),
        "tsot_note": (tsot or {}).get("note"),
        "resume_status": (resume or {}).get("status"),
        "resume_run": (resume or {}).get("run_name"),
        "resume_checkpoint": (resume or {}).get("latest_checkpoint"),
        "resume_launch": (resume or {}).get("launch"),
        "train_probe_status": t_probe.get("status"),
        "train_probe_age_s": _age_of("probes/train.json"),
        "trainer_summary": trainer.get("summary"),
        "trainer_age_s": _age_of("probes/trainer.json"),
        "train_fire": fire.get("summary"),
    }


def collect_fleet_queue():
    """FLEET agents + QUEUE depth — who is working on what, and what's pending."""
    f = _read_json(STATE / "FLEET.json")
    q = _read_json(STATE / "QUEUE.json")
    if f is None or q is None:
        return "UNREADABLE"
    agents = f.get("agents", [])
    cards = q.get("cards", [])
    by_status = {}
    for c in cards:
        by_status[c.get("status", "?")] = by_status.get(c.get("status", "?"), 0) + 1
    active = [
        {
            "card": c.get("id"),
            "lane": c.get("lane"),
            "status": c.get("status"),
            "claimed_utc": c.get("claimed_utc"),
            "bounce_count": c.get("bounce_count", 0),
            "title": (c.get("title") or c.get("objective") or "")[:70],
        }
        for c in cards
        if c.get("status") in ("running", "ready", "bounced")
    ]
    agent_rows = [
        {
            "card": a.get("card") or a.get("card_id"),
            "agent": a.get("agent") or a.get("kind"),
            "status": a.get("status"),
            "box": a.get("box"),
            "pid": a.get("pid"),
            "started_utc": a.get("started_utc") or a.get("spawned_utc"),
        }
        for a in agents
    ]
    return {
        "n_agents": len(agents),
        "agents": agent_rows,
        "n_cards": len(cards),
        "by_status": by_status,
        "active_cards": active,
    }


def collect_ps_audit():
    """Cheap ps audit: harness processes alive (tick, qgh, guardians, claude
    workers). Bounded, no scraping of process internals."""
    try:
        out = subprocess.run(
            ["ps", "-Ao", "pid,etime,command"], capture_output=True, text=True, timeout=15
        ).stdout
    except Exception:
        return "UNREADABLE"
    pats = (
        "qgh.py",
        "status_surface",
        "self_resume_guardian",
        "trainer_guardian",
        "reconciler",
        "sapo_judge",
        "judge_health",
        "session_keeper",
    )
    rows = []
    for ln in out.splitlines()[1:]:
        if any(p in ln for p in pats):
            rows.append(" ".join(ln.split())[:160])
    return rows[:25]


def collect(window_hours=1, now=None):
    now = now or time.time()
    return {
        "ts_utc": _now_iso(now),
        "events": collect_events(window_hours),
        "queue_schema": collect_queue_schema(),
        "freshness": collect_freshness(now),
        "scheduler": collect_scheduler(now),
        "ps_audit": collect_ps_audit(),
        "goal": collect_goal(),
        "training": collect_training(now),
        "fleet_queue": collect_fleet_queue(),
    }


def render(d):
    L = []
    L.append(f"# HARNESS DETAILED REPORT — {d['ts_utc']}")
    L.append("")
    L.append(
        f"_Auto-generated by `harness/scripts/detailed_report.py` (run by `qgh.py tick` every 3rd tick; window = last {d['events'].get('window_hours', 1)}h). _"
    )
    L.append("")

    # ---- GOAL (why any of this is running) ----
    g = d.get("goal")
    L.append("## GOAL")
    if g == "UNREADABLE" or not g:
        L.append("**GOAL.json UNREADABLE — INVESTIGATE**")
    else:
        L.append(f"- **objective:** {g.get('objective')}")
        L.append(
            f"- target {g.get('target_pass')} | status **{g.get('status')}** | opened {g.get('created_utc')}"
        )
        L.append(
            f"- best checkpoint: `{g.get('best_checkpoint')}` — **{g.get('best_n_passes')}/{g.get('best_n_tasks')}**"
            f" beats_base={g.get('best_beats_base')} (updated {g.get('best_updated')})"
        )
        if g.get("best_caveat"):
            L.append(f"- caveat: {g.get('best_caveat')}")
    L.append("")

    # ---- TRAINING (the main thread of the whole operation) ----
    t = d.get("training")
    L.append("## TRAINING")
    if not t:
        L.append("**training ledgers UNREADABLE — INVESTIGATE**")
    else:
        stale_probe = t["train_probe_age_s"] > 1800
        L.append(
            f"- authoritative engine: **{t.get('engine')}** run `{t.get('run_name')}` (TSoT card {t.get('tsot_card')})"
        )
        L.append(
            f"- resume: status **{t.get('resume_status')}** run `{t.get('resume_run')}` launch={t.get('resume_launch')}"
        )
        L.append(f"- checkpoint: `{t.get('resume_checkpoint')}`")
        L.append(
            f"- train probe: **{t.get('train_probe_status')}** (age {t['train_probe_age_s']}s"
            + (" — STALE >1800s" if stale_probe else "")
            + ")"
        )
        L.append(f"- trainer: {t.get('trainer_summary')} (age {t['trainer_age_s']}s)")
        L.append(f"- train-fire: {t.get('train_fire')}")
        if t.get("tsot_note"):
            L.append(f"- TSoT note: {t.get('tsot_note')}")
    L.append("")

    # ---- FLEET & QUEUE (who is working on what) ----
    fq = d.get("fleet_queue")
    L.append("## FLEET & QUEUE")
    if fq == "UNREADABLE" or not fq:
        L.append("**FLEET.json or QUEUE.json UNREADABLE — INVESTIGATE**")
    else:
        L.append(
            f"- fleet agents alive: **{fq['n_agents']}** | cards total {fq['n_cards']} "
            + " ".join(f"{k}={v}" for k, v in sorted(fq["by_status"].items()))
        )
        if fq["agents"]:
            L.append("")
            L.append("| card | agent | status | box | pid | started |")
            L.append("|---|---|---|---|---|---|")
            for a in fq["agents"][:15]:
                L.append(
                    f"| {a['card']} | {a['agent']} | {a['status']} | {a['box']} | {a['pid']} | {a['started_utc']} |"
                )
        else:
            L.append("- no live fleet rows (all agents stopped or fleet empty)")
        L.append("")
        L.append("**Active/dispatchable cards:**")
        L.append("")
        L.append("| status | card | lane | bounces | claimed | title |")
        L.append("|---|---|---|---|---|---|")
        for c in fq["active_cards"][:25]:
            L.append(
                f"| {c['status']} | {c['card']} | {c['lane']} | {c['bounce_count']} | {c['claimed_utc'] or '-'} | {c['title']} |"
            )
    L.append("")

    # ---- ERROR DIGEST (the section that must never be silent) ----
    ev = d["events"]
    L.append("## ERROR DIGEST (last window)")
    if ev == "UNREADABLE":
        L.append("**EVENTS.jsonl UNREADABLE — INVESTIGATE**")
    else:
        errs = ev.get("errors", [])
        if errs:
            L.append(f"**{len(errs)} ERROR-class events in window — EXACT payloads:**")
            L.append("")
            L.append("| ts | kind | payload |")
            L.append("|---|---|---|")
            for ts, kind, payload in errs[-25:]:
                L.append(f"| {ts} | {kind} | `{payload}` |")
        else:
            L.append("- none")
        L.append("")
        # C-9631 respawn-loop detector: a card dispatched 3+ times AND ghost-
        # rearmed 2+ times in the window is in a duplicate-worker respawn
        # loop (lost fleet rows / ghost rearm). This loop burned 15+ claude
        # spawns on C-9631 before anyone noticed.
        loops = ev.get("respawn_loops", [])
        if loops:
            L.append("**RESPAWN LOOPS (duplicate workers being spawned on the same card):**")
            L.append("")
            L.append("| card | dispatched | ghost_rearmed |")
            L.append("|---|---|---|")
            for r in loops[:10]:
                L.append(f"| {r['card']} | {r['dispatched']} | {r['ghost_rearmed']} |")
            L.append("")
        L.append(
            "**Event kind counts (window):** "
            + (", ".join(f"{k}={v}" for k, v in ev.get("counts", {}).items()) or "none")
        )
        L.append("")

    # ---- QUEUE SCHEMA AUDIT ----
    qs = d["queue_schema"]
    L.append("## QUEUE SCHEMA AUDIT (spawn_error prevention)")
    if qs == "UNREADABLE":
        L.append("**QUEUE.json UNREADABLE — INVESTIGATE**")
    else:
        L.append(f"- cards total={qs['total_cards']} dispatchable={qs['dispatchable']}")
        if qs["ok"]:
            L.append("- all dispatchable cards carry every required field ✅")
        else:
            L.append(
                "- **MISSING FIELDS on dispatchable cards (will degrade briefs or starve spawns):**"
            )
            for f, ids in qs["missing_fields"].items():
                L.append(f"  - `{f}` missing on {len(ids)}: {', '.join(ids)}")
    L.append("")

    # ---- LEDGER FRESHNESS ----
    L.append("## LEDGER FRESHNESS")
    L.append("| file | age_s | verdict |")
    L.append("|---|---|---|")
    for name, r in d["freshness"].items():
        L.append(f"| {name} | {r['age_s']} | {r['verdict']} |")
    L.append("")

    # ---- SCHEDULER ----
    L.append("## SCHEDULER")
    sch = d["scheduler"]
    ct = sch["crontab"]
    if ct == "UNREADABLE":
        L.append("- crontab UNREADABLE")
    else:
        for ln in ct:
            if ln.strip() and not ln.startswith("#"):
                L.append(f"- `{ln[:150]}`")
    L.append("")
    L.append("### claude-mcp-cron jobs")
    L.append("| job | last firing | failing? | log age_s |")
    L.append("|---|---|---|---|")
    for j in sch["mcp_cron_jobs"]:
        L.append(f"| {j['job']} | {j['last_firing']} | {j['failing']} | {j['log_age_s']} |")
    L.append("")

    # ---- PS AUDIT ----
    L.append("## PROCESS AUDIT (harness processes alive)")
    ps = d["ps_audit"]
    if ps == "UNREADABLE":
        L.append("- ps UNREADABLE")
    else:
        for ln in ps:
            L.append(f"- `{ln}`")
        if not ps:
            L.append("- none matched (quiet period or all dead — check freshness above)")
    L.append("")

    L.append("---")
    L.append(
        "_Fail-closed per section. Sources: EVENTS.jsonl, QUEUE.json, STATUS.md, crontab, "
        "claude-mcp-cron job logs. ERROR-class payloads always exact, never summarized._"
    )
    return "\n".join(L) + "\n"


def main():
    window = 1
    args = sys.argv[1:]
    if "--window-hours" in args:
        try:
            window = float(args[args.index("--window-hours") + 1])
        except (IndexError, ValueError):
            pass
    d = collect(window_hours=window)
    if "--json" in args:
        print(json.dumps(d, indent=2, default=str))
        return 0
    print(render(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
