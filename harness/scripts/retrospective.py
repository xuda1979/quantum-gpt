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
import re
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


# C-10202: dispatch-segment header in agents/<card>.log (same shape the reap
# path splits on via qgh.DISPATCH_SEG_RE).
_DISPATCH_HDR_RE = re.compile(r"^=====\s*dispatch\s+(\S+)\s+=====\s*$", re.MULTILINE)


def _api_error_signatures():
    """API-outage signatures with ONE source of truth: qgh.API_ERROR_SIGNATURES
    — the exact classifier the reap path uses when it decides a dead worker
    was an environmental spawn failure. Import failure degrades to () which
    makes the outage guard a no-op (fail-open to counting, status quo)."""
    try:
        import qgh

        return tuple(qgh.API_ERROR_SIGNATURES)
    except Exception:
        return ()


def _covering_segment_body(card, ev_ts):
    """C-10195: the agents/<card>.log dispatch-segment body covering ev_ts
    (the segment whose '===== dispatch <ts> =====' header is the latest one
    at or before the event ts — deaths are logged after their dispatch
    header and before the next one). Returns None when evidence is absent
    (missing/unreadable log, blank ts, no headers, or a death predating
    every segment) so every caller can fail OPEN uniformly. Never raises."""
    if not card or not ev_ts:
        return None
    try:
        text = (STATE / "agents" / (card + ".log")).read_text(errors="replace")
    except OSError:
        return None
    marks = list(_DISPATCH_HDR_RE.finditer(text))
    if not marks:
        return None
    body = None
    for i, m in enumerate(marks):
        if m.group(1) <= ev_ts:
            end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
            body = text[m.end() : end]
    return body


def _spawn_death_was_silent(card, ev_ts):
    """C-10195: was this spawn_failed_env a SILENT environmental death? The
    covering dispatch segment EXISTS but is empty/whitespace-only — the
    worker died without printing anything. qgh's reaper already classifies
    exactly this evidence shape (dead, no verdict, empty segment) as
    ENVIRONMENTAL, never the card's fault (C-9515: len(body) == 0 or
    wrapper_only). Returns True ONLY on positive empty-segment evidence:
    None (no segment) is evidence-absent and stays fail-open (counts)."""
    body = _covering_segment_body(card, ev_ts)
    return body is not None and body.strip() == ""


def _spawn_death_was_api_outage(card, ev_ts):
    """C-10202: was this spawn_failed_env an API-outage death? Primary
    evidence: the agents/<card>.log dispatch segment covering ev_ts.
    Returns True only when that segment's text matches an API-error
    signature. Evidence absent (None body) returns False = the event still
    counts toward the bounce threshold (fail-open, never silently suppress
    a genuine per-card signal)."""
    body = _covering_segment_body(card, ev_ts)
    if body is None:
        return False
    # C-10192: ONE classifier with the reap path -- qgh.is_api_error_text
    # knows the generic "API Error:" prefix, so a NEW outage variant is
    # recognized here too instead of fail-open counting as a per-card
    # signal. Import failure degrades to the exact-signature list (status quo).
    try:
        import qgh

        return bool(qgh.is_api_error_text(body))
    except Exception:
        sigs = _api_error_signatures()
        if not sigs:
            return False
        return any(sig in body for sig in sigs)


# C-10207: MEASURED 2026-10-01 provider outage (EVENTS 02:40-10:27Z, 12
# distinct cards, 344 spawn_failed_env): the per-card 15-min backoff
# STAGGERS env deaths so they almost never share a second — every one of
# the 37 same-second-"isolated" deaths had ANOTHER DISTINCT card's env
# death within <=375s. 600s covers that measured max nearest-other-card
# gap with headroom while staying far below the 15-min backoff period.
FLEET_OUTAGE_CLUSTER_GAP_S = 600.0
# an outage interval must span >= this many DISTINCT cards to count as
# FLEET-wide (measured incident intervals spanned 5-13 cards); a 2-card
# coincidence stays a per-card signal for the log-signature guard (C-10202)
# to adjudicate, so the two guards compose instead of overlapping.
FLEET_OUTAGE_MIN_CARDS = 3


def _fleet_outage_intervals(env_points):
    """C-10207: merge sorted (epoch, card) env-death points that are within
    FLEET_OUTAGE_CLUSTER_GAP_S of the previous point into intervals; an
    interval whose points span >= FLEET_OUTAGE_MIN_CARDS DISTINCT cards is a
    fleet-wide outage window. During a sustained outage every card death is
    within the gap of some OTHER card death, so the whole outage collapses
    into interval(s) spanning many cards — no spawn death inside it is a
    per-card design signal. A card dying repeatedly with NO other card env
    death within the gap stays isolated and still counts (returns tuples
    start,end,cards)."""
    intervals = []
    for t, card in env_points:
        if intervals and t - intervals[-1][1] <= FLEET_OUTAGE_CLUSTER_GAP_S:
            s, _prev_end, cards = intervals[-1]
            intervals[-1] = (s, t, cards.union((card,)))
        else:
            intervals.append((t, t, frozenset((card,))))
    return [iv for iv in intervals if len(iv[2]) >= FLEET_OUTAGE_MIN_CARDS]


def _in_fleet_outage_window(ev_ts, outage_intervals):
    """C-10207 ledger-only outage test for one spawn_failed_env event.
    Fail-open like the C-10202 log guard: evidence absent (unparseable ts)
    -> not an outage -> the event still counts toward the bounce threshold."""
    t = _parse_ts(ev_ts or "")
    if t is None:
        return False
    return any(s <= t <= e for s, e, _cards in outage_intervals)


def _in_fleet_leading_edge(ev_ts, outage_intervals):
    """C-10405: absorb the LEADING EDGE of a fleet outage — a reaped-dead
    no-verdict death whose ts is BEFORE an env-derived outage interval's start
    but within FLEET_OUTAGE_CLUSTER_GAP_S of it is part of that SAME incident
    (the reaper sees one reap at a time, so the first card dies just before
    the clustered spawn failures that define the interval), not a separate
    per-card failure. Deliberately BACKWARD-only: a death AFTER an interval
    still counts (C-10204: the window re-arms after the outage and must not
    swallow genuinely-later card deaths). Evidence absent fails OPEN."""
    t = _parse_ts(ev_ts or "")
    if t is None:
        return False
    return any(s - FLEET_OUTAGE_CLUSTER_GAP_S <= t < s for s, _e, _cards in outage_intervals)


def _bounce_counter(events):
    """C-10196: guarded per-card bounce counting factored out of
    _bounce_findings so the retirement pass can re-run the CURRENT guards
    over a HISTORICAL window -- the original filing window of an
    already-queued retro card."""
    # spawn_failed_env clustered at the same timestamp = fleet-wide outage.
    spawn_timestamps = Counter(e.get("ts") for e in events if e.get("kind") == "spawn_failed_env")
    # C-10207: env deaths from >= FLEET_OUTAGE_MIN_CARDS distinct cards
    # within FLEET_OUTAGE_CLUSTER_GAP_S of each other = fleet outage window,
    # even when per-card backoff staggers them into different seconds (the
    # ledger-only backstop for when agents/<card>.log is missing or rotated).
    env_points = sorted(
        (t, e.get("card"))
        for e in events
        if e.get("kind") == "spawn_failed_env"
        for t in (_parse_ts(e.get("ts", "") or ""),)
        if t is not None
    )
    outage_intervals = _fleet_outage_intervals(env_points)

    def counts_toward_bounce(e):
        if e.get("kind") == "card_bounced":
            return True
        if e.get("kind") == "spawn_failed_env":
            # only an ISOLATED spawn death (single card at that second) AND a
            # non-API-outage death is a per-card signal; a multi-card
            # same-second cluster is the env (C-10153), and so is a solo card
            # whose dispatch segment died printing an API-error signature
            # (C-10202). C-10195: a SILENT death (empty covering segment) is
            # not a per-card signal either; only a death that printed
            # something card-specific (non-API, non-empty) counts.
            return (
                spawn_timestamps.get(e.get("ts"), 0) == 1
                and not _spawn_death_was_api_outage(e.get("card"), e.get("ts"))
                and not _spawn_death_was_silent(e.get("card"), e.get("ts"))
                and not _in_fleet_outage_window(e.get("ts"), outage_intervals)
            )
        return False

    return Counter(e.get("card") for e in events if counts_toward_bounce(e))


def _bounce_findings(events):
    """Cards bounced >=2 in window — the strongest 'design is missing
    something' signal: a worker failed the same way twice.

    C-10153: a `spawn_failed_env` is only a PER-CARD design signal when it is
    ISOLATED (that card alone died at that second). When multiple cards fire
    spawn_failed_env in the SAME second it is a fleet-wide environment outage
    (API/box down) — an environmental death, not the card's fault, and must not
    count toward the per-card bounce threshold. card_bounced is always a
    genuine per-card bounce and always counts. This mirrors the throughput
    finder (C-9704) and errkind finder (C-9828): environmental failures are not
    counted as per-card faults, so the retro loop cannot auto-file a false
    'failed Nx -> root-cause fix' card against an innocent card (C-10152)."""
    bounces = _bounce_counter(events)
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


# C-9702/C-10146/C-10152a/C-10507/C-10517: every auto-detected failure class
# carries an in-path PROOF that the event was already contained. The
# retrospective must count the RESIDUAL (events whose own record does NOT
# prove auto-remediation), never the raw burst — a fully-self-healed window
# must NOT mint a "add automatic detection+fix" watcher card for a failure
# mode that already has automatic detection+fix (C-10247 residual model).
_CONTAINMENT_PROOF = {}


def _box_exec_dead_auto_remediated(ev, all_events):
    """box_exec_dead is auto-remediated iff its OWN `autofix` field is truthy —
    the flag is emitted in the SAME in-tick call that performs the reconciler
    kick (qgh.py event(STATE, 'box_exec_dead', {'box': name, 'autofix':
    bool(_kick)})). A missing autofix field cannot be proven -> counts
    fail-open (never silently suppress)."""
    return bool(ev.get("autofix"))


_CONTAINMENT_PROOF["box_exec_dead"] = _box_exec_dead_auto_remediated


def _error_kind_findings(events):
    """ERROR-class kinds seen >=5 times among UNPROVEN events — each residue is
    an un-automated failure mode: file a watcher/fixer card. An event whose
    own record proves in-path auto-remediation (e.g. box_exec_dead.autofix==true
    from the C-9702 kick) is NOT counted — the residual (unproven events only)
    drives the threshold. Events that CANNOT be proven auto-remediated always
    count fail-open (a missing proof is never silently suppressed)."""
    unproven = []
    for ev in events:
        kind = ev.get("kind")
        if kind not in _error_kinds():
            continue
        helper = _CONTAINMENT_PROOF.get(kind)
        try:
            if helper is not None and helper(ev, events):
                continue
        except Exception:
            pass  # a broken helper must never hide events (fail-open)
        unproven.append(ev)
    counts = Counter(e.get("kind") for e in unproven)
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
    """TRUE thrash = dispatched workers that DIED without producing a
    terminal RESULT verdict, in excess of workers that LANDED one.
    C-9704: the old metric counted done/dispatched and treated every
    non-done worker (blocked/partial/gate-bounced) as if it died, so a
    board whose workers all LAND verdicts still read as thrash and
    auto-filed false RETRO cards. A worker that landed a terminal RESULT
    (done/bounced/blocked/partial) did NOT die; only a worker reaped
    dead/stalled/overrun with NO verdict is a loss.
    C-10204: an ENVIRONMENTAL death is not a thrash death either — the two
    outage guards (log-signature C-10202, fleet-outage-window C-10207) compose
    the same way they do for the bounce finder; evidence absent fails OPEN
    (counts, status quo).
    C-10248/C-10583: the qgh.reaper emits BOTH `card_done` AND a
    `reaped(outcome=done)` for the SAME landed DONE worker (C-9680). Summing
    those event kinds double-counts every landing — the measured C-10583
    window showed 20 'done' events for 10 REAL landed workers, minting a
    false '20 done / 45 dispatched' RETRO card. LANDED is therefore counted
    per distinct worker (card), never per event.
    C-10324: deaths == landed is a WASH, not 'dying more than landing' —
    only deaths STRICTLY EXCEEDING landed files the card."""
    disp = sum(1 for e in events if e.get("kind") == "dispatched")
    env_points = sorted(
        (t, e.get("card"))
        for e in events
        if e.get("kind") == "spawn_failed_env"
        for t in (_parse_ts(e.get("ts", "") or ""),)
        if t is not None
    )
    outage_intervals = _fleet_outage_intervals(env_points)

    def _is_outage_death(e):
        return (
            _spawn_death_was_api_outage(e.get("card"), e.get("ts"))
            or _in_fleet_outage_window(e.get("ts"), outage_intervals)
            or _in_fleet_leading_edge(e.get("ts"), outage_intervals)
        )

    deaths = 0
    outage_excluded = 0
    for e in events:
        if (
            e.get("kind") == "reaped"
            and e.get("outcome") in ("dead", "stalled-killed", "overrun-killed")
            and e.get("verdict") is None
        ):
            if _is_outage_death(e):
                outage_excluded += 1
            else:
                deaths += 1
    # LANDED per DISTINCT worker (card): a card_done+reaped pair or a
    # reaped(outcome=done) still counts as ONE landed worker, never two.
    landed_cards = set()
    for e in events:
        if e.get("kind") == "card_done" and e.get("card"):
            landed_cards.add(e.get("card"))
        elif (
            e.get("kind") == "reaped"
            and e.get("outcome") in ("done", "bounced", "blocked", "partial")
            and e.get("card")
        ):
            landed_cards.add(e.get("card"))
    landed = len(landed_cards)
    if disp >= 6 and deaths > 0 and deaths > landed:
        return [
            {
                "sig": "thrash",
                "title": f"RETRO: fleet thrash — {deaths} died / {landed} landed / {disp} dispatched in window; workers are dying more than landing",
                "evidence": f"died={deaths} landed={landed} dispatched={disp}"
                + (f" outage_excluded={outage_excluded}" if outage_excluded else ""),
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
