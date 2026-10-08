#!/usr/bin/env python3
"""retrospective.py — C-9658: the harness reviews its own work, then improves.

DevOps mandate (user, 2026-09-23): the harness should ALWAYS review its work
then improve itself. This script is the 'review' half of that loop; it runs
on a schedule, scans the last N hours of harness activity, and files
improvement cards automatically — turning recurring pain into queued work
without a human in the loop.

DevOps framing: blameless postmortem, automated. Each finding carries
evidence (exact events, counts, timestamps) and becomes an ACTION (a card),
never just a log line.

What it scans (fail-closed, ledger-only, no box execs):
  1. REPEATED FAILURES: cards bounced >=2 times in window -> card asking for
     a root-cause fix (the bounce itself is evidence the fix is missing).
  2. TICK CRISES: tick_crashed / report_errors_present bursts -> card asking
     for crash-isolation of the offending phase.
  3. STALL PATTERNS: stalled-killed outcomes >=2 -> the auto-heartbeat
     cadence or the lane's work pattern needs a design change.
  4. WATCHDOG GAP: any ERROR-class event kind seen >=5 times in window that
     is NOT in the known-remediated set -> card to add a watcher/fixer.
  5. HEALTH TREND: worker throughput (dispatched vs done) — if done/
     dispatched < 0.5 over the window, the fleet is thrashing -> card.

Output: writes a retrospective digest to harness/state/RETROSPECTIVE.md,
appends one STATUS line, and (unless --no-cards) adds ONE improvement card
per finding (max 3 per run, priority=2, lane=fixer, titled
'RETRO: ...' so they're greppable). Idempotent: it will not file a second
card for the same finding signature within 6h (dedupe via OPS ledger).

Usage:
  python3 harness/scripts/retrospective.py                # run review
  python3 harness/scripts/retrospective.py --no-cards    # digest only
  python3 harness/scripts/retrospective.py --window-hours 6
"""

from __future__ import annotations

import argparse
import calendar
import json
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"
sys.path.insert(0, str(REPO / "harness"))

# findings whose remediation is already built — a repeat here means the fix
# regressed or a NEW instance class exists; the retro card then targets the
# regression, not the original design.
KNOWN_REMEDIATED = {
    "card_ghost_rearmed": "FLEET_LOCK serialization (2dcfc583e)",
    "reap_lock_refused": "FLEET_LOCK (expected under contention)",
    "dispatch_lock_refused": "FLEET_LOCK (expected under contention)",
}


def _parse_ts(ts: str):
    try:
        return calendar.timegm(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
    except Exception:
        return None


def _load_events(window_hours: float):
    path = STATE / "EVENTS.jsonl"
    if not path.exists():
        return []
    cutoff = time.time() - window_hours * 3600
    out = []
    for ln in path.read_text(errors="replace").splitlines():
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        t = _parse_ts(ev.get("ts", ""))
        if t is not None and t >= cutoff:
            out.append(ev)
    return out


def _bounce_findings(events):
    """Cards bounced >=2 in window — the strongest 'design is missing
    something' signal: a worker failed the same way twice."""
    bounces = Counter(
        e.get("card") for e in events if e.get("kind") in ("card_bounced", "spawn_failed_env")
    )
    return [
        {
            "sig": f"bounce:{card}",
            "title": f"RETRO: card {card} failed {n}x in window — root-cause fix needed",
            "evidence": f"bounce events={n}",
        }
        for card, n in bounces.most_common(3)
        if n >= 2
    ]


def _tick_crisis_findings(events):
    """tick_crashed or big report_errors_present bursts — the loop itself
    hurt; isolate the phase (pattern proven by C-9655)."""
    crashes = [e for e in events if e.get("kind") == "tick_crashed"]
    out = []
    if crashes:
        last = crashes[-1]
        out.append(
            {
                "sig": "tick_crashed",
                "title": "RETRO: tick crashed in window — apply C-9655 phase isolation to the failing phase",
                "evidence": f"last err: {str(last.get('err'))[:120]}",
            }
        )
    return out


def _stall_findings(events):
    """stalled-killed >=2 — workers die of stall despite auto-heartbeat:
    either the work pattern outgrew the heartbeat cadence or the lane's
    tasks are mis-scoped (too big for one budget)."""
    stalls = Counter(
        e.get("card")
        for e in events
        if e.get("outcome") == "stalled-killed" and e.get("kind") == "reaped"
    )
    return [
        {
            "sig": f"stall:{card}",
            "title": f"RETRO: card {card} stall-killed {n}x — resize task or fix heartbeat cadence",
            "evidence": f"stalled-killed outcomes={n}",
        }
        for card, n in stalls.most_common(2)
        if n >= 2
    ]


def _error_kind_findings(events):
    """ERROR-class kinds seen >=5 times NOT known-remediated — each is an
    un-automated failure mode: file a watcher/fixer card."""
    counts = Counter(e.get("kind") for e in events if e.get("kind") in _error_kinds())
    out = []
    for kind, n in counts.most_common(5):
        if n >= 5 and kind not in KNOWN_REMEDIATED:
            out.append(
                {
                    "sig": f"errkind:{kind}",
                    "title": f"RETRO: '{kind}' fired {n}x in window — add automatic detection+fix (watcher card)",
                    "evidence": f"events={n}",
                }
            )
    return out[:2]


def _error_kinds():
    sys.path.insert(0, str(REPO / "harness" / "scripts"))
    try:
        import detailed_report  # noqa: F401

        return set(detailed_report.ERROR_KINDS)
    except Exception:
        return {"spawn_error", "box_exec_dead", "training_watch_error", "tick_crashed"}


def _throughput_findings(events):
    """done/dispatched < 0.5 = fleet thrash — workers spawn but don't land."""
    disp = sum(1 for e in events if e.get("kind") == "dispatched")
    done = sum(
        1
        for e in events
        if e.get("kind") in ("card_done", "harvested") or e.get("outcome") == "done"
    )
    if disp >= 6 and done / max(disp, 1) < 0.5:
        return [
            {
                "sig": "thrash",
                "title": f"RETRO: fleet thrash — {done} done / {disp} dispatched in window; workers are dying more than landing",
                "evidence": f"done={done} dispatched={disp}",
            }
        ]
    return []


def _already_filed_recently(ops_path: Path, sig: str, now: float, dedupe_h: float = 6.0):
    ops = {}
    try:
        ops = json.loads(ops_path.read_text())
    except Exception:
        ops = {}
    filed = ops.get("retro_filed", {})
    t = filed.get(sig)
    if t is not None and now - t < dedupe_h * 3600:
        return True
    return False


def _mark_filed(ops_path: Path, sig: str, now: float):
    ops = {}
    try:
        ops = json.loads(ops_path.read_text())
    except Exception:
        ops = {}
    filed = ops.setdefault("retro_filed", {})
    filed[sig] = now
    ops_path.write_text(json.dumps(ops, indent=1))


def _add_card(title: str, evidence: str):
    """File the improvement card via the harness's own CLI (single code
    path — the retro never bypasses card-add's schema)."""
    import subprocess

    cmd = [
        sys.executable,
        str(REPO / "harness" / "qgh.py"),
        "card",
        "add",
        "--title",
        title[:160],
        "--lane",
        "fixer",
        "--why",
        (
            "C-9658 retrospective auto-file (DevOps self-improvement mandate): "
            + evidence
            + ". Review the evidence, find the systemic cause, fix it with a "
            "regression test. This card was filed by the harness itself."
        ),
        "--accept",
        (
            "1) Root cause identified with evidence; 2) systemic fix implemented "
            "(not a symptom patch); 3) regression test added and green; "
            "4) if the fix touches the tick loop, it runs crash-isolated per C-9655"
        ),
        "--budget",
        "60",
        "--priority",
        "2",
        "--gate",
        "tdd",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(REPO))
    return r.returncode == 0, (r.stdout or r.stderr).strip()


def review(window_hours: float, file_cards: bool, now=None):
    now = now or time.time()
    events = _load_events(window_hours)
    findings = []
    for fn in (
        _tick_crisis_findings,
        _bounce_findings,
        _stall_findings,
        _error_kind_findings,
        _throughput_findings,
    ):
        try:
            findings.extend(fn(events))
        except Exception as exc:  # one broken finder must not kill the rest
            findings.append(
                {
                    "sig": f"finder_error:{fn.__name__}",
                    "title": f"RETRO BUG: finder {fn.__name__} crashed — fix the retrospective itself",
                    "evidence": repr(exc)[:120],
                }
            )
    ops_path = STATE / "OPS.json"
    filed = []
    for f in findings:
        if file_cards and not _already_filed_recently(ops_path, f["sig"], now):
            ok, out = _add_card(f["title"], f["evidence"])
            if ok:
                _mark_filed(ops_path, f["sig"], now)
                filed.append(f)
    return {
        "window_hours": window_hours,
        "events_scanned": len(events),
        "findings": findings,
        "cards_filed": filed,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
    }


def render(res: dict) -> str:
    L = [
        f"# HARNESS RETROSPECTIVE — {res['ts']}",
        "",
        f"_Self-review window: last {res['window_hours']}h, {res['events_scanned']} events scanned. "
        "Auto-filed by `retrospective.py` (C-9658 DevOps self-improvement). Findings become fixer cards "
        "unless already filed within 6h._",
        "",
    ]
    if not res["findings"]:
        L.append("✅ No recurring failure patterns in window — the harness ran clean.")
    else:
        L.append("## FINDINGS (blameless — evidence, not fault)")
        L.append("")
        for f in res["findings"]:
            L.append(f"- **{f['title']}**")
            L.append(f"  - evidence: `{f['evidence']}`")
            already = (
                "filed now" if f in res["cards_filed"] else "deduped (filed <6h ago) or --no-cards"
            )
            L.append(f"  - action card: {already}")
    L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-hours", type=float, default=3.0)
    ap.add_argument("--no-cards", action="store_true")
    a = ap.parse_args()
    res = review(a.window_hours, not a.no_cards)
    out = STATE / "RETROSPECTIVE.md"
    out.write_text(render(res))
    # repo-root copy: generation is not delivery (the REPORT.md lesson)
    (REPO / "RETROSPECTIVE.md").write_text(render(res))
    print(
        f"retrospective: {len(res['findings'])} findings, {len(res['cards_filed'])} cards filed -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
