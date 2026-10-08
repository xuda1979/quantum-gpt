"""Coverage backlog #4 (2026-08-25): circuit breaker + temperature controls.

AdaptiveTemperatureState (escalation ladder), CircuitBreakerState (windowed
trip rules), observe_and_evaluate_breakers and maybe_stop_for_breaker (the
trainer's halt path). These rules decide whether NPU-hours keep burning on a
broken policy — the window/trip semantics and the fail-closed halt must be
pinned.
"""

from __future__ import annotations

import math
import sys
from argparse import Namespace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import (  # noqa: E402
    clamp_adaptive_behavior_temperature,
    escalate_temperature_on_flat_route,
    maybe_stop_for_breaker,
    observe_and_evaluate_breakers,
)
from training.grpo_utils import (  # noqa: E402
    AdaptiveTemperatureState,
    CircuitBreakerState,
    FrontierRouter,
    build_mixture_weights,
)

# ---------------------------------------------------------------------------
# AdaptiveTemperatureState — the escalation ladder
# ---------------------------------------------------------------------------


def test_temp_ladder_escalates_and_clamps_at_max() -> None:
    temp = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=1.4)
    assert temp.current_temp() == pytest.approx(0.8)
    # multiplicative formula: base * (1 + step_size * count) = 0.8 * 1.3
    assert temp.current_temp_at_count(2) == pytest.approx(1.04)
    assert temp.current_temp_at_count(50) == pytest.approx(1.4)  # clamped


def test_temp_skip_reasons_and_update_reset() -> None:
    temp = AdaptiveTemperatureState()
    temp.record_skip("empty_completion_mask")  # NOT a low-signal skip
    assert temp.consecutive_low_signal_skips == 0
    temp.record_skip("low_reward_signal")
    temp.record_skip("low_reward_signal")
    assert temp.consecutive_low_signal_skips == 2
    assert temp.current_temp() > temp.base_temp
    temp.record_update()
    assert temp.consecutive_low_signal_skips == 0
    assert temp.current_temp() == temp.base_temp


def test_temp_state_round_trip_and_defaults() -> None:
    temp = AdaptiveTemperatureState(base_temp=0.7, step_size=0.2, max_temp=1.3)
    temp.record_skip("low_reward_signal")
    restored = AdaptiveTemperatureState.from_dict(temp.to_dict())
    assert restored == temp
    # missing keys -> documented defaults
    defaults = AdaptiveTemperatureState.from_dict({})
    assert defaults.base_temp == 0.8 and defaults.max_temp == 1.4


def test_temp_escalation_ceiling_caps_ladder() -> None:
    temp = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=2.0)
    for _ in range(20):
        temp.record_skip("low_reward_signal")
    assert temp.current_temp() == pytest.approx(2.0)  # ladder says 2.0...
    assert clamp_adaptive_behavior_temperature(temp.current_temp()) == pytest.approx(1.3)


def test_escalate_flat_route_integrates_with_real_state() -> None:
    temp = AdaptiveTemperatureState()
    # cold-task class: all-fail RL group sampled below the entropy threshold
    escalate_temperature_on_flat_route(
        temp,
        route="frontier_rl",
        all_fail=True,
        entropy_mean=0.3,
    )
    assert temp.consecutive_low_signal_skips == 1
    # r10 (run-6 killer): a repair-routed LOW-entropy all-fail group is the
    # cold-collapse class and escalates BEFORE repair-routing (run-6 died with
    # 16 consecutive repair skips, temp stuck at 1.15, then no_trainable_tasks)
    escalate_temperature_on_flat_route(temp, route="repair_sft", all_fail=True, entropy_mean=0.3)
    assert temp.consecutive_low_signal_skips == 2
    # INVALID_OR_NOISY quarantine never escalates (unstable task, not a
    # diversity failure) and high-entropy groups never escalate (the run-3
    # death-spiral class: entropy 2.9 -> 6.4 ramping temp 1.0 -> 1.75)
    escalate_temperature_on_flat_route(
        temp, route="invalid_or_noisy", all_fail=True, entropy_mean=0.3
    )
    escalate_temperature_on_flat_route(temp, route="repair_sft", all_fail=True, entropy_mean=0.9)
    escalate_temperature_on_flat_route(temp, route="frontier_rl", all_fail=True, entropy_mean=0.9)
    assert temp.consecutive_low_signal_skips == 2


def test_no_trainable_tasks_breaker_still_fires_when_escalation_fails_to_recover() -> None:
    """2026-08-26 (r10) regression guard: the degenerate-rescue escalation must
    NOT mask the end-of-life breaker. If the collapsed policy keeps collapsing
    even at the 1.3 temp cap, the router keeps marking tasks repair until
    EVERY task is quarantined; build_mixture_weights then returns zero weights
    and the main loop fires ``no_trainable_tasks``
    (all_tasks_quarantined_or_zero_weight, grpo_trainer.py:4107-4122) — the
    run-6 death path must stay reachable.
    """
    tasks = [
        {"task_id": f"task_{i}", "meta": {"domain": "quantum", "category": "noise"}}
        for i in range(5)
    ]
    router = FrontierRouter()
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    for _ in range(20):
        # low-entropy all-fail groups escalate pre-repair (r10)...
        escalate_temperature_on_flat_route(
            temp, route="repair_sft", all_fail=True, entropy_mean=0.0137
        )
        # ...but the collapse never recovers: every task gets repair-quarantined
        for task in tasks:
            router.mark_repair(task["task_id"])
    # the ladder runs to the hard ceiling and holds there
    assert clamp_adaptive_behavior_temperature(temp.current_temp()) == pytest.approx(1.3)
    # all tasks quarantined -> zero mixture weights -> main-loop stop condition
    weights = build_mixture_weights(router, tasks, step=50)
    assert sum(weights) == 0.0
    assert not math.isfinite(sum(weights)) or sum(weights) <= 0.0


# ---------------------------------------------------------------------------
# CircuitBreakerState — windowed trip semantics
# ---------------------------------------------------------------------------


def _observe_window(
    breaker: CircuitBreakerState, *, end_step: int, facts: list[dict]
) -> list[dict]:
    """Feed window_size facts ending at end_step (a window boundary) and
    evaluate. end_step % window_size must be 0."""
    start = end_step - len(facts) + 1
    for offset, fact in enumerate(facts):
        breaker.observe_step(step=start + offset, **fact)
    return breaker.evaluate(step=end_step)


def _fact(**overrides) -> dict:
    base = dict(
        route="frontier_rl",
        non_finite=False,
        clip_fraction=0.0,
        entropy=3.0,
        repair_queued=False,
        repair_converted=0,
        all_fail_share=0.0,
    )
    base.update(overrides)
    return base


def test_breaker_does_not_fire_before_first_window() -> None:
    breaker = CircuitBreakerState()
    breaker.observe_step(step=1, **_fact(non_finite=True))
    assert breaker.evaluate(step=1) == []  # not a window boundary
    breaker.observe_step(step=9, **_fact(non_finite=True))
    assert breaker.evaluate(step=9) == []  # fewer than window_size facts


def test_breaker_non_finite_trips_after_two_windows_idempotently() -> None:
    breaker = CircuitBreakerState()
    trips = []
    for end_step in (10, 20, 30):  # 3 consecutive bad windows
        trips += _observe_window(
            breaker,
            end_step=end_step,
            facts=[_fact(non_finite=True)] * breaker.window_size,
        )
    assert [t["breaker"] for t in trips].count("non_finite") == 1  # trips ONCE
    assert "non_finite" in [t["breaker"] for t in breaker.tripped]
    assert breaker.should_stop is True
    assert "non-finite" in trips[0]["message"]


def test_breaker_clean_window_resets_consecutive() -> None:
    breaker = CircuitBreakerState()
    _observe_window(breaker, end_step=10, facts=[_fact(non_finite=True)] * 10)
    _observe_window(breaker, end_step=20, facts=[_fact()] * 10)  # clean
    assert breaker.tripped == []
    assert breaker.should_stop is False


def test_breaker_clip_fraction_rule() -> None:
    breaker = CircuitBreakerState()
    for end_step in (10, 20):
        _observe_window(breaker, end_step=end_step, facts=[_fact(clip_fraction=0.9)] * 10)
    assert "clip_fraction" in [t["breaker"] for t in breaker.tripped]
    breaker2 = CircuitBreakerState()
    _observe_window(breaker2, end_step=10, facts=[_fact(clip_fraction=0.2)] * 10)
    assert breaker2.tripped == []  # mean below the 0.5 limit


def test_breaker_all_fail_without_repair_rule() -> None:
    breaker = CircuitBreakerState()
    for end_step in (10, 20):
        _observe_window(
            breaker, end_step=end_step, facts=[_fact(all_fail_share=1.0, repair_queued=True)] * 10
        )
    assert "all_fail_without_repair" in [t["breaker"] for t in breaker.tripped]
    # with repair conversions, the same all-fail pattern must NOT trip
    breaker2 = CircuitBreakerState()
    for end_step in (10, 20):
        _observe_window(
            breaker2,
            end_step=end_step,
            facts=[_fact(all_fail_share=1.0, repair_queued=True, repair_converted=2)] * 10,
        )
    assert breaker2.tripped == []


def test_breaker_holdout_and_replay_regression_rules() -> None:
    breaker = CircuitBreakerState()
    breaker.report_holdout_pass1(0.80)
    breaker.report_holdout_pass1(0.75)  # -5pp > 3pp limit
    breaker.report_replay_pass1(0.70)
    breaker.report_replay_pass1(0.60)  # -10pp
    # the drop persists across both windows -> trips at the 2nd (required 2)
    trips = []
    for end_step in (10, 20):
        trips += _observe_window(breaker, end_step=end_step, facts=[_fact()] * 10)
    assert {"holdout_regression", "replay_regression"} <= {t["breaker"] for t in trips}
    # a small drop (<= 3pp) is not a regression
    breaker2 = CircuitBreakerState()
    breaker2.report_holdout_pass1(0.80)
    breaker2.report_holdout_pass1(0.78)
    _observe_window(breaker2, end_step=10, facts=[_fact()] * 10)
    assert breaker2.tripped == []


def test_breaker_entropy_collapse_requires_both_conditions() -> None:
    breaker = CircuitBreakerState(window_size=2, entropy_baseline_steps=4)
    # 4 baseline steps with high entropy + high yield
    for step in range(1, 5):
        breaker.observe_step(step=step, **_fact(entropy=4.0))
    # window 1: entropy collapsed (1.0 < 2.0) but yield is fine -> no violation
    trips = _observe_window(breaker, end_step=10, facts=[_fact(entropy=1.0)] * 2)
    assert all(t["breaker"] != "entropy_collapse" for t in trips)
    # windows 2+3: entropy collapsed AND yield collapsed -> trips at the 2nd
    for end_step in (12, 14):
        trips += _observe_window(
            breaker,
            end_step=end_step,
            facts=[_fact(entropy=1.0, all_fail_share=1.0)] * 2,
        )
    assert [t["breaker"] for t in trips].count("entropy_collapse") == 1


# ---------------------------------------------------------------------------
# the trainer's wrapper + halt path
# ---------------------------------------------------------------------------


def test_observe_and_evaluate_breakers_feeds_and_returns_events() -> None:
    breaker = CircuitBreakerState()
    trips = []
    for end_step in (10, 20):
        for offset in range(breaker.window_size):
            trips += observe_and_evaluate_breakers(
                breaker,
                step=end_step - breaker.window_size + 1 + offset,
                route="frontier_rl",
                non_finite=True,
                clip_fraction=0.0,
                entropy_mean=3.0,
                repair_queued=False,
                repair_converted_jsonl=None,
                all_fail=False,
            )
    assert any(t["breaker"] == "non_finite" for t in trips)


def test_maybe_stop_for_breaker_halt_path() -> None:
    breaker = CircuitBreakerState()
    breaker.tripped.append({"breaker": "non_finite", "step": 20, "window": 2})
    args = Namespace(stop_on_severe_breaker=True)
    assert maybe_stop_for_breaker(breaker, args, rank=0, trips=breaker.tripped) is True
    # without the flag the same state must NOT halt
    args2 = Namespace(stop_on_severe_breaker=False)
    assert maybe_stop_for_breaker(breaker, args2, rank=0, trips=breaker.tripped) is False
    # no trips -> never halts
    clean = CircuitBreakerState()
    assert maybe_stop_for_breaker(clean, args, rank=0, trips=[]) is False
