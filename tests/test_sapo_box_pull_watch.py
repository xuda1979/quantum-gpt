"""TDD (2026-09-01, P-10 from code-steward): the box-pull watch's stop
condition must be PER-RUN scoped, not a grep on the append-only ledger.

Bug: the loop greps the ledger for "ASI3 pull complete" / "ASI2 pull
complete" — a RE-INVOCATION after a prior successful run finds the old
markers and exits after one poll, silently pulling nothing for the new run.
Fix: the stop markers must include a per-invocation token (the start
timestamp) so only THIS run's completions satisfy the stop condition.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH = ROOT / "scripts" / "sapo_box_pull_watch.sh"


def test_stop_condition_is_per_run_scoped() -> None:
    source = WATCH.read_text(encoding="utf-8")
    # the stop markers must carry a per-invocation token (RUN_STAMP), so a
    # re-invocation after a prior success cannot match the old markers
    assert "RUN_STAMP" in source
    # the completion lines must embed the token
    assert "$RUN_STAMP ASI3 pull complete" in source
    assert "$RUN_STAMP ASI2 pull complete" in source
    # the stop grep must match only the token-scoped lines
    assert 'grep -q "$RUN_STAMP ASI3 pull complete"' in source
    assert 'grep -q "$RUN_STAMP ASI2 pull complete"' in source


def test_run_stamp_is_unique_per_invocation() -> None:
    source = WATCH.read_text(encoding="utf-8")
    # the token must include the start timestamp (date +%s) so two runs never collide
    assert 'RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)' in source
