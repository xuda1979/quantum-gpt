"""Unit tests for the reward-weighted loss path in training/qwen_sft_peft_kl.py.

We do NOT instantiate the full trainer (which needs a model + NPU). Instead
we test:
1. The legacy path: with reward_weighted_nll=False, per_artifact_kl_gate=False,
   partial_credit_upweight=0.0, the effective coefficients equal the base
   coefficients exactly (no regression).
2. The reward-weighted NLL path scales nll_coeff by reward_weighted_nll_weight.
3. The KL-gate path scales kl_coeff by kl_gate_weight.
4. The partial-credit-upweight path adds r_partial-weighted NLL.
5. End-to-end: kl_distill_loss with effective coefficients produces the
   expected numeric values vs. legacy.

These tests construct mock student/teacher tensors and call kl_distill_loss
directly with different coefficient values, mirroring what the training loop
does.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

torch = pytest.importorskip("torch")

from training.artifact_scoring import (
    kl_gate_weight,
    reward_weighted_nll_weight,
)
from training.qwen_sft_peft_kl import kl_distill_loss

# ---------------------------------------------------------------------------
# Mock tensor builders
# ---------------------------------------------------------------------------


def _make_mock_inputs(T: int = 6, V: int = 50, K: int = 5):
    """Build small deterministic student/teacher tensors for loss tests.

    T = sequence length (assistant tokens), V = vocab, K = teacher top-k.
    """
    torch.manual_seed(123)
    student_logits = torch.randn(T, V, dtype=torch.float32)
    # Teacher's argmax token ids (the "correct" tokens).
    teacher_token_ids = torch.tensor([10, 11, 12, 13, 14, 15], dtype=torch.long)
    teacher_logprob_argmax = torch.tensor([-0.5, -0.6, -0.4, -0.7, -0.3, -0.5], dtype=torch.float32)
    # Teacher top-k: ids and logprobs (K per position, -inf padding).
    teacher_topk_token_ids = torch.randint(0, V, (T, K), dtype=torch.long)
    teacher_topk_logprobs = torch.randn(T, K, dtype=torch.float32) - 1.0
    nll_labels = teacher_token_ids.clone()  # NLL targets = teacher argmax
    return dict(
        student_logits_at_positions=student_logits,
        teacher_token_ids=teacher_token_ids,
        teacher_logprob_argmax=teacher_logprob_argmax,
        teacher_topk_token_ids=teacher_topk_token_ids,
        teacher_topk_logprobs=teacher_topk_logprobs,
        nll_labels=nll_labels,
    )


# ---------------------------------------------------------------------------
# Coefficient computation contracts (mirrors the training loop logic)
# ---------------------------------------------------------------------------


def compute_effective_coeffs(
    *,
    base_nll_coeff: float,
    base_kl_coeff: float,
    reward_floor: float,
    row_reward: float,
    artifact_scores: dict,
    reward_weighted_nll: bool,
    per_artifact_kl_gate: bool,
    partial_credit_upweight: float,
):
    """Replicate the per-sample coefficient logic from the training loop."""
    nll_coeff_eff = base_nll_coeff
    kl_coeff_eff = base_kl_coeff
    if reward_weighted_nll or partial_credit_upweight > 0.0:
        nll_coeff_eff = base_nll_coeff * reward_weighted_nll_weight(
            reward=row_reward,
            reward_floor=reward_floor,
            r_partial=float(artifact_scores.get("r_partial", 0.0) or 0.0),
            partial_credit_upweight=partial_credit_upweight,
        )
    if per_artifact_kl_gate and artifact_scores:
        kl_coeff_eff = base_kl_coeff * kl_gate_weight(artifact_scores)
    return nll_coeff_eff, kl_coeff_eff


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_legacy_path_coefficients_unchanged():
    nll_eff, kl_eff = compute_effective_coeffs(
        base_nll_coeff=0.5,
        base_kl_coeff=0.5,
        reward_floor=0.2,
        row_reward=0.3,
        artifact_scores={"r_partial": 0.5, "r_teacher_confidence": 0.4},
        reward_weighted_nll=False,
        per_artifact_kl_gate=False,
        partial_credit_upweight=0.0,
    )
    assert nll_eff == 0.5
    assert kl_eff == 0.5


def test_reward_weighted_nll_scales_nll_coefficient():
    nll_eff, kl_eff = compute_effective_coeffs(
        base_nll_coeff=0.5,
        base_kl_coeff=0.5,
        reward_floor=0.2,
        row_reward=0.6,  # (0.6 - 0.2) / 0.8 = 0.5
        artifact_scores={"r_partial": 0.0},
        reward_weighted_nll=True,
        per_artifact_kl_gate=False,
        partial_credit_upweight=0.0,
    )
    assert nll_eff == pytest.approx(0.25)  # 0.5 * 0.5
    assert kl_eff == 0.5  # unchanged


def test_per_artifact_kl_gate_scales_kl_coefficient():
    nll_eff, kl_eff = compute_effective_coeffs(
        base_nll_coeff=0.5,
        base_kl_coeff=0.5,
        reward_floor=0.2,
        row_reward=0.6,
        artifact_scores={"r_teacher_confidence": 0.8},
        reward_weighted_nll=False,
        per_artifact_kl_gate=True,
        partial_credit_upweight=0.0,
    )
    assert nll_eff == 0.5  # unchanged
    assert kl_eff == pytest.approx(0.4)  # 0.5 * 0.8


def test_kl_gate_floors_at_0_3():
    nll_eff, kl_eff = compute_effective_coeffs(
        base_nll_coeff=0.5,
        base_kl_coeff=0.5,
        reward_floor=0.0,
        row_reward=0.5,
        artifact_scores={"r_teacher_confidence": 0.1},  # below floor
        reward_weighted_nll=False,
        per_artifact_kl_gate=True,
        partial_credit_upweight=0.0,
    )
    assert kl_eff == pytest.approx(0.5 * 0.3)  # floored


def test_partial_credit_upweight_adds_r_partial_weight():
    nll_eff, kl_eff = compute_effective_coeffs(
        base_nll_coeff=0.5,
        base_kl_coeff=0.5,
        reward_floor=0.0,
        row_reward=0.5,
        artifact_scores={"r_partial": 1.0},
        reward_weighted_nll=False,
        per_artifact_kl_gate=False,
        partial_credit_upweight=0.5,
    )
    # base = 0.5 (reward 0.5, floor 0.0); + 0.5 * 1.0 = 1.0; * nll_coeff 0.5 = 0.5
    assert nll_eff == pytest.approx(0.5 * 1.0)


def test_full_presets_combined():
    # Preset E (full): rw-nll + kl-gate + partial-up
    nll_eff, kl_eff = compute_effective_coeffs(
        base_nll_coeff=0.5,
        base_kl_coeff=0.5,
        reward_floor=0.2,
        row_reward=0.6,  # base rw weight = 0.5
        artifact_scores={"r_partial": 0.8, "r_teacher_confidence": 0.7},
        reward_weighted_nll=True,
        per_artifact_kl_gate=True,
        partial_credit_upweight=0.5,
    )
    # nll: 0.5 * (0.5 + 0.5*0.8) = 0.5 * 0.9 = 0.45
    assert nll_eff == pytest.approx(0.45)
    # kl: 0.5 * 0.7 = 0.35
    assert kl_eff == pytest.approx(0.35)


# ---------------------------------------------------------------------------
# End-to-end: kl_distill_loss with effective coefficients
# ---------------------------------------------------------------------------


def test_kl_distill_loss_legacy_vs_reward_weighted_produces_different_loss():
    inputs = _make_mock_inputs()
    # Legacy: nll_coeff=0.5, kl_coeff=0.5
    legacy_loss, legacy_stats = kl_distill_loss(
        **inputs,
        torch_module=torch,
        ignore_index=-100,
        kl_coeff=0.5,
        nll_coeff=0.5,
        temperature=1.0,
    )
    # Reward-weighted: nll_coeff scaled down (reward=0.3, floor=0.2 -> weight=0.125)
    rw_nll_coeff = 0.5 * 0.125
    rw_loss, rw_stats = kl_distill_loss(
        **inputs,
        torch_module=torch,
        ignore_index=-100,
        kl_coeff=0.5,
        nll_coeff=rw_nll_coeff,
        temperature=1.0,
    )
    # raw nll is the same (same inputs); the scaled total differs because
    # the nll coefficient is smaller.
    assert rw_stats["nll"] == legacy_stats["nll"]  # raw, unscaled
    assert rw_loss != legacy_loss
    # total_rw = rw_nll_coeff * nll + 0.5 * kl  <  total_legacy = 0.5 * nll + 0.5 * kl
    assert rw_loss < legacy_loss


def test_kl_distill_loss_legacy_path_deterministic():
    """Calling kl_distill_loss twice with the same coeffs gives the same loss."""
    inputs = _make_mock_inputs()
    loss1, _ = kl_distill_loss(
        **inputs,
        torch_module=torch,
        ignore_index=-100,
        kl_coeff=0.5,
        nll_coeff=0.5,
        temperature=1.0,
    )
    loss2, _ = kl_distill_loss(
        **inputs,
        torch_module=torch,
        ignore_index=-100,
        kl_coeff=0.5,
        nll_coeff=0.5,
        temperature=1.0,
    )
    assert torch.allclose(loss1, loss2)


def test_kl_distill_loss_zero_nll_coefficient_gives_kl_only():
    inputs = _make_mock_inputs()
    loss, stats = kl_distill_loss(
        **inputs,
        torch_module=torch,
        ignore_index=-100,
        kl_coeff=0.5,
        nll_coeff=0.0,
        temperature=1.0,
    )
    # With nll_coeff=0, total should equal kl_coeff * kl_loss.
    assert stats["total"] == pytest.approx(0.5 * stats["kl"])


def test_kl_distill_loss_zero_kl_coefficient_gives_nll_only():
    inputs = _make_mock_inputs()
    loss, stats = kl_distill_loss(
        **inputs,
        torch_module=torch,
        ignore_index=-100,
        kl_coeff=0.0,
        nll_coeff=0.5,
        temperature=1.0,
    )
    assert stats["total"] == pytest.approx(0.5 * stats["nll"])
