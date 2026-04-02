from __future__ import annotations

from pathlib import Path

import torch

from training.grpo_utils import (
    AdaptiveTemperatureState,
    append_grpo_metric_jsonl,
    brevity_reward,
    load_grpo_step_metrics_jsonl,
    build_grpo_metrics_payload_from_jsonl,
    build_grpo_metrics_payload,
    TaskCurriculum,
    build_grpo_step_record,
    build_reward_breakdown,
    estimate_detail_budget,
    interface_match_score,
    reward_signal_stats,
    summarize_python_interface,
)


def test_summarize_python_interface_extracts_signatures() -> None:
    code = """
class BellPair:
    pass

def phase_estimation(phase: float, n_bits: int) -> int:
    return 0
"""
    lines = summarize_python_interface(code)
    assert "class BellPair" in lines
    assert "phase_estimation(phase: float, n_bits: int) -> int" in lines


def test_interface_match_score_rewards_exact_match() -> None:
    required = [
        "phase_estimation(phase: float, n_bits: int) -> int",
        "phase_from_measurement(measurement: int, n_bits: int) -> float",
    ]
    candidate = list(required)
    assert interface_match_score(required, candidate) == 1.0


def test_build_reward_breakdown_adds_partial_verifier_credit() -> None:
    reward = build_reward_breakdown(
        code="def solve(x: int) -> int:\n    return x + 1\n",
        result={"passed": False, "details": ["case a failed"]},
        required_interface=["solve(x: int) -> int"],
        detail_budget=4,
        pass_weight=0.6,
        syntax_weight=0.1,
        interface_weight=0.15,
        verifier_weight=0.15,
    )
    assert reward["passed"] is False
    assert reward["syntax_reward"] == 1.0
    assert reward["interface_reward"] == 1.0
    assert reward["verifier_reward"] == 0.75
    assert 0.0 < float(reward["total_reward"]) < 1.0


def test_estimate_detail_budget_counts_test_markers() -> None:
    source = """
# Test one
failures.append("a")
details.append("b")
"""
    assert estimate_detail_budget(source, cap=8) == 3


def test_task_curriculum_prioritizes_harder_quantum_tasks() -> None:
    curriculum = TaskCurriculum(quantum_priority=1.5, uncertainty_bonus=0.2)
    curriculum.record("easy_quantum", 0.95)
    curriculum.record("easy_quantum", 0.95)
    hard_weight = curriculum.weight("hard_quantum", "quantum")
    easy_weight = curriculum.weight("easy_quantum", "quantum")
    software_weight = curriculum.weight("hard_software", "software")
    assert hard_weight > easy_weight
    assert hard_weight > software_weight


def test_reward_signal_stats_keeps_component_signal_visible() -> None:
    stats = reward_signal_stats(
        rewards=torch.tensor([0.15, 0.1125]),
        pass_rewards=torch.tensor([0.0, 0.0]),
        syntax_rewards=torch.tensor([0.0, 0.0]),
        interface_rewards=torch.tensor([0.0, 0.0]),
        verifier_rewards=torch.tensor([1.0, 0.75]),
    )
    assert stats["reward_std"] < 0.05
    assert stats["verifier_std"] >= 0.12
    assert stats["signal_std"] == stats["verifier_std"]


def test_build_grpo_step_record_persists_skip_metadata() -> None:
    record = build_grpo_step_record(
        step=3,
        task_name="quantum_qaoa_maxcut",
        domain="quantum",
        mean_reward=0.0546,
        signal_stats={
            "reward_std": 0.01,
            "signal_std": 0.01,
            "pass_std": 0.0,
            "syntax_std": 0.0,
            "interface_std": 0.0,
            "verifier_std": 0.12,
        },
        pass_rate=0.0,
        syntax_rate=1.0,
        interface_rate=0.5,
        verifier_rate=0.75,
        task_prob=0.42,
        task_state={"ema_reward": 0.0546, "seen": 1.0},
        advantage_scale=0.12,
        skipped=True,
        reason="low_reward_signal",
    )

    assert record["step"] == 3
    assert record["task"] == "quantum_qaoa_maxcut"
    assert record["domain"] == "quantum"
    assert record["skipped"] is True
    assert record["reason"] == "low_reward_signal"
    assert record["task_seen"] == 1
    assert record["verifier_rate"] == 0.75


def test_build_grpo_step_record_persists_update_metadata() -> None:
    record = build_grpo_step_record(
        step=4,
        task_name="quantum_superdense_coding",
        domain="quantum",
        mean_reward=0.8,
        signal_stats={
            "reward_std": 0.3,
            "signal_std": 0.3,
            "pass_std": 0.4,
            "syntax_std": 0.0,
            "interface_std": 0.0,
            "verifier_std": 0.0,
        },
        pass_rate=0.75,
        syntax_rate=1.0,
        interface_rate=1.0,
        verifier_rate=1.0,
        task_prob=0.25,
        task_state={"ema_reward": 0.8, "seen": 2.0},
        advantage_scale=0.3,
        loss=0.0125,
        adapter_init="outputs/demo-adapter/adapter",
    )

    assert record["step"] == 4
    assert record["task"] == "quantum_superdense_coding"
    assert record["loss"] == 0.0125
    assert record["adapter_init"] == "outputs/demo-adapter/adapter"
    assert "skipped" not in record
    assert "reason" not in record


def test_build_grpo_metrics_payload_summarizes_skips_and_updates() -> None:
    payload = build_grpo_metrics_payload(
        [
            build_grpo_step_record(
                step=1,
                task_name="quantum_qaoa_maxcut",
                domain="quantum",
                mean_reward=0.05,
                signal_stats={"reward_std": 0.01, "signal_std": 0.01},
                pass_rate=0.0,
                syntax_rate=1.0,
                interface_rate=0.5,
                verifier_rate=0.75,
                task_prob=0.4,
                task_state={"ema_reward": 0.05, "seen": 1.0},
                skipped=True,
                reason="low_reward_signal",
            ),
            build_grpo_step_record(
                step=2,
                task_name="quantum_superdense_coding",
                domain="quantum",
                mean_reward=0.8,
                signal_stats={"reward_std": 0.3, "signal_std": 0.3},
                pass_rate=0.75,
                syntax_rate=1.0,
                interface_rate=1.0,
                verifier_rate=1.0,
                task_prob=0.25,
                task_state={"ema_reward": 0.8, "seen": 2.0},
                loss=0.0125,
            ),
        ],
        planned_steps=2,
    )

    assert payload["summary"] == {
        "planned_steps": 2,
        "recorded_steps": 2,
        "updated_steps": 1,
        "skipped_steps": 1,
        "last_recorded_step": 2,
        "skip_reasons": {"low_reward_signal": 1},
    }


def test_build_grpo_metrics_payload_handles_empty_runs() -> None:
    payload = build_grpo_metrics_payload([], planned_steps=4)

    assert payload["summary"] == {
        "planned_steps": 4,
        "recorded_steps": 0,
        "updated_steps": 0,
        "skipped_steps": 0,
        "last_recorded_step": None,
        "skip_reasons": {},
    }


def test_build_grpo_metrics_payload_from_jsonl_replays_current_summary(tmp_path: Path) -> None:
    metrics_path = tmp_path / "grpo_step_metrics.jsonl"
    append_grpo_metric_jsonl(
        metrics_path,
        {
            "step": 1,
            "task": "quantum_qaoa_maxcut",
            "domain": "quantum",
            "skipped": True,
            "reason": "low_reward_signal",
        },
    )
    append_grpo_metric_jsonl(
        metrics_path,
        {
            "step": 2,
            "task": "quantum_superdense_coding",
            "domain": "quantum",
            "loss": 0.0125,
        },
    )
    append_grpo_metric_jsonl(
        metrics_path,
        {
            "step": 3,
            "task": "quantum_phase_estimation_circuit",
            "domain": "quantum",
            "skipped": True,
            "reason": "non_finite_loss",
        },
    )

    payload = build_grpo_metrics_payload_from_jsonl(metrics_path, planned_steps=5)

    assert payload["summary"] == {
        "planned_steps": 5,
        "recorded_steps": 3,
        "updated_steps": 1,
        "skipped_steps": 2,
        "last_recorded_step": 3,
        "skip_reasons": {
            "low_reward_signal": 1,
            "non_finite_loss": 1,
        },
    }


def test_load_grpo_step_metrics_jsonl_returns_empty_for_missing_file(tmp_path: Path) -> None:
    metrics_path = tmp_path / "missing.jsonl"

    assert load_grpo_step_metrics_jsonl(metrics_path) == []


def test_brevity_reward_short_code_gets_full_score() -> None:
    short = "def f(x):\n    return x + 1\n"
    assert brevity_reward(short, target_lines=40) == 1.0


def test_brevity_reward_long_code_gets_lower_score() -> None:
    long_code = "\n".join(f"x = {i}" for i in range(100))
    score = brevity_reward(long_code, target_lines=40)
    assert 0.0 < score < 1.0


def test_brevity_reward_empty_code_gets_zero() -> None:
    assert brevity_reward("", target_lines=40) == 0.0


def test_brevity_reward_creates_within_group_variance() -> None:
    """Brevity reward should differentiate completions even when all fail tests."""
    short = "def solve():\n    pass\n"
    long = "\n".join(f"line_{i} = {i}" for i in range(80))
    short_score = brevity_reward(short, target_lines=40)
    long_score = brevity_reward(long, target_lines=40)
    assert short_score > long_score
    assert short_score - long_score > 0.3  # meaningful difference


def test_build_reward_breakdown_includes_brevity_when_weighted() -> None:
    reward = build_reward_breakdown(
        code="def solve(x: int) -> int:\n    return x + 1\n",
        result={"passed": False, "details": ["case a failed"]},
        required_interface=["solve(x: int) -> int"],
        detail_budget=4,
        pass_weight=0.5,
        syntax_weight=0.1,
        interface_weight=0.1,
        verifier_weight=0.1,
        brevity_weight=0.2,
        brevity_target_lines=40,
    )
    assert "brevity_reward" in reward
    assert reward["brevity_reward"] == 1.0  # short code


def test_reward_signal_stats_includes_brevity_when_provided() -> None:
    stats = reward_signal_stats(
        rewards=torch.tensor([0.5, 0.5]),
        pass_rewards=torch.tensor([0.0, 0.0]),
        syntax_rewards=torch.tensor([1.0, 1.0]),
        interface_rewards=torch.tensor([0.0, 0.0]),
        verifier_rewards=torch.tensor([0.0, 0.0]),
        brevity_rewards=torch.tensor([1.0, 0.3]),
    )
    assert "brevity_std" in stats
    assert stats["brevity_std"] > 0.3
    assert stats["signal_std"] >= stats["brevity_std"]


# ---------------------------------------------------------------------------
# AdaptiveTemperatureState tests
# ---------------------------------------------------------------------------


def test_adaptive_temp_starts_at_base_temperature() -> None:
    state = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=1.4)
    assert state.current_temp() == 0.8


def test_adaptive_temp_escalates_after_low_reward_signal_skips() -> None:
    state = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=1.4)
    state.record_skip("low_reward_signal")
    assert state.current_temp() > 0.8
    state.record_skip("low_reward_signal")
    assert state.current_temp() > state.current_temp_at_count(1)


def test_adaptive_temp_does_not_escalate_for_other_skip_reasons() -> None:
    state = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=1.4)
    state.record_skip("empty_completion_mask")
    state.record_skip("non_finite_loss")
    assert state.current_temp() == 0.8


def test_adaptive_temp_caps_at_max_temp() -> None:
    state = AdaptiveTemperatureState(base_temp=0.8, step_size=0.5, max_temp=1.4)
    for _ in range(20):
        state.record_skip("low_reward_signal")
    assert state.current_temp() == 1.4


def test_adaptive_temp_resets_after_successful_update() -> None:
    state = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=1.4)
    state.record_skip("low_reward_signal")
    state.record_skip("low_reward_signal")
    assert state.current_temp() > 0.8
    state.record_update()
    assert state.current_temp() == 0.8


def test_adaptive_temp_consecutive_count_resets_after_update() -> None:
    state = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=1.4)
    state.record_skip("low_reward_signal")
    state.record_skip("low_reward_signal")
    state.record_update()
    assert state.consecutive_low_signal_skips == 0


def test_adaptive_temp_serializes_and_restores() -> None:
    state = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=1.4)
    state.record_skip("low_reward_signal")
    state.record_skip("low_reward_signal")
    snapshot = state.to_dict()
    restored = AdaptiveTemperatureState.from_dict(snapshot)
    assert restored.current_temp() == state.current_temp()
    assert restored.consecutive_low_signal_skips == state.consecutive_low_signal_skips


def test_adaptive_temp_current_temp_at_count_helper() -> None:
    state = AdaptiveTemperatureState(base_temp=0.8, step_size=0.15, max_temp=1.4)
    # With 0 consecutive skips, should be base_temp
    assert state.current_temp_at_count(0) == 0.8
    # With 1 skip, should be higher
    assert state.current_temp_at_count(1) > 0.8
    # With 1 skip, should be lower than with 2 skips
    assert state.current_temp_at_count(1) < state.current_temp_at_count(2)
