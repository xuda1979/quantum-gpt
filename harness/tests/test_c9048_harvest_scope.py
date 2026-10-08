"""C-9048 bounce-forensics regression tests.

All 7 cards bounced as "no RESULT verdict (dead)" (C-0023/C-0051/C-0069/
C-0073/C-9003/C-9004/C-9018) had worker replies containing valid RESULT
contract lines (EVENTS.jsonl reap verdicts + harness/state/agents/<id>.log).
Two reaper-side capture defects destroyed them:

  A) harvest_log leaks the PREVIOUS dispatch verdict into a dispatch that
     produced none: in an append-mode log, matches[-1] scans ALL segments,
     so a dead/empty last dispatch inherits seg1 PARTIAL. That defeated the
     environmental/API-outage re-arm (verdict no longer None) and burned
     bounce strikes with a lying reason.

  B) the no-verdict bounce reason lies ("no RESULT verdict" recorded while a
     PARTIAL verdict existed at reap) and no bounce reason on this path
     quotes the literal RESULT contract, so redispatches failed identically.
"""

from harness import harness_lib as H


def _write_log(tmp_path, text):
    p = tmp_path / "w.log"
    p.write_text(text, encoding="utf-8")
    return str(p)


SEG1 = (
    "\n===== dispatch 2026-09-16T19:50:00Z =====\n"
    "worked on the card\n"
    "RESULT: PARTIAL - ran out of time mid canary\n"
)
NO_RESULT_SEG = (
    "\n===== dispatch 2026-09-16T20:05:34Z =====\n"
    "claude died mid-run after an API error; no contract line printed\n"
)


def test_harvest_does_not_leak_previous_dispatch_verdict(tmp_path):
    # (A) RED: last dispatch produced no RESULT -> verdict must be None.
    # The old whole-file scan returned the earlier segment PARTIAL.
    path = _write_log(tmp_path, SEG1 + NO_RESULT_SEG)
    verdict, tail = H.harvest_log(path)
    assert verdict is None, (
        "harvest leaked the previous dispatch verdict into a dispatch "
        "that produced none (C-9048 defect A)"
    )
    assert isinstance(tail, list) and tail


def test_harvest_last_segment_wins_when_it_has_a_result(tmp_path):
    # C-9031 intent preserved: a fresh DONE in the last segment is the verdict.
    seg2 = "\n===== dispatch 2026-09-16T20:05:34Z =====\nok\nRESULT: DONE - 31/31\n"
    path = _write_log(tmp_path, SEG1 + seg2)
    verdict, _tail = H.harvest_log(path)
    assert verdict == "DONE"


def test_harvest_single_segment_unchanged(tmp_path):
    path = _write_log(tmp_path, "hello\nRESULT: BLOCKED - no box\n")
    verdict, _tail = H.harvest_log(path)
    assert verdict == "BLOCKED"


def test_bounce_reason_quotes_literal_result_contract():
    # (B) RED: H.bounce_reason does not exist yet. Every reason this path can
    # emit must quote the literal expected line so the redispatch succeeds
    # first try, and must never say "no RESULT verdict" when a verdict exists.
    literal = "RESULT: DONE|PARTIAL|BLOCKED"
    for verdict, outcome, over in [
        (None, "dead", False),
        (None, "overrun-killed", True),
        ("PARTIAL", "dead", False),
        (None, "harvested", False),
    ]:
        reason = H.bounce_reason(verdict, outcome, over)
        assert literal in reason, "bounce reason must quote the literal contract"
    # the recorded lie: verdict PARTIAL present but reason said "no RESULT verdict"
    reason = H.bounce_reason("PARTIAL", "dead", False)
    assert "no RESULT verdict" not in reason
    assert "PARTIAL" in reason
    # stall reason stays stall-named but also quotes the contract
    reason = H.bounce_reason(None, "stalled-killed", False)
    assert "stalled" in reason and literal in reason
