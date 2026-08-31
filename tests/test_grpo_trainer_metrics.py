from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest
import torch

from training import grpo_trainer
from training.grpo_utils import (
    REPAIR_SFT,
    AdaptiveTemperatureState,
    FrontierRouter,
    append_grpo_metric,
    append_grpo_metric_jsonl,
    build_grpo_step_record,
    build_mixture_weights,
    should_queue_flat_all_fail,
)


def test_repair_routed_skips_do_not_escalate_temperature() -> None:
    """2026-08-25 death-spiral fix: a repair-routed skip (``route=repair_sft``,
    emitted as ``reason=repair_sft_queued``) is a ROUTING decision — the task
    moves to the repair SFT lane — not a low-signal outcome. Run-3 died at
    step 42 because 5 consecutive repair skips ramped temperature
    1.0 -> 1.45 -> 1.6 -> 1.75, exploding entropy (2.9 -> 4.2 -> 6.4) into
    pure-SyntaxError candidates with reward exactly 0.0 (positive-feedback
    cascade -> ``no_trainable_tasks``). Repair-routed skips must leave the
    flat-route counter — and temperature — at base.
    """
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    assert temp.current_temp() == 1.0
    for _ in range(5):
        grpo_trainer.escalate_temperature_on_flat_route(temp, route="repair_sft")
    assert temp.consecutive_low_signal_skips == 0
    assert temp.current_temp() == pytest.approx(1.0)


def test_invalid_or_noisy_quarantine_does_not_escalate_temperature() -> None:
    """INVALID_OR_NOISY is a quarantine of an unstable task, not a diversity
    failure; RL routes escalate only through their own low-reward-skip gate.
    """
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    grpo_trainer.escalate_temperature_on_flat_route(temp, route="invalid_or_noisy")
    grpo_trainer.escalate_temperature_on_flat_route(temp, route="frontier_rl")
    assert temp.consecutive_low_signal_skips == 0
    assert temp.current_temp() == 1.0


def test_low_entropy_all_fail_frontier_group_escalates_temperature() -> None:
    """Cold-task class (dead-signal report 2026-08-24): an all-fail
    frontier_rl group whose completions are confident-but-wrong (low entropy —
    steps 6/7 of sapo-27b-ai-20260824T031524 ran at entropy 0.29-0.35) still
    FIRES a real update from a single narrow mode, so the old repair-only
    escalation never engaged. The next group must sample at elevated
    temperature to diversify.
    """
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="frontier_rl", all_fail=True, entropy_mean=0.31
    )
    assert temp.consecutive_low_signal_skips == 1
    assert temp.current_temp() == pytest.approx(1.15)


def test_high_entropy_all_fail_group_does_not_escalate_temperature() -> None:
    """An already-diverse all-fail group (e.g. step 3 entropy 0.632) is not a
    single-mode failure; escalating would only add sampling noise."""
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="frontier_rl", all_fail=True, entropy_mean=0.63
    )
    assert temp.consecutive_low_signal_skips == 0
    assert temp.current_temp() == 1.0


def test_low_signal_skips_escalate_but_never_exceed_temp_ceiling() -> None:
    """2026-08-25: genuine low-signal skips (low-entropy all-fail RL groups)
    still escalate, but the trainer-side ceiling hard-caps behavior
    temperature at 1.3. Run-3's ladder climbed to 1.75 before the step-42
    death; 1.3 is the escalation ceiling regardless of the ladder's
    ``max_temp`` (or a resumed state file carrying a higher ceiling).
    """
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    for _ in range(5):
        grpo_trainer.escalate_temperature_on_flat_route(
            temp, route="frontier_rl", all_fail=True, entropy_mean=0.31
        )
    assert temp.consecutive_low_signal_skips == 5
    # the raw ladder formula min(1.0 * (1 + 0.15*5), 2.0) = 1.75 — exactly the
    # run-3 death value; the clamp must pull it back to 1.3.
    assert temp.current_temp() == pytest.approx(1.75)
    assert grpo_trainer.TEMP_ESCALATION_CEILING == 1.3
    assert grpo_trainer.clamp_adaptive_behavior_temperature(temp.current_temp()) == pytest.approx(
        1.3
    )
    # clamp is a pure ceiling: below-ceiling values pass through untouched.
    assert grpo_trainer.clamp_adaptive_behavior_temperature(1.0) == pytest.approx(1.0)
    assert grpo_trainer.clamp_adaptive_behavior_temperature(1.29) == pytest.approx(1.29)
    assert grpo_trainer.clamp_adaptive_behavior_temperature(2.0) == pytest.approx(1.3)


def test_genuine_update_resets_escalated_temperature_to_base() -> None:
    """A genuine-signal step (successful gradient update) resets the flat-route
    counter and returns temperature to base: escalation only accumulates over
    CONSECUTIVE low-signal skips, and one real update clears the ramp (as
    before the patch)."""
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="frontier_rl", all_fail=True, entropy_mean=0.31
    )
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="frontier_rl", all_fail=True, entropy_mean=0.31
    )
    assert temp.consecutive_low_signal_skips == 2
    assert temp.current_temp() == pytest.approx(1.3)
    temp.record_update()
    assert temp.consecutive_low_signal_skips == 0
    assert temp.current_temp() == pytest.approx(1.0)


def test_entropy_escalation_gates_keep_routing_and_quarantine_neutral() -> None:
    """Escalation gates by ENTROPY, not route (2026-08-25 + 2026-08-26 r10).

    2026-08-25 contract (still pinned): INVALID_OR_NOISY quarantine never
    escalates (an unstable task is not a diversity failure), and high-entropy
    repair-routed groups never escalate (the run-3 death-spiral class:
    entropy 2.9 -> 6.4 repair skips ramping temp 1.0 -> 1.75).

    2026-08-26 (r10, run-6 killer): a repair-routed group that is ALL-FAIL
    and LOW-ENTROPY (entropy < 0.45) is the cold-collapse class — a
    confident-but-wrong single mode (run-6 step 25: entropy 0.0137,
    completions [1,1,1,1]). Repair-routing must not swallow the rescue
    signal (run-6: 16 consecutive repair skips, temp stuck at 1.15, policy
    never rescued, no_trainable_tasks death), so low-entropy all-fail groups
    escalate BEFORE repair-routing.
    """
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    # r10: low-entropy repair-routed all-fail NOW escalates (cold-collapse class)
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="repair_sft", all_fail=True, entropy_mean=0.31
    )
    assert temp.consecutive_low_signal_skips == 1
    # 2026-08-25 contract preserved: INVALID_OR_NOISY never escalates
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="invalid_or_noisy", all_fail=True, entropy_mean=0.1
    )
    assert temp.consecutive_low_signal_skips == 1
    # run-3 spiral class: high-entropy repair-routed groups never escalate
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="repair_sft", all_fail=True, entropy_mean=0.9
    )
    assert temp.consecutive_low_signal_skips == 1
    # RL low-entropy all-fail still escalates (unchanged)
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="frontier_rl", all_fail=True, entropy_mean=0.31
    )
    assert temp.consecutive_low_signal_skips == 2


def test_degenerate_eos_collapse_detector_alarms_and_escalates() -> None:
    """2026-08-26 (r10, run-6 killer): a collapsed policy emits ~1-token
    completions at near-zero entropy (run-6 step 25: completion_token_lengths
    [1,1,1,1], eos_terminated x4, entropy 0.0137). After N=3 consecutive
    degenerate steps the rescue alarm must fire AND escalate the ladder
    IMMEDIATELY — repair-routing alone never escalates (2026-08-25 contract),
    so without this detector run-6's 16 consecutive repair skips kept temp
    stuck at 1.15 until no_trainable_tasks killed the run.
    """
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    detector = grpo_trainer.DegeneratePolicyDetector()
    # healthy groups never alarm
    assert (
        grpo_trainer.alarm_degenerate_policy(
            detector, temp, entropy_mean=0.51, completion_token_lengths=[1056, 750, 823, 719]
        )
        is False
    )
    assert temp.consecutive_low_signal_skips == 0
    # the collapse signature requires BOTH near-zero entropy AND 1-token
    # completions — either one alone is not degenerate
    assert (
        grpo_trainer.is_degenerate_policy_step(
            entropy_mean=0.0137, completion_token_lengths=[800, 900, 700, 600]
        )
        is False
    )
    assert (
        grpo_trainer.is_degenerate_policy_step(
            entropy_mean=0.5, completion_token_lengths=[1, 1, 1, 1]
        )
        is False
    )
    assert (
        grpo_trainer.is_degenerate_policy_step(
            entropy_mean=0.0137, completion_token_lengths=[1, 1, 1, 1]
        )
        is True
    )
    # 3 consecutive degenerate steps -> alarm on the 3rd, with escalation
    fired = [
        grpo_trainer.alarm_degenerate_policy(
            detector, temp, entropy_mean=0.0137, completion_token_lengths=[1, 1, 1, 1]
        )
        for _ in range(3)
    ]
    assert fired == [False, False, True]
    assert detector.consecutive_degenerate == 3
    assert temp.consecutive_low_signal_skips == 1
    assert temp.current_temp() == pytest.approx(1.15)
    # one healthy step resets the streak
    assert (
        grpo_trainer.alarm_degenerate_policy(
            detector, temp, entropy_mean=0.63, completion_token_lengths=[800, 900, 700, 600]
        )
        is False
    )
    assert detector.consecutive_degenerate == 0


def test_degenerate_rescue_leaves_normal_all_fail_repair_routing_unchanged() -> None:
    """A NORMAL all-fail group (diverse completions, healthy entropy) that the
    router sends to the repair lane keeps the exact pre-fix routing behavior:
    the task is still repair-routed (mark_repair), the step is still skipped
    as repair_sft_queued, and no temperature escalation happens. Only the
    low-entropy/collapsed class gains escalation.
    """
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    grpo_trainer.escalate_temperature_on_flat_route(
        temp, route="repair_sft", all_fail=True, entropy_mean=0.63
    )
    assert temp.consecutive_low_signal_skips == 0
    detector = grpo_trainer.DegeneratePolicyDetector()
    for _ in range(5):
        assert (
            grpo_trainer.alarm_degenerate_policy(
                detector, temp, entropy_mean=0.63, completion_token_lengths=[800, 900, 700, 600]
            )
            is False
        )
    assert temp.consecutive_low_signal_skips == 0
    assert detector.consecutive_degenerate == 0


def test_repair_skip_no_escalate_contract_holds_for_non_degenerate_groups() -> None:
    """2026-08-25 contract, still pinned: repair-routed skips must NOT escalate
    temperature — for every NON-degenerate class. The run-3 death spiral was
    high-entropy (2.9 -> 6.4) repair skips ramping 1.0 -> 1.75; those must
    stay non-escalating forever. Only the 2026-08-26 cold-collapse class
    (low-entropy all-fail, entropy < 0.45) escalates.
    """
    temp = AdaptiveTemperatureState(base_temp=1.0, step_size=0.15, max_temp=2.0)
    for _ in range(5):
        grpo_trainer.escalate_temperature_on_flat_route(
            temp, route="repair_sft", all_fail=True, entropy_mean=0.63
        )
    assert temp.consecutive_low_signal_skips == 0
    assert temp.current_temp() == pytest.approx(1.0)
    # INVALID_OR_NOISY quarantine never escalates either
    for _ in range(5):
        grpo_trainer.escalate_temperature_on_flat_route(
            temp, route="invalid_or_noisy", all_fail=True, entropy_mean=0.1
        )
    assert temp.consecutive_low_signal_skips == 0
    assert temp.current_temp() == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# T1a (algorithm audit 2026-08-27): quarantine-integrity gate
# ---------------------------------------------------------------------------


def test_quarantine_gate_engages_only_on_collapse_signature() -> None:
    """A collapsed policy must never produce evidence-free quarantines (run-6:
    ALL 20 tasks quarantined incl. the 5 learnable ones, driven by the EOS
    collapse). The gate engages on: the 3-step degenerate alarm, OR a
    stub-collapse group (every completion < 8 tokens), OR entropy below the
    degenerate floor (0.05). It must NOT engage on healthy groups — the loss
    entropy-floor 1.5 is deliberately NOT the gate threshold (run-5's s11/s12
    repairs ran at entropy 0.25-0.32; a 1.5 bar would starve the repair lane).
    """
    gate = grpo_trainer.quarantine_gate_active
    # engaged: the 3-step degenerate alarm fired
    assert (
        gate(
            degenerate_policy_alarm=True,
            entropy_mean=0.5,
            completion_token_lengths=[800, 900, 700, 600],
        )
        is True
    )
    # engaged: entropy below the degenerate floor (run-6 step 25: 0.0136)
    assert (
        gate(
            degenerate_policy_alarm=False,
            entropy_mean=0.0137,
            completion_token_lengths=[800, 900, 700, 600],
        )
        is True
    )
    # engaged: stub-collapse completions (all < 8 tokens), even at healthy entropy
    assert (
        gate(
            degenerate_policy_alarm=False,
            entropy_mean=0.5,
            completion_token_lengths=[3, 5, 7, 2],
        )
        is True
    )
    # clear: healthy diverse group
    assert (
        gate(
            degenerate_policy_alarm=False,
            entropy_mean=0.63,
            completion_token_lengths=[800, 900, 700, 600],
        )
        is False
    )
    # clear boundary: entropy back above the 0.05 floor, healthy lengths
    assert (
        gate(
            degenerate_policy_alarm=False,
            entropy_mean=0.051,
            completion_token_lengths=[800, 900, 700, 600],
        )
        is False
    )
    # cold-but-healthy (entropy 0.31, long completions) is NOT gated
    assert (
        gate(
            degenerate_policy_alarm=False,
            entropy_mean=0.31,
            completion_token_lengths=[800, 900, 700, 600],
        )
        is False
    )


def test_collapse_gate_keeps_task_in_rl_pool_and_repair_resumes_when_clear() -> None:
    """T1a wiring composition: a flat all-fail group under the collapse gate
    stays in the RL targeted pool (the main loop's queue gate composes with
    quarantine_suppressed — no mark_repair, no repair record); a healthy
    all-fail group still repair-queues byte-identical; when the signature
    clears, repair routing resumes immediately.
    """

    def queue_decision(*, entropy_mean, lengths, alarm: bool = False) -> bool:
        gate = grpo_trainer.quarantine_gate_active(
            degenerate_policy_alarm=alarm,
            entropy_mean=entropy_mean,
            completion_token_lengths=lengths,
        )
        return (
            should_queue_flat_all_fail(
                all_fail=True,
                route="frontier_rl",
                update_signal_magnitude=0.0,
                threshold=0.05,
            )
            and not gate
        )

    # collapsed step: queue gate suppressed -> no repair record written
    assert queue_decision(entropy_mean=0.0137, lengths=[1, 1, 1, 1]) is False
    # healthy all-fail: repair queue fires (unchanged)
    assert queue_decision(entropy_mean=0.63, lengths=[800, 900, 700, 600]) is True
    # alarm-clear boundary: entropy back above the floor -> repair resumes
    assert queue_decision(entropy_mean=0.051, lengths=[800, 900, 700, 600]) is True
    # alarm fired this step: suppressed even at healthy entropy/lengths
    assert queue_decision(entropy_mean=0.63, lengths=[800, 900, 700, 600], alarm=True) is False


def test_probe_suppress_repair_keeps_collapsed_task_in_rl_pool() -> None:
    """T1a probe-level belt-and-braces: even when accumulating all-fail
    evidence would classify REPAIR_SFT, suppress_repair=True keeps the task
    in the RL targeted pool (route != repair_sft; mixture still samples it).
    Without suppression the same evidence repairs (unchanged path).
    """
    task = "quantum_circuit_phase_repair"
    router = FrontierRouter()
    for i in range(8):
        router.probe_record(
            task,
            step=i + 1,
            pass_rate=0.0,
            shaped_signal_std=0.0,
            group_size=4,
            suppress_repair=True,
        )
    assert router.route_of(task) != REPAIR_SFT
    tasks = [{"task_id": task, "meta": {"domain": "quantum", "category": "cat"}}]
    weights = build_mixture_weights(router, tasks, step=9)
    assert weights[0] > 0.0
    # without suppression the same evidence repairs (unchanged path)
    router2 = FrontierRouter()
    for i in range(8):
        router2.probe_record(task, step=i + 1, pass_rate=0.0, shaped_signal_std=0.0, group_size=4)
    assert router2.route_of(task) == REPAIR_SFT


# ---------------------------------------------------------------------------
# 2026-09-01 (data-efficiency lane): collapse detection must PRECEDE the
# expensive reward pass. The alarm needs only entropy_mean (logprob pass) and
# completion_token_lengths (generation diagnostics) — both available before
# any harness/judge call. Run-6 class: completions [1,1,1,1], entropy 0.0137,
# 16 consecutive repair skips — every step paid the full reward pass on
# 1-token garbage before the alarm fired at the END of the step.
# ---------------------------------------------------------------------------


def test_collapse_detection_precedes_reward_pass_in_step_loop() -> None:
    """A degenerate rollout must be detected BEFORE the expensive reward pass
    (harness subprocess + judge forwards per candidate): the step loop must
    compute alarm_degenerate_policy + the quarantine gate before any
    evaluate_candidate call, so a collapsed step can skip the reward pass
    instead of burning it on evidence-free 1-token completions."""
    source = Path(grpo_trainer.__file__).read_text(encoding="utf-8")
    loop = source[source.index("for step in range(1, args.grpo_steps + 1):") :]
    alarm_at = loop.index("alarm_degenerate_policy(")
    gate_at = loop.index("quarantine_suppressed = quarantine_gate_active(")
    reward_at = loop.index("evaluate_candidate(")
    assert alarm_at < reward_at, (
        "alarm_degenerate_policy must fire before evaluate_candidate in the "
        "step loop (2026-09-01 data-efficiency: a collapsed step must never "
        "pay the reward pass before the collapse is detected)"
    )
    assert gate_at < reward_at, (
        "the quarantine gate must be computed before the reward pass so "
        "quarantine_suppressed can gate the evaluation loop"
    )


def test_evidence_free_candidate_entry_feeds_the_record_emit_contract() -> None:
    """The synthesized evaluation entries used when the quarantine gate skips
    the reward pass must satisfy every downstream consumer of the step loop:
    the direct-index reward tensors (total_reward / pass_reward / shaped_reward
    / syntax_reward / interface_reward / verifier_reward), build_rollout_rewards
    (per-candidate record with n_tokens + stop_reason), and the emit path.
    Zero values, passed=False, evidence_free=True."""
    from training.grpo_trainer import (
        build_rollout_rewards,
        per_candidate_stop_reasons,
    )

    entries = [grpo_trainer.evidence_free_candidate_entry() for _ in range(3)]
    for key in (
        "total_reward",
        "pass_reward",
        "shaped_reward",
        "syntax_reward",
        "interface_reward",
        "verifier_reward",
    ):
        assert all(float(entry[key]) == 0.0 for entry in entries), key
    assert all(entry["passed"] is False for entry in entries)
    assert all(entry["evidence_free"] is True for entry in entries)
    assert all(entry["model_dim_scores"] == {} for entry in entries)
    lengths = [4, 1, 1]
    diagnostics = {
        "eos_terminated": [True, True, True],
        "fence_terminated": [False, False, False],
        "truncated": [False, False, False],
        "cap_run_with_fence_opener": [False, False, False],
        "completion_token_lengths": lengths,
    }
    records = build_rollout_rewards(
        entries,
        torch.zeros(3),
        completion_token_lengths=lengths,
        adv_scale=None,
        stop_reasons=per_candidate_stop_reasons(diagnostics),
    )
    assert [record["n_tokens"] for record in records] == lengths
    assert [record["stop_reason"] for record in records] == ["eos", "eos", "eos"]
    assert all(float(record["total_reward"]) == 0.0 for record in records)
    assert all(record["pass"] is False for record in records)
    assert all(record["advantage"] == 0.0 for record in records)


class _FakeCheckpointModel:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def save_pretrained(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / "adapter_config.json").write_text('{"r": 16}\n', encoding="utf-8")
        if self.fail:
            raise RuntimeError("synthetic save failure")
        (path / "adapter_model.safetensors").write_bytes(b"weights")


class _FakeSaveBackend:
    def save_pretrained(self, path: Path) -> None:
        (Path(path) / "tokenizer_config.json").write_text("{}\n", encoding="utf-8")


class _FakeTextPreprocessor:
    save_backend = _FakeSaveBackend()


def test_atomic_peft_checkpoint_never_exposes_temp_as_final(tmp_path: Path) -> None:
    checkpoint = tmp_path / "step_000001_adapter"
    result = grpo_trainer.save_peft_checkpoint_atomic(
        _FakeCheckpointModel(), _FakeTextPreprocessor(), checkpoint
    )

    assert result == checkpoint
    assert grpo_trainer.peft_checkpoint_complete(checkpoint)
    assert (checkpoint / "tokenizer_config.json").is_file()
    assert not list(tmp_path.glob(".step_000001_adapter.tmp-*"))


def test_peft_checkpoint_complete_requires_config_and_weights(tmp_path: Path) -> None:
    """The checkpoint-complete marker (artifact-integrity lane 2026-09-01):
    adapter_config.json PLUS weights (safetensors or bin); config-only and
    weights-only dirs are INCOMPLETE and must not pass."""
    ckpt = tmp_path / "step_000001_adapter"
    ckpt.mkdir()
    assert not grpo_trainer.peft_checkpoint_complete(ckpt)

    (ckpt / "adapter_config.json").write_text("{}", encoding="utf-8")
    assert not grpo_trainer.peft_checkpoint_complete(ckpt)

    (ckpt / "adapter_model.bin").write_bytes(b"w")
    assert grpo_trainer.peft_checkpoint_complete(ckpt)

    (ckpt / "adapter_model.bin").unlink()
    (ckpt / "adapter_model.safetensors").write_bytes(b"w")
    assert grpo_trainer.peft_checkpoint_complete(ckpt)

    (ckpt / "adapter_config.json").unlink()
    assert not grpo_trainer.peft_checkpoint_complete(ckpt)


def test_atomic_peft_checkpoint_cleans_failed_stage_without_final(tmp_path: Path) -> None:
    checkpoint = tmp_path / "step_000002_adapter"
    with pytest.raises(RuntimeError, match="synthetic save failure"):
        grpo_trainer.save_peft_checkpoint_atomic(
            _FakeCheckpointModel(fail=True), _FakeTextPreprocessor(), checkpoint
        )

    assert not checkpoint.exists()
    assert not list(tmp_path.glob(".step_000002_adapter.tmp-*"))


def test_append_grpo_metric_persists_skipped_step_reason() -> None:
    metrics: list[dict[str, object]] = []

    record = append_grpo_metric(
        metrics,
        step=1,
        task="quantum_qaoa_maxcut",
        domain="quantum",
        mean_reward=0.054625,
        reward_std=0.01,
        reward_signal_std=0.01,
        curriculum_prob=0.25,
        task_ema_reward=0.054625,
        task_seen=1,
        skipped=True,
        reason="low_reward_signal",
    )

    assert metrics == [record]
    assert record["skipped"] is True
    assert record["reason"] == "low_reward_signal"
    assert record["domain"] == "quantum"
    assert "loss" not in record


def test_append_grpo_metric_persists_update_loss() -> None:
    metrics: list[dict[str, object]] = []

    record = append_grpo_metric(
        metrics,
        step=2,
        task="quantum_phase_estimation_circuit",
        domain="quantum",
        mean_reward=0.21,
        reward_std=0.11,
        reward_signal_std=0.12,
        curriculum_prob=0.4,
        task_ema_reward=0.21,
        task_seen=3,
        skipped=False,
        loss=0.037,
    )

    assert metrics == [record]
    assert "skipped" not in record
    assert record["loss"] == 0.037
    assert "reason" not in record


def test_append_grpo_metric_omits_skipped_key_for_update_rows() -> None:
    metrics: list[dict[str, object]] = []

    record = append_grpo_metric(
        metrics,
        step=3,
        task="quantum_phase_estimation_circuit",
        domain="quantum",
        mean_reward=0.31,
        reward_std=0.14,
        reward_signal_std=0.14,
        curriculum_prob=0.2,
        task_ema_reward=0.31,
        task_seen=2,
        skipped=False,
        loss=0.021,
    )

    assert metrics == [record]
    assert "skipped" not in record
    assert record["loss"] == 0.021
    assert "reason" not in record


def test_append_grpo_metric_jsonl_persists_multiple_records(tmp_path: Path) -> None:
    metrics_path = tmp_path / "grpo_step_metrics.jsonl"
    first = {
        "step": 1,
        "task": "quantum_qaoa_maxcut",
        "domain": "quantum",
        "skipped": True,
        "reason": "low_reward_signal",
    }
    second = {
        "step": 2,
        "task": "quantum_superdense_coding",
        "domain": "quantum",
        "loss": 0.0125,
    }

    append_grpo_metric_jsonl(metrics_path, first)
    append_grpo_metric_jsonl(metrics_path, second)

    rows = [
        json.loads(line)
        for line in metrics_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows == [first, second]


def test_main_removes_stale_grpo_metrics_before_early_abort(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "grpo-run"
    output_dir.mkdir(parents=True)
    stale_metrics = output_dir / "grpo_metrics.json"
    stale_metrics.write_text('{"stale": true}\n', encoding="utf-8")

    monkeypatch.setattr(
        grpo_trainer,
        "parse_args",
        lambda: Namespace(
            model_name="models/OmniCoder-9B",
            adapter_init=None,
            tasks_dir=str(tmp_path / "tasks"),
            benchmark_file=None,
            domain_filter=None,
            output_dir=str(output_dir),
            device="cpu",
            group_size=4,
            grpo_steps=1,
            lr=1e-5,
            kl_coeff=0.05,
            temperature=0.8,
            max_new_tokens=128,
            max_adaptive_new_tokens=128,
            max_seq_length=2048,
            log_steps=1,
            lora_rank=8,
            lora_alpha=16,
            reward_pass_weight=0.6,
            reward_syntax_weight=0.1,
            reward_interface_weight=0.15,
            reward_verifier_weight=0.15,
            reward_detail_budget_cap=8,
            advantage_clip=2.5,
            ratio_clip_log_delta=8.0,
            logit_clip=50.0,
            min_reward_std=0.05,
            curriculum_ema_decay=0.9,
            curriculum_min_weight=0.05,
            curriculum_uncertainty_bonus=0.35,
            research_methods=[],
            quantum_priority=1.5,
            resume_from=None,
            repair_sidecar_pidfile=None,
            repair_sidecar_log=None,
            repair_sidecar_max_log_age=300,
            reward_brevity_weight=0.0,
            brevity_target_lines=40,
            npu_device_map="balanced-layers",
            overwrite_output_dir=True,
        ),
    )
    monkeypatch.setattr(grpo_trainer, "load_research_methods", lambda _methods: [])
    monkeypatch.setattr(grpo_trainer, "discover_tasks", lambda *_args, **_kwargs: [])
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.delenv("WORLD_SIZE", raising=False)

    with pytest.raises(ValueError, match="No GRPO tasks matched the requested filters"):
        grpo_trainer.main()

    assert not stale_metrics.exists()


def test_main_removes_stale_run_config_before_early_abort(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "grpo-run"
    output_dir.mkdir(parents=True)
    stale_run_config = output_dir / "run_config.json"
    stale_run_config.write_text('{"stale": true}\n', encoding="utf-8")

    monkeypatch.setattr(
        grpo_trainer,
        "parse_args",
        lambda: Namespace(
            model_name="models/OmniCoder-9B",
            adapter_init=None,
            tasks_dir=str(tmp_path / "tasks"),
            benchmark_file=None,
            domain_filter=None,
            output_dir=str(output_dir),
            device="cpu",
            group_size=4,
            grpo_steps=1,
            lr=1e-5,
            kl_coeff=0.05,
            temperature=0.8,
            max_new_tokens=128,
            max_adaptive_new_tokens=128,
            max_seq_length=2048,
            log_steps=1,
            lora_rank=8,
            lora_alpha=16,
            reward_pass_weight=0.6,
            reward_syntax_weight=0.1,
            reward_interface_weight=0.15,
            reward_verifier_weight=0.15,
            reward_detail_budget_cap=8,
            advantage_clip=2.5,
            ratio_clip_log_delta=8.0,
            logit_clip=50.0,
            min_reward_std=0.05,
            curriculum_ema_decay=0.9,
            curriculum_min_weight=0.05,
            curriculum_uncertainty_bonus=0.35,
            research_methods=[],
            quantum_priority=1.5,
            resume_from=None,
            repair_sidecar_pidfile=None,
            repair_sidecar_log=None,
            repair_sidecar_max_log_age=300,
            reward_brevity_weight=0.0,
            brevity_target_lines=40,
            npu_device_map="balanced-layers",
            overwrite_output_dir=True,
        ),
    )
    monkeypatch.setattr(grpo_trainer, "load_research_methods", lambda _methods: [])
    monkeypatch.setattr(grpo_trainer, "discover_tasks", lambda *_args, **_kwargs: [])
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.delenv("WORLD_SIZE", raising=False)

    with pytest.raises(ValueError, match="No GRPO tasks matched the requested filters"):
        grpo_trainer.main()

    assert not stale_run_config.exists()


def test_resume_adapter_consistency_rejects_older_checkpoint_pairing() -> None:
    """2026-08-24 bug-hunt: --adapter-init was never cross-validated against
    --resume-from. A step_NNNNNN_adapter older than the resume metrics' latest
    step would silently skip the recorded updates between them (resume_step
    gate) while continuing with stale weights — a silent policy rewind."""
    err = grpo_trainer.validate_resume_adapter_consistency(
        "outputs/sapo-run/step_000003_adapter", 10
    )
    assert err is not None
    assert "step 3" in err and "step 10" in err
    # Same step and newer checkpoints are fine.
    assert (
        grpo_trainer.validate_resume_adapter_consistency("outputs/sapo-run/step_000010_adapter", 10)
        is None
    )
    assert (
        grpo_trainer.validate_resume_adapter_consistency("outputs/sapo-run/step_000012_adapter", 10)
        is None
    )
    # Non-step adapters (warm distillation adapter) stay allowed with resume
    # records (deliberate re-warm strategy); no resume / no adapter is fine.
    assert (
        grpo_trainer.validate_resume_adapter_consistency("outputs/qg-27b-warm/adapter", 10) is None
    )
    assert grpo_trainer.validate_resume_adapter_consistency(None, 10) is None
    assert grpo_trainer.validate_resume_adapter_consistency("step_000003_adapter", 0) is None


def test_main_raises_on_inconsistent_resume_pairing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The main() entrypoint must refuse an adapter-init older than the resume
    metrics instead of silently skipping steps with stale weights."""
    output_dir = tmp_path / "grpo-run"
    output_dir.mkdir(parents=True)
    metrics_file = tmp_path / "prior.jsonl"
    metrics_file.write_text(
        '{"step": 10, "task": "quantum_a", "pass_rate": 0.5, "mean_reward": 0.1, '
        '"reward_std": 0.1, "task_ema_reward": 0.1, "task_seen": 1, "skipped": false}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        grpo_trainer,
        "parse_args",
        lambda: Namespace(
            model_name="models/OmniCoder-9B",
            adapter_init=str(tmp_path / "step_000003_adapter"),
            tasks_dir=str(tmp_path / "tasks"),
            benchmark_file=None,
            domain_filter=None,
            output_dir=str(output_dir),
            device="cpu",
            group_size=4,
            grpo_steps=1,
            lr=1e-5,
            kl_coeff=0.05,
            temperature=0.8,
            max_new_tokens=128,
            max_adaptive_new_tokens=128,
            max_seq_length=2048,
            log_steps=1,
            lora_rank=8,
            lora_alpha=16,
            reward_pass_weight=0.6,
            reward_syntax_weight=0.1,
            reward_interface_weight=0.15,
            reward_verifier_weight=0.15,
            reward_detail_budget_cap=8,
            advantage_clip=2.5,
            ratio_clip_log_delta=8.0,
            logit_clip=50.0,
            min_reward_std=0.05,
            curriculum_ema_decay=0.9,
            curriculum_min_weight=0.05,
            curriculum_uncertainty_bonus=0.35,
            research_methods=[],
            quantum_priority=1.5,
            resume_from=str(metrics_file),
            repair_sidecar_pidfile=None,
            repair_sidecar_log=None,
            repair_sidecar_max_log_age=300,
            reward_brevity_weight=0.0,
            brevity_target_lines=40,
            npu_device_map="balanced-layers",
            overwrite_output_dir=True,
        ),
    )
    monkeypatch.setattr(grpo_trainer, "load_research_methods", lambda _methods: [])
    monkeypatch.setattr(grpo_trainer, "discover_tasks", lambda *_args, **_kwargs: [])
    monkeypatch.delenv("RANK", raising=False)
    monkeypatch.delenv("LOCAL_RANK", raising=False)
    monkeypatch.delenv("WORLD_SIZE", raising=False)

    with pytest.raises(ValueError, match="older than the --resume-from metrics"):
        grpo_trainer.main()


# ---------------------------------------------------------------------------
# Training-log instrumentation (user requirement 2026-08-25): every training
# step must document EVERY training loss value (per-candidate loss_i with n_i
# token counts + the aggregate), the loss reduction (machine- + human-readable),
# and the reward scores of ALL rollout samples; plus the in-loop zero-change
# gate (a 0-change adapter vs base after an optimizer step is unacceptable).
# ---------------------------------------------------------------------------


def _instrumented_step_ctx(**overrides: object) -> dict[str, object]:
    ctx: dict[str, object] = {
        "step": 1,
        "task_name": "quantum_qaoa_maxcut",
        "domain": "quantum",
        "mean_reward": 0.3333,
        "signal_stats": {"reward_std": 0.12, "signal_std": 0.12},
        "task_prob": 0.5,
        "task_state": {"ema_reward": 0.3333, "seen": 1.0},
        "rollout_rewards": [
            {
                "index": 0,
                "total_reward": 0.4,
                "shaped_reward": 0.4,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": 0.05,
                "n_tokens": 512,
            },
            {
                "index": 1,
                "total_reward": 0.3,
                "shaped_reward": 0.3,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": -0.02,
                "n_tokens": 480,
            },
            {
                "index": 2,
                "total_reward": 0.0,
                "shaped_reward": 0.0,
                "pass": False,
                "pass_reward": 0.0,
                "advantage": -0.1,
                "n_tokens": 0,
            },
            {
                "index": 3,
                "total_reward": 0.5,
                "shaped_reward": 0.5,
                "pass": True,
                "pass_reward": 1.0,
                "advantage": 0.1,
                "n_tokens": 301,
            },
        ],
        "loss_reduction": (
            "per-candidate token-mean SAPO losses, equal per-candidate weights "
            "w_i = 1/G (length-neutral; NOT n_i/N token weighting), gradients "
            "accumulated via per-candidate backward"
        ),
    }
    ctx.update(overrides)
    return ctx


def _instrumented_per_candidate_losses() -> list[dict[str, object]]:
    return [
        {
            "index": 0,
            "n_tokens": 512,
            "weight": 0.25,
            "loss": 0.11,
            "advantage": 0.05,
            "sapo_gate_mean": 2.0,
        },
        {
            "index": 1,
            "n_tokens": 480,
            "weight": 0.25,
            "loss": 0.09,
            "advantage": -0.02,
            "sapo_gate_mean": 1.905,
        },
        {
            "index": 2,
            "n_tokens": 0,
            "weight": None,
            "loss": None,
            "advantage": -0.1,
            "excluded_reason": "zero_token_completion",
        },
        {
            "index": 3,
            "n_tokens": 301,
            "weight": 0.25,
            "loss": 0.14,
            "advantage": 0.1,
            "sapo_gate_mean": 2.003,
        },
    ]


def _instrumented_record(**overrides: object) -> dict[str, object]:
    """A complete updated-step record exercising every instrumentation field."""
    ctx = _instrumented_step_ctx()
    kwargs: dict[str, object] = {
        "step": int(ctx["step"]),
        "task_name": str(ctx["task_name"]),
        "domain": str(ctx["domain"]),
        "mean_reward": float(ctx["mean_reward"]),
        "signal_stats": ctx["signal_stats"],  # type: ignore[arg-type]
        "pass_rate": 0.25,
        "syntax_rate": 0.75,
        "interface_rate": 0.5,
        "verifier_rate": 0.5,
        "task_prob": float(ctx["task_prob"]),
        "task_state": ctx["task_state"],  # type: ignore[arg-type]
        "skipped": False,
        "loss": 0.085,
        "rollout_rewards": ctx["rollout_rewards"],  # type: ignore[arg-type]
        "loss_reduction": str(ctx["loss_reduction"]),
        "per_candidate_losses": _instrumented_per_candidate_losses(),
        "loss_breakdown": {
            "loss_mode": "sapo",
            "loss": 0.085,
            "loss_recomputed": 0.085,
            "candidate_count": 3,
            "loss_candidate_count": 3,
            "weighted_token_total": 1293.0,
            "reduction": "per_candidate_1_over_g",
            "dr_pair_loss_added": False,
            "dr_variance_correction_added": False,
        },
    }
    kwargs.update(overrides)
    return build_grpo_step_record(**kwargs)  # type: ignore[arg-type]


def test_step_record_persists_per_candidate_losses_and_rewards_for_all_candidates() -> None:
    """Requirement 1+3: the step record carries EVERY per-candidate loss_i with
    n_i token counts AND the reward scores of all rollout samples (raw reward,
    shaped reward, pass/fail, advantage), aligned 1:1 with candidate order —
    including zero-token candidates."""
    record = _instrumented_record()

    per_candidate = record["per_candidate_losses"]
    assert [int(entry["index"]) for entry in per_candidate] == [0, 1, 2, 3]
    assert [float(entry["n_tokens"]) for entry in per_candidate] == [512, 480, 0, 301]
    assert [float(entry["loss"]) for entry in per_candidate[:2]] == [
        pytest.approx(0.11),
        pytest.approx(0.09),
    ]
    assert [float(entry["loss"]) for entry in per_candidate[3:]] == [pytest.approx(0.14)]
    # zero-token candidate: explicitly marked, never a crash
    assert per_candidate[2]["n_tokens"] == 0
    assert per_candidate[2]["loss"] is None
    assert per_candidate[2]["excluded_reason"] == "zero_token_completion"
    # every candidate's advantage is logged next to its loss
    assert [float(entry["advantage"]) for entry in per_candidate] == [
        pytest.approx(0.05),
        pytest.approx(-0.02),
        pytest.approx(-0.1),
        pytest.approx(0.1),
    ]

    rollout = record["rollout_rewards"]
    assert len(rollout) == 4
    assert [int(entry["index"]) for entry in rollout] == [0, 1, 2, 3]
    assert rollout[0]["total_reward"] == pytest.approx(0.4)
    assert rollout[0]["shaped_reward"] == pytest.approx(0.4)
    assert rollout[0]["pass"] is False
    assert rollout[0]["advantage"] == pytest.approx(0.05)
    assert rollout[3]["pass"] is True
    assert rollout[2]["n_tokens"] == 0  # zero-token candidate still scored


def test_logged_aggregate_loss_matches_documented_reduction() -> None:
    """Requirement 2: the logged aggregate equals the documented reduction —
    the weighted sum of the per-candidate means (Σ w_i·loss_i, w_i = 1/G),
    within fp tolerance. The math auditor recomputes this identity from the
    record."""
    per_candidate = _instrumented_per_candidate_losses()
    expected = 0.25 * 0.11 + 0.25 * 0.09 + 0.25 * 0.14

    recomputed = grpo_trainer.recompute_aggregate_sapo_loss(per_candidate)
    assert recomputed == pytest.approx(expected)

    record = _instrumented_record()
    assert record["loss_breakdown"]["loss_recomputed"] == pytest.approx(expected)
    assert record["loss"] == pytest.approx(expected)
    # the auditor's identity: recompute from the persisted list == recorded loss
    assert grpo_trainer.recompute_aggregate_sapo_loss(
        record["per_candidate_losses"]
    ) == pytest.approx(record["loss"])


def test_step_record_has_loss_reduction_field_on_updated_and_skipped() -> None:
    """Requirement 2: an explicit loss_reduction field documents HOW the loss
    is reduced/aggregated, present on every step record — updated steps carry
    the path description, skipped steps carry it with a skip marker."""
    record = _instrumented_record()
    assert "loss_reduction" in record
    assert len(str(record["loss_reduction"])) > 20
    assert "per-candidate" in str(record["loss_reduction"])

    skipped = build_grpo_step_record(
        step=2,
        task_name="quantum_ghz",
        domain="quantum",
        mean_reward=0.0,
        signal_stats={"reward_std": 0.0, "signal_std": 0.0},
        pass_rate=0.0,
        syntax_rate=0.0,
        interface_rate=0.0,
        verifier_rate=0.0,
        task_prob=0.25,
        task_state={"ema_reward": 0.0, "seen": 2.0},
        skipped=True,
        reason="repair_sft_queued",
        loss_reduction="batched GSPO sequence-level clipped surrogate, single total_loss.backward()",
    )
    assert "loss_reduction" in skipped
    # the emit funnel appends the explicit no-loss marker on skipped records
    # (asserted in test_emit_step_record_writes_greppable_compact_line_and_jsonl);
    # the builder itself stays pure.


def test_emit_step_record_writes_greppable_compact_line_and_jsonl(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The train log gets a compact single line per step (grep-able via
    loss_breakdown=), and the jsonl stays parseable line-by-line."""
    metrics: list[dict[str, object]] = []
    path = tmp_path / "grpo_step_metrics.jsonl"
    grpo_trainer.emit_step_record(
        rank=0,
        metrics=metrics,
        step_metrics_path=path,
        log_steps=5,
        ctx=_instrumented_step_ctx(),
        skipped=True,
        reason="low_reward_signal",
    )
    out = capsys.readouterr().out
    compact_lines = [line for line in out.splitlines() if line.startswith("loss_breakdown=")]
    assert len(compact_lines) == 1
    compact = compact_lines[0]
    assert compact.startswith("loss_breakdown=step:1 skipped:1")
    assert "loss:NA" in compact
    assert "rewards:[0.4,0.3,0,0.5]" in compact
    assert "advantages:[0.05,-0.02,-0.1,0.1]" in compact

    parsed = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(parsed) == 1
    assert parsed[0]["step"] == 1
    assert parsed[0]["skipped"] is True
    assert "[skipped: no loss computed this step]" in parsed[0]["loss_reduction"]
    assert parsed[0]["rollout_rewards"][0]["total_reward"] == pytest.approx(0.4)


def test_emit_step_record_updated_compact_line_reports_loss_and_recomputed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Updated steps' compact line reports the loss value, the recomputed
    aggregate, and the per-candidate losses + token counts."""
    metrics: list[dict[str, object]] = []
    path = tmp_path / "grpo_step_metrics.jsonl"
    record = _instrumented_record()
    grpo_trainer.emit_step_record(
        rank=0,
        metrics=metrics,
        step_metrics_path=path,
        log_steps=5,
        ctx=_instrumented_step_ctx(),
        skipped=False,
        loss=float(record["loss"]),
        per_candidate_losses=record["per_candidate_losses"],
        loss_breakdown=record["loss_breakdown"],
        lora_b_max_delta=1e-4,
        zero_change_alarm=False,
    )
    out = capsys.readouterr().out
    compact = next(line for line in out.splitlines() if line.startswith("loss_breakdown="))
    assert "loss:0.085" in compact
    assert "recomputed:0.085" in compact
    assert "per_candidate:[0.11,0.09,NA,0.14]" in compact
    assert "n_tokens:[512,480,0,301]" in compact
    assert "zero_change_alarm:false" in compact


def test_zero_token_candidates_do_not_crash_record_emit(tmp_path: Path) -> None:
    """Requirement: zero-token/empty candidates are logged explicitly
    (n_tokens=0, loss=None, marked) and never crash the record emit — the
    jsonl stays parseable."""
    metrics: list[dict[str, object]] = []
    path = tmp_path / "grpo_step_metrics.jsonl"
    per_candidate = _instrumented_per_candidate_losses()
    per_candidate[1] = {
        "index": 1,
        "n_tokens": 0,
        "weight": None,
        "loss": None,
        "advantage": -0.02,
        "excluded_reason": "zero_token_completion",
    }
    grpo_trainer.emit_step_record(
        rank=0,
        metrics=metrics,
        step_metrics_path=path,
        log_steps=5,
        ctx=_instrumented_step_ctx(),
        skipped=False,
        loss=0.085,
        per_candidate_losses=per_candidate,
        loss_breakdown={
            "loss_mode": "sapo",
            "loss": 0.085,
            "loss_recomputed": 0.085,
            "reduction": "per_candidate_1_over_g",
        },
    )
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert len(rows) == 1
    entry = rows[0]["per_candidate_losses"][1]
    assert entry["n_tokens"] == 0
    assert entry["loss"] is None
    assert entry["excluded_reason"] == "zero_token_completion"


def test_step_metrics_jsonl_parses_line_by_line(tmp_path: Path) -> None:
    """Requirement: the record must stay jsonl-parseable per line — the full
    instrumented record round-trips through the jsonl without corrupting
    line boundaries (no embedded newlines in the field values)."""
    path = tmp_path / "grpo_step_metrics.jsonl"
    record = _instrumented_record()
    append_grpo_metric_jsonl(path, record)
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["step"] == record["step"]
    assert len(parsed["rollout_rewards"]) == 4
    assert len(parsed["per_candidate_losses"]) == 4
    assert (
        parsed["loss_breakdown"]["loss_recomputed"] == record["loss_breakdown"]["loss_recomputed"]
    )
    assert parsed["loss_reduction"] == record["loss_reduction"]


def test_build_rollout_rewards_aligned_with_candidate_order() -> None:
    """rollout_rewards is built aligned 1:1 with the rollout candidate order,
    carrying raw reward, shaped reward, pass/fail, advantage, token counts and
    repair-lane annotations when present."""
    evaluations = [
        {
            "total_reward": 0.4,
            "shaped_reward": 0.4,
            "pass_reward": 0.0,
            "self_repair_passed": False,
        },
        {"total_reward": 0.3, "shaped_reward": 0.3, "pass_reward": 0.0},
        {"total_reward": 0.0, "shaped_reward": 0.0, "pass_reward": 0.0},
        {"total_reward": 0.5, "shaped_reward": 0.5, "pass_reward": 1.0},
    ]
    advantages = torch.tensor([0.05, -0.02, -0.1, 0.1])
    rewards = grpo_trainer.build_rollout_rewards(
        evaluations, advantages, completion_token_lengths=[512, 480, 0, 301]
    )
    assert [int(entry["index"]) for entry in rewards] == [0, 1, 2, 3]
    assert rewards[0]["total_reward"] == pytest.approx(0.4)
    assert rewards[0]["shaped_reward"] == pytest.approx(0.4)
    assert rewards[0]["pass"] is False
    assert rewards[0]["advantage"] == pytest.approx(0.05)
    assert rewards[0]["n_tokens"] == 512
    assert rewards[2]["n_tokens"] == 0
    assert rewards[3]["pass"] is True
    assert rewards[3]["advantage"] == pytest.approx(0.1)
    assert rewards[0]["self_repair_passed"] is False
    assert "self_repair_passed" not in rewards[1]


def test_zero_change_gate_fires_on_exact_zero_lora_b_delta() -> None:
    """User directive 2026-08-25: a 0-change adapter (max|Δlora_B| == 0.0
    exactly after an optimizer step) is unacceptable — the gate must fire on
    an exact zero, not a tolerance. Simulated zero-grad step."""
    param = torch.nn.Parameter(torch.zeros(4, 4))
    snapshot = grpo_trainer.collect_lora_b_init_snapshot(
        ["model.layers.0.self_attn.q_proj.lora_B.default"], [param]
    )
    assert list(snapshot) == ["model.layers.0.self_attn.q_proj.lora_B.default"]
    optimizer = torch.optim.AdamW([param], lr=1e-4)
    param.grad = torch.zeros_like(param)  # zero gradient -> zero change
    optimizer.step()
    delta = grpo_trainer.measure_lora_b_max_delta(
        snapshot, {"model.layers.0.self_attn.q_proj.lora_B.default": param}
    )
    assert delta == 0.0
    assert grpo_trainer.zero_change_gate_fired(delta) is True


def test_zero_change_gate_does_not_fire_when_lora_b_moves() -> None:
    """A real optimizer step moves lora_B -> delta > 0 -> no alarm; when no
    lora_B parameter is tracked the gate is a silent no-op (None), never a
    false alarm."""
    param = torch.nn.Parameter(torch.zeros(4, 4))
    snapshot = grpo_trainer.collect_lora_b_init_snapshot(["lora_B"], [param])
    optimizer = torch.optim.AdamW([param], lr=1e-3)
    param.grad = torch.ones_like(param)
    optimizer.step()
    delta = grpo_trainer.measure_lora_b_max_delta(snapshot, {"lora_B": param})
    assert delta > 0.0
    assert grpo_trainer.zero_change_gate_fired(delta) is False
    assert grpo_trainer.zero_change_gate_fired(None) is False
    assert grpo_trainer.collect_lora_b_init_snapshot(["lora_A"], [param]) == {}


def test_lora_b_zero_change_alarm_persisted_in_step_record() -> None:
    """The per-step lora_B max delta and the zero_change_alarm +
    recommend-stop marker land in the step record; legacy records without the
    fields stay parseable."""
    record = _instrumented_record(
        lora_b_max_delta=0.0,
        zero_change_alarm=True,
        zero_change_recommend_stop=True,
    )
    assert record["lora_b_max_delta"] == 0.0
    assert record["zero_change_alarm"] is True
    assert record["zero_change_recommend_stop"] is True

    plain = _instrumented_record()
    assert "zero_change_alarm" not in plain
    assert "lora_b_max_delta" not in plain
