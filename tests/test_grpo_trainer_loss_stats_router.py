"""Coverage backlog #5 (2026-08-25): loss statistics + FrontierRouter.

stable_token_log_probs / stable_grpo_loss / stable_gspo_loss_metrics — the
trainer's gradient math (hand-computed contracts + the chunked-equivalence
claim) — and FrontierRouter (posterior routing, adaptive G, weights). These
are the numerics the math auditor re-derives from the step records; the
hand-computed checks keep them honest.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_utils import (  # noqa: E402
    FrontierRouter,
    chunked_log_probs_and_entropy,
    stable_grpo_loss,
    stable_gspo_loss_metrics,
    stable_token_log_probs,
)

# ---------------------------------------------------------------------------
# stable_token_log_probs
# ---------------------------------------------------------------------------


def test_stable_token_log_probs_gathers_correct_values() -> None:
    logits = torch.tensor([[[0.5, -1.0, 2.0], [1.0, 0.0, -0.5]]], dtype=torch.float32)
    targets = torch.tensor([[2, 0]], dtype=torch.long)
    out = stable_token_log_probs(logits, targets, logit_clip=10.0)
    manual = torch.log_softmax(logits, dim=-1)
    expected = manual.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    assert torch.allclose(out, expected, atol=1e-6)


def test_stable_token_log_probs_sanitizes_nonfinite() -> None:
    logits = torch.tensor([[[float("nan"), float("inf"), float("-inf"), 0.0]]], dtype=torch.float32)
    targets = torch.tensor([[0]], dtype=torch.long)
    out = stable_token_log_probs(logits, targets, logit_clip=3.0)
    # nan -> 0.0, posinf -> +3, neginf -> -3, all clamped to [-3, 3]
    safe = torch.tensor([[[0.0, 3.0, -3.0, 0.0]]])
    expected = torch.log_softmax(safe, dim=-1).gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    assert torch.allclose(out, expected, atol=1e-6)


def test_stable_token_log_probs_matches_chunked_equivalence() -> None:
    torch.manual_seed(7)
    logits = torch.randn(1, 3, 17, dtype=torch.float32)
    targets = torch.randint(0, 17, (1, 3))
    direct = stable_token_log_probs(logits, targets, logit_clip=8.0)
    chunked, _ = chunked_log_probs_and_entropy(
        logits, targets, logit_clip=8.0, chunk_size=5, return_entropy=True
    )
    # mathematically identical two-pass logsumexp; fp32 last-ULP rounding
    # differs from the single-pass log_softmax, so the contract is tight
    # allclose, not bit-exact equality
    assert torch.allclose(direct, chunked, atol=1e-5)


# ---------------------------------------------------------------------------
# stable_grpo_loss — the unclipped GRPO path (hand-computed)
# ---------------------------------------------------------------------------


def test_stable_grpo_loss_hand_computed() -> None:
    log_probs = torch.tensor([math.log(0.4), math.log(0.3)], dtype=torch.float32)
    old_log_probs = torch.tensor([math.log(0.2), math.log(0.6)], dtype=torch.float32)
    advantages = torch.tensor([1.0, -0.5], dtype=torch.float32)
    kl_coeff = 0.1
    ratio_clip_log_delta = 4.0  # wide clamp: no ratio clipping in this case
    loss = stable_grpo_loss(log_probs, old_log_probs, advantages, kl_coeff, ratio_clip_log_delta)
    r = torch.tensor([0.4 / 0.2, 0.3 / 0.6], dtype=torch.float32)
    expected = -torch.mean(r * advantages) + kl_coeff * torch.mean((r - 1.0) - torch.log(r))
    assert torch.allclose(loss, expected, atol=1e-6)
    # all-NaN inputs -> NaN loss (never a silent finite value)
    nan_loss = stable_grpo_loss(
        torch.tensor([float("nan")]),
        torch.tensor([0.0]),
        torch.tensor([1.0]),
        0.1,
        4.0,
    )
    assert torch.isnan(nan_loss)


# ---------------------------------------------------------------------------
# stable_gspo_loss_metrics — clipped sequence surrogate (hand-computed)
# ---------------------------------------------------------------------------


def test_stable_gspo_loss_clipped_surrogate_hand_computed() -> None:
    # sequence ratios straddling [1-clip_low, 1+clip_high] = [0.7, 1.2]
    lp = torch.tensor([math.log(0.5), 0.0, math.log(2.0)], dtype=torch.float32)
    old = torch.tensor([0.0, 0.0, 0.0], dtype=torch.float32)  # ratios 0.5, 1.0, 2.0
    adv = torch.tensor([1.0, 1.0, -1.0], dtype=torch.float32)
    clip_low, clip_high = 0.3, 0.2
    loss, stats = stable_gspo_loss_metrics(
        lp,
        old,
        adv,
        clip_low=clip_low,
        clip_high=clip_high,
        kl_coeff=0.0,
        numerical_log_ratio_clip=8.0,
    )
    r = torch.tensor([0.5, 1.0, 2.0])
    clipped = r.clamp(1.0 - clip_low, 1.0 + clip_high)  # [0.7, 1.0, 1.2]
    surrogate = torch.minimum(r * adv, clipped * adv)  # [0.5, 1.0, -1.2]
    assert torch.allclose(loss, -surrogate.mean(), atol=1e-6)
    # clip fractions: low=1/3 (0.5), high=1/3 (2.0), total=2/3
    assert stats["clip_low_fraction"] == pytest.approx(1.0 / 3.0)
    assert stats["clip_high_fraction"] == pytest.approx(1.0 / 3.0)
    assert stats["clip_total_fraction"] == pytest.approx(2.0 / 3.0)


def test_stable_gspo_loss_nan_and_length_weights() -> None:
    nan_loss, stats = stable_gspo_loss_metrics(
        torch.tensor([float("nan")]),
        torch.tensor([0.0]),
        torch.tensor([1.0]),
        clip_low=0.3,
        clip_high=0.2,
        kl_coeff=0.0,
        numerical_log_ratio_clip=8.0,
    )
    assert torch.isnan(nan_loss)
    assert stats["ratio_mean"] == 0.0
    # length weights scale the surrogate and report their mean
    lp = torch.tensor([math.log(0.5), 0.0, math.log(2.0)])
    old = torch.tensor([0.0, 0.0, 0.0])
    adv = torch.tensor([1.0, 1.0, -1.0])
    weights = torch.tensor([0.5, 1.0, 2.0])
    loss, stats = stable_gspo_loss_metrics(
        lp,
        old,
        adv,
        clip_low=0.3,
        clip_high=0.2,
        kl_coeff=0.0,
        numerical_log_ratio_clip=8.0,
        length_weights=weights,
    )
    r = torch.tensor([0.5, 1.0, 2.0])
    clipped = r.clamp(0.7, 1.2)
    surrogate = torch.minimum(r * adv, clipped * adv) * weights
    assert torch.allclose(loss, -surrogate.mean(), atol=1e-6)
    assert stats["length_weight_mean"] == pytest.approx(weights.mean().item())


# ---------------------------------------------------------------------------
# FrontierRouter — posterior routing, adaptive G, weights
# ---------------------------------------------------------------------------


def test_router_unprobed_defaults_and_learnability() -> None:
    router = FrontierRouter()
    state = router.get_state("task_a")
    assert state["probes"] == 0.0 and state["p_pass_ema"] == 0.0
    assert router.learnability("task_a") == pytest.approx(router.unprobed_learnability)
    assert router.route_of("task_a") == ""
    assert router.staleness("task_a", step=100) == 1.0


def test_router_probe_record_ema_posterior_and_all_fail_route() -> None:
    router = FrontierRouter()
    for step in (1, 2, 3):
        result = router.probe_record("task_a", step=step, pass_rate=0.0, shaped_signal_std=0.0)
    assert router.route_of("task_a") == "repair_sft"
    assert router.get_state("task_a")["probes"] == 3.0
    assert result["probes"] == 3.0
    assert result["posterior_mean"] < 0.1
    # EMA tracks the pass rate (decay 0.7)
    assert router.get_state("task_a")["p_pass_ema"] == 0.0


def test_router_flaky_oscillation_routes_to_quarantine() -> None:
    router = FrontierRouter()
    for step, rate in ((1, 1.0), (2, 0.0), (3, 1.0)):
        result = router.probe_record("task_a", step=step, pass_rate=rate, shaped_signal_std=0.0)
    assert result["flaky"] is True
    assert router.route_of("task_a") == "invalid_or_noisy"


def test_router_mastered_needs_samples_and_lower_bound() -> None:
    router = FrontierRouter()
    for step in range(1, 33):
        router.probe_record("task_a", step=step, pass_rate=1.0, shaped_signal_std=0.0)
    assert router.route_of("task_a") == "mastered_replay"
    # a single lucky group does NOT master (hysteresis)
    router2 = FrontierRouter()
    router2.probe_record("task_b", step=1, pass_rate=1.0, shaped_signal_std=0.0)
    assert router2.route_of("task_b") != "mastered_replay"


def test_router_weight_mastered_scale_and_quarantine_floor() -> None:
    router = FrontierRouter()
    # unprobed: weight >= the floor
    w_unprobed = router.weight("task_a", step=1, total_probes=0)
    assert w_unprobed >= router.min_weight
    # quarantined tasks get EXACTLY the floor
    router.mark_repair("task_b")
    assert router.weight("task_b", step=1, total_probes=0) == pytest.approx(router.min_weight)
    router.mark_invalid("task_c")
    assert router.weight("task_c", step=1, total_probes=0) == pytest.approx(router.min_weight)
    # mastered tasks are downweighted by the replay scale
    router2 = FrontierRouter()
    for step in range(1, 33):
        router2.probe_record("task_d", step=step, pass_rate=1.0, shaped_signal_std=0.0)
    assert router2.route_of("task_d") == "mastered_replay"
    router2.state["task_d"]["coverage_need"] = 1.0
    score = (
        router2.lambda_frontier * router2.learnability("task_d")
        + router2.lambda_novelty * router2.novelty_bonus("task_d", total_probes=100)
        + router2.lambda_staleness * router2.staleness("task_d", step=100)
    )
    assert router2.weight("task_d", step=100, total_probes=100) == pytest.approx(
        max(router2.min_weight, score * router2.mastered_replay_scale)
    )


def test_router_recommended_group_size() -> None:
    router = FrontierRouter()
    assert router.recommended_group_size("fresh") == 4  # < 2 samples
    # Beta(3,15) after 2 probes of 1/8: mean 1/6, std ~0.0855 ->
    # frontier_mass(0.10..0.90) ~= 0.78, inside the straddling band [0.2, 0.8]
    for step in (1, 2):
        router.probe_record("mid", step=step, pass_rate=0.125, shaped_signal_std=0.0, group_size=8)
    assert router.recommended_group_size("mid") == 16  # posterior straddles


def test_router_novelty_staleness_and_frontier_fraction() -> None:
    router = FrontierRouter()
    assert router.frontier_fraction() == 0.0  # nothing probed
    router.probe_record("learnable", step=1, pass_rate=0.5, shaped_signal_std=0.8, group_size=8)
    # repair routing needs ACCUMULATING all-fail evidence (hysteresis):
    # a single 0/8 group still lands in the frontier mass band
    for step in (1, 2, 3):
        router.probe_record(
            "repairing", step=step, pass_rate=0.0, shaped_signal_std=0.0, group_size=8
        )
    # learnable: shaped_std 0.8 >= frontier_threshold -> frontier_rl route
    assert router.route_of("learnable") in {"frontier_rl", "partial_repair_rl"}
    assert router.route_of("repairing") == "repair_sft"
    assert router.frontier_fraction() == pytest.approx(0.5)
    # novelty decays with probe count; staleness grows with elapsed steps
    assert router.novelty_bonus("learnable", total_probes=10) > 0.0
    assert router.staleness("learnable", step=1) == pytest.approx(0.0)
    assert router.staleness("learnable", step=101) > 0.0


def test_router_record_rl_update_and_coverage() -> None:
    router = FrontierRouter()
    router.record_rl_update("task_a")
    router.record_rl_update("task_a")
    assert router.get_state("task_a")["rl_updates"] == 2.0
    router.set_coverage_need("task_a", 0.25)
    router.load_coverage_map({"task_b": 2.0})
    assert router.get_state("task_a")["coverage_need"] == pytest.approx(0.25)
    assert router.get_state("task_b")["coverage_need"] == pytest.approx(2.0)
