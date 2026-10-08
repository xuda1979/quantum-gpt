"""Unit tests for the automatic checkpoint gate (training/checkpoint_gate.py).

Covers the plan's table 27 acceptance criteria and table 28 role rotation /
rollback semantics.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.checkpoint_gate import (  # noqa: E402
    GateDecision,
    GateMetrics,
    RoleState,
    evaluate_checkpoint_gate,
)

BASE = GateMetrics(
    quantum_pass1=0.60,
    code_pass1=0.55,
    semantic_v=0.70,
    quantum_error=0.02,
)


def test_accept_when_quantum_improves():
    cand = GateMetrics(
        quantum_pass1=0.65,
        code_pass1=0.56,
        semantic_v=0.72,
        quantum_error=0.02,
    )
    d: GateDecision = evaluate_checkpoint_gate(cand, BASE)
    assert d.accepted is True
    assert d.reasons == []


def test_accept_when_quantum_within_error_of_anchor():
    # A tiny nominal dip inside the statistical error band is not a regression.
    cand = GateMetrics(
        quantum_pass1=0.59,  # 0.01 below anchor, 0.02 error -> within band
        code_pass1=0.55,
        semantic_v=0.70,
        quantum_error=0.02,
    )
    d = evaluate_checkpoint_gate(cand, BASE)
    assert d.accepted is True


def test_reject_on_code_regression_beyond_3pp():
    cand = GateMetrics(
        quantum_pass1=0.62,
        code_pass1=0.50,  # -5pp > 3pp limit
        semantic_v=0.72,
        quantum_error=0.02,
    )
    d = evaluate_checkpoint_gate(cand, BASE)
    assert d.accepted is False
    assert any("code_pass1" in r for r in d.reasons)
    assert d.rejecting_reason is not None


def test_reject_on_quantum_regression_beyond_error():
    cand = GateMetrics(
        quantum_pass1=0.55,  # -5pp > error band
        code_pass1=0.56,
        semantic_v=0.72,
        quantum_error=0.02,
    )
    d = evaluate_checkpoint_gate(cand, BASE)
    assert d.accepted is False
    assert any("quantum_pass1" in r for r in d.reasons)


def test_reject_on_semantic_regression():
    cand = GateMetrics(
        quantum_pass1=0.64,
        code_pass1=0.56,
        semantic_v=0.60,  # -0.10 > 0.05 allowance
        quantum_error=0.02,
    )
    d = evaluate_checkpoint_gate(cand, BASE)
    assert d.accepted is False
    assert any("semantic_v" in r for r in d.reasons)


def test_reject_on_diversity_breaker():
    cand = GateMetrics(
        quantum_pass1=0.66,
        code_pass1=0.58,
        semantic_v=0.73,
        quantum_error=0.02,
        diversity_ok=False,
    )
    d = evaluate_checkpoint_gate(cand, BASE)
    assert d.accepted is False
    assert any("diversity" in r for r in d.reasons)


def test_reject_on_safety_issue():
    cand = GateMetrics(
        quantum_pass1=0.66,
        code_pass1=0.58,
        semantic_v=0.73,
        quantum_error=0.02,
        safety_ok=False,
    )
    d = evaluate_checkpoint_gate(cand, BASE)
    assert d.accepted is False
    assert any("safety" in r for r in d.reasons)


def test_reject_on_numerical_instability():
    cand = GateMetrics(
        quantum_pass1=0.66,
        code_pass1=0.58,
        semantic_v=0.73,
        quantum_error=0.02,
        numeric_ok=False,
    )
    d = evaluate_checkpoint_gate(cand, BASE)
    assert d.accepted is False
    assert any("numerical" in r for r in d.reasons)


def test_accept_rotates_roles_with_judge_lag():
    state = RoleState(anchor_id="ckpt1", judge_id="base", current_id="ckpt1")
    state.accept(new_checkpoint_id="ckpt2", base_id="base")
    # New checkpoint becomes anchor + trainable current.
    assert state.anchor_id == "ckpt2"
    assert state.current_id == "ckpt2"
    # Judge lags to the previous accepted (never the new one).
    assert state.judge_id == "ckpt1"


def test_reject_keeps_anchor_and_returns_factors():
    state = RoleState(anchor_id="ckpt1", judge_id="base", current_id="ckpt1")
    factors = state.reject(lr_factor=0.5, kl_factor=1.5)
    # Rejection does not change anchor/judge roles.
    assert state.anchor_id == "ckpt1"
    assert state.judge_id == "base"
    # Returns the rollback hyperparameter factors for the trainer to apply.
    assert factors == {"lr_factor": 0.5, "kl_factor": 1.5}
