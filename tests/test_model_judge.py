"""Tests for the frozen comprehensive judge: reward blend, response parsing,
and executable-anchor calibration.

The judge (base model / older accepted adapter) scores samples on five
dimensions; executable tests stay authoritative. A dimension contributes
reward weight only after calibration (AUC >= 0.85 / |rho| >= 0.6, n >= 200),
and the total judge mass is capped at 0.05, subtracted from the shaped term,
never from the pass reward.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from training.grpo_utils import (
    MAX_MODEL_JUDGE_WEIGHT,
    blend_comprehensive_reward,
)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CALIBRATION_SCRIPT = ROOT / "scripts" / "calibrate_model_judge.py"

from scripts.calibrate_model_judge import (  # noqa: E402
    compute_auc,
    compute_spearman_r,
    decide_enabled_dims,
)
from training.grpo_trainer import _parse_model_dim_scores  # noqa: E402


def test_blend_pass_always_outranks_fail() -> None:
    # Passing candidate with a hostile judge still beats a failing candidate
    # with a perfect judge: P dominates.
    passing = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.0,
        model_dim_scores={"correctness": 0.0},
        dim_weights={"correctness": 0.05},
    )
    failing = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.0,
        model_dim_scores={"correctness": 1.0},
        dim_weights={"correctness": 0.05},
    )
    assert passing > failing
    assert passing == 1.0


def test_blend_zero_weights_reduces_to_pass_plus_shaped() -> None:
    reward = blend_comprehensive_reward(
        pass_reward=0.5,
        shaped_reward=0.8,
        model_dim_scores={"correctness": 1.0},
        dim_weights={},
    )
    assert abs(reward - (0.5 + 0.5 * 0.8)) < 1e-9


def test_blend_judge_mass_capped_and_subtracted_from_shaped() -> None:
    reward = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.0,
        model_dim_scores={"correctness": 1.0, "efficiency": 1.0, "quality": 1.0},
        dim_weights={"correctness": 0.05, "efficiency": 0.05, "quality": 0.05},
    )
    # Total judge weight is capped at 0.05; the model term lives entirely
    # inside the (1 - P) mass, so with P=0 and S=0 the reward is exactly 0.05.
    assert abs(reward - 0.05) < 1e-9


def test_blend_truncation_penalty_bounded() -> None:
    reward = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.5,
        model_dim_scores={},
        dim_weights={},
        truncation_penalty=2.0,
    )
    assert 0.0 <= reward <= 1.0
    assert reward < 0.5


def test_parse_model_dim_scores_extracts_and_clamps() -> None:
    parsed = _parse_model_dim_scores(
        '{"correctness": 0.9, "runnability": 1.2, "result_correctness": -0.3, '
        '"efficiency": 0.7, "quality": "n/a"}'
    )
    assert parsed["correctness"] == 0.9
    assert parsed["runnability"] == 1.0  # clamped
    assert parsed["result_correctness"] == 0.0  # clamped
    assert parsed["efficiency"] == 0.7
    assert parsed["quality"] is None  # non-numeric -> missing


def test_parse_model_dim_scores_rejects_garbage() -> None:
    assert _parse_model_dim_scores("no json here") is None
    assert _parse_model_dim_scores("{}") is None
    assert _parse_model_dim_scores("") is None


def test_auc_perfect_random_and_reversed() -> None:
    assert compute_auc([True, True, False, False], [1.0, 0.9, 0.2, 0.1]) == 1.0
    assert compute_auc([True, True, False, False], [0.1, 0.2, 0.9, 1.0]) == 0.0
    assert compute_auc([True, False], [0.5, 0.5]) == 0.5  # ties
    assert compute_auc([True, True], [1.0, 0.9]) is None  # one class missing


def test_spearman_perfect_and_none() -> None:
    assert abs(compute_spearman_r([1.0, 2.0, 3.0], [0.1, 0.5, 0.9]) - 1.0) < 1e-9
    assert abs(compute_spearman_r([1.0, 2.0, 3.0], [0.9, 0.5, 0.1]) + 1.0) < 1e-9
    assert compute_spearman_r([1.0, 1.0], [0.5, 0.6]) is None  # zero variance


def test_calibration_gates_on_n_and_auc() -> None:
    # Too few samples: nothing enabled.
    assert (
        decide_enabled_dims(
            n=10,
            aucs={"correctness": 1.0, "runnability": 1.0, "result_correctness": 1.0},
            rho_efficiency=None,
        )
        == {}
    )
    # Below AUC threshold: nothing enabled.
    assert (
        decide_enabled_dims(
            n=250,
            aucs={"correctness": 0.7, "runnability": 0.8, "result_correctness": 0.6},
            rho_efficiency=None,
        )
        == {}
    )
    # Passing dimensions share the 0.05 cap uniformly.
    enabled = decide_enabled_dims(
        n=250,
        aucs={"correctness": 0.95, "runnability": 0.88, "result_correctness": 0.9},
        rho_efficiency=None,
    )
    assert set(enabled) == {"correctness", "runnability", "result_correctness"}
    assert abs(sum(enabled.values()) - MAX_MODEL_JUDGE_WEIGHT) < 1e-6
    assert all(weight > 0 for weight in enabled.values())


def test_calibration_efficiency_needs_negative_rho() -> None:
    # Positive rho (slower code scored higher) must NOT enable efficiency.
    enabled = decide_enabled_dims(
        n=250,
        aucs={"correctness": 1.0, "runnability": 1.0, "result_correctness": 1.0},
        rho_efficiency=0.9,
    )
    assert "efficiency" not in enabled
    # Negative rho of sufficient magnitude enables it.
    enabled = decide_enabled_dims(
        n=250,
        aucs={"correctness": 1.0, "runnability": 1.0, "result_correctness": 1.0},
        rho_efficiency=-0.8,
    )
    assert "efficiency" in enabled


def test_calibration_quality_never_auto_enabled() -> None:
    enabled = decide_enabled_dims(
        n=250,
        aucs={"correctness": 1.0, "runnability": 1.0, "result_correctness": 1.0},
        rho_efficiency=-0.8,
    )
    assert "quality" not in enabled


def test_calibration_script_end_to_end(tmp_path: Path) -> None:
    records_path = tmp_path / "judge_diagnostics.jsonl"
    with records_path.open("w", encoding="utf-8") as handle:
        for index in range(200):
            passed = index % 2 == 0
            handle.write(
                json.dumps(
                    {
                        "passed": passed,
                        "syntax_ok": True,
                        "verifier_rate": 1.0 if passed else 0.0,
                        "runtime_ms": 100 + index,
                        "model_dim_scores": {
                            "correctness": 0.95 if passed else 0.1,
                            "runnability": 0.9,
                            "result_correctness": 0.95 if passed else 0.1,
                            "efficiency": max(0.0, 1.0 - index / 1000.0),
                            "quality": 0.7,
                        },
                    }
                )
                + "\n"
            )
    out = tmp_path / "judge_calibration.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(CALIBRATION_SCRIPT),
            "--records",
            str(records_path),
            "--output",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    calibration = json.loads(out.read_text(encoding="utf-8"))
    assert calibration["n_samples"] == 200
    assert calibration["auc"]["correctness"] > 0.99
    # Efficiency vs runtime is negative and strong here.
    assert calibration["spearman_rho_efficiency_vs_runtime"] < -0.9
    enabled = calibration["enabled_dims"]
    assert "correctness" in enabled
    assert "efficiency" in enabled
    assert abs(sum(enabled.values()) - MAX_MODEL_JUDGE_WEIGHT) < 1e-6


def test_blend_uses_weights_from_calibration_file_shape() -> None:
    # The trainer reads {"enabled_dims": {...}} from the calibration file and
    # passes it straight into the blend; verify the shape composes.
    enabled = {"correctness": 0.016667, "runnability": 0.016667, "result_correctness": 0.016667}
    reward = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.5,
        model_dim_scores={"correctness": 1.0, "runnability": 0.5, "result_correctness": 0.0},
        dim_weights=enabled,
    )
    # Judge mean = (1.0 + 0.5 + 0.0)/3 = 0.5, mass 0.05 -> 0.025 model term.
    assert abs(reward - (0.5 * (1 - 0.05) + 0.025)) < 1e-9
