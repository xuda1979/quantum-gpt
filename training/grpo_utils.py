from __future__ import annotations

import ast
import json
import math
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch

from training.compat import strict_zip

# ---------------------------------------------------------------------------
# Comprehensive model-verifier score (frozen judge)
#
# The user requirement: the base model (and later, older accepted adapters)
# act as a frozen evaluator giving per-dimension scores on samples. Executable
# tests stay authoritative (P dominates); model dimensions are calibrated
# against executable anchors and start at zero reward weight.
# ---------------------------------------------------------------------------

MODEL_JUDGE_DIMENSIONS = (
    "correctness",
    "runnability",
    "result_correctness",
    "efficiency",
    "quality",
)
MAX_MODEL_JUDGE_WEIGHT = 0.05
MODEL_JUDGE_CALIBRATION_AUC = 0.85
MODEL_JUDGE_CALIBRATION_RHO = 0.6
MODEL_JUDGE_CALIBRATION_MIN_N = 200


def judge_composite_score(
    model_dim_scores: Mapping[str, float],
    dim_weights: Mapping[str, float],
) -> float:
    """The judge's weighted composite J used by ``blend_comprehensive_reward``.

    2026-08-26 (r16 judge wave): single source of truth for the model term —
    the same clamp + renormalization the blend applies. The per-candidate
    record stores this exact value (``judge_reward``) so the reward verifier
    can recompute the 3-way blend without duplicating the formula.
    """
    weights = {
        dim: min(MAX_MODEL_JUDGE_WEIGHT, max(0.0, float(dim_weights.get(dim, 0.0))))
        for dim in MODEL_JUDGE_DIMENSIONS
    }
    weight_sum = sum(weights.values())
    if weight_sum <= 0.0:
        return 0.0
    return sum(
        (weights[dim] / weight_sum)
        * min(1.0, max(0.0, float(model_dim_scores.get(dim, 0.0) or 0.0)))
        for dim in MODEL_JUDGE_DIMENSIONS
    )


def blend_comprehensive_reward(
    *,
    pass_reward: float,
    shaped_reward: float,
    model_dim_scores: Mapping[str, float],
    dim_weights: Mapping[str, float],
    truncation_penalty: float = 0.0,
    mode: str = "p_dominant",
    pass_mass: float = 0.50,
    shaped_mass: float = 0.40,
    judge_mass: float = 0.10,
) -> float:
    """Blend executable and frozen-judge signals into one reward.

    ``mode="p_dominant"`` (the FV-GSPO default / ablation baseline):

        R = P + (1 - P) * [ (1 - W) * S + W * mean(w_d * M_d) ] - T

        P (full test pass) always dominates: failing candidates can never
        outrank passing ones, and judge mass (W <= 0.05) is subtracted from the
        shaped term, never from P.

    ``mode="comprehensive"`` (user decision 2026-08-05 — the reward should NOT
    be executable-dominated):

        R = w_P * P + w_S * S + w_J * J - T,   w_P + w_S + w_J = 1

        with recommended masses (research memo 2026-08-26, r17)
        w_P=0.50, w_S=0.40, w_J=0.10. J is the frozen judge's composite
        (relative weights over the calibrated dimensions). The judge mass is
        active ONLY when at least one dimension passed calibration (an
        ACTIVE UNCALIBRATED judge injects ~0.5±noise into the advantages);
        until then the masses are renormalized over P and S and the judge
        contributes exactly 0. A failing candidate CAN outrank a passing one
        when its shaped/judge scores are high enough — that is the point of
        the comprehensive mode; the judge is evidence-anchored and
        calibration-gated so it does not contradict executable evidence.

    ``mode="tiered"`` (review 2026-08-05 #5 — recommended): a constrained
    hierarchy that keeps execution authoritative while the reward is rich:

        R = (1-P) * min(0.95, Q_progress)  +  P * (1 + alpha*Q_efficiency + gamma*Q_quality)

    - any passing candidate outranks any failing candidate (hard tier);
    - all-fail groups still get learnable partial-progress signal;
    - passing candidates are differentiated by efficiency and quality
      (frozen-judge dims, only when calibrated);
    - resource optimization cannot be achieved by deleting required compute
      (passing is gated on full semantic pass).

    Model dimension scores are clamped to [0, 1] in all modes.
    """
    bounded_pass = min(1.0, max(0.0, float(pass_reward)))
    bounded_shaped = min(1.0, max(0.0, float(shaped_reward)))
    # 2026-08-26 (r16): the model term is computed by the shared helper so the
    # recorded per-candidate judge_reward is EXACTLY the blend's term.
    weight_sum = sum(
        min(MAX_MODEL_JUDGE_WEIGHT, max(0.0, float(dim_weights.get(dim, 0.0))))
        for dim in MODEL_JUDGE_DIMENSIONS
    )
    model_term = judge_composite_score(model_dim_scores, dim_weights)
    penalty = min(1.0, max(0.0, float(truncation_penalty)))
    if mode == "tiered":
        q_progress = min(0.95, max(0.0, bounded_shaped - penalty))
        if bounded_pass >= 1.0:
            efficiency = min(1.0, max(0.0, float(model_dim_scores.get("efficiency", 0.0) or 0.0)))
            quality = min(1.0, max(0.0, float(model_dim_scores.get("quality", 0.0) or 0.0)))
            alpha = max(0.0, float(pass_mass))
            gamma = max(0.0, float(shaped_mass))
            return min(2.0, 1.0 + alpha * efficiency + gamma * quality)
        return q_progress
    if mode == "comprehensive":
        bounded_pass_mass = max(0.0, float(pass_mass))
        bounded_shaped_mass = max(0.0, float(shaped_mass))
        if weight_sum > 0.0:
            # 2026-09-01 (ADVERSARIAL-JUDGE lane): the judge mass is BOUNDED.
            # (a) [0,1] — w_J is a fraction of the unit blend (w_P+w_S+w_J=1);
            #     a typo like --reward-judge-mass 2.0 used to renormalize to a
            #     ~55% judge share and dominate pass (2.0/(0.5+0.4+2.0)).
            # (b) the residual mass (1 - w_P - w_S) — enforces the documented
            #     sum-to-one contract.
            # (c) the executable-pass mass — the judge alone can NEVER decide
            #     a pass: P=0,S=0 with a perfect J stays below the P=1
            #     candidate regardless of misconfiguration (the blend mirrors
            #     the prompt's executable anchor). All documented masses
            #     (0.50/0.40/0.10) pass through untouched.
            effective_judge = min(
                max(0.0, min(1.0, float(judge_mass))),
                max(0.0, 1.0 - bounded_pass_mass - bounded_shaped_mass),
                bounded_pass_mass,
            )
        else:
            effective_judge = 0.0
        total_mass = max(1e-8, bounded_pass_mass + bounded_shaped_mass + effective_judge)
        reward = (
            bounded_pass_mass / total_mass * bounded_pass
            + bounded_shaped_mass / total_mass * bounded_shaped
            + effective_judge / total_mass * model_term
            - penalty
        )
        return min(1.0, max(0.0, reward))
    total_w = min(weight_sum, MAX_MODEL_JUDGE_WEIGHT)
    reward = (
        bounded_pass
        + (1.0 - bounded_pass) * ((1.0 - total_w) * bounded_shaped + total_w * model_term)
        - penalty
    )
    return min(1.0, max(0.0, reward))


def _build_grpo_metric_record(
    *,
    step: int,
    task: str,
    domain: str,
    mean_reward: float,
    reward_std: float,
    reward_signal_std: float,
    curriculum_prob: float,
    task_ema_reward: float,
    task_seen: int,
    skipped: bool,
    pass_rate: float | None = None,
    syntax_rate: float | None = None,
    interface_rate: float | None = None,
    verifier_rate: float | None = None,
    pass_std: float | None = None,
    syntax_std: float | None = None,
    interface_std: float | None = None,
    verifier_std: float | None = None,
    advantage_scale: float | None = None,
    reason: str | None = None,
    loss: float | None = None,
    adapter_init: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "task": task,
        "domain": domain,
        "mean_reward": mean_reward,
        "reward_std": reward_std,
        "reward_signal_std": reward_signal_std,
        "curriculum_prob": curriculum_prob,
        "task_ema_reward": task_ema_reward,
        "task_seen": task_seen,
    }
    if skipped:
        record["skipped"] = True
    optional_fields = {
        "pass_rate": pass_rate,
        "syntax_rate": syntax_rate,
        "interface_rate": interface_rate,
        "verifier_rate": verifier_rate,
        "pass_std": pass_std,
        "syntax_std": syntax_std,
        "interface_std": interface_std,
        "verifier_std": verifier_std,
        "advantage_scale": advantage_scale,
        "reason": reason,
        "loss": loss,
        "adapter_init": adapter_init,
    }
    for key, value in optional_fields.items():
        if value is not None:
            record[key] = value
    return record


def append_grpo_metric(
    metrics: list[dict[str, Any]],
    record: Mapping[str, Any] | None = None,
    **record_kwargs: Any,
) -> dict[str, Any]:
    persisted = dict(record) if record is not None else _build_grpo_metric_record(**record_kwargs)
    metrics.append(persisted)
    return persisted


def append_grpo_metric_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), sort_keys=True) + "\n")


def load_grpo_step_metrics_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(json.loads(line))
    return records


def build_grpo_metrics_payload_from_jsonl(path: Path, *, planned_steps: int) -> dict[str, Any]:
    return build_grpo_metrics_payload(
        load_grpo_step_metrics_jsonl(path), planned_steps=planned_steps
    )


def build_grpo_step_record(
    *,
    step: int,
    task_name: str,
    domain: str,
    mean_reward: float,
    signal_stats: dict[str, float],
    mean_shaped_reward: float | None = None,
    pass_rate: float | None,
    syntax_rate: float | None,
    interface_rate: float | None,
    verifier_rate: float | None,
    task_prob: float,
    task_state: dict[str, float],
    advantage_scale: float | None = None,
    loo_advantage_rms: float | None = None,
    loo_advantage_mean_abs: float | None = None,
    update_signal_magnitude: float | None = None,
    update_signal_kind: str | None = None,
    update_signal_threshold: float | None = None,
    skipped: bool = False,
    reason: str | None = None,
    loss: float | None = None,
    adapter_init: str | None = None,
    self_eval_rate: float | None = None,
    route: str | None = None,
    ratio_mean: float | None = None,
    clip_low_fraction: float | None = None,
    clip_high_fraction: float | None = None,
    seq_kl: float | None = None,
    entropy_mean: float | None = None,
    generation_tokens: int | None = None,
    repair_queued: bool | None = None,
    # Guardian alarm 8 (2026-08-26): per-step flag recorded from the
    # sidecar-liveness guard (training/sidecar_liveness.py). False/None when
    # the repair sidecar is dead or unprovable — ops must see this in
    # grpo_step_metrics.jsonl instead of a silent queue starvation.
    sidecar_alive: bool | None = None,
    all_fail: bool | None = None,
    frontier_fraction: float | None = None,
    breaker_trips: list[dict[str, Any]] | None = None,
    model_dim_scores: dict[str, float] | None = None,
    model_judge_enabled: bool | None = None,
    posterior_lower: float | None = None,
    posterior_upper: float | None = None,
    flaky: bool | None = None,
    group_size: int | None = None,
    # 2026-08-26 (r10, greedy-augmented rollouts): how many of the group's
    # candidates were generated at temperature 0 (greedy argmax) and graded
    # through the same harness/reward path.
    greedy_count: int | None = None,
    # Derived step-record fields. These MUST be passed here (before the record
    # is appended) — the trainer used to mutate the returned record after
    # emit_step_record() had already written the JSONL, silently dropping them
    # from grpo_step_metrics.jsonl (2026-08-22 audit #1/#2).
    mean_response_length: float | None = None,
    truncation_rate: float | None = None,
    eos_termination_rate: float | None = None,
    # 2026-08-26 (r10, router lane): True when the EOS-collapse rescue alarm
    # fired on this step (3rd consecutive step with entropy < 0.05 and ~1-token
    # completions). The behavior temperature was escalated immediately —
    # before repair-routing — as the run-6 killer's rescue path.
    degenerate_policy_alarm: bool | None = None,
    # 2026-08-27 (T1a, router lane): True when the collapse gate suppressed
    # repair-routing on this step (degenerate alarm, or stub-collapse
    # completions, or entropy below the degenerate floor). No repair record
    # was written; the task stayed in the RL targeted pool.
    quarantine_suppressed: bool | None = None,
    # 2026-08-26 (r10, rollout lane): the 3-way stop-reason breakdown.
    # fence_termination_rate = share of completions that closed a code
    # fence; cap_run_with_fence_opener_rate = share of TRUNCATED completions
    # whose raw text still contains a fence opener (the fence-stop-regression
    # class — the stop regex missed a fence the extraction still sees).
    fence_termination_rate: float | None = None,
    cap_run_with_fence_opener_rate: float | None = None,
    completion_token_lengths: list[int] | None = None,
    raw_response_chars: list[int] | None = None,
    extracted_code_chars: list[int] | None = None,
    generation_token_budget: int | None = None,
    trust_region_violated: bool | None = None,
    lr: float | None = None,
    trust_region_violation_count: int | None = None,
    ratio_after_update: float | None = None,
    clip_fraction_after_update: float | None = None,
    seq_kl_after: float | None = None,
    old_policy_age: int | None = None,
    optimizer_substeps_per_rollout: int | None = None,
    gradient_norms: list[float] | None = None,
    inner_early_stop_reason: str | None = None,
    sapo_per_candidate_stats: list[dict[str, float]] | None = None,
    kl_beta: float | None = None,
    dr_pair_mined: bool | None = None,
    dr_pair_reward_gap: float | None = None,
    dr_pair_loss_value: float | None = None,
    dr_pair_loss_weight: float | None = None,
    dr_variance_correction_value: float | None = None,
    dr_psi: float | None = None,
    dr_psi_init: float | None = None,
    dr_psi_warmup_steps: int | None = None,
    dr_psi_current_step: int | None = None,
    # ── training-log instrumentation (2026-08-25, user requirement) ──
    # Every step record must document every training loss value, the loss
    # reduction, the reward scores of ALL rollout samples, and the zero-change
    # gate status. Field-name stability is part of the contract: the math
    # auditor (reports/sapo-training-math-audit-2026-08-24.md) recomputes the
    # blend/loss identity from these exact keys.
    rollout_rewards: list[dict[str, Any]] | None = None,
    loss_reduction: str | None = None,
    per_candidate_losses: list[dict[str, Any]] | None = None,
    loss_breakdown: dict[str, Any] | None = None,
    lora_b_max_delta: float | None = None,
    zero_change_alarm: bool | None = None,
    zero_change_recommend_stop: bool | None = None,
) -> dict[str, float | int | bool | str]:
    record: dict[str, float | int | bool | str] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "task": task_name,
        "domain": domain,
        "mean_reward": mean_reward,
        "reward_std": float(signal_stats["reward_std"]),
        "reward_signal_std": float(signal_stats["signal_std"]),
        "curriculum_prob": task_prob,
        "task_ema_reward": float(task_state["ema_reward"]),
        "task_seen": int(task_state["seen"]),
    }
    if pass_rate is not None:
        record["pass_rate"] = pass_rate
    if mean_shaped_reward is not None:
        record["mean_shaped_reward"] = float(mean_shaped_reward)
    if syntax_rate is not None:
        record["syntax_rate"] = syntax_rate
    if interface_rate is not None:
        record["interface_rate"] = interface_rate
    if verifier_rate is not None:
        record["verifier_rate"] = verifier_rate
    if "pass_std" in signal_stats:
        record["pass_std"] = float(signal_stats["pass_std"])
    if "syntax_std" in signal_stats:
        record["syntax_std"] = float(signal_stats["syntax_std"])
    if "interface_std" in signal_stats:
        record["interface_std"] = float(signal_stats["interface_std"])
    if "verifier_std" in signal_stats:
        record["verifier_std"] = float(signal_stats["verifier_std"])
    if advantage_scale is not None:
        record["advantage_scale"] = advantage_scale
    if loo_advantage_rms is not None:
        record["loo_advantage_rms"] = float(loo_advantage_rms)
    if loo_advantage_mean_abs is not None:
        record["loo_advantage_mean_abs"] = float(loo_advantage_mean_abs)
    if update_signal_magnitude is not None:
        record["update_signal_magnitude"] = float(update_signal_magnitude)
    if update_signal_kind is not None:
        record["update_signal_kind"] = str(update_signal_kind)
    if update_signal_threshold is not None:
        record["update_signal_threshold"] = float(update_signal_threshold)
    if skipped:
        record["skipped"] = True
        if reason is not None:
            record["reason"] = reason
    if loss is not None:
        record["loss"] = loss
    if adapter_init is not None:
        record["adapter_init"] = adapter_init
    if self_eval_rate is not None:
        record["self_eval_rate"] = self_eval_rate
    if route is not None:
        record["route"] = route
    if ratio_mean is not None:
        record["ratio_mean"] = ratio_mean
    if clip_low_fraction is not None:
        record["clip_low_fraction"] = clip_low_fraction
    if clip_high_fraction is not None:
        record["clip_high_fraction"] = clip_high_fraction
    if seq_kl is not None:
        record["seq_kl"] = seq_kl
    if entropy_mean is not None:
        record["entropy_mean"] = entropy_mean
    if generation_tokens is not None:
        record["generation_tokens"] = generation_tokens
    if repair_queued is not None:
        record["repair_queued"] = repair_queued
    if sidecar_alive is not None:
        record["sidecar_alive"] = bool(sidecar_alive)
    if all_fail is not None:
        record["all_fail"] = all_fail
    if frontier_fraction is not None:
        record["frontier_fraction"] = frontier_fraction
    if breaker_trips:
        record["breaker_trips"] = list(breaker_trips)
    if model_dim_scores:
        record["model_dim_scores"] = dict(model_dim_scores)
    if model_judge_enabled is not None:
        record["model_judge_enabled"] = bool(model_judge_enabled)
    if posterior_lower is not None:
        record["posterior_lower"] = posterior_lower
    if posterior_upper is not None:
        record["posterior_upper"] = posterior_upper
    if flaky is not None:
        record["flaky"] = bool(flaky)
    if group_size is not None:
        record["group_size"] = int(group_size)
    if greedy_count is not None:
        record["greedy_count"] = int(greedy_count)
    if mean_response_length is not None:
        record["mean_response_length"] = float(mean_response_length)
    if truncation_rate is not None:
        record["truncation_rate"] = float(truncation_rate)
    if eos_termination_rate is not None:
        record["eos_termination_rate"] = float(eos_termination_rate)
    if degenerate_policy_alarm is not None:
        record["degenerate_policy_alarm"] = bool(degenerate_policy_alarm)
    if quarantine_suppressed is not None:
        record["quarantine_suppressed"] = bool(quarantine_suppressed)
    if fence_termination_rate is not None:
        record["fence_termination_rate"] = float(fence_termination_rate)
    if cap_run_with_fence_opener_rate is not None:
        record["cap_run_with_fence_opener_rate"] = float(cap_run_with_fence_opener_rate)
    if completion_token_lengths is not None:
        record["completion_token_lengths"] = [int(value) for value in completion_token_lengths]
    if raw_response_chars is not None:
        record["raw_response_chars"] = [int(value) for value in raw_response_chars]
    if extracted_code_chars is not None:
        record["extracted_code_chars"] = [int(value) for value in extracted_code_chars]
    if generation_token_budget is not None:
        record["generation_token_budget"] = int(generation_token_budget)
    if trust_region_violated is not None:
        record["trust_region_violated"] = bool(trust_region_violated)
    if lr is not None:
        record["lr"] = float(lr)
    if trust_region_violation_count is not None:
        record["trust_region_violation_count"] = int(trust_region_violation_count)
    if ratio_after_update is not None:
        record["ratio_after_update"] = float(ratio_after_update)
    if clip_fraction_after_update is not None:
        record["clip_fraction_after_update"] = float(clip_fraction_after_update)
    if seq_kl_after is not None:
        record["seq_kl_after"] = float(seq_kl_after)
    if old_policy_age is not None:
        record["old_policy_age"] = int(old_policy_age)
    if optimizer_substeps_per_rollout is not None:
        record["optimizer_substeps_per_rollout"] = int(optimizer_substeps_per_rollout)
    if gradient_norms is not None:
        record["gradient_norms"] = [float(value) for value in gradient_norms]
    if inner_early_stop_reason is not None:
        record["inner_early_stop_reason"] = str(inner_early_stop_reason)
    if sapo_per_candidate_stats:
        record["sapo_per_candidate_stats"] = [dict(s) for s in sapo_per_candidate_stats]
    if kl_beta is not None:
        record["kl_beta"] = float(kl_beta)
    if dr_pair_mined is not None:
        record["dr_pair_mined"] = bool(dr_pair_mined)
    if dr_pair_reward_gap is not None:
        record["dr_pair_reward_gap"] = float(dr_pair_reward_gap)
    if dr_pair_loss_value is not None:
        record["dr_pair_loss_value"] = float(dr_pair_loss_value)
    if dr_pair_loss_weight is not None:
        record["dr_pair_loss_weight"] = float(dr_pair_loss_weight)
    if dr_variance_correction_value is not None:
        record["dr_variance_correction_value"] = float(dr_variance_correction_value)
    if dr_psi is not None:
        record["dr_psi"] = float(dr_psi)
    if dr_psi_init is not None:
        record["dr_psi_init"] = float(dr_psi_init)
    if dr_psi_warmup_steps is not None:
        record["dr_psi_warmup_steps"] = int(dr_psi_warmup_steps)
    if dr_psi_current_step is not None:
        record["dr_psi_current_step"] = int(dr_psi_current_step)
    if rollout_rewards is not None:
        record["rollout_rewards"] = [dict(value) for value in rollout_rewards]
    if loss_reduction is not None:
        record["loss_reduction"] = str(loss_reduction)
    if per_candidate_losses is not None:
        record["per_candidate_losses"] = [dict(value) for value in per_candidate_losses]
    if loss_breakdown is not None:
        record["loss_breakdown"] = dict(loss_breakdown)
    if lora_b_max_delta is not None:
        record["lora_b_max_delta"] = float(lora_b_max_delta)
    if zero_change_alarm is not None:
        record["zero_change_alarm"] = bool(zero_change_alarm)
    if zero_change_recommend_stop is not None:
        record["zero_change_recommend_stop"] = bool(zero_change_recommend_stop)
    return record


def build_grpo_metrics_payload(
    records: list[dict[str, Any]], *, planned_steps: int
) -> dict[str, Any]:
    skipped_records = [record for record in records if bool(record.get("skipped"))]
    skip_reasons = Counter(
        str(record.get("reason")) for record in skipped_records if record.get("reason")
    )
    updated_steps = sum(1 for record in records if not bool(record.get("skipped")))
    last_recorded_step = records[-1].get("step") if records else None
    return {
        "metrics": records,
        "summary": {
            "planned_steps": planned_steps,
            "recorded_steps": len(records),
            "updated_steps": updated_steps,
            "skipped_steps": len(skipped_records),
            "last_recorded_step": last_recorded_step,
            "skip_reasons": dict(sorted(skip_reasons.items())),
        },
    }


def summarize_python_interface(source: str) -> list[str]:
    if not source.strip():
        return []
    try:
        tree = ast.parse(source)
    except Exception:
        return []

    lines: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args: list[str] = []
            total_args = list(node.args.posonlyargs) + list(node.args.args)
            defaults = list(node.args.defaults)
            default_offset = len(total_args) - len(defaults)
            for index, arg in enumerate(total_args):
                arg_text = arg.arg
                if arg.annotation is not None:
                    arg_text += f": {ast.unparse(arg.annotation)}"
                if index >= default_offset:
                    arg_text += f" = {ast.unparse(defaults[index - default_offset])}"
                args.append(arg_text)
            if node.args.vararg is not None:
                args.append(f"*{node.args.vararg.arg}")
            if node.args.kwonlyargs:
                if node.args.vararg is None:
                    args.append("*")
                # plain zip: kwonlyargs and kw_defaults are equal-length BY
                # CONSTRUCTION (the AST spec pairs each kw-only arg with a
                # default slot, None when absent); the strict-zip keyword is
                # py3.10-only even as False and the canonical venv is py3.9
                # (2026-08-26 Deploy Integrity register gate).
                for kwarg, default in strict_zip(node.args.kwonlyargs, node.args.kw_defaults):
                    kwarg_text = kwarg.arg
                    if kwarg.annotation is not None:
                        kwarg_text += f": {ast.unparse(kwarg.annotation)}"
                    if default is not None:
                        kwarg_text += f" = {ast.unparse(default)}"
                    args.append(kwarg_text)
            if node.args.kwarg is not None:
                args.append(f"**{node.args.kwarg.arg}")
            signature = f"{node.name}({', '.join(args)})"
            if node.returns is not None:
                signature += f" -> {ast.unparse(node.returns)}"
            lines.append(signature)
        elif isinstance(node, ast.ClassDef):
            lines.append(f"class {node.name}")
    return lines


def estimate_detail_budget(test_source: str, cap: int = 8) -> int:
    if not test_source.strip():
        return 1
    count = 0
    for raw_line in test_source.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# Test "):
            count += 1
            continue
        if "failures.append(" in line or "details.append(" in line:
            count += 1
    return max(1, min(cap, count or 1))


def _append_message_template(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                parts.append("{value}")
        return "".join(parts)
    return None


# 2026-09-01 PROMPT-INTEGRITY audit: hints that pin the graded numeric ANSWER
# must not enter the train prompt. Structural quantities (sizes, shapes,
# traces, norms, tolerances) stay -- they describe the contract, not the
# computed result.
_STRUCTURAL_HINT_WORDS = frozenset(
    {
        "amplitude",
        "count",
        "data",
        "depth",
        "edges",
        "entries",
        "error",
        "features",
        "fidelity",
        "gates",
        "generators",
        "labels",
        "length",
        "list",
        "matrix",
        "norm",
        "points",
        "shape",
        "shots",
        "size",
        "strings",
        "terms",
        "trace",
    }
)
_DECISIVE_PAREN_RE = re.compile(r"\([^)]*\d[^)]*\)")  # e.g. "(3 and 5)"
_DECISIVE_VALUE_RE = re.compile(
    # expected 1.000000 / expected 4 / expected 0/0 / need<=-2.6 /
    # should be 0 -- a concrete numeric literal as the stated outcome
    r"(?:expected|need)\s*(?:[<>]=?|==)?\s*-?(?:\d+\.\d{3,}|\d+(?:/\d+)?)"
    r"|should\s+be\s*-?\d+(?:\.\d+)?"
)
_SHAPE_RE = re.compile(r"\d+\s*x\s*\d+", re.IGNORECASE)


def _is_decisive_numeric_hint(hint: str) -> bool:
    """True when a hint pins a decisive numeric answer (not structural)."""
    if _SHAPE_RE.search(hint):
        return False  # "expected 2x2" / "expected [4, 4]" shapes are structural
    if any(word in hint.lower() for word in _STRUCTURAL_HINT_WORDS):
        return False  # sizes/counts/tolerances describe the contract
    return bool(_DECISIVE_PAREN_RE.search(hint) or _DECISIVE_VALUE_RE.search(hint))


def extract_behavior_hints_from_test_source(
    test_source: str, cap: int = 8, *, suppress_decisive_numeric: bool = False
) -> list[str]:
    if not test_source.strip():
        return []

    hints: list[str] = []

    def _keep(hint: str) -> bool:
        if suppress_decisive_numeric and _is_decisive_numeric_hint(hint):
            return False
        return True

    for raw_line in test_source.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# Test "):
            comment = line.lstrip("#").strip()
            if len(comment) >= 12 and comment not in hints and _keep(comment):
                hints.append(comment)

    try:
        tree = ast.parse(test_source)
    except Exception:
        tree = None

    if tree is not None:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute) or node.func.attr != "append":
                continue
            if not isinstance(node.func.value, ast.Name):
                continue
            if node.func.value.id not in {"failures", "details", "error_failures"}:
                continue
            if not node.args:
                continue
            template = _append_message_template(node.args[0])
            if not template:
                continue
            normalized = " ".join(template.split())
            if normalized and normalized not in hints and _keep(normalized):
                hints.append(normalized)
            if len(hints) >= cap:
                break

    return hints[:cap]


def _normalize_signature(signature: str) -> str:
    return re.sub(r"\s+", "", signature.strip().lower())


def _extract_symbol_name(signature: str) -> str:
    text = signature.strip()
    if text.startswith("class "):
        return text[len("class ") :].split("(", 1)[0].split(":", 1)[0].strip().lower()
    return text.split("(", 1)[0].strip().lower()


def interface_match_score(required_interface: list[str], candidate_interface: list[str]) -> float:
    if not required_interface:
        return 1.0
    if not candidate_interface:
        return 0.0

    required_exact = {_normalize_signature(line) for line in required_interface}
    candidate_exact = {_normalize_signature(line) for line in candidate_interface}
    required_names = {_extract_symbol_name(line) for line in required_interface}
    candidate_names = {_extract_symbol_name(line) for line in candidate_interface}

    exact_overlap = len(required_exact & candidate_exact) / max(1, len(required_exact))
    name_overlap = len(required_names & candidate_names) / max(1, len(required_names))
    return 0.5 * exact_overlap + 0.5 * name_overlap


def _safe_details(result: dict | None) -> list[str]:
    if not isinstance(result, dict):
        return []
    raw_details = result.get("details") or []
    if not isinstance(raw_details, list):
        raw_details = [raw_details]
    details: list[str] = []
    for item in raw_details:
        text = str(item).strip()
        if text:
            details.append(text)
    return details


def _has_runtime_failure(details: list[str]) -> bool:
    runtime_markers = (
        "SyntaxError:",
        "IndentationError:",
        "TabError:",
        "AttributeError:",
        "ImportError:",
        "ModuleNotFoundError:",
        "NameError:",
        "TypeError:",
        "unsupported operand type",
    )
    return any(any(marker in detail for marker in runtime_markers) for detail in details)


# ---------------------------------------------------------------------------
# Continuous reward shaping from harness detail numerics
#
# Root cause of the GSPO/SAPO deadlock: with pass rate ~ 0 the binary
# ``pass_reward`` is 0.0 for every candidate in the group, so the group-
# relative advantages are all equal -> NO policy gradient (and the FV-GSPO
# router sees signal_std ~ 0 and ships all-fail groups to the repair lane
# instead of RL). The harness ``details`` list carries continuous numeric
# evidence of how close a failing candidate actually got
# (``counts: P(00)=0.4931 P(11)=0.5069``, ``vqe: energy=-1.48250
# need<=-1.50000``, ``xeb: fidelity=0.8765 need>=0.9000``,
# ``hhl: max abs error=0.0521 need<=0.0500``, ...). We turn that evidence
# into partial credit so the policy always receives a monotone signal:
#
#   shaped_reward = 1.0 if passed else min(0.9, 0.5 + 0.5 * progress)
#
# ``progress`` in [0, 1] is the best per-line closeness (max across lines):
#   - probability-like values (P(..), fidelity, fraction, success, echo,
#     overlap, survival, amplitude, generic [0,1] magnitudes) with a
#     ``need>=`` / ``v < T`` higher-better threshold T: progress = v / T
#     (v just below T is a near miss -> progress -> 1);
#   - the same without a threshold: progress = the value itself; two or more
#     P(..) values on one line (concentration checks) use their sum;
#   - error-like values (error/err/epc/...) with a ``need<=`` / ``v > T``
#     lower-better threshold T: progress = T / v; without a threshold:
#     progress = exp(-v / 0.1);
#   - energy-like values (energy/E0/E) with a lower-better threshold X:
#     progress = exp(-max(0, v - X) / max(0.1, 0.25*|X|)) — an energy just
#     above X is a near miss; with a printed target (exact/true/theory/
#     expected/ideal/analytic): progress = exp(-|v - T| / scale);
#   - anything parseable but unclassified: floor 0.1 (tiny credit);
#   - no numeric evidence at all, or a runtime failure (traceback/crash):
#     0.0 — a crash is never a near miss.
# The 0.9 cap keeps any failing candidate strictly below a passing one.
# Documented decision: robustness > precision; the exact formula matters
# less than NON-ZERO, monotone signal for near-misses.
# ---------------------------------------------------------------------------

_NUM_RE = r"[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?"

# key=value  (lazy key so "P(00)=0.49" -> key "P(00", "max abs error=0.05" -> key)
_DETAIL_KV_RE = re.compile(r"([A-Za-z_|<>][^=\n]{0,24}?)=\s*(" + _NUM_RE + r")")
# whitespace form: "energy -1.4825", "P(0) 0.60", "theory 0.75", "exact -2.0209"
_DETAIL_WS_RE = re.compile(
    r"((?:P\([^)]*\)|energy|fidelity|error|phase|amplitude|probability|"
    r"overlap|theory|exact|expected|ideal|true|analytic|tol|threshold|vs|E0|value))"
    r"\s*[:=]?\s*(" + _NUM_RE + r")",
    re.IGNORECASE,
)
# comparator form on FAIL lines: "fidelity 0.8765 < 0.9000", "error 0.0521 > 0.0500",
# and the equality-miss form "optimize_circuit lost gates: 3 != 5" where the
# pass condition wanted the two sides equal (2026-08-24 audit: the targeted10
# harnesses report "!= 5" failures; treating the RHS as a lower-better
# threshold would be wrong).
_DETAIL_CMP_RE = re.compile(r"(" + _NUM_RE + r")\s*(>=|<=|>|<|!=)\s*(" + _NUM_RE + r")")
# explicit threshold markers: "need>=0.85", "need<=-1.50000", "need >= 0.6000"
_DETAIL_NEED_RE = re.compile(r"need\s*(>=|<=|>|<)\s*(" + _NUM_RE + r")", re.IGNORECASE)
# target keyword + comparator on FAIL lines: "expected >= 3.500000",
# "expected <= 0.500000", "expected > 2.000000000" — the harness states the
# pass threshold right after the target keyword (2026-08-31 vigilance audit:
# quantum_rl_v2_qaoa_p2_maxcut's near-miss emitted ONLY
# "optimized_cut=3.000000, expected >= 3.500000" and shaped 0.0 — the
# differentiated-signal cure was defeated on that v9 wave-1 task).
_DETAIL_TARGET_CMP_RE = re.compile(
    r"\b(expected|true|theory|ideal|analytic|exact|threshold|target|vs)\s*(>=|<=|>|<)\s*("
    + _NUM_RE
    + r")",
    re.IGNORECASE,
)
# arrow form on FAIL lines — the targeted10 harnesses report numeric near-misses
# as "phase_estimation(0.25, 3) -> 3, expected 2" and "-> cost 1, expected 2"
# (the observed value follows the arrow, optionally behind a unit word).  The
# value is only scored when the line also carries a pass target/threshold, so a
# bare arrow number ("-> [0, 0]") never invents signal.
_DETAIL_ARROW_RE = re.compile(r"->\s*(?:(?:[A-Za-z_][A-Za-z0-9_]*)\s+)?(" + _NUM_RE + r")")
# qrng normalization: "range=[0,10)"
_DETAIL_RANGE_RE = re.compile(r"range=\[0,(\d+)\]")

# keys whose numeric value is a count/auxiliary, never progress evidence
# (they still score when a threshold on the same line makes them meaningful)
_DETAIL_SKIP_KEYS = frozenset(
    {
        "total",
        "n",
        "shots",
        "len",
        "counts",
        "support",
        "spread",
        "best",
        "opt",
        "nodes",
        "edges",
        "levels",
        "ints",
        "range",
        "decay",
    }
)

_PROGRESS_FLOOR = 0.1
_PROGRESS_CAP = 0.9


def _progress_for_pair(
    key: str,
    value: float,
    *,
    higher_better: float | None,
    lower_better: float | None,
    target: float | None,
    tolerance: float | None = None,
) -> float:
    """Closeness of one observed (key, value) pair to its pass condition."""
    k = key.lower()
    # ── threshold-anchored rules (strongest evidence) ──
    if higher_better is not None and higher_better > 0.0:
        return _clamp01(value / higher_better)
    if higher_better is not None:
        # zero-valued threshold ("expected >= 0.000000000"): closeness is the
        # excess of the deficit (T - v) above zero, on the value's own scale —
        # a tiny negative eigenvalue is a near miss, a large one is not.
        scale = max(0.05, 0.25 * max(abs(value), 1.0))
        excess = max(0.0, 0.0 - value)
        return math.exp(-excess / scale)
    if lower_better is not None:
        if lower_better > 0.0:
            return _clamp01(lower_better / value) if value > 0.0 else 0.0
        # energy-style threshold (negative): excess above X is the miss
        scale = max(0.1, 0.25 * max(abs(lower_better), abs(value)))
        excess = max(0.0, value - lower_better)
        return math.exp(-excess / scale)
    if target is not None:
        if k in _DETAIL_SKIP_KEYS and "p(" not in k:
            return 0.0
        scale = max(0.05, 0.25 * max(abs(target), abs(value)))
        excess = max(0.0, abs(value - target) - (tolerance or 0.0))
        return math.exp(-excess / scale)
    if k in _DETAIL_SKIP_KEYS:
        return 0.0
    # ── magnitude rules ──
    if "p(" in k or k in (
        "fidelity",
        "fraction",
        "success",
        "echo",
        "overlap",
        "survival",
        "amplitude",
        "est",
        "extrapolated",
        "mean",
        "max p",
        "probability",
    ):
        if 0.0 <= value <= 1.0:
            return value
        return 0.0
    if "err" in k or "error" in k or "trotter" in k or k == "epc":
        return math.exp(-abs(value) / 0.1)
    if k in ("energy", "e0", "e", "hubbard", "value"):
        return _PROGRESS_FLOOR
    # generic bounded magnitude (zexp <Z...Z>=0.75, printed probs)
    if 0.0 <= value <= 1.0:
        return value
    return 0.0


def _detail_progress(line: str) -> float:
    """Continuous closeness of ONE detail line to its pass threshold."""
    pairs: list[tuple[str, float]] = []
    for match in _DETAIL_KV_RE.finditer(line):
        key = match.group(1)
        # "P(00)>=0.3000" parses as key "P(00>" + "=0.3000": the value is a
        # THRESHOLD, not a measurement. Drop comparator-suffixed keys unless
        # the ">" is the closer of a "<...>" observable ("<Z...Z>=0.75");
        # "<"-suffixed keys ("need<") are always threshold text.  "!"-suffixed
        # keys are the LEFT side of "!=" ("lost gates: 3 !" = 5): the value is
        # the EXPECTED quantity, not the observation — crediting it would give
        # full near-miss credit to a failing candidate (2026-08-24 audit).
        if key.endswith("<") or key.endswith("!") or (key.endswith(">") and "<" not in key):
            continue
        pairs.append((key, float(match.group(2))))
    for match in _DETAIL_WS_RE.finditer(line):
        pairs.append((match.group(1), float(match.group(2))))
    # the KV and WS regexes both match "P(00)=0.25" — dedupe so the
    # concentration sum rule does not double-count
    pairs = list(dict.fromkeys(pairs))

    thresholds: list[tuple[str, float]] = []  # ("higher"|"lower", value)
    cmp_values: list[tuple[float, str, float]] = []  # (observed, op, rhs) for
    # the comparator-only form ("support 4 < 5", "success rate 0.74 < 0.95")
    for match in _DETAIL_CMP_RE.finditer(line):
        value = float(match.group(1))
        threshold = float(match.group(3))
        op = match.group(2)
        cmp_values.append((value, op, threshold))
        # on a FAILED line "v < T" means the pass wanted v >= T (higher better)
        if op in ("<", "<="):
            thresholds.append(("higher", threshold))
        elif op in (">", ">="):
            thresholds.append(("lower", threshold))
        # "!=" is an equality miss: pass wanted value == rhs. The rhs becomes
        # the target for the equality-distance rule below, NOT a threshold.
    for match in _DETAIL_NEED_RE.finditer(line):
        threshold = float(match.group(2))
        thresholds.append(("higher" if match.group(1).startswith(">") else "lower", threshold))
    # target keyword + comparator ("expected >= 3.5"): same threshold
    # semantics as the need form, keyed off the pass-target vocabulary.
    for match in _DETAIL_TARGET_CMP_RE.finditer(line):
        threshold = float(match.group(3))
        thresholds.append(("higher" if match.group(2).startswith(">") else "lower", threshold))

    higher = None
    lower = None
    for direction, threshold in thresholds:
        if direction == "higher":
            higher = max(higher or threshold, threshold)
        else:
            lower = min(lower or threshold, threshold)

    target_keys = {"exact", "true", "theory", "expected", "ideal", "analytic", "threshold", "vs"}
    targets: list[float] = []
    tolerance: float | None = None
    for key, value in pairs:
        k = key.lower()
        if k == "tol":
            tolerance = value
        elif k in target_keys:
            targets.append(value)
    target = max(targets) if targets else None

    # concentration checks: two or more DISTINCT P(..) values on one line use
    # their sum (keys may carry "counts: " prefixes -> canonicalize on the
    # bare "P(...)" token so the same measurement is never counted twice)
    p_by_name: dict[str, float] = {}
    for k, v in pairs:
        name = re.search(r"P\([^)]*\)", k)
        if name and 0.0 <= v <= 1.0:
            p_by_name[name.group(0)] = v
    if len(p_by_name) >= 2:
        sum_progress = _clamp01(sum(p_by_name.values()))
        if sum_progress >= 0.5:
            return sum_progress

    best = 0.0
    for key, value in pairs:
        if key.lower() in target_keys or key.lower() == "tol":
            continue
        # qrng mean normalization against the printed range
        if key.lower() == "mean":
            range_match = _DETAIL_RANGE_RE.search(line)
            if range_match:
                value = value / max(1.0, float(range_match.group(1)))
            else:
                continue
        best = max(
            best,
            _progress_for_pair(
                key,
                value,
                higher_better=higher,
                lower_better=lower,
                target=target,
                tolerance=tolerance,
            ),
        )
    # comparator-only lines ("support 4 < 5", "success rate 0.74 < 0.95")
    # carry the observed value only inside the comparator itself
    for value, op, threshold in cmp_values:
        if op in ("<", "<="):
            best = max(
                best,
                _progress_for_pair(
                    "cmp", value, higher_better=higher, lower_better=None, target=None
                ),
            )
        elif op in (">", ">="):
            best = max(
                best,
                _progress_for_pair(
                    "cmp", value, higher_better=None, lower_better=lower, target=None
                ),
            )
        else:  # "!=" equality miss: closeness of the observation to the rhs
            best = max(
                best,
                _progress_for_pair(
                    "cmp", value, higher_better=None, lower_better=None, target=threshold
                ),
            )
    # Arrow form ("phase_estimation(0.25, 3) -> 3, expected 2"): the observed
    # value after "->" is only scored when the line also states a pass
    # target/threshold; a bare arrow number or list is not closeness evidence.
    if target is not None or higher is not None or lower is not None:
        for match in _DETAIL_ARROW_RE.finditer(line):
            value = float(match.group(1))
            best = max(
                best,
                _progress_for_pair(
                    "arrow",
                    value,
                    higher_better=higher,
                    lower_better=lower,
                    target=target,
                    tolerance=tolerance,
                ),
            )
    return best


def shaped_reward_from_details(passed: bool, details: list[str]) -> float:
    """Continuous partial credit from the harness detail strings.

    passed -> 1.0. Otherwise -> min(0.9, 0.5 + 0.5 * progress) where
    ``progress`` is the best per-line numeric closeness to the pass
    threshold; 0.0 when no numeric evidence exists or the candidate crashed.
    """
    if passed:
        return 1.0
    if _has_runtime_failure(details):
        return 0.0  # a crash is never a near miss
    progress = 0.0
    for detail in details or []:
        if not isinstance(detail, str):
            detail = str(detail)
        if not detail.strip():
            continue
        progress = max(progress, _detail_progress(detail))
    if progress <= 0.0:
        return 0.0
    return min(_PROGRESS_CAP, 0.5 + 0.5 * progress)


def brevity_reward(code: str, target_lines: int = 40) -> float:
    """Reward concise solutions: 1.0 at target_lines, decaying for longer code.

    This creates within-group variance even when all completions fail tests,
    breaking the flat-reward deadlock that causes GRPO steps to be skipped.
    """
    lines = code.strip().splitlines()
    n = len(lines)
    if n == 0:
        return 0.0
    if n <= target_lines:
        return 1.0
    # Smooth decay: halves reward every target_lines lines over the target
    return max(0.0, math.exp(-0.7 * (n - target_lines) / max(target_lines, 1)))


def _stdlib_module_roots() -> set[str]:
    roots = set(sys.builtin_module_names)
    stdlib_names = getattr(sys, "stdlib_module_names", None)
    if stdlib_names:
        roots.update(stdlib_names)
    roots.update(
        {
            "abc",
            "argparse",
            "bisect",
            "collections",
            "copy",
            "csv",
            "dataclasses",
            "datetime",
            "functools",
            "heapq",
            "importlib",
            "itertools",
            "json",
            "math",
            "operator",
            "pathlib",
            "random",
            "re",
            "statistics",
            "string",
            "typing",
        }
    )
    return roots


def import_hygiene_score(
    code: str,
    *,
    single_file_expected: bool,
    allowed_import_roots: list[str] | None = None,
) -> float:
    if not single_file_expected:
        return 1.0
    if not code.strip():
        return 0.0
    try:
        tree = ast.parse(code)
    except Exception:
        return 0.0

    allowed_roots = set(allowed_import_roots or [])
    allowed_roots.update(_stdlib_module_roots())

    imported_roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root:
                    imported_roots.append(root)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                imported_roots.append(".")
                continue
            module_name = node.module or ""
            root = module_name.split(".", 1)[0]
            if root:
                imported_roots.append(root)

    if not imported_roots:
        return 1.0

    violations = 0
    for root in imported_roots:
        if root == ".":
            violations += 1
            continue
        if root not in allowed_roots:
            violations += 1
    return max(0.0, 1.0 - violations / max(1, len(imported_roots)))


def build_reward_breakdown(
    *,
    code: str,
    result: dict | None,
    required_interface: list[str],
    detail_budget: int,
    pass_weight: float,
    syntax_weight: float,
    interface_weight: float,
    verifier_weight: float,
    brevity_weight: float = 0.0,
    brevity_target_lines: int = 40,
    import_hygiene_weight: float = 0.0,
    single_file_expected: bool = False,
    allowed_import_roots: list[str] | None = None,
) -> dict[str, float | int | bool]:
    syntax_ok = False
    if code.strip():
        try:
            ast.parse(code)
            syntax_ok = True
        except Exception:
            syntax_ok = False

    candidate_interface = summarize_python_interface(code) if syntax_ok else []
    interface_reward = (
        interface_match_score(required_interface, candidate_interface) if syntax_ok else 0.0
    )

    passed = bool(result.get("passed")) if isinstance(result, dict) else False
    details = _safe_details(result)
    failure_count = 0 if passed else max(1, len(details))
    capped_budget = max(1, detail_budget)
    verifier_reward = (
        1.0 if passed else max(0.0, 1.0 - min(failure_count, capped_budget) / capped_budget)
    )
    if not passed and _has_runtime_failure(details):
        verifier_reward = 0.0
    # Binary pass stays in the metrics (pass_rate); the REWARD the policy sees
    # is the continuous ``shaped_reward`` (1.0 on pass, partial credit on
    # near-misses) — with pass rate ~ 0 the binary gives the group NO
    # advantage variation, hence no gradient (the GSPO/SAPO failure mode).
    pass_reward = 1.0 if passed else 0.0
    shaped_reward = shaped_reward_from_details(passed, details)
    syntax_reward = 1.0 if syntax_ok else 0.0
    brevity_score = brevity_reward(code, target_lines=brevity_target_lines) if syntax_ok else 0.0
    import_hygiene = (
        import_hygiene_score(
            code,
            single_file_expected=single_file_expected,
            allowed_import_roots=allowed_import_roots,
        )
        if syntax_ok
        else 0.0
    )

    weight_sum = (
        pass_weight
        + syntax_weight
        + interface_weight
        + verifier_weight
        + brevity_weight
        + import_hygiene_weight
    )
    # The weighted sum uses the continuous shaped credit in place of the
    # binary pass_reward (pass_reward stays in the dict purely for metrics).
    total_reward = (
        pass_weight * shaped_reward
        + syntax_weight * syntax_reward
        + interface_weight * interface_reward
        + verifier_weight * verifier_reward
        + brevity_weight * brevity_score
        + import_hygiene_weight * import_hygiene
    ) / max(weight_sum, 1e-8)

    return {
        "passed": passed,
        "pass_reward": pass_reward,
        "shaped_reward": shaped_reward,
        "syntax_reward": syntax_reward,
        "interface_reward": interface_reward,
        "verifier_reward": verifier_reward,
        "brevity_reward": brevity_score,
        "import_hygiene_reward": import_hygiene,
        "failure_count": failure_count,
        "detail_budget": capped_budget,
        "total_reward": total_reward,
    }


@dataclass
class TaskCurriculum:
    ema_decay: float = 0.9
    min_weight: float = 0.05
    quantum_priority: float = 1.5
    uncertainty_bonus: float = 0.35
    state: dict[str, dict[str, float]] = field(default_factory=dict)

    def get_state(self, task_id: str) -> dict[str, float]:
        current = self.state.get(task_id)
        if current is None:
            current = {"ema_reward": 0.0, "seen": 0.0}
            self.state[task_id] = current
        return current

    def weight(self, task_id: str, domain: str | None) -> float:
        current = self.get_state(task_id)
        ema_reward = float(current["ema_reward"])
        seen = float(current["seen"])
        difficulty = max(0.05, 1.0 - ema_reward)
        uncertainty = self.uncertainty_bonus / math.sqrt(seen + 1.0)
        domain_scale = self.quantum_priority if domain == "quantum" else 1.0
        return max(self.min_weight, domain_scale * (difficulty + uncertainty))

    def record(self, task_id: str, observed_reward: float) -> dict[str, float]:
        current = self.get_state(task_id)
        ema_reward = float(current["ema_reward"])
        seen = float(current["seen"]) + 1.0
        updated = self.ema_decay * ema_reward + (1.0 - self.ema_decay) * observed_reward
        current["ema_reward"] = updated
        current["seen"] = seen
        return current


def frontier_learnability(*, pass_rate: float, shaped_signal_std: float) -> float:
    bounded_pass_rate = min(1.0, max(0.0, float(pass_rate)))
    binary_variance = 4.0 * bounded_pass_rate * (1.0 - bounded_pass_rate)
    return min(1.0, max(binary_variance, max(0.0, float(shaped_signal_std))))


def classify_frontier_route(
    *,
    pass_rate: float,
    shaped_signal_std: float,
    frontier_threshold: float = 0.10,
    mastered_threshold: float = 0.95,
) -> str:
    bounded_pass_rate = min(1.0, max(0.0, float(pass_rate)))
    learnability = frontier_learnability(
        pass_rate=bounded_pass_rate,
        shaped_signal_std=shaped_signal_std,
    )
    if bounded_pass_rate >= mastered_threshold and shaped_signal_std < frontier_threshold:
        return "mastered_replay"
    if bounded_pass_rate == 0.0:
        if learnability >= frontier_threshold:
            return "partial_repair_rl"
        return "repair_sft"
    if learnability >= frontier_threshold:
        return "frontier_rl"
    return "mastered_replay"


@dataclass
class BetaPosterior:
    """Beta posterior over a task's pass probability (review 2026-08-05 #4).

    p_x ~ Beta(alpha_0 + s_x, beta_0 + f_x) with a weak uniform prior
    (alpha_0 = beta_0 = 1). Credible bounds use a normal approximation
    (z = 1.28 gives an ~80% interval); frontier_mass approximates
    P(0.10 < p < 0.90) — the probability the task is genuinely learnable.
    """

    alpha: float = 1.0
    beta: float = 1.0

    def update(self, successes: int, failures: int) -> None:
        self.alpha += max(0, int(successes))
        self.beta += max(0, int(failures))

    @property
    def samples(self) -> int:
        return int(self.alpha + self.beta - 2)

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def std(self) -> float:
        n = self.alpha + self.beta
        return math.sqrt(self.alpha * self.beta / (n * n * (n + 1.0)))

    def credible_bounds(self, z: float = 1.28) -> tuple[float, float]:
        margin = z * self.std
        return (max(0.0, self.mean - margin), min(1.0, self.mean + margin))

    def frontier_mass(self, lo: float = 0.10, hi: float = 0.90) -> float:
        def _phi(z: float) -> float:
            return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

        z_lo = (lo - self.mean) / max(self.std, 1e-9)
        z_hi = (hi - self.mean) / max(self.std, 1e-9)
        return max(0.0, min(1.0, _phi(z_hi) - _phi(z_lo)))


def classify_posterior_route(
    posterior: BetaPosterior,
    shaped_signal_std: float,
    *,
    flaky: bool = False,
    frontier_threshold: float = 0.10,
    mastered_threshold: float = 0.95,
    repair_threshold: float = 0.10,
    min_mastered_samples: int = 32,
) -> str:
    """Posterior routing with hysteresis (review 2026-08-05 #4).

    With G=8 a single lucky 8/8 group must NOT mark a task mastered and a
    single stochastic failure must not bounce it back: mastered requires
    enough cumulative samples AND the lower credible bound above the
    threshold; repair requires the upper credible bound very low (all-fail
    evidence accumulating); flaky oscillation routes to quarantine.
    """
    if flaky:
        return INVALID_OR_NOISY
    lower, upper = posterior.credible_bounds()
    shaped = max(0.0, float(shaped_signal_std))
    if (
        posterior.samples >= min_mastered_samples
        and lower >= mastered_threshold
        and shaped < frontier_threshold
    ):
        return MASTERED_REPLAY
    if upper <= repair_threshold and shaped < frontier_threshold:
        return REPAIR_SFT
    if shaped >= frontier_threshold:
        # meaningful partial signal: all-failish posterior -> partial repair RL
        if posterior.mean < 0.125:
            return PARTIAL_REPAIR_RL
        return FRONTIER_RL
    if posterior.frontier_mass() >= 0.5:
        return FRONTIER_RL
    return MASTERED_REPLAY


def leave_one_out_advantages(rewards: torch.Tensor) -> torch.Tensor:
    if rewards.numel() <= 1:
        return torch.zeros_like(rewards)
    group_total = rewards.sum()
    other_mean = (group_total - rewards) / float(rewards.numel() - 1)
    return rewards - other_mean


def normalize_group_rewards(
    rewards: torch.Tensor,
    mode: str = "none",
    epsilon: float = 1e-8,
) -> tuple[torch.Tensor, dict[str, float | str | None]]:
    """Normalize the RAW reward scores across all group candidates before they
    feed the GRPO/SAPO advantage computation (user directive 2026-08-27 r19).

    ``mode="none"`` (the default / inert): returns the input unchanged and the
    record ``{"mode": "none"}`` — byte-identical to the prior path.

    ``mode="minmax"``: min-max scale the group to the unit interval [0, 1],
    preserving order. A FLAT group (range == 0) is left unchanged (never a
    divide-by-zero, never NaN/Inf — the output stays finite and all-equal).

    Returns (normalized, record) where record carries the scale + mode for the
    reward verifier / step record.
    """
    flat = rewards.float()
    rec: dict[str, float | str | None] = {"mode": mode}
    if mode == "none":
        return rewards, rec
    if mode == "minmax":
        rmin = float(flat.min().item())
        rmax = float(flat.max().item())
        rec["min"] = rmin
        rec["max"] = rmax
        rng = rmax - rmin
        if rng <= epsilon:
            # flat group: leave unchanged (stable, finite, order-preserving)
            rec["flat"] = True
            return rewards, rec
        norm = (flat - rmin) / rng
        rec["flat"] = False
        return norm, rec
    raise ValueError(f"normalize_group_rewards: unknown mode {mode!r}")


# ---------------------------------------------------------------------------
# Teacher-Free FV-GSPO helpers (Teacher-Free-FV-GSPO-Final-Plan-ZH.docx)
#
# These three helpers are the `training/grpo_utils.py` deliverables listed in
# the plan's code-change checklist (table 30): tiered_teacher_free_reward,
# cluster_adjusted_advantages and teacher_free_route. They intentionally
# implement the *intent* of the plan — a teacher-free (no reference/teacher
# model) pass-dominant closed loop — while keeping behaviours numerically safe
# and testable. See the review notes in docs/grpo-teacher-free-review-2026-08-08.md
# for the reasoning behind the (small) deviations from the literal plan text.
# ---------------------------------------------------------------------------


def tiered_teacher_free_reward(
    *,
    passed_flags: Sequence[bool],
    syntax_scores: Sequence[float],
    interface_scores: Sequence[float],
    semantic_scores: Sequence[float],
    import_scores: Sequence[float],
    efficiency_scores: Sequence[float] | None = None,
    diversity_scores: Sequence[float] | None = None,
    judge_scores: Sequence[float] | None = None,
    judge_calibrated: bool = False,
) -> list[float]:
    """Pass-dominant (tiered) per-candidate reward for teacher-free FV-GSPO.

    Implements the plan's §4.3 / table 16 "pass-dominant 分层奖励" with the hard
    invariant that *every* passing candidate outranks *every* failing candidate:

        pass   : R_i = 1.00 + 0.03*E_i + 0.02*D_i     (>= 1.00)
        failed : R_i = min(0.95, 0.10*S_i + 0.10*I_i + 0.65*V_i + 0.10*H_i + 0.05*J_i)

    The judge (J) is given zero weight until it is calibrated; when uncalibrated
    the semantic-progress weight is raised to 0.70 exactly as the plan requires
    so the all-failed case still carries a learnable partial-progress signal.

    E and D only ever differentiate candidates that already fully pass; a failing
    candidate can never receive more than 0.95, which is strictly below the 1.00
    floor of any passing candidate.
    """
    n = len(passed_flags)
    eff_semantic_w = 0.70 if not judge_calibrated else 0.65
    eff_judge_w = 0.00 if not judge_calibrated else 0.05
    rewards: list[float] = []
    for i in range(n):
        if passed_flags[i]:
            eff = float(efficiency_scores[i]) if efficiency_scores else 0.0
            div = float(diversity_scores[i]) if diversity_scores else 0.0
            rewards.append(1.00 + 0.03 * _clamp01(eff) + 0.02 * _clamp01(div))
        else:
            s = _clamp01(float(syntax_scores[i]))
            it = _clamp01(float(interface_scores[i]))
            v = _clamp01(float(semantic_scores[i]))
            h = _clamp01(float(import_scores[i]))
            j = _clamp01(float(judge_scores[i])) if (judge_scores and judge_calibrated) else 0.0
            raw = 0.10 * s + 0.10 * it + eff_semantic_w * v + 0.10 * h + eff_judge_w * j
            rewards.append(min(0.95, raw))
    return rewards


def cluster_adjusted_advantages(
    advantages: Sequence[float],
    cluster_ids: Sequence[Any],
) -> list[float]:
    """Divide per-candidate LOO advantages by their structural cluster size.

    Plan §6 / table 22: each candidate's advantage is scaled by the reciprocal of
    the size of its structure cluster (AST + circuit signature) so that repeated /
    near-duplicate code in the same cluster is down-weighted and diversity is
    protected. The LOO advantages themselves must be computed first (see
    `leave_one_out_advantages`); this helper only applies the cluster penalty.

    `advantages` and `cluster_ids` must have equal length and be positionally
    aligned (index i = candidate i). Cluster sizes are counted within the given
    batch of `cluster_ids`.
    """
    if not advantages:
        return []
    sizes: dict[Any, int] = Counter(cluster_ids)
    out: list[float] = []
    # strict pairing: a length mismatch is a caller bug and must raise (see
    # training.compat.strict_zip — one home for the py3.9-safe strict zip).
    for adv, cid in strict_zip(advantages, cluster_ids):
        size = max(1, int(sizes.get(cid, 1)))
        out.append(float(adv) / float(size))
    return out


def teacher_free_route(
    *,
    pass_count: int,
    group_size: int,
    reward_range: float,
    max_semantic_progress: float,
    consecutive_mastered: int = 0,
    unstable: bool = False,
) -> str:
    """Select the teacher-free route for a task group (plan §5.1 / table 18).

    Routing rules (all failing candidates share ... ; only the group-level
    summary statistics are required here):

      frontier_rl       : some (1 .. G-1) candidates fully pass -> all go to LOO/GSPO.
      partial_repair_rl : none pass but there is meaningful progress
                          (reward_range>=0.10 OR max(V)>=0.30) -> shaped-RL all.
      mastered_replay   : two consecutive 8/8 groups -> skip (kept in replay pool).
      self_repair       : none pass AND reward_range<0.10 AND max(V)<0.30 -> no RL
                          update; emit an execution-feedback repair prompt instead.
      quarantine        : unstable execution / backend errors -> isolate, no train.
    """
    if unstable:
        return "quarantine"
    if consecutive_mastered >= 2 and pass_count == group_size:
        return "mastered_replay"
    if pass_count >= 1:
        return "frontier_rl"
    if reward_range >= 0.10 or max_semantic_progress >= 0.30:
        return "partial_repair_rl"
    return "self_repair"


def _clamp01(x: float) -> float:
    return min(1.0, max(0.0, float(x)))


def stable_gspo_loss(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    *,
    clip_low: float,
    clip_high: float,
    kl_coeff: float,
    numerical_log_ratio_clip: float,
) -> torch.Tensor:
    finite_mask = (
        torch.isfinite(log_probs) & torch.isfinite(old_log_probs) & torch.isfinite(advantages)
    )
    if not finite_mask.any():
        return log_probs.new_tensor(float("nan"))

    safe_log_probs = log_probs[finite_mask]
    safe_old_log_probs = old_log_probs[finite_mask].detach()
    safe_advantages = advantages[finite_mask].detach()
    log_ratio = (safe_log_probs - safe_old_log_probs).clamp(
        -numerical_log_ratio_clip,
        numerical_log_ratio_clip,
    )
    sequence_ratio = torch.exp(log_ratio)
    clipped_ratio = sequence_ratio.clamp(1.0 - clip_low, 1.0 + clip_high)
    surrogate = torch.minimum(
        sequence_ratio * safe_advantages,
        clipped_ratio * safe_advantages,
    )
    approximate_kl = old_sampled_kl(
        safe_log_probs,
        safe_old_log_probs,
        numerical_log_ratio_clip=numerical_log_ratio_clip,
    )
    total = -surrogate.mean() + kl_coeff * approximate_kl
    if not torch.isfinite(total):
        return log_probs.new_tensor(float("nan"))
    return total


def stable_grpo_loss(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    kl_coeff: float,
    ratio_clip_log_delta: float,
) -> torch.Tensor:
    finite_mask = (
        torch.isfinite(log_probs) & torch.isfinite(old_log_probs) & torch.isfinite(advantages)
    )
    if not finite_mask.any():
        return log_probs.new_tensor(float("nan"))

    safe_log_probs = log_probs[finite_mask]
    safe_old_log_probs = old_log_probs[finite_mask].detach()
    safe_advantages = advantages[finite_mask].detach()

    log_ratio = (safe_log_probs - safe_old_log_probs).clamp(
        -ratio_clip_log_delta,
        ratio_clip_log_delta,
    )
    ratio = torch.exp(log_ratio)
    pg_loss = -(ratio * safe_advantages).mean()

    kl = old_sampled_kl(
        safe_log_probs,
        safe_old_log_probs,
        numerical_log_ratio_clip=ratio_clip_log_delta,
    )
    total = pg_loss + kl_coeff * kl
    if not torch.isfinite(total):
        return log_probs.new_tensor(float("nan"))
    return total


def stable_token_log_probs(
    logits: torch.Tensor,
    target_ids: torch.Tensor,
    logit_clip: float,
) -> torch.Tensor:
    safe_logits = torch.nan_to_num(
        logits.float(),
        nan=0.0,
        posinf=logit_clip,
        neginf=-logit_clip,
    ).clamp(-logit_clip, logit_clip)
    safe_targets = target_ids.long()
    log_probs = torch.log_softmax(safe_logits, dim=-1)
    vocab_size = log_probs.shape[-1]
    flat_log_probs = log_probs.reshape(-1, vocab_size)
    flat_targets = safe_targets.reshape(-1, 1)
    flat_selected = flat_log_probs.gather(1, flat_targets)
    return flat_selected.reshape(safe_targets.shape)


def resolve_entropy_pos_cap(
    prompt_len: int, entropy_token_cap: int | None, seq_len: int
) -> int | None:
    """Absolute logits-position bound for the entropy branch.

    2026-08-26 (run-8 OOM root cause): ``entropy_token_cap`` counts COMPLETION
    tokens after the prompt (the completion starts at target position
    ``prompt_len - 1``); this maps it to an absolute position cap. ``None`` or
    ``<= 0`` keeps the full sequence (legacy behavior); a cap larger than the
    sequence is clamped to the sequence (identical to uncapped).
    """
    if entropy_token_cap is None or int(entropy_token_cap) <= 0:
        return None
    cap = max(int(prompt_len) - 1, 0) + int(entropy_token_cap)
    return min(cap, max(int(seq_len), 0))


class _ChunkedRecomputeBackward(torch.autograd.Function):
    """Autograd wrapper with a chunk-streaming backward for the chunked-vocab
    log-prob/entropy pass (2026-08-26 run-9 backward-OOM root cause).

    The PLAIN autograd path retains per-chunk fp32 tensors (clamp/exp/
    gather saves at [1,S,8192]) in the graph over the FULL sequence until
    loss.backward() — measured ~10.9 GiB per candidate at the 27B contract
    (43.6 GiB for a 4-candidate train pass; the run-9 58.72/60.96 GiB
    backward crash). The forward here saves only the [1,S] intermediates
    (per-position max, logsumexp, neg-entropy, targets) plus the logits view
    (shared storage — no copy); the backward re-derives p = exp((x/T -
    max))/Z chunk-by-chunk and accumulates the exact softmax gradients
    incrementally — peak O(S x chunk) instead of O(S x V). Forward outputs
    are bit-identical to the plain path (same math, same order).
    """

    @staticmethod
    def forward(  # type: ignore[override]
        ctx,
        logits: torch.Tensor,
        target_ids: torch.Tensor,
        logit_clip: float,
        chunk_size: int,
        policy_temperature: float,
        entropy_pos_cap: int | None,
        return_entropy: bool,
    ):
        vocab_size = logits.shape[-1]

        def _clamped_chunk(start: int, pos_cap: int | None = None) -> torch.Tensor:
            chunk = logits[:, :, start : start + chunk_size]
            if pos_cap is not None:
                chunk = chunk[:, :pos_cap, :]
            return torch.nan_to_num(
                chunk.float(),
                nan=0.0,
                posinf=logit_clip,
                neginf=-logit_clip,
            ).clamp(-logit_clip, logit_clip) / float(policy_temperature)

        per_pos_max = None
        for start in range(0, vocab_size, chunk_size):
            chunk_max = _clamped_chunk(start).amax(dim=-1)
            per_pos_max = (
                chunk_max if per_pos_max is None else torch.maximum(per_pos_max, chunk_max)
            )
        sum_exp = torch.zeros_like(per_pos_max)
        gathered = per_pos_max.new_full(target_ids.shape, float("nan"))
        for start in range(0, vocab_size, chunk_size):
            chunk = _clamped_chunk(start)
            sum_exp = sum_exp + (chunk - per_pos_max.unsqueeze(-1)).exp().sum(dim=-1)
            sel = (target_ids >= start) & (target_ids < start + chunk_size)
            if bool(sel.any()):
                idx = (target_ids - start).clamp(min=0, max=chunk_size - 1).unsqueeze(-1)
                vals = chunk.gather(2, idx).squeeze(-1)
                gathered = gathered.masked_scatter(sel, vals[sel])
        log_z = per_pos_max + sum_exp.log()
        token_log_probs = gathered - log_z
        neg_entropy = None
        if return_entropy:
            neg_entropy = torch.zeros_like(per_pos_max)
            log_z_shifted = sum_exp.log()
            pos_cap = entropy_pos_cap if entropy_pos_cap is not None else per_pos_max.shape[1]
            pm = per_pos_max[:, :pos_cap]
            se = sum_exp[:, :pos_cap]
            lz = log_z_shifted[:, :pos_cap]
            for start in range(0, vocab_size, chunk_size):
                chunk = _clamped_chunk(start, pos_cap=pos_cap)
                shifted = chunk - pm.unsqueeze(-1)
                p = shifted.exp() / se.unsqueeze(-1)
                log_p = shifted - lz.unsqueeze(-1)
                neg_entropy[:, :pos_cap] = neg_entropy[:, :pos_cap] + (p * log_p).sum(dim=-1)

        ctx.logit_clip = float(logit_clip)
        ctx.chunk_size = int(chunk_size)
        ctx.policy_temperature = float(policy_temperature)
        ctx.entropy_pos_cap = entropy_pos_cap
        ctx.save_for_backward(logits, target_ids, per_pos_max, sum_exp, neg_entropy)
        if return_entropy:
            return token_log_probs, -neg_entropy
        return token_log_probs

    @staticmethod
    def backward(ctx, *grad_outputs):  # type: ignore[override]
        logits, target_ids, per_pos_max, sum_exp, neg_entropy = ctx.saved_tensors
        clip = ctx.logit_clip
        cs = ctx.chunk_size
        temp = ctx.policy_temperature
        vocab_size = logits.shape[-1]
        grad_tokens = grad_outputs[0]
        grad_entropy = grad_outputs[1] if len(grad_outputs) > 1 else None

        # p = exp((x_clamped/T - max)) / Z — recomputed per chunk; gradients:
        #   token-lp term:  d lps_i/dx_v = (delta_{v,t} - p_v) / T
        #   entropy term:   d H_i/dx_v  = -(1/T) p_v (log p_v + H_i)
        sum_exp.log()
        E = -neg_entropy if neg_entropy is not None else None
        if grad_entropy is not None and E is not None and ctx.entropy_pos_cap is not None:
            # The entropy output beyond the cap is a CONSTANT zero (the plain
            # path's CopySlices base) — the incoming gradient there must not
            # propagate (the sum's gradient reaches every position, including
            # the constant zeros).
            ge = grad_entropy.clone()
            ge[:, int(ctx.entropy_pos_cap) :] = 0.0
            grad_entropy = ge
        grad_x = torch.zeros(logits.shape, dtype=torch.float32, device=logits.device)
        for start in range(0, vocab_size, cs):
            raw = logits[:, :, start : start + cs]
            rawf = raw.float()
            safe = (
                torch.nan_to_num(rawf, nan=0.0, posinf=clip, neginf=-clip).clamp(-clip, clip) / temp
            )
            shifted = safe - per_pos_max.unsqueeze(-1)
            p = shifted.exp() / sum_exp.unsqueeze(-1)
            # nan/inf replaced and out-of-clip positions carry no gradient
            # through nan_to_num/clamp (matches the plain autograd path).
            mask = torch.isfinite(rawf) & (rawf >= -clip) & (rawf <= clip)
            onehot = torch.zeros_like(p)
            sel = (target_ids >= start) & (target_ids < start + cs)
            if bool(sel.any()):
                # Per-position one-hot at the target column. scatter_ is
                # exact even when two positions share a column; the clamped
                # out-of-chunk indices are masked off afterwards.
                idx = (target_ids - start).clamp(min=0, max=cs - 1).unsqueeze(-1)
                onehot.scatter_(2, idx, torch.ones_like(onehot[:, :, :1]))
                onehot *= sel.unsqueeze(-1).float()
            chunk_grad = grad_tokens.unsqueeze(-1) * (onehot - p) / temp
            if grad_entropy is not None and E is not None:
                chunk_grad = chunk_grad + (
                    grad_entropy.unsqueeze(-1) * (-(1.0 / temp)) * p * (p.log() + E.unsqueeze(-1))
                )
            grad_x[:, :, start : start + cs] += chunk_grad * mask
        return grad_x, None, None, None, None, None, None


def chunked_log_probs_and_entropy(
    logits: torch.Tensor,
    target_ids: torch.Tensor,
    logit_clip: float,
    chunk_size: int = 8192,
    return_entropy: bool = False,
    policy_temperature: float = 1.0,
    entropy_pos_cap: int | None = None,
    recompute_backward: bool = False,
):
    """Memory-bounded equivalent of stable_token_log_probs() (+ per-position entropy).

    For a 27B model the vocab axis is 248320: stable_token_log_probs materializes
    full-vocab fp32 logits + log_softmax output (multiple GB at seq 1024) on the
    single NPU that holds the lm_head — the observed stall/OOM zone in the ASI2
    8-NPU sharded runs. This walks the vocab in chunks with a two-pass
    per-position max / logsumexp, so peak extra memory is ~chunk_size × seq fp32
    and the result is numerically identical (same nan_to_num + clamp, exact
    two-pass logsumexp).

    `logits` has shape [1, S, V] and `target_ids` shape [1, S], aligned position
    for position (the caller performs any shift, exactly as with
    stable_token_log_probs). When return_entropy is True also returns
    per-position entropy -Σ p log p at those positions.

    2026-08-26 (run-9 backward-OOM root cause): ``recompute_backward=True``
    routes through ``_ChunkedRecomputeBackward`` — the forward is the same
    math (outputs bit-identical), but the backward streams chunk-by-chunk
    instead of retaining the per-chunk fp32 tensors in the graph (measured
    ~10.9 GiB/candidate retained at the 27B contract; the run-9 58.72 GiB
    backward crash). Trainer default ON via --chunked-recompute-backward.
    """
    if not math.isfinite(policy_temperature) or policy_temperature <= 0.0:
        raise ValueError("policy_temperature must be finite and > 0")
    if recompute_backward:
        return _ChunkedRecomputeBackward.apply(
            logits,
            target_ids.long(),
            logit_clip,
            chunk_size,
            policy_temperature,
            entropy_pos_cap,
            return_entropy,
        )
    x = logits
    targets = target_ids.long()
    if x.shape[-2] != targets.shape[-1]:
        raise ValueError("target_ids must align position-for-position with logits")
    vocab_size = x.shape[-1]

    def _clamped_chunk(start: int, pos_cap: int | None = None) -> torch.Tensor:
        chunk = x[:, :, start : start + chunk_size]
        # 2026-08-26 (run-8 OOM root cause): the entropy branch only needs the
        # first ``pos_cap`` positions — slice BEFORE the fp32 materialization
        # so the nan_to_num/clamp saved tensors (retained in the autograd
        # graph until backward) are [1,pos_cap,8192], not [1,S,8192].
        if pos_cap is not None:
            chunk = chunk[:, :pos_cap, :]
        safe = torch.nan_to_num(
            chunk.float(),
            nan=0.0,
            posinf=logit_clip,
            neginf=-logit_clip,
        ).clamp(-logit_clip, logit_clip)
        # model.generate samples from softmax(logits / temperature).  Rollout
        # log-probabilities must use that same behavior distribution or any
        # adaptive temperature escalation corrupts the SAPO importance ratio.
        return safe / float(policy_temperature)

    # Pass 1: per-position max over clamped chunk values.
    per_pos_max = None
    for start in range(0, vocab_size, chunk_size):
        chunk_max = _clamped_chunk(start).amax(dim=-1)
        per_pos_max = chunk_max if per_pos_max is None else torch.maximum(per_pos_max, chunk_max)

    # Pass 2: logsumexp + target gathers per chunk.
    sum_exp = torch.zeros_like(per_pos_max)
    gathered = per_pos_max.new_full(targets.shape, float("nan"))
    for start in range(0, vocab_size, chunk_size):
        chunk = _clamped_chunk(start)
        sum_exp = sum_exp + (chunk - per_pos_max.unsqueeze(-1)).exp().sum(dim=-1)
        sel = (targets >= start) & (targets < start + chunk_size)
        if bool(sel.any()):
            # gather validates every index, so clamp both ends; masked_scatter
            # only takes the in-chunk positions.
            idx = (targets - start).clamp(min=0, max=chunk_size - 1).unsqueeze(-1)
            vals = chunk.gather(2, idx).squeeze(-1)
            gathered = gathered.masked_scatter(sel, vals[sel])

    log_z = per_pos_max + sum_exp.log()
    token_log_probs = gathered - log_z
    if not return_entropy:
        return token_log_probs

    # Pass 3 (entropy): H = -(p · log p) per position with p = exp(x - max)/Z.
    # Every term has the same sign, so the chunked sum is cancellation-free.
    neg_entropy = torch.zeros_like(per_pos_max)
    log_z_shifted = sum_exp.log()
    # 2026-08-26 (run-8 OOM root cause): the entropy branch's per-chunk fp32
    # tensors (clamp/exp/p/log_p at [1,S,8192]) are retained in the autograd
    # graph over the FULL sequence — ~37 GiB for a 4-candidate 27B train pass
    # at S=1700 (measured), the run-8 59.8 GiB NPU-0 peak. ``entropy_pos_cap``
    # bounds the branch to the first N positions (a floor needs a rough mean,
    # not the full sequence); the log_z / log-prob path is untouched (lps
    # bit-identical). Positions beyond the cap stay 0 in the returned tensor;
    # the capped caller masks them out.
    pos_cap = entropy_pos_cap if entropy_pos_cap is not None else per_pos_max.shape[1]
    pm = per_pos_max[:, :pos_cap]
    se = sum_exp[:, :pos_cap]
    lz = log_z_shifted[:, :pos_cap]
    for start in range(0, vocab_size, chunk_size):
        chunk = _clamped_chunk(start, pos_cap=pos_cap)
        shifted = chunk - pm.unsqueeze(-1)
        p = shifted.exp() / se.unsqueeze(-1)
        log_p = shifted - lz.unsqueeze(-1)
        neg_entropy[:, :pos_cap] = neg_entropy[:, :pos_cap] + (p * log_p).sum(dim=-1)
    return token_log_probs, -neg_entropy


def reward_signal_stats(
    rewards: torch.Tensor,
    pass_rewards: torch.Tensor,
    syntax_rewards: torch.Tensor,
    interface_rewards: torch.Tensor,
    verifier_rewards: torch.Tensor,
    brevity_rewards: torch.Tensor | None = None,
) -> dict[str, float]:
    reward_std = float(rewards.std(unbiased=False).item())
    pass_std = float(pass_rewards.std(unbiased=False).item())
    syntax_std = float(syntax_rewards.std(unbiased=False).item())
    interface_std = float(interface_rewards.std(unbiased=False).item())
    verifier_std = float(verifier_rewards.std(unbiased=False).item())
    brevity_std = (
        float(brevity_rewards.std(unbiased=False).item()) if brevity_rewards is not None else 0.0
    )
    signal_std = max(reward_std, pass_std, syntax_std, interface_std, verifier_std, brevity_std)
    result = {
        "reward_std": reward_std,
        "pass_std": pass_std,
        "syntax_std": syntax_std,
        "interface_std": interface_std,
        "verifier_std": verifier_std,
        "signal_std": signal_std,
    }
    if brevity_rewards is not None:
        result["brevity_std"] = brevity_std
    return result


def policy_update_signal_magnitude(
    *,
    advantage_mode: str,
    signal_stats: Mapping[str, float],
    loo_advantage_rms: float | None,
) -> tuple[float, str]:
    """Select the signal magnitude used by the flat-group update gate.

    Raw component standard deviations are not on the scale of their weighted
    contribution to total reward. Canonical LOO mode therefore gates on the
    RMS of the final clipped advantages that actually enter SAPO. The
    ``group_std`` ablation retains its historical max-component statistic.
    """
    if advantage_mode == "loo":
        magnitude = 0.0 if loo_advantage_rms is None else float(loo_advantage_rms)
        return max(0.0, magnitude), "loo_advantage_rms"
    return max(0.0, float(signal_stats.get("signal_std", 0.0))), "reward_signal_std"


def should_queue_flat_all_fail(
    *, all_fail: bool, route: str, update_signal_magnitude: float, threshold: float
) -> bool:
    """Return whether an RL-routed group has no usable policy gradient.

    Router component dispersion can be nonzero even when the final reward and
    LOO advantages are flat (for example an inactive brevity component). Such
    a group must enter the repair lane immediately instead of being discarded
    as a generic low-signal skip and sampled again later.
    """
    return (
        bool(all_fail) and route in RL_ROUTES and float(update_signal_magnitude) < float(threshold)
    )


# ---------------------------------------------------------------------------
# Adaptive temperature escalation
# ---------------------------------------------------------------------------


@dataclass
class AdaptiveKLState:
    """Adaptive KL penalty (design §4): beta rises when sequence KL drifts
    beyond target, falls when it is far below target.

    ProRL-style capability preservation: the anchor policy stays fixed until a
    checkpoint passes held-out regression gates; the KL controller keeps the
    policy close to the anchor by adjusting beta from the measured sequence KL
    (the per-response mean log-ratio already computed by the trainer).
    """

    target_kl: float = 0.05
    up_rate: float = 1.2
    down_rate: float = 0.9
    min_kl: float = 1e-4
    max_kl: float = 0.5
    beta: float = 0.005

    def update(self, seq_kl: float) -> float:
        if seq_kl > self.target_kl * 1.5:
            self.beta = min(self.max_kl, self.beta * self.up_rate)
        elif seq_kl < self.target_kl * 0.5:
            self.beta = max(self.min_kl, self.beta * self.down_rate)
        return self.beta

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_kl": self.target_kl,
            "up_rate": self.up_rate,
            "down_rate": self.down_rate,
            "min_kl": self.min_kl,
            "max_kl": self.max_kl,
            "beta": self.beta,
        }


@dataclass
class AdaptiveTemperatureState:
    """Tracks consecutive low-reward-signal skips and escalates sampling temperature.

    When all completions in a group score similarly (reward_std < min_reward_std),
    GRPO steps are skipped.  Raising sampling temperature forces more diverse
    completions in the next step, increasing the chance of at least one correct
    answer and breaking the flat-reward deadlock.

    Temperature formula:
        current_temp = min(base_temp * (1 + step_size * consecutive_skips), max_temp)

    Temperature resets to base_temp after any successful gradient update.
    """

    base_temp: float = 0.8
    step_size: float = 0.15
    max_temp: float = 1.4
    consecutive_low_signal_skips: int = 0

    _LOW_SIGNAL_REASON: str = "low_reward_signal"

    def current_temp_at_count(self, count: int) -> float:
        """Return the escalated temperature for a given consecutive-skip count."""
        raw = self.base_temp * (1.0 + self.step_size * count)
        return min(raw, self.max_temp)

    def current_temp(self) -> float:
        """Return the effective sampling temperature given the current skip count."""
        return self.current_temp_at_count(self.consecutive_low_signal_skips)

    def record_skip(self, reason: str) -> None:
        """Update state after a skipped GRPO step.

        Only increments the escalation counter for sampling-diversity
        failures: ``low_reward_signal`` (flat RL groups) and
        ``degenerate_policy`` (2026-08-26 r10 — the EOS-collapse rescue
        alarm: a collapsed policy emitting ~1-token completions at near-zero
        entropy escalates the same ladder so the NEXT group samples more
        diversely). Other skip reasons (empty mask, non-finite loss,
        repair-routing) do not indicate a temperature-diversity problem and
        should not escalate sampling.
        """
        if reason in (self._LOW_SIGNAL_REASON, DEGENERATE_POLICY_REASON):
            self.consecutive_low_signal_skips += 1

    def record_update(self) -> None:
        """Reset the escalation counter after a successful gradient update."""
        self.consecutive_low_signal_skips = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_temp": self.base_temp,
            "step_size": self.step_size,
            "max_temp": self.max_temp,
            "consecutive_low_signal_skips": self.consecutive_low_signal_skips,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AdaptiveTemperatureState:
        return cls(
            base_temp=float(data.get("base_temp", 0.8)),
            step_size=float(data.get("step_size", 0.15)),
            max_temp=float(data.get("max_temp", 1.4)),
            consecutive_low_signal_skips=int(data.get("consecutive_low_signal_skips", 0)),
        )


# ---------------------------------------------------------------------------
# Frontier-Verifier GSPO (FV-GSPO)
#
# Implements the frontier router, mixture sampling, GSPO loss statistics,
# completion entropy, shared-MAD scaling, repair-queue persistence, and the
# circuit-breaker monitor described in docs/frontier-verifier-gspo-design-2026-08-04.md.
# ---------------------------------------------------------------------------

FRONTIER_RL = "frontier_rl"
MASTERED_REPLAY = "mastered_replay"
REPAIR_SFT = "repair_sft"
PARTIAL_REPAIR_RL = "partial_repair_rl"
INVALID_OR_NOISY = "invalid_or_noisy"

RL_ROUTES = frozenset({FRONTIER_RL, PARTIAL_REPAIR_RL})

# 2026-08-26 (r10, run-6 killer): skip reason for the EOS-collapse rescue
# alarm. A collapsed policy (entropy < 0.05 AND ~1-token completions for 3
# consecutive steps) escalates the SAME ladder as low_reward_signal — the
# ladder is the only rescue path, and repair-routing alone never escalates
# (run-6: 16 consecutive repair skips, temp stuck at 1.15, no_trainable_tasks).
DEGENERATE_POLICY_REASON = "degenerate_policy"


@dataclass
class FrontierRouter:
    """Route training tasks by measured frontier learnability and weight sampling.

    Replaces inverse-difficulty-only sampling (``TaskCurriculum.weight``): a task
    is sampled according to

        w_x = c_x [ lambda_f * L_x + lambda_n * sqrt(log(1+N)/(1+n_x)) + lambda_s * S_x ]

    where L_x is learnability (max of binary pass variance and shaped reward
    dispersion), c_x is a training-only coverage need, n_x is the number of
    recent probes, N is the total probe count, and S_x is probe staleness.
    Mastered tasks are downweighted to a small replay quota instead of being
    the most-sampled group (the failure mode of inverse-difficulty sampling).
    """

    frontier_threshold: float = 0.10
    mastered_threshold: float = 0.95
    lambda_frontier: float = 1.0
    lambda_novelty: float = 0.5
    lambda_staleness: float = 0.25
    staleness_half_life: float = 50.0
    unprobed_learnability: float = 0.5
    min_weight: float = 0.05
    mastered_replay_scale: float = 0.15
    ema_decay: float = 0.7
    state: dict[str, dict[str, float]] = field(default_factory=dict)

    min_mastered_samples: int = 32
    repair_threshold: float = 0.10

    # 2026-08-27 (T1b, algorithm audit): lineage difficulty manifest — the
    # v8 tasks that never passed a first-visit probe across run-4..7 (15/20)
    # get a cold-start sampling discount (capability-matched E2H curriculum:
    # RL mass concentrates on the learnable set while hard tasks stay
    # sampleable). The discount floors at ``min_weight`` (NEVER zeroes a task)
    # and is removed the first time the task shows pass>0 in the run. Absent
    # manifest (None) => byte-identical to pre-manifest behavior.
    difficulty_manifest: frozenset[str] | None = None
    difficulty_scale: float = 0.25
    _proven_this_run: set[str] = field(default_factory=set)

    def get_state(self, task_id: str) -> dict[str, float]:
        current = self.state.get(task_id)
        if current is None:
            current = {
                "p_pass_ema": 0.0,
                "shaped_std_ema": 0.0,
                "probes": 0.0,
                "last_probe_step": 0.0,
                "route": "",
                "coverage_need": 1.0,
                "rl_updates": 0.0,
                "posterior_alpha": 1.0,
                "posterior_beta": 1.0,
                "flaky": 0.0,
                "group_size_last": 0.0,
            }
            self.state[task_id] = current
        return current

    def posterior(self, task_id: str) -> BetaPosterior:
        current = self.get_state(task_id)
        return BetaPosterior(
            alpha=float(current["posterior_alpha"]),
            beta=float(current["posterior_beta"]),
        )

    def set_coverage_need(self, task_id: str, need: float) -> None:
        """Coverage need comes from the training-only skill/failure inventory."""
        current = self.get_state(task_id)
        current["coverage_need"] = max(0.0, float(need))

    def load_coverage_map(self, mapping: Mapping[str, float] | None) -> None:
        for task_id, need in (mapping or {}).items():
            self.set_coverage_need(str(task_id), float(need))

    def probe_record(
        self,
        task_id: str,
        step: int,
        pass_rate: float,
        shaped_signal_std: float,
        group_size: int = 8,
        *,
        suppress_repair: bool = False,
    ) -> dict[str, float | str]:
        """Record one G-rollout probe and classify the group's route.

        Posterior routing (review 2026-08-05 #4): the pass posterior
        Beta(alpha_0 + s, beta_0 + f) accumulates successes/failures across
        probes, and routing uses credible intervals with hysteresis (a single
        lucky 8/8 group does NOT mark a task mastered; an all-fail group needs
        accumulating evidence before the repair lane). EMA fields remain for
        stable sampling weights. Oscillating extreme outcomes (1 -> 0 -> 1 or
        0 -> 1 -> 0) flag flakiness and route to quarantine.
        """
        current = self.get_state(task_id)
        probes = float(current["probes"]) + 1.0
        decay = self.ema_decay
        p_pass = decay * float(current["p_pass_ema"]) + (1.0 - decay) * float(pass_rate)
        shaped_std = decay * float(current["shaped_std_ema"]) + (1.0 - decay) * float(
            shaped_signal_std
        )
        current["p_pass_ema"] = p_pass
        current["shaped_std_ema"] = shaped_std
        current["probes"] = probes
        current["last_probe_step"] = float(step)
        current["group_size_last"] = float(max(1, int(group_size)))

        successes = int(round(float(pass_rate) * max(1, int(group_size))))
        failures = max(0, int(group_size) - successes)
        posterior = BetaPosterior(
            alpha=float(current["posterior_alpha"]),
            beta=float(current["posterior_beta"]),
        )
        posterior.update(successes, failures)
        current["posterior_alpha"] = posterior.alpha
        current["posterior_beta"] = posterior.beta

        # Flake detection: extreme outcomes oscillating across consecutive probes.
        history = list(current.get("probe_history") or [])
        history.append(round(float(pass_rate), 3))
        history = history[-3:]
        current["probe_history"] = history
        flaky = (
            len(history) == 3
            and all(rate in (0.0, 1.0) for rate in history)
            and history[0] != history[1]
            and history[1] != history[2]
        )
        current["flaky"] = 1.0 if flaky else 0.0

        current["route"] = classify_posterior_route(
            posterior,
            shaped_signal_std=float(shaped_signal_std),
            flaky=flaky,
            frontier_threshold=self.frontier_threshold,
            mastered_threshold=self.mastered_threshold,
            repair_threshold=self.repair_threshold,
            min_mastered_samples=self.min_mastered_samples,
        )
        if suppress_repair and current["route"] == REPAIR_SFT:
            # 2026-08-27 (T1a, algorithm audit): a collapsed policy must never
            # produce evidence-free quarantines (run-6: ALL 20 tasks incl. the
            # 5 learnable ones were repair-quarantined under the EOS collapse).
            # The group stays in the RL targeted pool under the escalated temp
            # ladder; posterior evidence still accumulates for when the policy
            # recovers.
            current["route"] = FRONTIER_RL
        if float(pass_rate) > 0.0:
            # T1b: first pass>0 in the run proves the task and removes the
            # lineage difficulty discount (full weight restored).
            self._proven_this_run.add(task_id)
        lower, upper = posterior.credible_bounds()
        return {
            "route": current["route"],
            "learnability": frontier_learnability(
                pass_rate=float(pass_rate), shaped_signal_std=float(shaped_signal_std)
            ),
            "p_pass_ema": p_pass,
            "shaped_std_ema": shaped_std,
            "probes": probes,
            "posterior_mean": posterior.mean,
            "posterior_lower": lower,
            "posterior_upper": upper,
            "flaky": flaky,
        }

    def recommended_group_size(self, task_id: str) -> int:
        """Adaptive G (review #4): 4 for fresh/decisive tasks, 16 when the
        posterior straddles a routing boundary, 8 otherwise."""
        current = self.get_state(task_id)
        posterior = BetaPosterior(
            alpha=float(current["posterior_alpha"]),
            beta=float(current["posterior_beta"]),
        )
        if posterior.samples < 2:
            return 4
        mass = posterior.frontier_mass()
        if 0.2 <= mass <= 0.8:
            return 16
        return 8

    def record_rl_update(self, task_id: str) -> None:
        current = self.get_state(task_id)
        current["rl_updates"] = float(current["rl_updates"]) + 1.0

    def mark_repair(self, task_id: str) -> None:
        """Quarantine a proven flat all-fail task from further RL sampling."""
        self.get_state(task_id)["route"] = REPAIR_SFT

    def mark_invalid(self, task_id: str) -> None:
        """Quarantine an unstable/invalid task from further RL sampling."""
        self.get_state(task_id)["route"] = INVALID_OR_NOISY

    def learnability(self, task_id: str) -> float:
        current = self.get_state(task_id)
        if float(current["probes"]) == 0.0:
            return self.unprobed_learnability
        return frontier_learnability(
            pass_rate=float(current["p_pass_ema"]),
            shaped_signal_std=float(current["shaped_std_ema"]),
        )

    def route_of(self, task_id: str) -> str:
        current = self.get_state(task_id)
        # Explicit quarantine decisions are authoritative even when applied
        # before a statistical probe (for example by an external validator).
        if current["route"] in {REPAIR_SFT, INVALID_OR_NOISY}:
            return str(current["route"])
        if float(current["probes"]) == 0.0:
            return ""
        return str(current["route"])

    def staleness(self, task_id: str, step: int) -> float:
        current = self.get_state(task_id)
        if float(current["probes"]) == 0.0:
            return 1.0
        elapsed = max(0.0, float(step) - float(current["last_probe_step"]))
        return min(1.0, elapsed / self.staleness_half_life)

    def novelty_bonus(self, task_id: str, total_probes: int) -> float:
        current = self.get_state(task_id)
        probes = float(current["probes"])
        return math.sqrt(math.log(1.0 + float(max(0, total_probes))) / (1.0 + probes))

    def weight(self, task_id: str, step: int, total_probes: int) -> float:
        current = self.get_state(task_id)
        coverage = max(0.0, float(current["coverage_need"]))
        learn = self.learnability(task_id)
        score = (
            self.lambda_frontier * learn
            + self.lambda_novelty * self.novelty_bonus(task_id, total_probes)
            + self.lambda_staleness * self.staleness(task_id, step)
        )
        weight = coverage * score
        route = self.route_of(task_id)
        if route == MASTERED_REPLAY:
            weight *= self.mastered_replay_scale
        elif route in {REPAIR_SFT, INVALID_OR_NOISY}:
            return self.min_weight
        if (
            self.difficulty_manifest is not None
            and task_id in self.difficulty_manifest
            and task_id not in self._proven_this_run
        ):
            # 2026-08-27 (T1b): lineage difficulty prior — down-weight hard
            # tasks pre-signal. NEVER zero: the max(min_weight, ...) floor
            # below still applies, so hard tasks stay sampleable.
            weight *= self.difficulty_scale
        return max(self.min_weight, weight)

    def frontier_fraction(self) -> float:
        """Fraction of probed tasks currently classified as learnable RL routes."""
        probed = [s for s in self.state.values() if float(s["probes"]) > 0.0]
        if not probed:
            return 0.0
        learnable = [s for s in probed if s["route"] in RL_ROUTES]
        return len(learnable) / len(probed)

    def flat_mastered_share(self) -> float:
        """Share of probed tasks currently routed mastered_replay
        (review #11: reduce replay mass when mastered tasks repeatedly produce
        flat groups)."""
        probed = [s for s in self.state.values() if float(s["probes"]) > 0.0]
        if not probed:
            return 0.0
        mastered = [s for s in probed if s["route"] == MASTERED_REPLAY]
        return len(mastered) / len(probed)


def restore_router_from_record(
    router: FrontierRouter,
    tasks: Sequence[Mapping[str, Any]],
    record: Mapping[str, Any],
    *,
    default_group_size: int,
) -> tuple[str, bool]:
    """Restore one persisted router observation without changing its meaning.

    Historical records sometimes stored ``task_dir.name`` instead of the
    canonical metadata id. Resolve both forms, replay only the policy reward's
    dispersion (not inactive component variance), preserve the recorded group
    size, and restore sticky repair/invalid quarantine after the posterior
    update.
    """
    recorded = str(record.get("task", ""))
    aliases: dict[str, str] = {}
    for task in tasks:
        task_id = str(task.get("task_id", ""))
        if not task_id:
            continue
        aliases[task_id] = task_id
        task_dir = task.get("task_dir")
        if task_dir is not None:
            aliases[Path(task_dir).name] = task_id
    task_id = aliases.get(recorded, recorded)
    probed = False
    pass_rate = record.get("pass_rate")
    if task_id and pass_rate is not None:
        try:
            reward_std = float(record.get("reward_std", 0.0) or 0.0)
        except (TypeError, ValueError):
            reward_std = 0.0
        if not math.isfinite(reward_std):
            reward_std = 0.0
        try:
            group_size = int(record.get("group_size", default_group_size))
        except (TypeError, ValueError):
            group_size = int(default_group_size)
        router.probe_record(
            task_id,
            int(record.get("step", 0)),
            float(pass_rate),
            max(0.0, reward_std),
            group_size=max(1, group_size),
        )
        probed = True

    recorded_route = str(record.get("route", ""))
    if task_id and recorded_route == REPAIR_SFT:
        router.mark_repair(task_id)
    elif task_id and recorded_route == INVALID_OR_NOISY:
        router.mark_invalid(task_id)
    return task_id, probed


def build_mixture_weights(
    router: FrontierRouter,
    tasks: list[dict],
    step: int,
    *,
    mix_targeted: float = 0.5,
    mix_neighbor: float = 0.25,
    mix_replay: float = 0.25,
    recent_frontier: list[str] | None = None,
    neighbor_window: int = 10,
    adaptive: bool = False,
) -> list[float]:
    """Sample weights that mix 50% targeted, 25% neighboring variants, 25% replay.

    With ``adaptive=True`` (review 2026-08-05 #11) the masses respond to router
    state: targeted mass rises with frontier yield (range 0.25-0.75), replay
    mass shrinks when mastered tasks repeatedly produce flat groups, and the
    mixture is renormalized. The fixed 50/25/25 prior is the starting point;
    adaptation never empties a pool.

    - targeted pool: frontier_rl / partial_repair_rl routes plus never-probed tasks
      (probing is the top priority, so fresh tasks are always explorable);
    - neighbor pool: tasks in the same category as a recently selected frontier
      task (generalization across nearby variants of the failed skill);
    - replay pool: mastered_replay tasks.

    Falls back to the targeted pool when no neighbors exist. Unprobed tasks are
    always members of the targeted pool so the router can discover them.
    """
    if len(tasks) == 0:
        return []
    targeted: list[int] = []
    replay: list[int] = []
    quarantined: list[int] = []
    neighbor_categories: set[str] = set()
    recent = list((recent_frontier or [])[-neighbor_window:])
    by_id = {task["task_id"]: task for task in tasks}
    for task_id in recent:
        task = by_id.get(task_id)
        if task is not None:
            category = str(task.get("meta", {}).get("category", "")).strip()
            if category:
                neighbor_categories.add(category)
    for index, task in enumerate(tasks):
        route = router.route_of(task["task_id"])
        if route == MASTERED_REPLAY:
            replay.append(index)
        elif route in {REPAIR_SFT, INVALID_OR_NOISY}:
            quarantined.append(index)
        else:
            targeted.append(index)
    neighbor = [
        index
        for index in targeted
        if index not in replay
        and str(tasks[index].get("meta", {}).get("category", "")).strip() in neighbor_categories
    ]
    if not neighbor:
        neighbor = list(targeted)

    total_probes = int(sum(float(state.get("probes", 0.0)) for state in router.state.values()))

    def _within_pool(indices: list[int], mass: float) -> dict[int, float]:
        if not indices:
            return {}
        raw = {
            index: router.weight(
                tasks[index]["task_id"],
                step=step,
                total_probes=total_probes,
            )
            for index in indices
        }
        raw_total = sum(raw.values())
        if raw_total <= 0.0:
            per = mass / len(indices)
            return {index: per for index in indices}
        return {index: mass * value / raw_total for index, value in raw.items()}

    weights_map: dict[int, float] = {}

    def _accumulate(mass: float, indices: list[int]) -> None:
        for index, per in _within_pool(indices, mass).items():
            weights_map[index] = weights_map.get(index, 0.0) + per

    effective_targeted = float(mix_targeted)
    effective_neighbor = float(mix_neighbor)
    effective_replay = float(mix_replay)
    if adaptive:
        # Frontier yield up -> more targeted (range 0.25..0.75).
        frontier = router.frontier_fraction()
        effective_targeted = 0.25 + 0.5 * frontier
        # Flat mastered groups -> less replay (floor at 0.05).
        effective_replay = max(0.05, float(mix_replay) * (1.0 - router.flat_mastered_share()))
        # Keep the neighbor share relative to the (shrunken) replay share.
        remaining = 1.0 - effective_targeted - effective_replay
        effective_neighbor = max(0.05, remaining)
        scale = 1.0 / (effective_targeted + effective_neighbor + effective_replay)
        effective_targeted *= scale
        effective_neighbor *= scale
        effective_replay *= scale

    _accumulate(effective_targeted, targeted)
    _accumulate(effective_neighbor, neighbor)
    _accumulate(effective_replay, replay)
    total = sum(weights_map.values())
    if total <= 0.0:
        # Every task is quarantined/repair-only. Returning uniform weights here
        # silently resurrects those tasks and burns another rollout group on
        # data that the router already proved unusable for RL. The trainer
        # treats an all-zero vector as an explicit no-trainable-task stop.
        return [0.0] * len(tasks)
    return [weights_map.get(index, 0.0) / total for index in range(len(tasks))]


def sequence_ratio_stats(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    *,
    clip_low: float,
    clip_high: float,
    numerical_log_ratio_clip: float = 8.0,
) -> dict[str, float]:
    """FP32 sequence-ratio statistics for trust-region monitoring.

    With a synchronous one-rollout-per-step implementation the policy at loss
    time equals the rollout policy, so the pre-update ratio is 1 by
    construction and GSPO clipping is inactive (review finding 2026-08-05).
    These stats are measured on the POST-update policy to make the trust
    region observable:

        ratio_before_update  (should be ~1.0; nonzero clip fraction here would
                              indicate stale rollouts or a distribution mismatch)
        ratio_after_update
        clip_fraction_after
        seq_kl_after
    """
    finite_mask = torch.isfinite(log_probs) & torch.isfinite(old_log_probs)
    if not finite_mask.any():
        return {
            "ratio_before_update": 0.0,
            "ratio_after_update": 0.0,
            "clip_fraction_before_update": 0.0,
            "clip_fraction_after_update": 0.0,
            "seq_kl_after": 0.0,
        }
    safe_current = log_probs[finite_mask].float()
    safe_old = old_log_probs[finite_mask].float()
    log_ratio = (safe_current - safe_old).clamp(-numerical_log_ratio_clip, numerical_log_ratio_clip)
    ratio = torch.exp(log_ratio)
    # The responses were sampled from ``old``.  Schulman's non-negative k3
    # estimator for KL(old || current) therefore uses r=current/old:
    # E_old[(r - 1) - log(r)].  The former signed mean(old-current) could be
    # negative and let large probability increases evade the trust region.
    seq_kl = (torch.expm1(log_ratio) - log_ratio).clamp_min(0.0).mean()
    n = float(ratio.numel())
    return {
        "ratio_before_update": float(ratio.mean().item()),
        "ratio_after_update": float(ratio.mean().item()),
        "clip_fraction_before_update": 0.0,  # by construction in synchronous mode
        "clip_fraction_after_update": float(
            ((ratio < 1.0 - clip_low) | (ratio > 1.0 + clip_high)).sum().item() / n
        ),
        "seq_kl_after": float(seq_kl.item()),
    }


def old_sampled_kl(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    *,
    numerical_log_ratio_clip: float = 8.0,
) -> torch.Tensor:
    """Non-negative k3 estimate of ``KL(old || current)`` on old samples.

    If ``x ~ old`` and ``r(x) = current(x) / old(x)``, Schulman's k3
    estimator is ``(r - 1) - log(r)``.  Keeping the direction explicit here
    prevents accidental reuse of the reference-policy formula used by
    frameworks that instead sample from the *current* policy.
    """
    finite_mask = torch.isfinite(log_probs) & torch.isfinite(old_log_probs)
    if not finite_mask.any():
        return log_probs.new_tensor(float("nan"))
    log_ratio = (log_probs[finite_mask].float() - old_log_probs[finite_mask].float()).clamp(
        -numerical_log_ratio_clip,
        numerical_log_ratio_clip,
    )
    return (torch.expm1(log_ratio) - log_ratio).clamp_min(0.0).mean()


def stable_gspo_loss_metrics(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    *,
    clip_low: float,
    clip_high: float,
    kl_coeff: float,
    numerical_log_ratio_clip: float,
    length_weights: torch.Tensor | None = None,
) -> tuple[torch.Tensor, dict[str, float]]:
    """GSPO sequence-level clipped objective with diagnostic statistics.

    The GSPO paper clips the *sequence* importance ratio (already computed by
    the trainer as completion log-probability mean per token). GSPO ratios live
    on a different scale than token PPO ratios, so ``clip_low``/``clip_high``
    are calibrated separately (e.g. 3e-4/4e-4) while
    ``numerical_log_ratio_clip`` remains a wide clamp only for finite
    exponentiation.

    ``length_weights`` (optional, LUSPO-style length neutralization — review
    2026-08-05 #3): the sequence-mean ratio dilutes long responses; multiplying
    each surrogate by w_i = min(|y_i| / L_reference, w_max) neutralizes that
    bias so complete long implementations are not underweighted:

        J = mean_i [ w_i * min(s_i A_i, clip(s_i) A_i) ] - beta * KL

    Returns ``(loss, stats)`` where stats include the low/high clip fractions
    used by the clipping circuit breaker.
    """
    finite_mask = (
        torch.isfinite(log_probs) & torch.isfinite(old_log_probs) & torch.isfinite(advantages)
    )
    nan_loss = log_probs.new_tensor(float("nan"))
    empty_stats = {
        "ratio_mean": 0.0,
        "ratio_median": 0.0,
        "clip_low_fraction": 0.0,
        "clip_high_fraction": 0.0,
        "clip_total_fraction": 0.0,
        "seq_kl": 0.0,
        "length_weight_mean": 0.0,
    }
    if not finite_mask.any():
        return nan_loss, empty_stats

    safe_log_probs = log_probs[finite_mask]
    safe_old_log_probs = old_log_probs[finite_mask].detach()
    safe_advantages = advantages[finite_mask].detach()
    log_ratio = (safe_log_probs - safe_old_log_probs).clamp(
        -numerical_log_ratio_clip,
        numerical_log_ratio_clip,
    )
    sequence_ratio = torch.exp(log_ratio)
    clipped_ratio = sequence_ratio.clamp(1.0 - clip_low, 1.0 + clip_high)
    surrogate = torch.minimum(
        sequence_ratio * safe_advantages,
        clipped_ratio * safe_advantages,
    )
    length_weight_mean = 0.0
    if length_weights is not None:
        safe_weights = length_weights[finite_mask].float().clamp_min(0.0)
        surrogate = surrogate * safe_weights
        length_weight_mean = float(safe_weights.mean().item())
    approximate_kl = old_sampled_kl(
        safe_log_probs,
        safe_old_log_probs,
        numerical_log_ratio_clip=numerical_log_ratio_clip,
    )
    total = -surrogate.mean() + kl_coeff * approximate_kl
    if not torch.isfinite(total):
        return nan_loss, empty_stats

    n = float(sequence_ratio.numel())
    stats = {
        "ratio_mean": float(sequence_ratio.mean().item()),
        "ratio_median": float(sequence_ratio.median().item()),
        "clip_low_fraction": float((sequence_ratio < 1.0 - clip_low).sum().item() / n),
        "clip_high_fraction": float((sequence_ratio > 1.0 + clip_high).sum().item() / n),
        "clip_total_fraction": float(
            ((sequence_ratio < 1.0 - clip_low) | (sequence_ratio > 1.0 + clip_high)).sum().item()
            / n
        ),
        "seq_kl": float(approximate_kl.item()),
        "length_weight_mean": length_weight_mean,
    }
    return total, stats


def sapo_loss_metrics(
    token_log_probs: list[torch.Tensor],
    old_token_log_probs: list[torch.Tensor],
    advantages: torch.Tensor,
    *,
    tau_pos: float,
    tau_neg: float,
    kl_coeff: float,
    numerical_log_ratio_clip: float,
) -> tuple[torch.Tensor, dict[str, float]]:
    """SAPO — Soft Adaptive Policy Optimization (Qwen team, arXiv:2511.20347).

    Replaces GSPO's hard sequence clip with a SMOOTH sigmoid gate g(r) on the
    per-token importance ratio, applied to ALL tokens of each sample:

        r_{i,t}      = exp(cur_lp_{i,t} - old_lp_{i,t})          (token-level)
        g(r)         = (4 / tau) * sigmoid(tau * (r - 1))         (smooth decay)
        tau          = tau_pos if A_i > 0 else tau_neg            (asymmetric)
        L            = -mean_{i,t} [ g(r_{i,t}) * A_i ]
                       + kl * mean[(r_{i,t} - 1) - log(r_{i,t})]

    - No hard clip: the gate continuously attenuates the gradient as the ratio
      drifts (larger tau -> faster decay), keeping a smooth trust region.
      Recommended tau_pos=1.0, tau_neg=1.05 (faster decay for negative-reward
      tokens stabilizes training).
    - SAPO/GRPO aggregation: average tokens within each completion, then
      average completions.  This is deliberately *not* BNPO's global token
      mean: otherwise long completions receive more policy-gradient weight.
    - A_i is the group/LOO advantage, constant across tokens of a sample.

    Args are per-token log-prob lists (one tensor per completion) and the
    per-completion advantages. Returns ``(loss, stats)`` with stats mirroring
    the GSPO record keys (seq_kl, ratio_mean, clip_high_fraction as the
    fraction of tokens whose ratio exceeds the tau-decay knee).

    Training-log instrumentation (2026-08-25): stats additionally carries the
    batch's own ``loss`` value and mean ``advantage`` (plus the existing
    ``n_tokens``), so the trainer's per-candidate records are self-contained
    and the math auditor can recompute the aggregate loss identity
    (``loss_i == -sapo_gate_mean_i * A_i + kl_coeff * seq_kl_i`` per candidate)
    from the persisted JSONL. The trainer calls this function with exactly one
    completion per call, so ``loss``/``advantage`` equal the per-candidate
    values there; for multi-completion calls they are the batch means.
    """
    nan_loss = torch.tensor(float("nan"), dtype=torch.float32)
    empty_stats = {
        "ratio_mean": 0.0,
        "ratio_median": 0.0,
        "clip_low_fraction": 0.0,
        "clip_high_fraction": 0.0,
        "clip_total_fraction": 0.0,
        "seq_kl": 0.0,
        "length_weight_mean": 0.0,
        "sapo_gate_mean": 0.0,
        # Finite token count backing the stats above; lets the trainer
        # token-weight per-candidate stats into a batch-level aggregate
        # (2026-08-22 audit #3) instead of keeping only the last candidate.
        "n_tokens": 0.0,
        # 2026-08-25 instrumentation: the candidate's own loss and advantage.
        "loss": 0.0,
        "advantage": 0.0,
    }
    if not token_log_probs or len(token_log_probs) != len(old_token_log_probs):
        return nan_loss, empty_stats
    if len(token_log_probs) != int(advantages.numel()):
        return nan_loss, empty_stats

    sample_losses: list[torch.Tensor] = []
    sample_kls: list[torch.Tensor] = []
    all_ratio: list[torch.Tensor] = []
    all_gate: list[torch.Tensor] = []
    for i, (cur, old) in enumerate(strict_zip(token_log_probs, old_token_log_probs)):
        if cur is None or old is None or cur.numel() == 0 or old.numel() == 0:
            continue
        n = min(cur.numel(), old.numel())
        cur_t = cur[:n].float()
        old_t = old[:n].float().detach()
        advantage = advantages[i].float().detach()
        finite_mask = torch.isfinite(cur_t) & torch.isfinite(old_t) & torch.isfinite(advantage)
        if not finite_mask.any():
            continue
        cur_t = cur_t[finite_mask]
        old_t = old_t[finite_mask]
        log_ratio = (cur_t - old_t).clamp(-numerical_log_ratio_clip, numerical_log_ratio_clip)
        ratio = torch.exp(log_ratio)
        tau_value = tau_pos if float(advantage.item()) > 0.0 else tau_neg
        tau = torch.tensor(tau_value, dtype=cur_t.dtype, device=cur_t.device)
        gate = (4.0 / tau) * torch.sigmoid(tau * (ratio - 1.0))
        sample_losses.append((-gate * advantage).mean())

        # These tokens were sampled from the rollout/old policy.  For
        # KL(old || current), k3 uses r=current/old, not its reciprocal:
        # (r - 1) - log(r).  The reciprocal direction is appropriate only
        # when the expectation is over current-policy samples.
        sample_kls.append((torch.expm1(log_ratio) - log_ratio).clamp_min(0.0).mean())
        all_ratio.append(ratio.detach())
        all_gate.append(gate.detach())

    if not sample_losses:
        return nan_loss, empty_stats

    approximate_kl = torch.stack(sample_kls).mean()
    total = torch.stack(sample_losses).mean() + kl_coeff * approximate_kl
    if not torch.isfinite(total):
        return nan_loss, empty_stats

    ratio = torch.cat(all_ratio)
    gate = torch.cat(all_gate)
    n = float(ratio.numel())
    knee_pos = 1.0 + 1.0 / max(float(tau_pos), 1e-6)
    knee_neg = 1.0 - 1.0 / max(float(tau_neg), 1e-6)
    stats = {
        "ratio_mean": float(ratio.mean().item()),
        "ratio_median": float(ratio.median().item()),
        "clip_low_fraction": float((ratio < knee_neg).sum().item() / n),
        "clip_high_fraction": float((ratio > knee_pos).sum().item() / n),
        "clip_total_fraction": float(((ratio < knee_neg) | (ratio > knee_pos)).sum().item() / n),
        "seq_kl": float(approximate_kl.item()),
        "length_weight_mean": 0.0,
        "sapo_gate_mean": float(gate.mean().item()),
        "n_tokens": n,
        # 2026-08-25 instrumentation: the value actually returned (equals the
        # per-candidate loss in the trainer's one-candidate-per-call path) and
        # the mean advantage of the batch.
        "loss": float(total.item()),
        "advantage": float(advantages.float().mean().item()),
    }
    return total, stats


def completion_entropy(
    logits: torch.Tensor,
    completion_mask: torch.Tensor,
) -> torch.Tensor:
    """Mean per-token Shannon entropy (nats) over completion tokens.

    Monitors exploration: entropy collapse while frontier yield decreases is a
    circuit-breaker condition (Entropy Mechanism / Clip-Cov).
    """
    safe_logits = torch.nan_to_num(logits.float(), nan=0.0, posinf=50.0, neginf=-50.0)
    log_probs = torch.log_softmax(safe_logits, dim=-1)
    probs = log_probs.exp()
    token_entropy = -(probs * log_probs).sum(dim=-1)
    masked = token_entropy.masked_select(completion_mask.bool())
    if masked.numel() == 0:
        return token_entropy.new_tensor(0.0)
    return masked.mean()


class RunningMAD:
    """Shared (across tasks) running mean-absolute-deviation scale.

    The batch dispersion statistic is the mean absolute deviation from the
    batch mean (``mean(|x - mean(x)|)``) — NOT the median absolute deviation
    and NOT the standard deviation (2026-09-01 research/vigilance: the
    docstring previously said "median"; the implementation, and the
    hand-computed tests, are mean-absolute-deviation).

    Dr.GRPO forbids per-question reward-standard-deviation normalization; a
    single fixed MAD shared by the whole batch is the only allowed batch-level
    scaling and it must not reweight each question by its own variance.
    """

    def __init__(self, decay: float = 0.99, init: float = 1.0) -> None:
        self.decay = decay
        self._mean: float = 0.0
        self._mad: float = float(init)
        self._count: int = 0

    def update(self, values: torch.Tensor) -> float:
        count = values.numel()
        if count == 0:
            return self._mad
        values_np = values.detach().float()
        mean = float(values_np.mean().item())
        mad = float((values_np - mean).abs().mean().item())
        if mad <= 0.0:
            # Flat group: no dispersion evidence (all LOO advantages ~0). Do
            # NOT move the running scale — the old fallback (1.0) pulled the
            # EMA toward 1.0 with weight (1-decay) per flat group, turning
            # shared_mad into a no-op in flat-heavy runs (2026-08-24: run
            # sapo-27b-ai-20260824T075223 kept adv_scale ~0.97-0.99 across
            # 10 steps while true signal-group MAD was ~0.3 -> the intended
            # ~3x advantage amplification never engaged). Flat batches also
            # carry no evidence for the first-batch initialization.
            return self._mad
        if self._count == 0:
            self._mean = mean
            self._mad = mad
        else:
            self._mean = self.decay * self._mean + (1.0 - self.decay) * mean
            self._mad = self.decay * self._mad + (1.0 - self.decay) * mad
        self._count += count
        return self._mad

    @property
    def scale(self) -> float:
        return max(self._mad, 1e-8)


def append_repair_queue_record(path: Path, record: Mapping[str, Any]) -> dict[str, Any]:
    """Append one all-fail repair candidate (execution-grounded, deduplicated).

    The repair SFT/DPO stage consumes this queue; records are deduplicated by
    task id + candidate code hash so repeated all-fail probes do not flood it.
    """
    import hashlib

    persisted = dict(record)
    code = str(record.get("best_code") or "")
    code_hash = hashlib.sha1(code.encode("utf-8")).hexdigest()[:10]
    persisted["code_hash"] = code_hash
    task_id = str(record.get("task_id") or "")
    dedup_key = f"{task_id}:{code_hash}"
    persisted["dedup_key"] = dedup_key
    seen: set[str] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                seen.add(str(json.loads(line).get("dedup_key", "")))
            except json.JSONDecodeError:
                continue
    if dedup_key in seen:
        persisted["duplicate"] = True
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(persisted, sort_keys=True) + "\n")
        persisted["duplicate"] = False
    return persisted


def build_judge_diagnostics_record(
    *,
    task_id: str,
    passed: bool,
    syntax_ok: bool,
    verifier_rate: float,
    model_dim_scores: Mapping[str, float | None],
    runtime_ms: float | None = None,
    step: int | None = None,
) -> dict[str, Any]:
    """One per-candidate judge diagnostic for calibration.

    Consumed by ``scripts/calibrate_model_judge.py``: executable anchors
    (passed / syntax_ok / verifier_rate, optional runtime_ms) paired with the
    frozen judge's per-dimension scores. Dimensions without a usable score are
    stored as None and excluded from calibration.
    """
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "step": step,
        "passed": bool(passed),
        "syntax_ok": bool(syntax_ok),
        "verifier_rate": float(verifier_rate),
        "runtime_ms": runtime_ms,
        "model_dim_scores": {dim: model_dim_scores.get(dim) for dim in MODEL_JUDGE_DIMENSIONS},
    }


def count_repair_conversions(path: Path | None | str) -> int:
    """Number of verified conversion records written by the repair stage."""
    if path is None:
        return 0
    if isinstance(path, str):
        path = Path(path)
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            if bool(json.loads(line).get("converted", False)):
                count += 1
        except json.JSONDecodeError:
            continue
    return count


@dataclass
class CircuitBreakerState:
    """Per-window circuit breakers for FV-GSPO (see design §Monitoring).

    A rule violation inside one evaluation window marks the window bad; a rule
    that stays bad for ``required_windows`` consecutive windows trips and emits
    an event. ``should_stop`` is True when a severe breaker tripped, so the
    trainer can halt a remote run instead of burning NPU-hours on a broken
    policy.
    """

    window_size: int = 10
    required_windows: int = 2
    entropy_baseline_steps: int = 20
    clip_fraction_limit: float = 0.50
    all_fail_share_limit: float = 0.40
    entropy_collapse_ratio: float = 0.5
    frontier_yield_collapse_ratio: float = 0.5
    holdout_drop_limit_pp: float = 3.0

    def __post_init__(self) -> None:
        self._step_facts: list[dict[str, Any]] = []
        self._entropy_baseline: float | None = None
        self._frontier_baseline: float | None = None
        self._window_violations: dict[str, int] = {}
        self._consecutive: dict[str, int] = {}
        self.tripped: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self._holdout_history: list[float] = []
        self._replay_history: list[float] = []
        self._window_count: int = 0

    # -- external eval feeds (used by the monitoring loop / eval gate) --
    def report_holdout_pass1(self, value: float) -> None:
        self._holdout_history.append(float(value))

    def report_replay_pass1(self, value: float) -> None:
        self._replay_history.append(float(value))

    def observe_step(
        self,
        *,
        step: int,
        route: str,
        non_finite: bool,
        clip_fraction: float,
        entropy: float | None,
        repair_queued: bool,
        repair_converted: int,
        all_fail_share: float,
    ) -> None:
        self._step_facts.append(
            {
                "step": step,
                "route": route,
                "non_finite": non_finite,
                "clip_fraction": float(clip_fraction),
                "entropy": entropy,
                "repair_queued": repair_queued,
                "repair_converted": repair_converted,
                "all_fail_share": float(all_fail_share),
            }
        )

    def evaluate(self, *, step: int) -> list[dict[str, Any]]:
        """Close a window (step % window_size == 0) and evaluate all rules.

        Returns newly tripped breakers as events; callers should append them to
        step metrics. Trips are idempotent within a run (a breaker trips once).
        """
        if step <= 0 or step % self.window_size != 0:
            return []
        window = self._step_facts[-self.window_size :]
        if len(window) < self.window_size:
            return []

        entropies = [f["entropy"] for f in window if f["entropy"] is not None]
        if (
            entropies
            and self._entropy_baseline is None
            and len(self._step_facts) >= (self.entropy_baseline_steps + self.window_size)
        ):
            baseline_steps = self._step_facts[: self.entropy_baseline_steps]
            baseline_ent = [f["entropy"] for f in baseline_steps if f["entropy"] is not None]
            if baseline_ent:
                self._entropy_baseline = float(sorted(baseline_ent)[len(baseline_ent) // 2])
        if self._frontier_baseline is None and len(self._step_facts) >= (
            self.entropy_baseline_steps + self.window_size
        ):
            baseline_fracs = [
                f["all_fail_share"] for f in self._step_facts[: self.entropy_baseline_steps]
            ]
            if baseline_fracs:
                self._frontier_baseline = 1.0 - (sum(baseline_fracs) / len(baseline_fracs))

        violations: dict[str, bool] = {}
        non_finite_any = any(f["non_finite"] for f in window)
        violations["non_finite"] = non_finite_any
        clip_mean = sum(f["clip_fraction"] for f in window) / self.window_size
        violations["clip_fraction"] = clip_mean > self.clip_fraction_limit

        entropy_mean = sum(entropies) / len(entropies) if entropies else None
        frontier_yield = 1.0 - (sum(f["all_fail_share"] for f in window) / self.window_size)
        entropy_collapse = False
        if (
            entropy_mean is not None
            and self._entropy_baseline is not None
            and self._frontier_baseline is not None
        ):
            entropy_collapse = (
                entropy_mean < self.entropy_collapse_ratio * self._entropy_baseline
                and frontier_yield < self.frontier_yield_collapse_ratio * self._frontier_baseline
            )
        violations["entropy_collapse"] = entropy_collapse

        all_fail_mean = sum(f["all_fail_share"] for f in window) / self.window_size
        queue_grew = any(f["repair_queued"] for f in window)
        converted_total = max(f["repair_converted"] for f in window)
        violations["all_fail_without_repair"] = (
            all_fail_mean > self.all_fail_share_limit and queue_grew and converted_total == 0
        )

        if len(self._holdout_history) >= 2:
            prev, current = self._holdout_history[-2], self._holdout_history[-1]
            # Values are pass@1 fractions (0.80); the limit is in percentage points.
            violations["holdout_regression"] = (prev - current) * 100.0 > self.holdout_drop_limit_pp
        if len(self._replay_history) >= 2:
            prev, current = self._replay_history[-2], self._replay_history[-1]
            violations["replay_regression"] = (prev - current) * 100.0 > self.holdout_drop_limit_pp

        self._window_count += 1
        newly_tripped: list[dict[str, Any]] = []
        for rule, violated in violations.items():
            if violated:
                self._consecutive[rule] = self._consecutive.get(rule, 0) + 1
            else:
                self._consecutive[rule] = 0
            if self._consecutive[rule] >= self.required_windows and rule not in {
                t.get("breaker") for t in self.tripped
            }:
                event = {
                    "event": "circuit_breaker_trip",
                    "breaker": rule,
                    "step": step,
                    "window": self._window_count,
                    "message": self._describe(rule, window=window),
                }
                self.tripped.append(event)
                self.events.append(event)
                newly_tripped.append(event)
        return newly_tripped

    def _describe(self, rule: str, *, window: list[dict[str, Any]]) -> str:
        if rule == "non_finite":
            return "non-finite loss or gradient persists across windows"
        if rule == "clip_fraction":
            return "GSPO clip fraction exceeds 50% after learning-rate reduction"
        if rule == "entropy_collapse":
            return "generation entropy collapses while frontier yield decreases"
        if rule == "all_fail_without_repair":
            return "all-fail rollout share exceeds 40% without repair conversion"
        if rule == "holdout_regression":
            return "held-out pass@1 drops by more than 3 percentage points"
        if rule == "replay_regression":
            return "broad software replay drops by more than 3 percentage points"
        return f"unknown breaker {rule}"

    @property
    def should_stop(self) -> bool:
        return bool(self.tripped)

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_size": self.window_size,
            "required_windows": self.required_windows,
            "window_count": self._window_count,
            "tripped": list(self.tripped),
            "consecutive": dict(self._consecutive),
            "entropy_baseline": self._entropy_baseline,
        }
