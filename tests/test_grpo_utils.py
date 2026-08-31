from __future__ import annotations

from pathlib import Path

import pytest
import torch

from training.grpo_utils import (
    AdaptiveTemperatureState,
    FrontierRouter,
    TaskCurriculum,
    append_grpo_metric_jsonl,
    brevity_reward,
    build_grpo_metrics_payload,
    build_grpo_metrics_payload_from_jsonl,
    build_grpo_step_record,
    build_mixture_weights,
    build_reward_breakdown,
    classify_frontier_route,
    estimate_detail_budget,
    frontier_learnability,
    import_hygiene_score,
    interface_match_score,
    leave_one_out_advantages,
    load_grpo_step_metrics_jsonl,
    policy_update_signal_magnitude,
    reward_signal_stats,
    sapo_loss_metrics,
    shaped_reward_from_details,
    stable_gspo_loss,
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


def test_import_hygiene_score_penalizes_invented_helper_imports() -> None:
    score = import_hygiene_score(
        "from qaoa import solve\nimport itertools\n",
        single_file_expected=True,
    )
    assert score == 0.5


def test_build_reward_breakdown_includes_import_hygiene_signal() -> None:
    reward = build_reward_breakdown(
        code="from qaoa import helper\n\ndef solve(x: int) -> int:\n    return x\n",
        result={"passed": False, "details": ["case a failed"]},
        required_interface=["solve(x: int) -> int"],
        detail_budget=4,
        pass_weight=0.6,
        syntax_weight=0.1,
        interface_weight=0.15,
        verifier_weight=0.1,
        import_hygiene_weight=0.05,
        single_file_expected=True,
    )
    assert reward["import_hygiene_reward"] == 0.0
    assert 0.0 <= float(reward["total_reward"]) < 1.0


def test_build_reward_breakdown_zeros_verifier_credit_for_runtime_failures() -> None:
    reward = build_reward_breakdown(
        code="def solve(x: int) -> int:\n    return missing_name + x\n",
        result={"passed": False, "details": ["NameError: name 'missing_name' is not defined"]},
        required_interface=["solve(x: int) -> int"],
        detail_budget=4,
        pass_weight=0.6,
        syntax_weight=0.1,
        interface_weight=0.15,
        verifier_weight=0.15,
    )
    assert reward["syntax_reward"] == 1.0
    assert reward["interface_reward"] == 1.0
    assert reward["verifier_reward"] == 0.0


def test_build_reward_breakdown_does_not_reward_unparseable_code_as_partial_progress() -> None:
    reward = build_reward_breakdown(
        code="def solve(:\n    pass\n",
        result={
            "passed": False,
            "details": ["SyntaxError: invalid syntax (candidate.py, line 1)"],
        },
        required_interface=["solve()"],
        # A large test budget previously turned a one-line SyntaxError into
        # 7/8 generic verifier credit, despite the candidate never executing.
        detail_budget=8,
        pass_weight=0.6,
        syntax_weight=0.1,
        interface_weight=0.15,
        verifier_weight=0.15,
    )

    assert reward["syntax_reward"] == 0.0
    assert reward["verifier_reward"] == 0.0
    assert reward["total_reward"] == 0.0


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


def test_frontier_learnability_peaks_for_mixed_outcomes() -> None:
    assert frontier_learnability(pass_rate=0.5, shaped_signal_std=0.0) == 1.0
    assert frontier_learnability(pass_rate=0.0, shaped_signal_std=0.0) == 0.0
    assert frontier_learnability(pass_rate=1.0, shaped_signal_std=0.0) == 0.0
    assert frontier_learnability(pass_rate=0.0, shaped_signal_std=0.3) == 0.3


def test_classify_frontier_route_separates_rl_repair_and_replay() -> None:
    assert classify_frontier_route(pass_rate=0.5, shaped_signal_std=0.2) == "frontier_rl"
    assert classify_frontier_route(pass_rate=0.0, shaped_signal_std=0.2) == "partial_repair_rl"
    assert classify_frontier_route(pass_rate=0.0, shaped_signal_std=0.01) == "repair_sft"
    assert classify_frontier_route(pass_rate=1.0, shaped_signal_std=0.01) == "mastered_replay"


def test_leave_one_out_advantages_use_other_group_members_as_baseline() -> None:
    advantages = leave_one_out_advantages(torch.tensor([1.0, 0.0, 0.5]))
    assert torch.allclose(advantages, torch.tensor([0.75, -0.75, 0.0]))
    assert torch.allclose(leave_one_out_advantages(torch.tensor([0.4])), torch.tensor([0.0]))


def test_stable_gspo_loss_applies_asymmetric_sequence_clipping() -> None:
    current = torch.log(torch.tensor([2.0, 0.5]))
    old = torch.zeros(2)
    advantages = torch.tensor([1.0, -1.0])

    loss = stable_gspo_loss(
        current,
        old,
        advantages,
        clip_low=0.2,
        clip_high=0.3,
        kl_coeff=0.0,
        numerical_log_ratio_clip=8.0,
    )

    assert torch.isclose(loss, torch.tensor(-0.25), atol=1e-6)


def test_stable_gspo_loss_returns_nan_without_finite_samples() -> None:
    loss = stable_gspo_loss(
        torch.tensor([float("nan")]),
        torch.tensor([0.0]),
        torch.tensor([1.0]),
        clip_low=0.2,
        clip_high=0.3,
        kl_coeff=0.0,
        numerical_log_ratio_clip=8.0,
    )
    assert torch.isnan(loss)


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


def test_loo_update_gate_uses_actual_clipped_advantage_rms() -> None:
    magnitude, kind = policy_update_signal_magnitude(
        advantage_mode="loo",
        signal_stats={"signal_std": 0.5},
        loo_advantage_rms=0.01,
    )

    # A large raw component dispersion must not disguise a nearly-flat
    # weighted LOO objective.
    assert magnitude == 0.01
    assert kind == "loo_advantage_rms"
    assert magnitude < 0.05


def test_group_std_update_gate_preserves_legacy_component_signal() -> None:
    magnitude, kind = policy_update_signal_magnitude(
        advantage_mode="group_std",
        signal_stats={"signal_std": 0.5},
        loo_advantage_rms=None,
    )

    assert magnitude == 0.5
    assert kind == "reward_signal_std"


def test_trainer_uses_selected_update_signal_for_both_flat_group_gates() -> None:
    trainer = (Path(__file__).resolve().parents[1] / "training/grpo_trainer.py").read_text(
        encoding="utf-8"
    )

    assert trainer.count("update_signal_magnitude < args.min_reward_std") == 2


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
    # 2026-08-26 (r10): the EOS-collapse rescue flag rides the skipped record
    # when the alarm fired; absent otherwise.
    assert "degenerate_policy_alarm" not in record


def test_build_grpo_step_record_persists_degenerate_policy_alarm() -> None:
    """2026-08-26 (r10, run-6 killer): when the EOS-collapse rescue alarm
    fires, the step record must carry ``degenerate_policy_alarm: true`` so
    monitoring can see the escalation (and soft-resume tooling can audit it).
    """
    record = build_grpo_step_record(
        step=25,
        task_name="quantum_circuit_phase_repair",
        domain="quantum",
        mean_reward=0.0,
        signal_stats={
            "reward_std": 0.0,
            "signal_std": 0.0,
            "pass_std": 0.0,
            "syntax_std": 0.0,
            "interface_std": 0.0,
            "verifier_std": 0.0,
        },
        pass_rate=0.0,
        syntax_rate=0.0,
        interface_rate=0.0,
        verifier_rate=0.0,
        task_prob=0.05,
        task_state={"ema_reward": 0.0, "seen": 1.0},
        skipped=True,
        reason="repair_sft_queued",
        degenerate_policy_alarm=True,
    )
    assert record["degenerate_policy_alarm"] is True
    assert record["reason"] == "repair_sft_queued"


def test_build_grpo_step_record_persists_quarantine_suppressed() -> None:
    """T1a (2026-08-27): when the collapse gate suppressed repair-routing the
    record carries ``quarantine_suppressed: true``; absent otherwise."""
    record = build_grpo_step_record(
        step=12,
        task_name="quantum_bitstring_maxcut_landscape",
        domain="quantum",
        mean_reward=0.0,
        signal_stats={
            "reward_std": 0.0,
            "signal_std": 0.0,
            "pass_std": 0.0,
            "syntax_std": 0.0,
            "interface_std": 0.0,
            "verifier_std": 0.0,
        },
        pass_rate=0.0,
        syntax_rate=0.0,
        interface_rate=0.0,
        verifier_rate=0.0,
        task_prob=0.05,
        task_state={"ema_reward": 0.0, "seen": 1.0},
        skipped=True,
        reason="low_reward_signal",
        quarantine_suppressed=True,
    )
    assert record["quarantine_suppressed"] is True
    assert record["reason"] == "low_reward_signal"


# ---------------------------------------------------------------------------
# T1b (algorithm audit 2026-08-27): lineage difficulty manifest
# ---------------------------------------------------------------------------


def test_difficulty_manifest_downweights_hard_tasks_never_zero() -> None:
    """T1b: the lineage difficulty manifest (15/20 v8 tasks never passed
    across run-4..7) applies a cold-start weight discount: pre-signal, a hard
    task's sampling weight is BELOW a learnable task's — and the discount
    NEVER zeroes a task (floor >= min_weight; capability-matched curriculum).
    """
    hard = "quantum_bitstring_maxcut_landscape"
    easy = "quantum_bell_basis_discrimination"
    router = FrontierRouter(difficulty_manifest=frozenset({hard}))
    w_hard = router.weight(hard, step=1, total_probes=0)
    w_easy = router.weight(easy, step=1, total_probes=0)
    assert w_hard < w_easy
    assert w_hard >= router.min_weight
    assert w_hard > 0.0


def test_difficulty_manifest_first_pass_restores_full_weight() -> None:
    """T1b: the FIRST pass>0 in the run removes the discount — the task's
    weight becomes byte-identical to an identical router without the manifest.
    """
    task = "quantum_qft_periodic_state"
    router = FrontierRouter(difficulty_manifest=frozenset({task}))
    w_before = router.weight(task, step=1, total_probes=0)
    router.probe_record(task, step=2, pass_rate=0.5, shaped_signal_std=0.3, group_size=4)
    w_after = router.weight(task, step=3, total_probes=1)
    assert w_after > w_before
    plain = FrontierRouter()
    plain.probe_record(task, step=2, pass_rate=0.5, shaped_signal_std=0.3, group_size=4)
    assert w_after == pytest.approx(plain.weight(task, step=3, total_probes=1))


def test_no_difficulty_manifest_weights_identical() -> None:
    """T1b: without a manifest the router weights are byte-identical to the
    pre-manifest behavior (hard and easy tasks weigh the same pre-signal)."""
    router = FrontierRouter()
    w_hard = router.weight("quantum_bitstring_maxcut_landscape", step=1, total_probes=0)
    w_easy = router.weight("quantum_bell_basis_discrimination", step=1, total_probes=0)
    assert w_hard == pytest.approx(w_easy)


def test_difficulty_manifest_mixture_mass_prefers_learnable_set() -> None:
    """T1b at the mixture level: with the manifest, aggregate sampling mass
    on the hard set is BELOW the learnable set pre-signal, and every task
    keeps positive mass (E2H emphasis, never zeroed)."""
    tasks = [
        {"task_id": f"hard_{i}", "meta": {"domain": "quantum", "category": "noise"}}
        for i in range(3)
    ] + [{"task_id": "learnable", "meta": {"domain": "quantum", "category": "noise"}}]
    router = FrontierRouter(difficulty_manifest=frozenset({"hard_0", "hard_1", "hard_2"}))
    weights = build_mixture_weights(router, tasks, step=1)
    hard_mass = sum(weights[i] for i in range(3))
    assert hard_mass < weights[3]
    assert all(w > 0.0 for w in weights)


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
        loo_advantage_rms=0.4,
        loo_advantage_mean_abs=0.35,
        update_signal_magnitude=0.4,
        update_signal_kind="loo_advantage_rms",
        update_signal_threshold=0.05,
        loss=0.0125,
        adapter_init="outputs/demo-adapter/adapter",
        optimizer_substeps_per_rollout=1,
        gradient_norms=[0.25],
        inner_early_stop_reason="non_finite_gradient",
        eos_termination_rate=0.75,
        completion_token_lengths=[128, 256, 512, 400],
        raw_response_chars=[500, 900, 1800, 1400],
        extracted_code_chars=[480, 700, 800, 1200],
        generation_token_budget=896,
    )

    assert record["step"] == 4
    assert record["task"] == "quantum_superdense_coding"
    assert record["loss"] == 0.0125
    assert record["adapter_init"] == "outputs/demo-adapter/adapter"
    assert record["loo_advantage_rms"] == 0.4
    assert record["loo_advantage_mean_abs"] == 0.35
    assert record["update_signal_magnitude"] == 0.4
    assert record["update_signal_kind"] == "loo_advantage_rms"
    assert record["update_signal_threshold"] == 0.05
    assert record["optimizer_substeps_per_rollout"] == 1
    assert record["gradient_norms"] == [0.25]
    assert record["inner_early_stop_reason"] == "non_finite_gradient"
    assert record["eos_termination_rate"] == 0.75
    assert record["completion_token_lengths"] == [128, 256, 512, 400]
    assert record["raw_response_chars"] == [500, 900, 1800, 1400]
    assert record["extracted_code_chars"] == [480, 700, 800, 1200]
    assert record["generation_token_budget"] == 896
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


# ---------------------------------------------------------------------------
# Shaped-reward calibration regression tests (2026-08-24 data-efficiency audit)
#
# The next SAPO launch runs the frozen targeted10 manifest
# (evals/benchmarks/quantum_grpo_training_v7_targeted_integrity.txt). Its
# harnesses report failures in the arrow form
#     f"phase_estimation({phase}, {n_bits}) -> {actual}, expected {expected}"
# (real lines: "phase_estimation(0.25, 3) -> 3, expected 2") and the
# comparator form "optimize_circuit lost gates: 3 != 5". Before 2026-08-24
# the parser only scored `key=value` lines, so these near-misses earned
# shaped reward 0.0 — identical to a SyntaxError crash — and all-fail groups
# on 9/10 targeted10 tasks carried no continuous policy signal.
# ---------------------------------------------------------------------------


def test_shaped_reward_parses_arrow_actual_expected_lines() -> None:
    # Real failure lines captured from a near-miss candidate run against
    # evals/tasks/quantum/phase_measurement_register/tests.py (off by one on
    # every check).
    lines = [
        "phase_estimation(0.0, 3) -> 1, expected 0",
        "phase_estimation(0.25, 3) -> 3, expected 2",
        "phase_estimation(0.5, 3) -> 5, expected 4",
        "phase_estimation(0.75, 4) -> 13, expected 12",
    ]
    for line in lines:
        assert shaped_reward_from_details(False, [line]) > 0.0, line
    # The pass cap applies to arrow-form near-misses too.
    for line in lines:
        assert shaped_reward_from_details(False, [line]) <= 0.9, line


def test_shaped_reward_arrow_form_orders_near_vs_far_miss() -> None:
    near = shaped_reward_from_details(False, ["phase_estimation(0.25, 3) -> 3, expected 2"])
    mid = shaped_reward_from_details(False, ["phase_estimation(0.25, 3) -> 8, expected 2"])
    far = shaped_reward_from_details(False, ["phase_estimation(0.25, 3) -> 18, expected 2"])
    assert near > 0.0
    assert near > mid > far > 0.0


def test_shaped_reward_arrow_form_with_unit_word() -> None:
    # bitstring_maxcut_landscape: "brute_force_maxcut(triangle) -> cost 1, expected 2"
    assert (
        shaped_reward_from_details(False, ["brute_force_maxcut(triangle) -> cost 1, expected 2"])
        > 0.0
    )
    assert shaped_reward_from_details(
        False, ["brute_force_maxcut(triangle) -> cost 1, expected 2"]
    ) > shaped_reward_from_details(False, ["brute_force_maxcut(triangle) -> cost 0, expected 2"])


def test_shaped_reward_parses_neq_comparator_as_equality_miss() -> None:
    # circuit_depth_optimization: "optimize_circuit lost gates: 3 != 5"
    near = shaped_reward_from_details(False, ["optimize_circuit lost gates: 4 != 5"])
    far = shaped_reward_from_details(False, ["optimize_circuit lost gates: 1 != 5"])
    assert near > 0.0
    assert near > far > 0.0


def test_shaped_reward_does_not_credit_expected_side_of_neq() -> None:
    # The key=value regex must not treat the "!=" right-hand side (the
    # EXPECTED value) as the measurement: a candidate failing "3 != 5,
    # expected 5" must not receive full near-miss credit because 5 == 5.
    line = "optimize_circuit lost gates: 3 != 5, expected 5"
    assert 0.0 <= shaped_reward_from_details(False, [line]) < 0.9


def test_shaped_reward_still_zeros_list_and_pure_text_lines() -> None:
    # List-valued arrows carry no scalar closeness evidence — must stay 0.
    assert (
        shaped_reward_from_details(
            False, ["teleportation_corrections(0) -> [0, 0], expected [1, 0]"]
        )
        == 0.0
    )
    assert (
        shaped_reward_from_details(
            False, ["repair_phase_sequence([1,2,3]) -> [1,2,2], expected [1,2,3]"]
        )
        == 0.0
    )
    # Pure-text failures (measurement_bug_repair) stay 0.
    assert shaped_reward_from_details(False, ["mapping for '10' was incorrect"]) == 0.0


def test_shaped_reward_preserves_existing_kv_and_comparator_credit() -> None:
    # Previously-scored formats must not regress.
    assert shaped_reward_from_details(False, ["landscape length=7, expected 8"]) > 0.5
    assert shaped_reward_from_details(False, ["fidelity 0.8765 < 0.9000"]) > 0.8
    assert shaped_reward_from_details(False, ["vqe: energy=-1.48250 need<=-1.50000"]) > 0.8
    assert (
        shaped_reward_from_details(False, ["bit_flip_code(0,1): corrected_state=1, expected 0"])
        > 0.0
    )


# ---------------------------------------------------------------------------
# Target-keyword + comparator form ("expected >= 3.500000") — 2026-08-31
# algorithm-vigilance audit. quantum_rl_v2_qaoa_p2_maxcut's near-miss
# candidate emitted ONLY "optimized_cut=3.000000, expected >= 3.500000" and
# shaped_reward_from_details returned 0.0 — the differentiated-signal cure
# defeated on a v9 wave-1 task. The form appears in 6/12 v9 harness
# templates (qaoa_p2_maxcut, depolarizing_kraus, depolarizing_bell_mixed,
# vqe_penny_energy, trotter_suzuki_1qubit, bell_chsh).
# ---------------------------------------------------------------------------


def test_shaped_reward_scores_expected_with_comparator_threshold() -> None:
    # "expected >= T" states the pass threshold right after the target keyword.
    near = shaped_reward_from_details(False, ["optimized_cut=3.000000, expected >= 3.500000"])
    assert near > 0.5, f"qaoa near-miss shaped={near} (the v9 differentiated-signal defect)"
    assert near <= 0.9, f"near-miss must stay below the pass cap: {near}"
    # far-miss orders below the near-miss
    far = shaped_reward_from_details(False, ["optimized_cut=0.500000, expected >= 3.500000"])
    assert 0.0 < far < near, f"far-miss {far} must be below near-miss {near}"


def test_shaped_reward_scores_expected_less_equal_threshold() -> None:
    # "expected <= T" (trotter_suzuki_1qubit second_error template).
    near = shaped_reward_from_details(False, ["second_error=0.400000, expected <= 0.500000"])
    assert near > 0.5, f"lower-better near-miss shaped={near}"
    assert near <= 0.9
    assert shaped_reward_from_details(False, ["second_error=2.000000, expected <= 0.500000"]) < near


def test_shaped_reward_scores_zero_threshold_expected_ge() -> None:
    # "expected >= 0.000000000" (depolarizing_bell_mixed min_eigenvalue
    # template): a tiny negative eigenvalue is a near miss, not a crash.
    near = shaped_reward_from_details(
        False, ["min_eigenvalue=-0.000000001, expected >= 0.000000000"]
    )
    assert near > 0.5, f"zero-threshold near-miss shaped={near}"
    far = shaped_reward_from_details(
        False, ["min_eigenvalue=-2.000000000, expected >= 0.000000000"]
    )
    assert 0.0 <= far < near, f"far-miss {far} must be below near-miss {near}"


def test_shaped_reward_expected_comparator_does_not_break_prose_lines() -> None:
    # Pure-text lines stay 0.0 — the comparator must attach to a target
    # keyword AND a number.
    assert (
        shaped_reward_from_details(
            False,
            [
                "second_error=0.061115 >= first_error/4=0.015279, expected symmetric-splitting improvement"
            ],
        )
        > 0.0
    )
    assert shaped_reward_from_details(False, ["expected improvement only"]) == 0.0


def test_sapo_loss_metrics_stats_include_loss_and_advantage() -> None:
    """Training-log instrumentation (2026-08-25): the per-candidate stats the
    trainer persists must carry the candidate's own loss value and advantage
    (plus n_tokens) so the aggregate loss identity can be recomputed from the
    records. Backward-compatible: existing keys are unchanged."""
    cur = torch.tensor([[0.1, 0.2]])
    old = torch.tensor([[0.0, 0.0]])
    loss, stats = sapo_loss_metrics(
        [cur],
        [old],
        torch.tensor([1.0]),
        tau_pos=1.0,
        tau_neg=1.05,
        kl_coeff=0.01,
        numerical_log_ratio_clip=8.0,
    )
    assert abs(stats["loss"] - float(loss.item())) < 1e-6
    assert abs(stats["advantage"] - 1.0) < 1e-6
    assert stats["n_tokens"] == 2.0
    # existing keys preserved
    assert "sapo_gate_mean" in stats
    assert "seq_kl" in stats
    # empty batch still returns the same key set (with loss/advantage stubs)
    empty_loss, empty_stats = sapo_loss_metrics(
        [],
        [],
        torch.tensor([], dtype=torch.float32),
        tau_pos=1.0,
        tau_neg=1.05,
        kl_coeff=0.01,
        numerical_log_ratio_clip=8.0,
    )
    assert empty_loss.item() != empty_loss.item()  # NaN
    assert empty_stats["n_tokens"] == 0.0
    assert "loss" in empty_stats
    assert "advantage" in empty_stats


def test_grpo_utils_has_no_strict_zip_keyword() -> None:
    """Deploy Integrity py3.9 register gate (2026-08-26): the strict-zip
    keyword is py3.10-only even as False — a source-level guard (a runtime
    test cannot catch the syntax on py3.14)."""
    import inspect
    import re

    from training import grpo_utils as gu

    source = inspect.getsource(gu)
    assert not re.search(
        r"zip\([^)]*strict", source
    ), "zip(..., strict=) is py3.10-only; use plain zip + a length guard"


def test_training_has_no_runtime_union_isinstance() -> None:
    """Deploy Integrity py3.9 gate (2026-08-26 canary): `isinstance(x, int |
    float)` evaluates the union AT RUNTIME — py3.10-only — and would raise
    TypeError in the box's py3.9 venv on the self-eval/model-dim paths.
    Source-level guard (a runtime test cannot catch it on py3.14)."""
    import inspect
    import re

    from training import grpo_trainer as gt
    from training import grpo_utils as gu_mod

    for module in (gu_mod, gt):
        source = inspect.getsource(module)
        assert not re.search(
            r"isinstance\([^)]*\|", source
        ), "isinstance unions are py3.10-only; use tuples"
