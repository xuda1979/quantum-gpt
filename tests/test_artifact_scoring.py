"""Unit tests for training/artifact_scoring.py.

Covers:
- Issue classifier keyword table + conservative fallback.
- Score-vector range contracts (all fields in [0, 1]).
- Behavioural contracts: r_pass pinning, r_partial max-severity, length
  penalty piecewise-linear, hallucination fraction.
- Trainer-side helpers: kl_gate_weight, reward_weighted_nll_weight.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.artifact_scoring import (
    CONFIDENCE_FLOOR_FOR_KL_GATE,
    classify_issue,
    classify_issues,
    kl_gate_weight,
    reward_weighted_nll_weight,
    score_artifact,
)

# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "issue,expected",
    [
        ("Syntax error on line 5", "syntax"),
        ("IndentationError: unexpected indent", "syntax"),
        ("ModuleNotFoundError: no module named 'qiskit_aer'", "import_error"),
        ("Cannot import name 'AerSimulator' from 'qiskit_aer'", "import_error"),
        ("NameError: name 'qc' is not defined", "name_error"),
        ("AttributeError: 'QuantumCircuit' object has no attribute 'run'", "name_error"),
        ("Uses deprecated qiskit.Aer — should use qiskit_aer.AerSimulator", "deprecated_api"),
        ("qiskit.execute is deprecated; use backend.run", "deprecated_api"),
        ("Wrong API: should use qiskit.qasm2.export instead of .qasm()", "wrong_api"),
        ("Misuse of the circuit.draw() method", "wrong_api"),
        ("Hallucinated import: 'qiskit.magic' does not exist", "hallucinated_import"),
        ("Nonexistent module 'pennylane.quantum_magic'", "hallucinated_import"),
        ("Style: line too long (pep8)", "style"),
        ("pyflakes: unused import 'numpy'", "style"),
        ("The algorithm does not produce the correct statevector", "logic"),
        ("Wrong gate ordering leads to incorrect unitary", "logic"),
        ("", "other"),
        ("   ", "other"),
    ],
)
def test_classify_issue_keyword_table(issue, expected):
    assert classify_issue(issue) == expected


def test_classify_issues_maps_each_string():
    issues = ["Syntax error", "NameError: x", "style issue", "totally unknown problem"]
    cats = classify_issues(issues)
    assert cats == ["syntax", "name_error", "style", "logic"]


def test_classify_issue_conservative_fallback_to_logic():
    # Unrecognised non-empty criticism must fall into "logic", NOT "other".
    assert classify_issue("the student's qubit allocation is suboptimal") == "logic"


# ---------------------------------------------------------------------------
# score_artifact: range contracts
# ---------------------------------------------------------------------------


def test_score_artifact_all_fields_in_range_for_perfect_sample():
    result = {"is_correct": True, "confidence": 0.95, "issues": []}
    scores = score_artifact(result, correct_answer="print('hello')", resample_attempts=1)
    assert set(scores.keys()) == {
        "r_pass",
        "r_partial",
        "r_runnable",
        "r_api_correct",
        "r_style",
        "r_length_penalty",
        "r_hallucination_penalty",
        "r_teacher_confidence",
        "r_first_pass",
    }
    for k, v in scores.items():
        assert 0.0 <= v <= 1.0, f"{k}={v} out of [0,1]"


def test_score_artifact_perfect_sample_values():
    result = {"is_correct": True, "confidence": 0.95, "issues": []}
    scores = score_artifact(result, correct_answer="print('hello')", resample_attempts=1)
    assert scores["r_pass"] == 1.0
    assert scores["r_partial"] == 1.0
    assert scores["r_runnable"] == 1.0
    assert scores["r_api_correct"] == 1.0
    assert scores["r_style"] == 1.0
    assert scores["r_length_penalty"] == 0.0  # short answer
    assert scores["r_hallucination_penalty"] == 0.0
    assert scores["r_teacher_confidence"] == 0.95
    assert scores["r_first_pass"] == 1.0


def test_score_artifact_total_failure_values():
    result = {
        "is_correct": False,
        "confidence": 0.2,
        "issues": ["Syntax error on line 3", "NameError: 'qc' not defined"],
    }
    scores = score_artifact(result, correct_answer="x", resample_attempts=3)
    assert scores["r_pass"] == 0.0
    assert scores["r_runnable"] == 0.0  # syntax + name_error both affect runnable
    assert scores["r_partial"] < 1.0  # at least one severe issue
    assert scores["r_teacher_confidence"] == 0.2
    assert scores["r_first_pass"] == 0.0


# ---------------------------------------------------------------------------
# score_artifact: behavioural contracts
# ---------------------------------------------------------------------------


def test_r_partial_pinned_to_1_when_is_correct():
    # Teacher says correct but lists some minor issues; r_partial must be 1.0.
    result = {
        "is_correct": True,
        "confidence": 0.9,
        "issues": ["style: line too long", "could use a helper function"],
    }
    scores = score_artifact(result, correct_answer="ok", resample_attempts=1)
    assert scores["r_partial"] == 1.0


def test_r_partial_uses_max_severity_not_sum():
    # Two mild issues should not compound to a total drop.
    result = {
        "is_correct": False,
        "confidence": 0.5,
        "issues": ["style: line too long", "unused import"],
    }
    scores = score_artifact(result, correct_answer="ok", resample_attempts=1)
    # Style max weight is 0.4 (unused import); r_partial = 1 - 0.4 = 0.6
    assert scores["r_partial"] == pytest.approx(0.6)


def test_r_partial_one_severe_issue_drops_to_zero():
    result = {
        "is_correct": False,
        "confidence": 0.5,
        "issues": ["Syntax error", "style: line too long"],
    }
    scores = score_artifact(result, correct_answer="ok", resample_attempts=1)
    # Syntax weight is 1.0; r_partial = 1 - 1.0 = 0.0
    assert scores["r_partial"] == 0.0


def test_r_runnable_zero_if_syntax_issue_present():
    result = {"is_correct": False, "confidence": 0.5, "issues": ["Syntax error"]}
    scores = score_artifact(result, correct_answer="ok", resample_attempts=1)
    assert scores["r_runnable"] == 0.0


def test_r_runnable_one_if_only_logic_issue():
    result = {"is_correct": False, "confidence": 0.5, "issues": ["the algorithm is incorrect"]}
    scores = score_artifact(result, correct_answer="ok", resample_attempts=1)
    assert scores["r_runnable"] == 1.0


def test_r_api_correct_zero_if_hallucinated_import():
    result = {
        "is_correct": False,
        "confidence": 0.5,
        "issues": ["Hallucinated import 'qiskit.magic'"],
    }
    scores = score_artifact(result, correct_answer="ok", resample_attempts=1)
    assert scores["r_api_correct"] == 0.0
    assert scores["r_hallucination_penalty"] == 1.0  # 1/1 issues are halluc


def test_r_hallucination_penalty_fraction():
    result = {
        "is_correct": False,
        "confidence": 0.5,
        "issues": ["Hallucinated import 'x'", "style issue", "logic problem"],
    }
    scores = score_artifact(result, correct_answer="ok", resample_attempts=1)
    assert scores["r_hallucination_penalty"] == pytest.approx(1 / 3)


def test_r_length_penalty_piecewise_linear():
    short = score_artifact(
        {"is_correct": True, "confidence": 1.0, "issues": []},
        correct_answer="x" * 100,
        resample_attempts=1,
    )
    assert short["r_length_penalty"] == 0.0

    at_threshold = score_artifact(
        {"is_correct": True, "confidence": 1.0, "issues": []},
        correct_answer="x" * 4000,
        resample_attempts=1,
    )
    assert at_threshold["r_length_penalty"] == 0.0

    mid = score_artifact(
        {"is_correct": True, "confidence": 1.0, "issues": []},
        correct_answer="x" * 6000,
        resample_attempts=1,
    )
    assert mid["r_length_penalty"] == pytest.approx(0.5)

    saturated = score_artifact(
        {"is_correct": True, "confidence": 1.0, "issues": []},
        correct_answer="x" * 8000,
        resample_attempts=1,
    )
    assert saturated["r_length_penalty"] == 1.0

    over = score_artifact(
        {"is_correct": True, "confidence": 1.0, "issues": []},
        correct_answer="x" * 12000,
        resample_attempts=1,
    )
    assert over["r_length_penalty"] == 1.0


def test_r_teacher_confidence_clamped():
    high = score_artifact(
        {"is_correct": True, "confidence": 1.5, "issues": []},
        correct_answer="ok",
        resample_attempts=1,
    )
    assert high["r_teacher_confidence"] == 1.0
    low = score_artifact(
        {"is_correct": False, "confidence": -0.3, "issues": []},
        correct_answer="ok",
        resample_attempts=1,
    )
    assert low["r_teacher_confidence"] == 0.0
    none = score_artifact(
        {"is_correct": True, "issues": []}, correct_answer="ok", resample_attempts=1
    )
    assert none["r_teacher_confidence"] == 0.5  # default when missing


def test_r_first_pass_resample_attempts():
    first = score_artifact(
        {"is_correct": True, "confidence": 1.0, "issues": []},
        correct_answer="ok",
        resample_attempts=1,
    )
    assert first["r_first_pass"] == 1.0
    second = score_artifact(
        {"is_correct": True, "confidence": 1.0, "issues": []},
        correct_answer="ok",
        resample_attempts=2,
    )
    assert second["r_first_pass"] == 0.0


def test_score_artifact_handles_missing_issues_field():
    result = {"is_correct": True, "confidence": 0.9}  # no "issues" key
    scores = score_artifact(result, correct_answer="ok", resample_attempts=1)
    assert scores["r_partial"] == 1.0
    assert scores["r_runnable"] == 1.0


# ---------------------------------------------------------------------------
# Trainer-side helpers
# ---------------------------------------------------------------------------


def test_kl_gate_weight_floors_confidence():
    scores = {"r_teacher_confidence": 0.1}
    assert kl_gate_weight(scores) == CONFIDENCE_FLOOR_FOR_KL_GATE
    scores = {"r_teacher_confidence": 0.8}
    assert kl_gate_weight(scores) == 0.8
    scores = {}  # missing -> default 1.0
    assert kl_gate_weight(scores) == 1.0


def test_reward_weighted_nll_weight_legacy_path():
    # partial_credit_upweight=0 -> pure rescaled reward weight.
    w = reward_weighted_nll_weight(
        reward=0.5, reward_floor=0.2, r_partial=0.5, partial_credit_upweight=0.0
    )
    # (0.5 - 0.2) / (1 - 0.2) = 0.3 / 0.8 = 0.375
    assert w == pytest.approx(0.375)


def test_reward_weighted_nll_weight_floor_gives_zero():
    w = reward_weighted_nll_weight(
        reward=0.2, reward_floor=0.2, r_partial=1.0, partial_credit_upweight=0.5
    )
    assert w == pytest.approx(0.5)  # 0 + 0.5 * 1.0


def test_reward_weighted_nll_weight_perfect_gives_one_plus_upweight():
    w = reward_weighted_nll_weight(
        reward=1.0, reward_floor=0.2, r_partial=1.0, partial_credit_upweight=0.5
    )
    assert w == pytest.approx(1.5)


def test_reward_weighted_nll_weight_below_floor_clamped_to_zero():
    w = reward_weighted_nll_weight(
        reward=0.1, reward_floor=0.2, r_partial=0.0, partial_credit_upweight=0.0
    )
    assert w == 0.0


def test_reward_weighted_nll_weight_r_partial_only_contributes_when_positive():
    # partial_credit_upweight is the H1 knob; at 0 it should not contribute.
    w_off = reward_weighted_nll_weight(
        reward=0.5, reward_floor=0.0, r_partial=1.0, partial_credit_upweight=0.0
    )
    w_on = reward_weighted_nll_weight(
        reward=0.5, reward_floor=0.0, r_partial=1.0, partial_credit_upweight=0.5
    )
    assert w_off == pytest.approx(0.5)
    assert w_on == pytest.approx(1.0)
