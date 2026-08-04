"""Tests for the Frontier-Verifier GSPO (FV-GSPO) components.

Covers the frontier router, 50/25/25 mixture sampling, Dr.GRPO leave-one-out
advantages, the GSPO sequence-clipped loss with diagnostics, completion
entropy, shared running MAD, the repair queue, and the circuit-breaker monitor
described in docs/frontier-verifier-gspo-design-2026-08-04.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

from training.grpo_utils import (
    FRONTIER_RL,
    MASTERED_REPLAY,
    PARTIAL_REPAIR_RL,
    REPAIR_SFT,
    CircuitBreakerState,
    FrontierRouter,
    RunningMAD,
    append_repair_queue_record,
    build_mixture_weights,
    completion_entropy,
    count_repair_conversions,
    stable_gspo_loss,
    stable_gspo_loss_metrics,
)


def _task(task_id: str, category: str = "circuit_construction") -> dict:
    return {
        "task_id": task_id,
        "meta": {"id": task_id, "domain": "quantum", "category": category},
        "task_dir": Path(f"/tmp/{task_id}"),
    }


def test_router_probe_classifies_mixed_group_as_frontier() -> None:
    router = FrontierRouter()
    probe = router.probe_record("t1", step=1, pass_rate=0.5, shaped_signal_std=0.2)
    assert probe["route"] == FRONTIER_RL
    assert probe["learnability"] == 1.0  # binary variance peaks at p=0.5
    assert router.route_of("t1") == FRONTIER_RL


def test_router_probe_routes_all_fail_flat_to_repair() -> None:
    router = FrontierRouter()
    probe = router.probe_record("t2", step=1, pass_rate=0.0, shaped_signal_std=0.01)
    assert probe["route"] == REPAIR_SFT


def test_router_probe_routes_all_fail_with_signal_to_partial_rl() -> None:
    router = FrontierRouter()
    probe = router.probe_record("t3", step=1, pass_rate=0.0, shaped_signal_std=0.2)
    assert probe["route"] == PARTIAL_REPAIR_RL


def test_router_probe_routes_all_pass_flat_to_mastered_replay() -> None:
    router = FrontierRouter()
    probe = router.probe_record("t4", step=1, pass_rate=1.0, shaped_signal_std=0.01)
    assert probe["route"] == MASTERED_REPLAY


def test_router_weight_downweights_mastered_and_prefers_unprobed() -> None:
    router = FrontierRouter()
    router.probe_record("mastered", step=1, pass_rate=1.0, shaped_signal_std=0.01)
    router.probe_record("frontier", step=1, pass_rate=0.5, shaped_signal_std=0.2)
    mastered_weight = router.weight("mastered", step=2, total_probes=2)
    frontier_weight = router.weight("frontier", step=2, total_probes=2)
    unprobed_weight = router.weight("fresh", step=2, total_probes=2)
    # Never-probed tasks must be explorable (probing is the top priority).
    assert unprobed_weight > mastered_weight
    assert frontier_weight > mastered_weight


def test_router_staleness_grows_with_time_since_last_probe() -> None:
    router = FrontierRouter(staleness_half_life=10.0)
    router.probe_record("t", step=1, pass_rate=0.5, shaped_signal_std=0.2)
    assert router.staleness("t", step=1) == 0.0
    assert router.staleness("t", step=6) == 0.5
    assert router.staleness("t", step=11) == 1.0


def test_router_coverage_need_multiplies_weight() -> None:
    router = FrontierRouter()
    router.probe_record("t", step=1, pass_rate=0.5, shaped_signal_std=0.2)
    base = router.weight("t", step=2, total_probes=1)
    router.set_coverage_need("t", 3.0)
    boosted = router.weight("t", step=2, total_probes=1)
    assert boosted > 2.5 * base


def test_router_frontier_fraction_counts_learnable_routes() -> None:
    router = FrontierRouter()
    router.probe_record("a", step=1, pass_rate=0.5, shaped_signal_std=0.2)  # frontier
    router.probe_record("b", step=1, pass_rate=0.0, shaped_signal_std=0.2)  # partial
    router.probe_record("c", step=1, pass_rate=1.0, shaped_signal_std=0.01)  # mastered
    assert router.frontier_fraction() == 2 / 3


def test_mixture_weights_split_targeted_neighbor_replay() -> None:
    router = FrontierRouter()
    tasks = [
        _task("frontier_a", category="circuit_construction"),
        _task("frontier_b", category="circuit_construction"),
        _task("mastered_c", category="error_handling"),
        _task("fresh_d", category="circuit_construction"),
    ]
    router.probe_record("frontier_a", step=1, pass_rate=0.5, shaped_signal_std=0.2)
    router.probe_record("frontier_b", step=1, pass_rate=0.4, shaped_signal_std=0.3)
    router.probe_record("mastered_c", step=1, pass_rate=1.0, shaped_signal_std=0.01)
    weights = build_mixture_weights(
        router,
        tasks,
        step=2,
        recent_frontier=["frontier_a"],
        neighbor_window=10,
    )
    total = sum(weights)
    # Pools: targeted = {frontier_a, frontier_b, fresh_d} (mass 0.5 across 3),
    # neighbor = same category as frontier_a = {frontier_a, frontier_b, fresh_d}
    # (mass 0.25 across 3), replay = {mastered_c} (mass 0.25 alone).
    mastered_mass = weights[2]
    assert mastered_mass / total == 0.25
    frontier_mass = weights[0] + weights[1] + weights[3]
    assert abs(frontier_mass / total - 0.75) < 1e-9
    assert all(w >= 0.0 for w in weights)


def test_mixture_weights_fall_back_to_targeted_without_neighbors() -> None:
    router = FrontierRouter()
    tasks = [
        _task("frontier_a", category="c1"),
        _task("mastered_b", category="c2"),
    ]
    router.probe_record("frontier_a", step=1, pass_rate=0.5, shaped_signal_std=0.2)
    router.probe_record("mastered_b", step=1, pass_rate=1.0, shaped_signal_std=0.01)
    weights = build_mixture_weights(router, tasks, step=2, recent_frontier=[])
    assert all(w > 0.0 for w in weights)


def test_gspo_loss_metrics_match_plain_loss_and_report_clip_fractions() -> None:
    torch.manual_seed(0)
    log_probs = torch.randn(8)
    old_log_probs = log_probs + torch.randn(8) * 0.1
    advantages = torch.tensor([1.0, 0.5, -0.5, 1.0, 0.0, -1.0, 0.8, -0.3])
    plain = stable_gspo_loss(
        log_probs,
        old_log_probs,
        advantages,
        clip_low=3e-4,
        clip_high=4e-4,
        kl_coeff=0.005,
        numerical_log_ratio_clip=8.0,
    )
    loss, stats = stable_gspo_loss_metrics(
        log_probs,
        old_log_probs,
        advantages,
        clip_low=3e-4,
        clip_high=4e-4,
        kl_coeff=0.005,
        numerical_log_ratio_clip=8.0,
    )
    assert torch.allclose(loss, plain)
    assert stats["clip_low_fraction"] >= 0.0
    assert stats["clip_high_fraction"] >= 0.0
    assert (
        stats["clip_total_fraction"]
        <= stats["clip_low_fraction"] + stats["clip_high_fraction"] + 1e-9
    )
    assert stats["ratio_mean"] > 0.0


def test_gspo_loss_metrics_returns_nan_stats_for_empty_batch() -> None:
    loss, stats = stable_gspo_loss_metrics(
        torch.tensor([float("nan")]),
        torch.tensor([0.0]),
        torch.tensor([1.0]),
        clip_low=3e-4,
        clip_high=4e-4,
        kl_coeff=0.005,
        numerical_log_ratio_clip=8.0,
    )
    assert not torch.isfinite(loss)


def test_completion_entropy_is_lower_for_peaked_distribution() -> None:
    peaked = torch.zeros(1, 4, 8)
    peaked[:, :, 0] = 10.0  # token 0 nearly certain
    peaked_mask = torch.ones(1, 4, dtype=torch.bool)
    uniform = torch.zeros(1, 4, 8)
    uniform_mask = torch.ones(1, 4, dtype=torch.bool)
    peaked_entropy = completion_entropy(peaked, peaked_mask).item()
    uniform_entropy = completion_entropy(uniform, uniform_mask).item()
    assert peaked_entropy < uniform_entropy
    assert abs(uniform_entropy - 2.079) < 0.02  # ln(8)


def test_completion_entropy_masks_only_completion_tokens() -> None:
    logits = torch.zeros(1, 4, 4)
    mask = torch.zeros(1, 4, dtype=torch.bool)
    mask[:, 2:] = True
    entropy = completion_entropy(logits, mask).item()
    assert abs(entropy - 1.386) < 0.02  # ln(4) over two tokens


def test_running_mad_shared_scale_converges() -> None:
    mad = RunningMAD()
    for _ in range(3):
        mad.update(torch.tensor([1.0, -1.0, 0.5, -0.5]))
    assert mad.scale > 0.0
    # Advantages of magnitude ~1 give MAD ~1 (approx), not reweighted per group.
    assert 0.1 < mad.scale < 5.0


def test_repair_queue_dedupes_same_code_for_same_task(tmp_path: Path) -> None:
    queue_path = tmp_path / "repair_queue.jsonl"
    first = append_repair_queue_record(
        queue_path,
        {
            "task_id": "t1",
            "best_code": "def f():\n    pass",
            "failures": ["AssertionError"],
        },
    )
    second = append_repair_queue_record(
        queue_path,
        {
            "task_id": "t1",
            "best_code": "def f():\n    pass",
            "failures": ["AssertionError"],
        },
    )
    assert first["duplicate"] is False
    assert second["duplicate"] is True
    assert len(list(queue_path.read_text(encoding="utf-8").splitlines())) == 1


def test_repair_queue_counts_conversions(tmp_path: Path) -> None:
    converted_path = tmp_path / "repair_converted.jsonl"
    for converted in (True, True, False):
        converted_path.open("a", encoding="utf-8").write(
            json.dumps({"converted": converted}) + "\n"
        )
    assert count_repair_conversions(converted_path) == 2
    assert count_repair_conversions(None) == 0


def test_breaker_trips_only_after_two_windows_non_finite() -> None:
    breaker = CircuitBreakerState(window_size=4, required_windows=2)
    trips: list[dict] = []
    for step in range(1, 13):
        breaker.observe_step(
            step=step,
            route=FRONTIER_RL,
            non_finite=True,
            clip_fraction=0.0,
            entropy=2.0,
            repair_queued=False,
            repair_converted=0,
            all_fail_share=0.0,
        )
        trips.extend(breaker.evaluate(step=step))
    # First window (step 4) marks one violation; trip needs two consecutive.
    assert len(trips) == 1
    assert trips[0]["breaker"] == "non_finite"
    assert breaker.should_stop


def test_breaker_does_not_trip_when_violation_recovers() -> None:
    breaker = CircuitBreakerState(window_size=4, required_windows=2)
    for step in range(1, 9):
        breaker.observe_step(
            step=step,
            route=FRONTIER_RL,
            non_finite=step <= 4,
            clip_fraction=0.0,
            entropy=2.0,
            repair_queued=False,
            repair_converted=0,
            all_fail_share=0.0,
        )
        breaker.evaluate(step=step)
    assert not breaker.should_stop


def test_breaker_clip_fraction_trip() -> None:
    breaker = CircuitBreakerState(window_size=4, required_windows=2)
    trips: list[dict] = []
    for step in range(1, 13):
        breaker.observe_step(
            step=step,
            route=FRONTIER_RL,
            non_finite=False,
            clip_fraction=0.9,  # > 0.50 limit
            entropy=2.0,
            repair_queued=False,
            repair_converted=0,
            all_fail_share=0.0,
        )
        trips.extend(breaker.evaluate(step=step))
    assert any(t["breaker"] == "clip_fraction" for t in trips)


def test_breaker_entropy_collapse_requires_frontier_yield_decline() -> None:
    breaker = CircuitBreakerState(window_size=4, required_windows=2, entropy_baseline_steps=8)
    # Baseline: healthy entropy + healthy frontier yield.
    for step in range(1, 9):
        breaker.observe_step(
            step=step,
            route=FRONTIER_RL,
            non_finite=False,
            clip_fraction=0.0,
            entropy=2.0,
            repair_queued=False,
            repair_converted=0,
            all_fail_share=0.0,
        )
        breaker.evaluate(step=step)
    trips: list[dict] = []
    for step in range(9, 21):
        breaker.observe_step(
            step=step,
            route=REPAIR_SFT,
            non_finite=False,
            clip_fraction=0.0,
            entropy=0.1,  # collapsed
            repair_queued=True,
            repair_converted=0,
            all_fail_share=1.0,  # frontier yield collapsed
        )
        trips.extend(breaker.evaluate(step=step))
    assert any(t["breaker"] == "entropy_collapse" for t in trips)


def test_breaker_all_fail_without_repair_conversion() -> None:
    breaker = CircuitBreakerState(window_size=4, required_windows=2)
    trips: list[dict] = []
    for step in range(1, 13):
        breaker.observe_step(
            step=step,
            route=REPAIR_SFT,
            non_finite=False,
            clip_fraction=0.0,
            entropy=2.0,
            repair_queued=True,
            repair_converted=0,
            all_fail_share=1.0,
        )
        trips.extend(breaker.evaluate(step=step))
    assert any(t["breaker"] == "all_fail_without_repair" for t in trips)


def test_breaker_all_fail_with_conversion_does_not_trip() -> None:
    breaker = CircuitBreakerState(window_size=4, required_windows=2)
    trips: list[dict] = []
    for step in range(1, 13):
        breaker.observe_step(
            step=step,
            route=REPAIR_SFT,
            non_finite=False,
            clip_fraction=0.0,
            entropy=2.0,
            repair_queued=True,
            repair_converted=3,  # repair stage is converting
            all_fail_share=1.0,
        )
        trips.extend(breaker.evaluate(step=step))
    assert not any(t["breaker"] == "all_fail_without_repair" for t in trips)


def test_breaker_holdout_regression_reports_drop() -> None:
    breaker = CircuitBreakerState(window_size=4, required_windows=2)
    breaker.report_holdout_pass1(0.80)
    trips: list[dict] = []
    for step in range(1, 13):
        if step == 5:
            breaker.report_holdout_pass1(0.70)  # -10pp vs baseline (window 2)
        elif step == 9:
            breaker.report_holdout_pass1(0.65)  # -5pp again (window 3)
        breaker.observe_step(
            step=step,
            route=FRONTIER_RL,
            non_finite=False,
            clip_fraction=0.0,
            entropy=2.0,
            repair_queued=False,
            repair_converted=0,
            all_fail_share=0.0,
        )
        trips.extend(breaker.evaluate(step=step))
    # Two consecutive windows with a >3pp drop trip the breaker.
    assert any(t["breaker"] == "holdout_regression" for t in trips)
