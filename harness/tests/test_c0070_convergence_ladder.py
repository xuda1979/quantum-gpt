#!/usr/bin/env python3
"""C-0070: convergence ladder instrument tests.

Covers:
  - LADDER spec: per-round stages mapped to existing card IDs
    (eval C-0015/C-0052 class, mine C-0016, train C-0029/C-0066) with
    entry and exit criteria per stage.
  - no-progress detector: FIRES on a plateau (N consecutive rounds with
    pass_adapter not increasing), STAYS SILENT on progress and when
    there is not enough history.
  - report-only escalation: emit appends an event to EVENTS.jsonl and
    never mutates QUEUE.json; the queue-minting path is documented as
    the operator command, not executed by the detector.

These tests do NOT hit the network and do NOT touch harness/state.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

import convergence_ladder as cl  # noqa: E402


def _hist(passes):
    return [{"round": i + 1, "pass_adapter": p, "source": "test"} for i, p in enumerate(passes)]


# ---------------------------------------------------------------------------
# LADDER spec: stages -> cards, entry/exit criteria
# ---------------------------------------------------------------------------


def test_ladder_spec_maps_stages_to_cards():
    by_stage = {s["stage"]: s["cards"] for s in cl.LADDER["stages"]}
    assert "C-0015" in by_stage["eval"] and "C-0052" in by_stage["eval"]
    assert "C-0016" in by_stage["mine"]
    assert "C-0029" in by_stage["train"] and "C-0066" in by_stage["train"]


def test_ladder_spec_has_entry_and_exit_per_stage():
    for s in cl.LADDER["stages"]:
        assert isinstance(s.get("entry"), list) and s["entry"], s["stage"]
        assert isinstance(s.get("exit"), list) and s["exit"], s["stage"]


def test_ladder_spec_round_order_is_eval_mine_train():
    order = [s["stage"] for s in cl.LADDER["stages"]]
    assert order == ["eval", "mine", "train"]


# ---------------------------------------------------------------------------
# no-progress detector: fires on plateau, silent on progress
# ---------------------------------------------------------------------------


def test_detector_fires_on_plateau():
    rec = cl.detect_no_progress(_hist([3, 3, 3, 3]), n=3)
    assert rec["plateau"] is True
    assert rec["n"] == 3
    assert rec["last_pass"] == 3


def test_detector_silent_when_improvement_is_inside_window():
    # climbed 1 -> 3 then stalled 2 rounds: only 2 consecutive
    # non-increasing rounds follow the improvement, so n=3 stays silent
    rec = cl.detect_no_progress(_hist([1, 3, 3, 3]), n=3)
    assert rec["plateau"] is False


def test_detector_silent_on_progress():
    rec = cl.detect_no_progress(_hist([1, 2, 3, 4]), n=3)
    assert rec["plateau"] is False


def test_detector_silent_when_a_round_increases_in_window():
    rec = cl.detect_no_progress(_hist([1, 1, 2, 3]), n=3)
    assert rec["plateau"] is False


def test_detector_silent_with_fewer_than_n_plus_one_rounds():
    # N flat rounds give only N-1 observable deltas: no verdict, no fire
    rec = cl.detect_no_progress(_hist([3, 3, 3]), n=3)
    assert rec["plateau"] is False


def test_detector_needs_a_baseline_round():
    rec = cl.detect_no_progress(_hist([3]), n=3)
    assert rec["plateau"] is False


def test_detector_decrease_counts_as_no_progress():
    rec = cl.detect_no_progress(_hist([5, 4, 3, 2]), n=3)
    assert rec["plateau"] is True


# ---------------------------------------------------------------------------
# escalation event + report-only emit
# ---------------------------------------------------------------------------


def test_escalation_event_shape():
    ev = cl.build_escalation_event(_hist([3, 3, 3, 3]), n=3)
    assert ev["kind"] == "no_progress_escalated"
    assert ev["card"] == "C-0070"
    assert ev["n"] == 3
    assert ev["rounds"] == [2, 3, 4]
    assert ev["last_pass"] == 3
    assert "qgh.py card add" in ev["escalation_path"]


def test_emit_escalation_is_report_only(tmp_path):
    state = str(tmp_path)
    ev = cl.build_escalation_event(_hist([3, 3, 3, 3]), n=3)
    cl.emit_escalation(state, ev)
    lines = (tmp_path / "EVENTS.jsonl").read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["kind"] == "no_progress_escalated"
    # report-only: the queue is never touched
    assert not (tmp_path / "QUEUE.json").exists()


def test_emit_escalation_refuses_to_fire_without_plateau(tmp_path):
    state = str(tmp_path)
    ev = cl.build_escalation_event(_hist([1, 2, 3, 4]), n=3)
    assert cl.emit_escalation(state, ev) is False
    assert not (tmp_path / "EVENTS.jsonl").exists()


def test_module_documents_queue_mint_command():
    assert "qgh.py card add" in (cl.__doc__ or "")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
