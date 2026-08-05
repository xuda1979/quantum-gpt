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

import torch

from training.grpo_utils import (
    MAX_MODEL_JUDGE_WEIGHT,
    blend_comprehensive_reward,
    sequence_ratio_stats,
    stable_gspo_loss_metrics,
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


def test_comprehensive_mode_fail_can_outrank_pass() -> None:
    """In comprehensive mode the pass term does NOT dominate (user decision)."""
    failing = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=1.0,
        model_dim_scores={"correctness": 1.0, "efficiency": 1.0},
        dim_weights={"correctness": 0.025, "efficiency": 0.025},
        mode="comprehensive",
    )
    passing = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.0,
        model_dim_scores={"correctness": 0.0, "efficiency": 0.0},
        dim_weights={"correctness": 0.025, "efficiency": 0.025},
        mode="comprehensive",
    )
    # 0.40*1 + 0.35*1 + 0.25*1 = 1.0 vs 0.40*1 + 0 = 0.40
    assert failing > passing


def test_comprehensive_mode_masses_renormalize_without_judge() -> None:
    reward = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.0,
        model_dim_scores={},
        dim_weights={},  # nothing calibrated yet -> judge mass 0
        mode="comprehensive",
    )
    # masses renormalize over P and S: 0.40/(0.40+0.35) = 0.5333
    assert abs(reward - 0.40 / 0.75) < 1e-9


def test_comprehensive_mode_default_masses() -> None:
    reward = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=1.0,
        model_dim_scores={"correctness": 1.0, "runnability": 1.0},
        dim_weights={"correctness": 0.025, "runnability": 0.025},
        mode="comprehensive",
    )
    assert abs(reward - 1.0) < 1e-9  # all components perfect
    reward = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.0,
        model_dim_scores={"correctness": 1.0},
        dim_weights={"correctness": 0.05},
        mode="comprehensive",
    )
    assert abs(reward - 0.25) < 1e-9  # judge mass only


def test_comprehensive_mode_judge_mass_uses_relative_dim_weights() -> None:
    reward = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.0,
        model_dim_scores={"correctness": 1.0, "efficiency": 0.0},
        dim_weights={"correctness": 0.04, "efficiency": 0.01},
        mode="comprehensive",
    )
    # model term = (0.8*1.0 + 0.2*0.0) = 0.8; judge mass 0.25 -> 0.20
    assert abs(reward - 0.20) < 1e-9


def test_p_dominant_still_dominates_when_requested() -> None:
    passing = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.0,
        model_dim_scores={"correctness": 0.0},
        dim_weights={"correctness": 0.05},
        mode="p_dominant",
    )
    failing = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.5,
        model_dim_scores={"correctness": 1.0},
        dim_weights={"correctness": 0.05},
        mode="p_dominant",
    )
    assert passing == 1.0
    assert failing < passing
    assert abs(failing - (0.5 * 0.95 + 0.05)) < 1e-9


def test_judge_diagnostics_record_shape() -> None:
    """Per-candidate diagnostics pair executable anchors with judge scores."""
    from training.grpo_utils import build_judge_diagnostics_record

    record = build_judge_diagnostics_record(
        task_id="t1",
        passed=False,
        syntax_ok=True,
        verifier_rate=0.5,
        model_dim_scores={"correctness": 0.1, "efficiency": None},
        step=3,
    )
    assert record["passed"] is False
    assert record["syntax_ok"] is True
    assert record["verifier_rate"] == 0.5
    assert record["model_dim_scores"]["correctness"] == 0.1
    assert record["model_dim_scores"]["efficiency"] is None
    assert record["step"] == 3
    # calibrate_model_judge.py's loader consumes this shape directly.
    import tempfile

    from scripts.calibrate_model_judge import load_records

    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as handle:
        handle.write(__import__("json").dumps(record) + "\n")
        path = handle.name
    loaded = load_records(Path(path))
    assert loaded[0]["model_dim_scores"]["correctness"] == 0.1


def test_fp32_ratio_boundaries_stay_distinguishable() -> None:
    """Review #2: at FP32, the 3e-4/4e-4 clip boundaries must be
    distinguishable — FP16/BF16 would quantize them away (torch.finfo
    eps: FP16 ~9.8e-4, BF16 ~7.8e-3 near 1.0)."""
    log_ratios = torch.tensor(
        [
            -0.0010,
            -0.0004,
            -0.0003,
            -0.0001,
            0.0000,
            0.0001,
            0.0003,
            0.0004,
            0.0010,
        ],
        dtype=torch.float32,
    )
    old = torch.zeros_like(log_ratios)
    stats = sequence_ratio_stats(log_ratios, old, clip_low=3e-4, clip_high=4e-4)
    ratios = torch.exp(log_ratios)
    # Values strictly inside the clip window: 0.0000, -0.0001, 0.0001
    n = float(ratios.numel())
    expected_clip = float(((ratios < 1.0 - 3e-4) | (ratios > 1.0 + 4e-4)).sum().item() / n)
    assert stats["clip_fraction_after_update"] == expected_clip
    assert stats["clip_fraction_after_update"] > 0.0  # clipping is measurable
    # FP32 spacing near 1.0 is ~1.2e-7 — far below 1e-4, so boundaries resolve.
    assert torch.finfo(torch.float32).eps < 3e-4 / 10
    # The same ratios in BF16 would quantize the boundaries away.
    assert torch.finfo(torch.bfloat16).eps > 3e-4
    assert torch.finfo(torch.float16).eps > 3e-4


def test_sequence_ratio_stats_synchronous_mode() -> None:
    """Review #1: in the synchronous one-step implementation the pre-update
    ratio is 1 by construction (clip fraction 0); after a move the stats
    reflect the post-update policy."""
    # Pre-update: current == old -> ratios all 1 -> no clipping.
    old = torch.tensor([-1.0, -0.5, 0.0], dtype=torch.float32)
    stats = sequence_ratio_stats(old, old, clip_low=3e-4, clip_high=4e-4)
    assert stats["ratio_before_update"] == 1.0
    assert stats["clip_fraction_before_update"] == 0.0
    # Post-update: policy moved.
    moved = old + torch.tensor([-0.01, 0.0, 0.0], dtype=torch.float32)  # policy moved AWAY
    stats = sequence_ratio_stats(moved, old, clip_low=3e-4, clip_high=4e-4)
    assert stats["clip_fraction_after_update"] > 0.0
    assert stats["seq_kl_after"] > 0.0


def test_tiered_mode_hard_tier_separation() -> None:
    """Review #5: tiered reward keeps execution authoritative while rich."""
    # Any passing candidate outranks any failing candidate, even with a
    # hostile judge on the passer and a perfect judge on the failure.
    passing = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.0,
        model_dim_scores={"efficiency": 0.0, "quality": 0.0},
        dim_weights={"efficiency": 0.025, "quality": 0.025},
        mode="tiered",
    )
    failing = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=1.0,  # perfect progress on a failing candidate
        model_dim_scores={"efficiency": 1.0, "quality": 1.0},
        dim_weights={"efficiency": 0.025, "quality": 0.025},
        mode="tiered",
    )
    assert failing <= 0.95
    assert passing >= 1.0
    assert passing > failing


def test_tiered_mode_passers_differentiated_by_efficiency_quality() -> None:
    efficient = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=1.0,
        model_dim_scores={"efficiency": 1.0, "quality": 1.0},
        dim_weights={"efficiency": 0.025, "quality": 0.025},
        mode="tiered",
        pass_mass=0.10,
        shaped_mass=0.10,
    )
    plain = blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=1.0,
        model_dim_scores={"efficiency": 0.0, "quality": 0.0},
        dim_weights={"efficiency": 0.025, "quality": 0.025},
        mode="tiered",
        pass_mass=0.10,
        shaped_mass=0.10,
    )
    assert abs(efficient - 1.20) < 1e-9
    assert abs(plain - 1.00) < 1e-9
    assert efficient > plain


def test_tiered_mode_failures_learnable_and_capped() -> None:
    progress = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.7,
        model_dim_scores={},
        dim_weights={},
        mode="tiered",
    )
    assert abs(progress - 0.70) < 1e-9
    maxed = blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=1.0,
        model_dim_scores={"efficiency": 1.0},
        dim_weights={"efficiency": 0.025},
        mode="tiered",
    )
    assert maxed <= 0.95


def test_length_neutral_gspo_weights_long_responses() -> None:
    """Review #3: LUSPO-style length weights neutralize the sequence-mean
    ratio's dilution of long responses (capped so one long candidate cannot
    dominate)."""
    torch.manual_seed(1)
    log_probs = torch.randn(6)
    old_log_probs = torch.randn(6) * 0.1
    advantages = torch.tensor([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    lengths = torch.tensor([50.0, 100.0, 200.0, 400.0, 800.0, 1600.0])
    weights = torch.clamp(lengths / 256.0, max=4.0)
    plain, plain_stats = stable_gspo_loss_metrics(
        log_probs,
        old_log_probs,
        advantages,
        clip_low=3e-4,
        clip_high=4e-4,
        kl_coeff=0.005,
        numerical_log_ratio_clip=8.0,
    )
    weighted, weighted_stats = stable_gspo_loss_metrics(
        log_probs,
        old_log_probs,
        advantages,
        clip_low=3e-4,
        clip_high=4e-4,
        kl_coeff=0.005,
        numerical_log_ratio_clip=8.0,
        length_weights=weights,
    )
    assert not torch.allclose(plain, weighted)
    assert abs(weighted_stats["length_weight_mean"] - float(weights.mean().item())) < 1e-9
    # The cap is enforced: the longest response gets w=4.0, not 1600/256=6.25.
    assert float(weights.max().item()) == 4.0
    # With weights all 1.0 the loss matches the plain GSPO loss.
    ones = torch.ones_like(lengths)
    plain2, _ = stable_gspo_loss_metrics(
        log_probs,
        old_log_probs,
        advantages,
        clip_low=3e-4,
        clip_high=4e-4,
        kl_coeff=0.005,
        numerical_log_ratio_clip=8.0,
        length_weights=ones,
    )
    assert torch.allclose(plain, plain2)
