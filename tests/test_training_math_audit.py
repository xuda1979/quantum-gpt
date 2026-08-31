"""Training-math audit — independent recomputation of the SAPO reward/loss
math on synthetic fixtures (2026-08-24 training-math-auditor role).

Every expected value below is hand-derived from the published formulas
(arXiv:2511.20347 + the code's own docs), NOT from the implementation under
test — a disagreement is a math defect.
"""

from __future__ import annotations

import math

import pytest
import torch

from training.grpo_utils import (
    RunningMAD,
    blend_comprehensive_reward,
    leave_one_out_advantages,
    sapo_loss_metrics,
)

# ---------------------------------------------------------------------------
# 1. REWARD BLEND — p_dominant: R = P + (1-P) * [(1-w)*S + w*J] - T
# ---------------------------------------------------------------------------


def test_blend_p_dominant_pass_dominates_and_judge_renormalizes_away() -> None:
    # Judge off (dim_weights empty -> total_w=0 -> J term vanishes):
    assert blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=0.3,
        model_dim_scores={},
        dim_weights={},
        mode="p_dominant",
        pass_mass=0.40,
        shaped_mass=0.35,
        judge_mass=0.25,
    ) == pytest.approx(1.0)
    assert blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.8,
        model_dim_scores={},
        dim_weights={},
        mode="p_dominant",
    ) == pytest.approx(0.8)
    # Non-binary pass input (partial credit): affine in (P, S).
    assert blend_comprehensive_reward(
        pass_reward=0.5,
        shaped_reward=0.8,
        model_dim_scores={},
        dim_weights={},
        mode="p_dominant",
    ) == pytest.approx(0.5 + 0.5 * 0.8)


def test_blend_p_dominant_judge_mass_blends_shaped_and_judge() -> None:
    # Judge ON: dim_weights {correctness: 0.4}, score 0.5. The judge weight is
    # CAPPED at MAX_MODEL_JUDGE_WEIGHT=0.05 ("W <= 0.05, subtracted from the
    # shaped term"): R = (1-0.05)*0.8 + 0.05*0.5 = 0.785 for a failing cand.
    assert blend_comprehensive_reward(
        pass_reward=0.0,
        shaped_reward=0.8,
        model_dim_scores={"correctness": 0.5},
        dim_weights={"correctness": 0.4},
        mode="p_dominant",
    ) == pytest.approx(0.785)


def test_blend_clamps_and_applies_truncation_penalty() -> None:
    # Clamp to [0,1] and subtract the truncation penalty (bounded [0,1]).
    assert blend_comprehensive_reward(
        pass_reward=1.0,
        shaped_reward=1.0,
        model_dim_scores={},
        dim_weights={},
        mode="p_dominant",
        truncation_penalty=0.25,
    ) == pytest.approx(0.75)
    assert blend_comprehensive_reward(
        pass_reward=2.0,
        shaped_reward=2.0,
        model_dim_scores={},
        dim_weights={},
        mode="p_dominant",
    ) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 2. REWARD NORMALIZATION — LOO per group + RunningMAD shared scale
# ---------------------------------------------------------------------------


def test_loo_advantages_hand_recomputed() -> None:
    rewards = torch.tensor([1.0, 0.8, 0.6, 0.4])
    adv = leave_one_out_advantages(rewards)
    expected = torch.tensor(
        [
            1.0 - (0.8 + 0.6 + 0.4) / 3,  # 0.4
            0.8 - (1.0 + 0.6 + 0.4) / 3,  # 0.1333...
            0.6 - (1.0 + 0.8 + 0.4) / 3,  # -0.1333...
            0.4 - (1.0 + 0.8 + 0.6) / 3,  # -0.4
        ]
    )
    assert torch.allclose(adv, expected, atol=1e-6)
    assert leave_one_out_advantages(torch.tensor([0.5])).sum() == pytest.approx(0.0)
    assert leave_one_out_advantages(torch.tensor([0.5, 0.5])).sum() == pytest.approx(0.0)


def test_running_mad_ema_hand_recomputed() -> None:
    mad = RunningMAD(decay=0.9, init=1.0)
    # First batch: values [1,2,3,4] -> mean 2.5, mad 1.0 -> scale becomes 1.0.
    assert mad.update(torch.tensor([1.0, 2.0, 3.0, 4.0])) == pytest.approx(1.0)
    # Second batch [3,4,5,6]: mean 4.5, mad 1.0 -> EMA: 0.9*1.0 + 0.1*1.0 = 1.0.
    assert mad.update(torch.tensor([3.0, 4.0, 5.0, 6.0])) == pytest.approx(1.0)
    # Third batch [5,7,9,11]: mean 8, mad 2 -> EMA: 0.9*1.0 + 0.1*2.0 = 1.1.
    assert mad.update(torch.tensor([5.0, 7.0, 9.0, 11.0])) == pytest.approx(1.1)


def test_running_mad_flat_group_does_not_move_scale() -> None:
    """2026-08-24 flat-group fix: a zero-dispersion batch (all LOO advantages
    ~0 on flat all-fail/all-pass groups) must NOT pull the EMA toward 1.0."""
    mad = RunningMAD(decay=0.99, init=0.36)
    mad.update(torch.tensor([1.0, 2.0, 3.0, 4.0]))  # real dispersion batch
    assert mad.scale == pytest.approx(1.0)
    mad.update(torch.tensor([0.0, 0.0, 0.0, 0.0]))  # flat batch: no movement
    assert mad.scale == pytest.approx(1.0)
    mad.update(torch.tensor([0.5, 0.5, 0.5, 0.5]))
    assert mad.scale == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 3. SAPO LOSS — per-token gate, asymmetric tau, token-mean then 1/G mean
# ---------------------------------------------------------------------------


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def test_sapo_loss_hand_recomputed_two_candidates() -> None:
    """Candidate 1 (A=+1.0, tau_pos=1.0): cur [0.1, 0.2] vs old [0.0, 0.0].
    r = [e^0.1, e^0.2]; gate = 4*sigmoid(r-1); loss1 = -mean(gate*A).
    Candidate 2 (A=-1.0, tau_neg=1.05): cur [-0.1, -0.2] vs old [0.0, 0.0].
    Batch loss = (loss1 + loss2)/2 + kl_coeff * mean(k3)."""
    c1_cur = torch.tensor([[0.1, 0.2]])
    c1_old = torch.tensor([[0.0, 0.0]])
    c2_cur = torch.tensor([[-0.1, -0.2]])
    c2_old = torch.tensor([[0.0, 0.0]])

    r1 = [math.exp(0.1), math.exp(0.2)]
    g1 = [4.0 * _sigmoid(x - 1.0) for x in r1]
    loss1 = -sum(g1) / 2.0  # A=+1: -mean(gate*A)
    k31 = [(x - 1.0 - math.log(x)) for x in r1]
    mean_k31 = sum(k31) / 2.0

    r2 = [math.exp(-0.1), math.exp(-0.2)]
    g2 = [(4.0 / 1.05) * _sigmoid(1.05 * (x - 1.0)) for x in r2]
    loss2 = +sum(g2) / 2.0  # A=-1: -mean(gate*A) = +mean(gate)
    k32 = [(x - 1.0 - math.log(x)) for x in r2]
    mean_k32 = sum(k32) / 2.0

    expected_loss = (loss1 + loss2) / 2.0 + 0.01 * (mean_k31 + mean_k32) / 2.0

    loss, stats = sapo_loss_metrics(
        [c1_cur, c2_cur],
        [c1_old, c2_old],
        torch.tensor([1.0, -1.0]),
        tau_pos=1.0,
        tau_neg=1.05,
        kl_coeff=0.01,
        numerical_log_ratio_clip=8.0,
    )
    assert loss.item() == pytest.approx(expected_loss, abs=1e-5)
    assert stats["sapo_gate_mean"] == pytest.approx((sum(g1) / 2 + sum(g2) / 2) / 2, abs=1e-5)
    assert stats["n_tokens"] == pytest.approx(4.0)


def test_sapo_loss_uses_equal_1_over_g_weights_not_token_mean() -> None:
    """Aggregation is mean over candidates (each = token-mean), NOT a global
    token mean. Candidate 1 has 1 token with a large ratio, candidate 2 has 3
    tokens at ratio 1: the 1/G loss differs from the global token mean."""
    c1_cur = torch.tensor([[1.0]])  # r = e^1
    c1_old = torch.tensor([[0.0]])
    c2_cur = torch.tensor([[0.0], [0.0], [0.0]])  # r = 1 for all
    c2_old = torch.tensor([[0.0], [0.0], [0.0]])
    adv = torch.tensor([1.0, 1.0])

    loss, _ = sapo_loss_metrics(
        [c1_cur, c2_cur],
        [c1_old, c2_old],
        adv,
        tau_pos=1.0,
        tau_neg=1.05,
        kl_coeff=0.0,
        numerical_log_ratio_clip=8.0,
    )
    gate_c1 = 4.0 * _sigmoid(math.e - 1.0)
    gate_c2 = 4.0 * _sigmoid(0.0)  # = 2.0
    expected_1g = -(gate_c1 + gate_c2) / 2.0
    global_token_mean = -(gate_c1 * 1.0 + gate_c2 * 3.0) / 4.0
    assert loss.item() == pytest.approx(expected_1g, abs=1e-5)
    assert loss.item() != pytest.approx(global_token_mean, abs=1e-5)


def test_sapo_loss_clamps_log_ratio_at_plus_minus_8() -> None:
    """numerical_log_ratio_clip=8 bounds the exponentiation: cur-old = +10
    behaves as +8 (r = e^8), and -10 as e^-8."""
    cur = torch.tensor([[10.0, -10.0]])
    old = torch.tensor([[0.0, 0.0]])
    loss, stats = sapo_loss_metrics(
        [cur],
        [old],
        torch.tensor([1.0]),
        tau_pos=1.0,
        tau_neg=1.05,
        kl_coeff=0.0,
        numerical_log_ratio_clip=8.0,
    )
    r8 = math.exp(8.0)
    expected_gate_mean = (4.0 * _sigmoid(r8 - 1.0) + 4.0 * _sigmoid(math.exp(-8.0) - 1.0)) / 2.0
    assert stats["sapo_gate_mean"] == pytest.approx(expected_gate_mean, abs=1e-5)
    assert math.isfinite(loss.item())


def test_sapo_loss_zero_token_and_nan_guards() -> None:
    loss, stats = sapo_loss_metrics(
        [],
        [],
        torch.tensor([], dtype=torch.float32),
        tau_pos=1.0,
        tau_neg=1.05,
        kl_coeff=0.01,
        numerical_log_ratio_clip=8.0,
    )
    assert math.isnan(loss.item())  # empty batch -> NaN loss -> trainer's isfinite guard
    assert stats["n_tokens"] == 0.0
