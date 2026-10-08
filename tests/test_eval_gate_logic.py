"""Unit tests for the eval-regression gate in scripts/rl_distill_pipeline.py.

Tests only the pure decision logic (_eval_gate_tripped, _read_eval_verdict,
_load_eval_gate) — no network, no model, no heavy deps. The pipeline module
imports cleanly on py3.14 because it only needs stdlib at import time.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.rl_distill_pipeline import (  # noqa: E402
    EvalGateConfig,
    _eval_gate_tripped,
    _load_eval_gate,
    _read_eval_verdict,
)


class TestLoadEvalGate:
    def test_defaults_when_empty(self):
        g = _load_eval_gate({})
        assert g.enabled is False
        assert g.verdict_path == ""
        assert g.tolerance_pass_at_1 == 0.03
        assert g.tolerance_r_runnable == 0.20
        assert g.required_consecutive == 2

    def test_loads_all_fields(self):
        g = _load_eval_gate(
            {
                "enabled": True,
                "verdict_path": "/tmp/verdict.json",
                "poll_every_seconds": 60,
                "tolerance_pass_at_1": 0.05,
                "tolerance_r_runnable": 0.15,
                "required_consecutive": 1,
            }
        )
        assert g.enabled is True
        assert g.verdict_path == "/tmp/verdict.json"
        assert g.poll_every_seconds == 60
        assert g.tolerance_pass_at_1 == 0.05
        assert g.tolerance_r_runnable == 0.15
        assert g.required_consecutive == 1


class TestReadEvalVerdict:
    def test_missing_path_returns_none(self, tmp_path):
        assert _read_eval_verdict("") is None
        assert _read_eval_verdict(str(tmp_path / "nope.json")) is None

    def test_valid_json(self, tmp_path):
        p = tmp_path / "verdict.json"
        p.write_text(json.dumps({"adapter_eval_pass_at_1": 0.4}))
        v = _read_eval_verdict(str(p))
        assert v is not None
        assert v["adapter_eval_pass_at_1"] == 0.4

    def test_corrupt_json_returns_none(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("{not json")
        assert _read_eval_verdict(str(p)) is None


class TestEvalGateTripped:
    def test_disabled_gate_never_trips(self):
        gate = EvalGateConfig(enabled=False)
        assert _eval_gate_tripped(gate, {"adapter_eval_pass_at_1": 0.0}) is None

    def test_no_verdict_never_trips(self):
        gate = EvalGateConfig(enabled=True)
        assert _eval_gate_tripped(gate, None) is None

    def test_small_dip_no_consecutive_does_not_trip(self):
        gate = EvalGateConfig(enabled=True, tolerance_pass_at_1=0.03, required_consecutive=2)
        verdict = {
            "adapter_eval_pass_at_1": 0.50,
            "baseline_eval_pass_at_1": 0.55,  # 0.05 drop >= tolerance
            "consecutive_regressions": 1,  # but only 1 consecutive — not enough
        }
        assert _eval_gate_tripped(gate, verdict) is None

    def test_dip_with_consecutive_trips(self):
        gate = EvalGateConfig(enabled=True, tolerance_pass_at_1=0.03, required_consecutive=2)
        verdict = {
            "adapter_eval_pass_at_1": 0.50,
            "baseline_eval_pass_at_1": 0.55,
            "consecutive_regressions": 2,
        }
        reason = _eval_gate_tripped(gate, verdict)
        assert reason is not None
        assert "eval_regression" in reason
        assert "0.500" in reason
        assert "0.550" in reason

    def test_r_runnable_collapse_trips_immediately(self):
        gate = EvalGateConfig(enabled=True, tolerance_r_runnable=0.20, required_consecutive=99)
        verdict = {
            "r_runnable": 0.70,
            "baseline_r_runnable": 0.95,  # 0.25 drop >= 0.20
            "consecutive_regressions": 0,  # even with 0 consecutive — runnable is foundational
        }
        reason = _eval_gate_tripped(gate, verdict)
        assert reason is not None
        assert "r_runnable collapse" in reason

    def test_flat_or_improving_does_not_trip(self):
        gate = EvalGateConfig(enabled=True, tolerance_pass_at_1=0.03, required_consecutive=1)
        verdict = {
            "adapter_eval_pass_at_1": 0.60,
            "baseline_eval_pass_at_1": 0.55,  # improved
            "consecutive_regressions": 0,
        }
        assert _eval_gate_tripped(gate, verdict) is None

    def test_dip_within_tolerance_does_not_trip(self):
        gate = EvalGateConfig(enabled=True, tolerance_pass_at_1=0.03, required_consecutive=1)
        verdict = {
            "adapter_eval_pass_at_1": 0.53,
            "baseline_eval_pass_at_1": 0.55,  # 0.02 drop < 0.03 tolerance
            "consecutive_regressions": 5,
        }
        assert _eval_gate_tripped(gate, verdict) is None

    def test_missing_fields_does_not_trip(self):
        gate = EvalGateConfig(enabled=True)
        assert _eval_gate_tripped(gate, {}) is None
        assert _eval_gate_tripped(gate, {"adapter_eval_pass_at_1": 0.4}) is None
