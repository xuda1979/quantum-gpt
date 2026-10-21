"""C-10583 RED: the retrospective FLEET-THRASH (throughput) finder regression
introduced by 9772a5837 (C-10571) — the paired card_done+reaped-outcome=done
events for ONE landed DONE worker are counted TWICE.

Measured incident (C-10583, auto-filed 2026-10-21T16:15:14Z from the 3h window):
title "RETRO: fleet thrash — 20 done / 45 dispatched in window". Replaying the
exact window from EVENTS.jsonl shows 45 dispatched, 10 card_done + 10
reaped(outcome=done) events — the SAME 10 landed workers, because the qgh.py
reaper emits BOTH the canonical `card_done` AND a `reaped` outcome=done for a
landed DONE worker (C-9680). The pre-fix finder summed
card_done(10)+harvested(0)+reaped-outcome-done(10) = 20 "done" from 10 real
landings -> done/dispatched = 0.444 < 0.5 -> false retro card.

There were also 12 genuine no-verdict deaths (13:15:55Z..16:13:46Z) — so the
truthful finder must report 12 died / 10 landed / 45 dispatched (still a
genuine thrash, deaths > landed — but with CORRECT evidence), never the
double-counted "20 done / 45 dispatched".

Systemic fix under test: _throughput_findings must measure TRUE losses (reaped
dead/stalled-killed/overrun-killed with NO terminal RESULT verdict) versus
unique landed workers (done/bounced/blocked/partial OR card_done/harvested —
deduped to one per worker/card), and must NOT double-count the paired
card_done+reaped events. Environmental guards (outage/API/silent) compose per
C-10198/C-10204/C-10307/C-10405.
"""

import sys
import time
from pathlib import Path

import conftest  # noqa: F401

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import retrospective  # noqa: E402


def _iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def _disp(ts, card="C-A"):
    return dict(ts=ts, kind="dispatched", card=card, lane="fixer", pid=1, budget_min=60)


def _landed_pair(ts, card):
    """The canonical reaper emit pair for ONE landed DONE worker (C-9680):
    both events carry the same card and same-second; the finder must count
    them as ONE landed worker, never two."""
    return [
        dict(ts=ts, kind="card_done", card=card, pid=1),
        dict(
            ts=ts, kind="reaped", card=card, pid=1, lane="evaluator", outcome="done", verdict="DONE"
        ),
    ]


def _death(card, ts, outcome="dead"):
    return dict(
        ts=ts, kind="reaped", card=card, pid=1, lane="evaluator", outcome=outcome, verdict=None
    )


def _c10583_real_filing_shape():
    """Exact C-10583 measured filing window (2026-10-21T13:15:14Z ->
    16:15:14Z): 45 dispatched, 12 REAL landed workers (10 DONE pairs + 2
    PARTIAL reaped — C-10540, C-10564), 12 genuine no-verdict deaths.
    The pre-fix finder summed card_done(10)+reaped-outcome-done(10) = 20
    'done' from 10 real DONE landings and filed a FALSE '20 done / 45
    dispatched' thrash card. The TRUTH is died=12 landed=12 dispatched=45
    — a BALANCED WASH (C-10324: deaths == landed is not 'dying more than
    landing') so NO thrash card should ever be filed."""
    base = 1792599313  # filing epoch for the real window (10-21T16:15:13Z)
    events = [_disp(_iso(base - i * 133)) for i in range(45)]
    # 10 landed DONE workers, each a canonical card_done+reaped pair
    for i in range(10):
        events += _landed_pair(_iso(base - 1800 - i * 300), f"C-LND{i}")
    # 2 landed PARTIAL workers — still landed (a terminal RESULT verdict)
    for i in range(2):
        ts = _iso(base - 900 - i * 450)
        events.append(
            dict(
                ts=ts,
                kind="reaped",
                card=f"C-PAR{i}",
                pid=1,
                lane="evaluator",
                outcome="partial",
                verdict="PARTIAL",
            )
        )
    # 12 genuine no-verdict deaths (dead / overrun-killed), no env pairing
    outcomes = [
        "overrun-killed",
        "dead",
        "overrun-killed",
        "overrun-killed",
        "dead",
        "overrun-killed",
        "overrun-killed",
        "overrun-killed",
        "overrun-killed",
        "overrun-killed",
        "overrun-killed",
        "overrun-killed",
    ]
    for i, oc in enumerate(outcomes):
        ts = _iso(base - 3600 + i * 240)
        events.append(_death(f"C-DED{i}", ts, outcome=oc))
    return events


def test_real_c10583_window_is_a_balanced_wash_no_thrash():
    """Frozen reconstruction of the REAL C-10583 filing window. died=12
    landed=12 is a balanced WASH — the '20 done / 45 dispatched' false card
    was minted only by double-counting. The fixed finder must NOT file."""
    events = _c10583_real_filing_shape()
    out = retrospective._throughput_findings(events)
    assert not out, "died == landed balanced wash must NOT file thrash, got " + repr(out)


def test_real_c10583_window_landed_not_double_counted():
    """Even in a genuinely-thrashier variant of the window the evidence must
    carry died/landed (never the double-counted 'done=20')."""
    events = _c10583_real_filing_shape()
    # remove the 2 partial landings -> 10 landed / 12 died -> genuine thrash
    events = [
        e
        for e in events
        if not (e.get("kind") == "reaped" and e.get("card") in ("C-PAR0", "C-PAR1"))
    ]
    out = retrospective._throughput_findings(events)
    assert out, "12 died / 10 landed is genuine thrash and must still file"
    ev = out[0]["evidence"]
    assert "died=12" in ev, repr(out)
    assert "landed=10" in ev, "must count 10 landed workers, not 20: " + repr(out)
    assert "dispatched=45" in ev, repr(out)
    assert "20 done" not in " ".join(out[0].values()), (
        "double-counted done=20 evidence must never be emitted: " + repr(out)
    )


def test_landed_pair_is_one_worker_not_two():
    """Core invariant: the paired card_done+reaped-outcome-done events for a
    single worker count as ONE landed worker (never the double-counted value).
    A board of ONLY pairs (4 workers, 8 events) is a healthy landed board,
    not thrash."""
    base = time.time() - 600
    events = [_disp(_iso(base - i * 60)) for i in range(8)]
    for i in range(4):
        events += _landed_pair(_iso(base - 400 + i * 30), f"C-L{i}")
    out = retrospective._throughput_findings(events)
    assert not out, "4 all-landed workers must not file thrash, got " + repr(out)


def test_all_died_with_no_landed_is_thrash():
    """Guard: a window with many deaths and zero landings is still genuine
    thrash (no over-suppression from the dedupe fix)."""
    base = time.time() - 600
    events = [_disp(_iso(base - i * 60)) for i in range(8)]
    for i in range(6):
        events.append(_death(f"C-GEN{i}", _iso(base - 300 + i * 10)))
    out = retrospective._throughput_findings(events)
    assert out and out[0]["evidence"] == "died=6 landed=0 dispatched=8", repr(out)


def test_balanced_deaths_equal_landings_is_not_thrash():
    """C-10324 contract: deaths == landed is a WASH, not 'dying more than
    landing'. The dedupe fix must not regress this equality edge."""
    base = time.time() - 600
    events = [_disp(_iso(base - i * 60)) for i in range(10)]
    events += _landed_pair(_iso(base - 500), "C-LAND")
    events.append(_death("C-DIE", _iso(base - 400)))
    out = retrospective._throughput_findings(events)
    assert not out, "died == landed must not file thrash, got " + repr(out)


def test_deaths_strictly_exceeding_landings_still_files():
    """C-10324 guard: 2 died / 1 landed is genuinely dying more than landing
    and must still file with the true counts."""
    base = time.time() - 600
    events = [_disp(_iso(base - i * 60)) for i in range(8)]
    events += _landed_pair(_iso(base - 500), "C-LAND")
    for i in range(2):
        events.append(_death(f"C-GEN{i}", _iso(base - 200 - i * 60)))
    out = retrospective._throughput_findings(events)
    assert out, "2 died / 1 landed is genuine thrash and must still file"
    assert "died=2" in out[0]["evidence"] and "landed=1" in out[0]["evidence"], repr(out)
