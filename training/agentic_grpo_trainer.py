#!/usr/bin/env python3
"""Trajectory-level GRPO trainer for agentic coding tasks.

This lifts the existing single-shot GRPO path to multi-turn trajectories:

- sample a full tool-using trajectory per group element
- score the final candidate with the existing verifier-aware reward stack
- compute group-relative advantages at the trajectory level
- broadcast each trajectory advantage across the assistant turns in that path
- save wall-clock checkpoints on a fixed cadence for long remote runs
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
import transformers

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.agent_trajectory_rollout import (  # noqa: E402
    AGENT_SYSTEM_PROMPT,
    assistant_logprob_over_trajectory,
    rollout_trajectory,
    summarize_trajectory_behavior,
)
from training.agentic_control_plane_schema import build_run_manifest  # noqa: E402
from training.grpo_trainer import (  # noqa: E402
    build_task_runtime_context,
    discover_tasks,
    evaluate_candidate,
    load_requested_task_ids,
    load_test_harness,
)
from training.grpo_utils import (  # noqa: E402
    AdaptiveTemperatureState,
    TaskCurriculum,
    append_grpo_metric,
    append_grpo_metric_jsonl,
    build_grpo_metrics_payload,
    build_grpo_step_record,
    load_grpo_step_metrics_jsonl,
    reward_signal_stats,
    stable_grpo_loss,
    summarize_python_interface,
)
from training.model_backend import (  # noqa: E402
    run_text_forward_preflight,
    select_transformers_model_loader,
)
from training.qwen_sft_peft import (  # noqa: E402
    apply_selective_training_controls,
    collect_trainable_parameters,
    enable_layernorm_training,
    enforce_min_trainable_parameters,
    enforce_trainable_parameter_budget,
    load_text_preprocessor_backend,
    probe_model_runtime_compat,
    resolve_lora_target_modules,
)
from training.research_plugins import load_research_methods, summarize_methods  # noqa: E402
from training.text_preprocessor_backend import (  # noqa: E402
    build_supervised_text_example,
    pad_supervised_text_batch,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True)
    parser.add_argument(
        "--adapter-init",
        default=None,
        help="Optional PEFT adapter directory to continue from before agentic GRPO updates.",
    )
    parser.add_argument("--tasks-dir", default="evals/tasks")
    parser.add_argument(
        "--resume-from",
        default=None,
        help="Path to a previous grpo_step_metrics.jsonl to resume from.",
    )
    parser.add_argument(
        "--benchmark-file",
        default=None,
        help="Optional text file with task ids to include; '#' comments are ignored.",
    )
    parser.add_argument(
        "--domain-filter",
        nargs="*",
        default=None,
        help="Optional domain allowlist, for example --domain-filter software quantum.",
    )
    parser.add_argument("--output-dir", default="outputs/agentic-grpo-v1")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--group-size", type=int, default=8)
    parser.add_argument("--grpo-steps", type=int, default=100)
    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--kl-coeff", type=float, default=0.05)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument(
        "--adaptive-temp-step",
        type=float,
        default=0.15,
        help="Per-skip temperature escalation factor.",
    )
    parser.add_argument(
        "--adaptive-temp-max",
        type=float,
        default=1.4,
        help="Maximum sampling temperature after adaptive escalation.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--max-seq-length", type=int, default=4096)
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument("--max-test-runs", type=int, default=3)
    parser.add_argument("--log-steps", type=int, default=5)
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument(
        "--training-mode",
        choices=["lora", "native"],
        default="lora",
        help="Use LoRA/PEFT training by default. Use native for dependency-light ASI1 smoke runs.",
    )
    parser.add_argument(
        "--gradient-checkpointing",
        action="store_true",
        help="Enable model gradient checkpointing and disable KV cache to reduce training memory.",
    )
    parser.add_argument(
        "--train-layernorm",
        action="store_true",
        help="Also train LayerNorm/RMSNorm-style normalization parameters alongside LoRA.",
    )
    parser.add_argument(
        "--max-trainable-parameters",
        type=int,
        default=None,
        help="Fail if the trainable parameter count exceeds this budget.",
    )
    parser.add_argument(
        "--min-trainable-parameters",
        type=int,
        default=None,
        help="Fail if the trainable parameter count is below this floor.",
    )
    parser.add_argument(
        "--target-modules",
        nargs="*",
        default=None,
        help="Optional explicit LoRA target module suffixes.",
    )
    parser.add_argument(
        "--target-module-regex",
        nargs="*",
        default=None,
        help="Optional regex patterns matched against full module names.",
    )
    parser.add_argument(
        "--trainable-param-regex",
        nargs="*",
        default=None,
        help="Optional regex allowlist for trainable parameter names.",
    )
    parser.add_argument(
        "--freeze-param-regex",
        nargs="*",
        default=None,
        help="Optional regex denylist for parameter names to freeze after allowlist filtering.",
    )
    parser.add_argument("--reward-pass-weight", type=float, default=0.6)
    parser.add_argument("--reward-syntax-weight", type=float, default=0.1)
    parser.add_argument("--reward-interface-weight", type=float, default=0.15)
    parser.add_argument("--reward-verifier-weight", type=float, default=0.15)
    parser.add_argument(
        "--reward-brevity-weight",
        type=float,
        default=0.0,
        help="Weight for brevity reward; set >0 to break flat-reward deadlocks.",
    )
    parser.add_argument(
        "--reward-import-hygiene-weight",
        type=float,
        default=0.05,
        help="Penalty weight for invented non-stdlib imports on single-file tasks.",
    )
    parser.add_argument(
        "--trajectory-write-bonus",
        type=float,
        default=0.04,
        help="Small agentic reward for trajectories that write or finalize a non-empty candidate.",
    )
    parser.add_argument(
        "--trajectory-final-bonus",
        type=float,
        default=0.02,
        help="Small agentic reward for trajectories that terminate with final_answer.",
    )
    parser.add_argument(
        "--trajectory-timeout-penalty",
        type=float,
        default=0.02,
        help="Small penalty for turn-budget/no-tool trajectories that never write a candidate.",
    )
    parser.add_argument(
        "--trajectory-prewrite-test-penalty",
        type=float,
        default=0.02,
        help="Per-call penalty for run_tests before write_file, capped at two calls.",
    )
    parser.add_argument(
        "--trajectory-repeated-read-penalty",
        type=float,
        default=0.01,
        help="Per-call penalty for repeated read_file before write_file, capped at two calls.",
    )
    parser.add_argument("--brevity-target-lines", type=int, default=40)
    parser.add_argument("--reward-detail-budget-cap", type=int, default=8)
    parser.add_argument("--advantage-clip", type=float, default=2.5)
    parser.add_argument("--ratio-clip-log-delta", type=float, default=8.0)
    parser.add_argument("--logit-clip", type=float, default=50.0)
    parser.add_argument(
        "--min-reward-std",
        type=float,
        default=0.05,
        help="Minimum standard deviation across total or component rewards required to update.",
    )
    parser.add_argument("--curriculum-ema-decay", type=float, default=0.9)
    parser.add_argument("--curriculum-min-weight", type=float, default=0.05)
    parser.add_argument("--curriculum-uncertainty-bonus", type=float, default=0.35)
    parser.add_argument(
        "--quantum-priority",
        type=float,
        default=1.5,
        help="Sampling multiplier for quantum tasks in the adaptive curriculum.",
    )
    parser.add_argument("--research-methods", nargs="*", default=[])
    parser.add_argument(
        "--checkpoint-interval-seconds",
        type=int,
        default=3600,
        help="Wall-clock cadence for intermediate adapter checkpoints.",
    )
    parser.add_argument(
        "--checkpoint-every-steps",
        type=int,
        default=0,
        help="Optional step cadence for intermediate adapter checkpoints; combines with wall-clock cadence.",
    )
    parser.add_argument(
        "--online-eval-benchmark-file",
        default="evals/benchmarks/quantum_generalization_holdout_v1.txt",
        help="Optional held-out benchmark file for lightweight online eval during training.",
    )
    parser.add_argument(
        "--online-eval-every-steps",
        type=int,
        default=8,
        help="Run lightweight held-out online eval every N training steps; set 0 to disable.",
    )
    parser.add_argument(
        "--online-eval-max-tasks",
        type=int,
        default=4,
        help="Maximum number of held-out tasks to audit per online eval run.",
    )
    parser.add_argument(
        "--online-eval-temperature",
        type=float,
        default=0.2,
        help="Sampling temperature for held-out online eval rollouts.",
    )
    parser.add_argument(
        "--live-status-window",
        type=int,
        default=10,
        help="Number of recent training records to summarize in live_status.json.",
    )
    parser.add_argument(
        "--trajectory-health-min-read-before-write-rate",
        type=float,
        default=0.5,
        help="Emit an alert when recent trajectories fall below this read-before-write rate.",
    )
    parser.add_argument(
        "--trajectory-health-min-tests-before-final-rate",
        type=float,
        default=0.4,
        help="Emit an alert when recent final-answer trajectories rarely run tests before finalizing.",
    )
    parser.add_argument(
        "--trajectory-health-max-no-tool-rate",
        type=float,
        default=0.2,
        help="Emit an alert when recent no-tool-call rates get too high.",
    )
    return parser.parse_args()


def build_agentic_prompt(task: dict[str, Any], research_methods: list[Any] | None = None) -> str:
    meta = task["meta"]
    parts: list[str] = []
    if "task_prompt" in meta:
        parts.append(str(meta["task_prompt"]))
    elif "description" in meta:
        parts.append(f"Task: {meta['description']}")
    else:
        parts.append(f"Task: {meta.get('name', task['task_dir'].name)}")

    parts.append(f"Task id: {meta.get('id', task['task_dir'].name)}")
    parts.append(
        f"Domain: {meta.get('domain', 'unknown')}\nCategory: {meta.get('category', 'unknown')}"
    )

    candidate_file = meta.get("candidate_file")
    if candidate_file:
        interface_lines = task.get("required_interface") or summarize_python_interface(
            (task["task_dir"] / candidate_file).read_text(encoding="utf-8")
        )
        if interface_lines:
            parts.append(
                "Required interface:\n" + "\n".join(f"- {line}" for line in interface_lines)
            )

    behavior_hints = task.get("behavior_hints") or []
    if behavior_hints:
        parts.append(
            "Behavioral requirements:\n" + "\n".join(f"- {line}" for line in behavior_hints)
        )

    if task.get("single_file_expected", False):
        parts.append(
            "Implementation constraints:\n"
            f"- Keep the solution self-contained in `{candidate_file}`.\n"
            "- Do not depend on repository-local helpers or invent non-standard modules."
        )

    parts.append(
        "Workflow:\n"
        f"- Read `{candidate_file or 'the candidate file'}` first.\n"
        "- Make minimal targeted repairs.\n"
        "- Run tests before finalizing when the signal is useful.\n"
        "- End by emitting `final_answer` with the full candidate source."
    )
    prompt = "\n\n".join(parts)
    for method in research_methods or []:
        prompt = method.augment_grpo_prompt(prompt, task=task, stage="grpo")
    return prompt


def grpo_loss(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    kl_coeff: float,
    ratio_clip_log_delta: float,
) -> torch.Tensor:
    return stable_grpo_loss(
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=advantages,
        kl_coeff=kl_coeff,
        ratio_clip_log_delta=ratio_clip_log_delta,
    )


def trajectory_behavior_reward(
    trajectory_summary: dict[str, Any], *, terminated: str, args: argparse.Namespace
) -> float:
    tool_counts = dict(trajectory_summary.get("tool_counts") or {})
    write_calls = int(tool_counts.get("write_file", 0))
    final_calls = int(tool_counts.get("final_answer", 0))
    prewrite_tests = int(trajectory_summary.get("run_tests_before_write_calls", 0))
    repeated_reads = int(trajectory_summary.get("repeated_read_calls", 0))
    reward = 0.0
    if write_calls > 0 or final_calls > 0:
        reward += float(args.trajectory_write_bonus)
    if terminated == "final_answer":
        reward += float(args.trajectory_final_bonus)
    reward -= min(prewrite_tests, 2) * float(args.trajectory_prewrite_test_penalty)
    reward -= min(repeated_reads, 2) * float(args.trajectory_repeated_read_penalty)
    if write_calls == 0 and final_calls == 0 and terminated in {"turn_budget", "no_tool_call"}:
        reward -= float(args.trajectory_timeout_penalty)
    return reward


def clear_device_cache(torch_module: Any, device: Any) -> None:
    device_type = getattr(device, "type", str(device)).lower()
    if device_type == "cuda" and torch_module.cuda.is_available():
        torch_module.cuda.empty_cache()
    elif device_type == "npu" and hasattr(torch_module, "npu"):
        try:
            torch_module.npu.empty_cache()
        except Exception:
            pass


def checkpoint_due(*, interval_seconds: int, last_saved_at: float, now: float) -> bool:
    return interval_seconds > 0 and (now - last_saved_at) >= interval_seconds


@dataclass
class WallClockCheckpointState:
    interval_seconds: int
    last_saved_at: float
    every_steps: int = 0
    last_saved_step: int = 0
    saved_count: int = 0

    def due(self, *, now: float, step: int | None = None) -> bool:
        if self.every_steps > 0 and step is not None and step > self.last_saved_step:
            if (step - self.last_saved_step) >= self.every_steps:
                return True
        return checkpoint_due(
            interval_seconds=self.interval_seconds,
            last_saved_at=self.last_saved_at,
            now=now,
        )

    def mark_saved(self, *, now: float, step: int | None = None) -> None:
        self.last_saved_at = now
        if step is not None:
            self.last_saved_step = step
        self.saved_count += 1


def _checkpoint_dir_for_step(output_dir: Path, step: int) -> Path:
    checkpoint_dir = output_dir / "checkpoints" / f"step-{step:05d}"
    if not checkpoint_dir.exists():
        return checkpoint_dir
    suffix = 1
    while True:
        candidate = output_dir / "checkpoints" / f"step-{step:05d}-r{suffix}"
        if not candidate.exists():
            return candidate
        suffix += 1


def save_runtime_checkpoint(
    *,
    output_dir: Path,
    save_model: Any,
    save_backend: Any,
    optimizer: Any,
    adaptive_temp: AdaptiveTemperatureState,
    curriculum: TaskCurriculum,
    step: int,
    metrics_record: dict[str, Any] | None,
    step_metrics_path: Path,
    checkpoint_interval_seconds: int,
) -> Path:
    checkpoint_dir = _checkpoint_dir_for_step(output_dir, step)
    adapter_dir = checkpoint_dir / "adapter"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(save_model, "save_pretrained"):
        save_model.save_pretrained(adapter_dir)
    save_backend.save_pretrained(adapter_dir)
    if step_metrics_path.exists():
        shutil.copy2(step_metrics_path, checkpoint_dir / step_metrics_path.name)
    runtime_state = {
        "step": step,
        "optimizer_state": optimizer.state_dict(),
        "python_random_state": random.getstate(),
        "torch_rng_state": torch.random.get_rng_state(),
        "adaptive_temp_state": adaptive_temp.to_dict(),
        "curriculum_state": dict(curriculum.state),
    }
    if torch.cuda.is_available():
        try:
            runtime_state["cuda_rng_state_all"] = torch.cuda.get_rng_state_all()
        except Exception:
            pass
    if hasattr(torch, "npu"):
        try:
            runtime_state["npu_rng_state_all"] = torch.npu.get_rng_state_all()
        except Exception:
            pass
    torch.save(runtime_state, checkpoint_dir / "runtime_state.pt")
    checkpoint_payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "checkpoint_interval_seconds": checkpoint_interval_seconds,
        "latest_record": metrics_record,
        "adapter_dir": str(adapter_dir),
        "runtime_state_path": str(checkpoint_dir / "runtime_state.pt"),
    }
    (checkpoint_dir / "checkpoint_state.json").write_text(
        json.dumps(checkpoint_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "latest_checkpoint.json").write_text(
        json.dumps({"step": step, "checkpoint_dir": str(checkpoint_dir)}, indent=2) + "\n",
        encoding="utf-8",
    )
    return checkpoint_dir


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        tmp_path = Path(handle.name)
        handle.write(json.dumps(payload, indent=2) + "\n")
    tmp_path.replace(path)


def emit_training_log_event(stage: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    event = {
        "stage": stage,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **(payload or {}),
    }
    print(json.dumps(event, ensure_ascii=False, sort_keys=True), flush=True)
    return event


def build_run_started_log_event_payload(
    *,
    args: argparse.Namespace,
    output_dir: Path,
    requested_task_ids: set[str] | None,
    online_eval_task_ids: set[str] | None,
    allowed_domains: set[str] | None,
    rank: int,
    local_rank: int,
    world_size: int,
    research_methods: list[Any],
    resume_step: int,
) -> dict[str, Any]:
    return {
        "model_name": args.model_name,
        "output_dir": str(output_dir),
        "training_mode": args.training_mode,
        "adapter_init": args.adapter_init,
        "resume_from": args.resume_from,
        "resume_step": resume_step,
        "rank": rank,
        "local_rank": local_rank,
        "world_size": world_size,
        "device": str(args.device),
        "tasks_dir": args.tasks_dir,
        "benchmark_file": args.benchmark_file,
        "requested_task_count": len(requested_task_ids or []),
        "domain_filter": sorted(allowed_domains) if allowed_domains else None,
        "online_eval_benchmark_file": args.online_eval_benchmark_file,
        "online_eval_requested_task_count": len(online_eval_task_ids or []),
        "online_eval_every_steps": args.online_eval_every_steps,
        "online_eval_max_tasks": args.online_eval_max_tasks,
        "group_size": args.group_size,
        "grpo_steps": args.grpo_steps,
        "lr": args.lr,
        "kl_coeff": args.kl_coeff,
        "temperature": args.temperature,
        "max_new_tokens": args.max_new_tokens,
        "max_seq_length": args.max_seq_length,
        "max_turns": args.max_turns,
        "max_test_runs": args.max_test_runs,
        "checkpoint_interval_seconds": args.checkpoint_interval_seconds,
        "checkpoint_every_steps": args.checkpoint_every_steps,
        "reward_weights": {
            "pass": args.reward_pass_weight,
            "syntax": args.reward_syntax_weight,
            "interface": args.reward_interface_weight,
            "verifier": args.reward_verifier_weight,
            "brevity": args.reward_brevity_weight,
            "import_hygiene": args.reward_import_hygiene_weight,
            "trajectory_write_bonus": args.trajectory_write_bonus,
            "trajectory_final_bonus": args.trajectory_final_bonus,
            "trajectory_timeout_penalty": args.trajectory_timeout_penalty,
            "trajectory_prewrite_test_penalty": args.trajectory_prewrite_test_penalty,
            "trajectory_repeated_read_penalty": args.trajectory_repeated_read_penalty,
        },
        "curriculum": {
            "ema_decay": args.curriculum_ema_decay,
            "min_weight": args.curriculum_min_weight,
            "uncertainty_bonus": args.curriculum_uncertainty_bonus,
            "quantum_priority": args.quantum_priority,
        },
        "trajectory_health_thresholds": {
            "min_read_before_write_rate": args.trajectory_health_min_read_before_write_rate,
            "min_tests_before_final_rate": args.trajectory_health_min_tests_before_final_rate,
            "max_no_tool_call_rate": args.trajectory_health_max_no_tool_rate,
        },
        "lora": {
            "rank": args.lora_rank,
            "alpha": args.lora_alpha,
            "target_modules": list(args.target_modules) if args.target_modules else None,
            "target_module_regex": list(args.target_module_regex)
            if args.target_module_regex
            else None,
        },
        "research_methods": summarize_methods(research_methods),
        "log_contract": {
            "stdout_json_stages": [
                "training_run_started",
                "training_task_inventory",
                "model_loader_selected",
                "text_preprocessor_loaded",
                "model_loaded",
                "model_on_device",
                "text_forward_preflight",
                "training_step_summary",
                "checkpoint_saved",
                "online_eval_complete",
                "training_completed",
            ],
            "artifact_files": [
                "run_manifest.json",
                "job_health.json",
                "live_status.json",
                "grpo_step_metrics.jsonl",
                "online_eval_history.jsonl",
                "online_eval_latest.json",
                "checkpoint_history.jsonl",
                "latest_checkpoint.json",
                "run_config.json",
                "grpo_metrics.json",
                "train_log_tail.txt",
            ],
        },
    }


def build_task_inventory_log_event_payload(
    *,
    tasks: list[dict[str, Any]],
    benchmark_file: str | None,
    online_eval_benchmark_file: str | None,
    allowed_domains: set[str] | None,
    research_methods: list[Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    domains = Counter(str((task.get("meta") or {}).get("domain") or "unknown") for task in tasks)
    categories = Counter(
        str((task.get("meta") or {}).get("category") or "unknown") for task in tasks
    )
    task_ids = [
        str(
            task.get("task_id")
            or (task.get("meta") or {}).get("id")
            or task.get("task_dir", "unknown")
        )
        for task in tasks
    ]
    return {
        "task_count": len(tasks),
        "domain_counts": dict(sorted(domains.items())),
        "category_counts": dict(sorted(categories.items())),
        "sample_task_ids": task_ids[:12],
        "benchmark_file": benchmark_file,
        "online_eval_benchmark_file": online_eval_benchmark_file,
        "online_eval_every_steps": args.online_eval_every_steps,
        "domain_filter": sorted(allowed_domains) if allowed_domains else None,
        "group_size": args.group_size,
        "steps": args.grpo_steps,
        "research_methods": summarize_methods(research_methods),
        "checkpoint_interval_seconds": args.checkpoint_interval_seconds,
        "checkpoint_every_steps": args.checkpoint_every_steps,
    }


def safe_payload_preview(value: Any, *, max_chars: int = 240) -> Any:
    if isinstance(value, str):
        return (
            value
            if len(value) <= max_chars
            else value[:max_chars] + f"...[truncated {len(value) - max_chars} chars]"
        )
    if isinstance(value, dict):
        return {
            str(key): safe_payload_preview(item, max_chars=max_chars) for key, item in value.items()
        }
    if isinstance(value, list):
        return [safe_payload_preview(item, max_chars=max_chars) for item in value[:8]]
    return value


def evaluation_component_summary(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    if not evaluations:
        return {}
    numeric_keys = [
        "total_reward",
        "base_total_reward",
        "trajectory_behavior_reward",
        "pass_reward",
        "syntax_reward",
        "interface_reward",
        "verifier_reward",
        "brevity_reward",
        "import_hygiene_reward",
        "failure_count",
        "detail_budget",
    ]
    summary: dict[str, Any] = {}
    for key in numeric_keys:
        values = [float(entry[key]) for entry in evaluations if entry.get(key) is not None]
        if values:
            summary[f"mean_{key}"] = sum(values) / len(values)
            summary[f"min_{key}"] = min(values)
            summary[f"max_{key}"] = max(values)
    failure_categories: Counter[str] = Counter()
    for evaluation in evaluations:
        for detail in evaluation.get("details") or []:
            failure_categories[classify_failure_detail(str(detail))] += 1
    if failure_categories:
        summary["failure_categories"] = dict(sorted(failure_categories.items()))
    return summary


def build_step_log_event_payload(
    *,
    record: dict[str, Any],
    task: dict[str, Any],
    task_weight: float,
    weight_sum: float,
    group_size: int,
    world_size: int,
    rank: int,
    effective_temperature: float,
    adaptive_temp: AdaptiveTemperatureState,
    evaluations: list[dict[str, Any]],
    trajectory_summaries: list[dict[str, Any]],
    checkpoint_state: WallClockCheckpointState,
    latest_checkpoint: dict[str, Any] | None,
    latest_online_eval: dict[str, Any] | None,
) -> dict[str, Any]:
    meta = task.get("meta") or {}
    return {
        "step": record.get("step"),
        "rank": rank,
        "world_size": world_size,
        "training_mode": record.get("training_mode"),
        "skipped": bool(record.get("skipped")),
        "reason": record.get("reason"),
        "loss": record.get("loss"),
        "task": {
            "task_id": task.get("task_id") or meta.get("id") or record.get("task"),
            "name": record.get("task"),
            "domain": record.get("domain") or meta.get("domain"),
            "category": meta.get("category"),
            "candidate_file": meta.get("candidate_file"),
        },
        "curriculum": {
            "selected_task_weight": float(task_weight),
            "weight_sum": float(weight_sum),
            "selection_probability": record.get("curriculum_prob"),
            "task_ema_reward": record.get("task_ema_reward"),
            "task_seen": record.get("task_seen"),
        },
        "sampling": {
            "group_size": group_size,
            "temperature": effective_temperature,
            "adaptive_temperature": adaptive_temp.to_dict(),
        },
        "reward": {
            "mean_reward": record.get("mean_reward"),
            "reward_std": record.get("reward_std"),
            "reward_signal_std": record.get("reward_signal_std"),
            "pass_rate": record.get("pass_rate"),
            "syntax_rate": record.get("syntax_rate"),
            "interface_rate": record.get("interface_rate"),
            "verifier_rate": record.get("verifier_rate"),
            "advantage_scale": record.get("advantage_scale"),
            "components": evaluation_component_summary(evaluations),
        },
        "trajectory_health": {
            "mean_turns": record.get("mean_turns"),
            "mean_test_runs": record.get("mean_test_runs"),
            "termination_counts": record.get("termination_counts") or {},
            "tool_counts": record.get("trajectory_tool_counts") or {},
            "read_before_write_rate": record.get("read_before_write_rate"),
            "tests_before_final_rate": record.get("tests_before_final_rate"),
            "no_tool_call_rate": record.get("no_tool_call_rate"),
            "think_call_rate": record.get("think_call_rate"),
        },
        "checkpoint": {
            "interval_seconds": checkpoint_state.interval_seconds,
            "every_steps": checkpoint_state.every_steps,
            "saved_count": checkpoint_state.saved_count,
            "last_saved_step": checkpoint_state.last_saved_step,
            "latest_step": (latest_checkpoint or {}).get("step"),
            "latest_dir": (latest_checkpoint or {}).get("checkpoint_dir"),
        },
        "online_eval_latest": safe_payload_preview(latest_online_eval),
        "trajectory_samples": safe_payload_preview(trajectory_summaries[:2], max_chars=180),
    }


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def classify_failure_detail(detail: str) -> str:
    text = detail.strip().lower()
    if not text:
        return "unknown"
    if "syntaxerror" in text or "indentationerror" in text:
        return "syntax_error"
    if "modulenotfounderror" in text or "importerror" in text:
        return "import_error"
    if "assert" in text or "expected" in text:
        return "assertion_failure"
    if "attributeerror" in text:
        return "attribute_error"
    if "typeerror" in text:
        return "type_error"
    if "nameerror" in text:
        return "name_error"
    if "valueerror" in text:
        return "value_error"
    if "timeout" in text:
        return "timeout"
    if "runtimeerror" in text:
        return "runtime_error"
    return "other_failure"


def build_live_status_payload(
    *,
    records: list[dict[str, Any]],
    planned_steps: int,
    checkpoint_state: WallClockCheckpointState,
    latest_checkpoint: dict[str, Any] | None,
    latest_online_eval: dict[str, Any] | None,
    world_size: int,
    status: str,
    started_at: float,
    recent_window: int,
    min_read_before_write_rate: float,
    min_tests_before_final_rate: float,
    max_no_tool_rate: float,
) -> dict[str, Any]:
    metrics_payload = build_grpo_metrics_payload(records, planned_steps=planned_steps)
    summary = metrics_payload["summary"]
    recent_records = records[-max(recent_window, 1) :]
    recent_updated = [record for record in recent_records if not bool(record.get("skipped"))]
    recent_rewards = [float(record.get("mean_reward", 0.0)) for record in recent_records]
    recent_pass_rates = [
        float(record["pass_rate"])
        for record in recent_records
        if record.get("pass_rate") is not None
    ]
    recent_loss_values = [
        float(record["loss"]) for record in recent_records if record.get("loss") is not None
    ]
    recent_read_before_write_rates = [
        float(record["read_before_write_rate"])
        for record in recent_records
        if record.get("read_before_write_rate") is not None
    ]
    recent_tests_before_final_rates = [
        float(record["tests_before_final_rate"])
        for record in recent_records
        if record.get("tests_before_final_rate") is not None
    ]
    recent_no_tool_rates = [
        float(record["no_tool_call_rate"])
        for record in recent_records
        if record.get("no_tool_call_rate") is not None
    ]
    recent_think_rates = [
        float(record["think_call_rate"])
        for record in recent_records
        if record.get("think_call_rate") is not None
    ]
    prior_records = (
        records[: -max(recent_window, 1)] if len(records) > max(recent_window, 1) else []
    )
    prior_pass_rates = [
        float(record["pass_rate"])
        for record in prior_records
        if record.get("pass_rate") is not None
    ]
    prior_rewards = [float(record.get("mean_reward", 0.0)) for record in prior_records]
    termination_counts: Counter[str] = Counter()
    for record in recent_records:
        for key, value in dict(record.get("termination_counts") or {}).items():
            termination_counts[str(key)] += int(value)

    regression_alerts: list[dict[str, Any]] = []
    recent_mean_pass_rate = _mean(recent_pass_rates)
    prior_mean_pass_rate = _mean(prior_pass_rates)
    if recent_mean_pass_rate is not None and prior_mean_pass_rate is not None:
        pass_rate_drop = prior_mean_pass_rate - recent_mean_pass_rate
        if pass_rate_drop >= 0.20:
            regression_alerts.append(
                {
                    "kind": "pass_rate_drop",
                    "previous_mean_pass_rate": prior_mean_pass_rate,
                    "recent_mean_pass_rate": recent_mean_pass_rate,
                    "delta": pass_rate_drop,
                    "window": max(recent_window, 1),
                }
            )
    recent_mean_reward = _mean(recent_rewards)
    prior_mean_reward = _mean(prior_rewards)
    if recent_mean_reward is not None and prior_mean_reward is not None:
        reward_drop = prior_mean_reward - recent_mean_reward
        if reward_drop >= 0.30:
            regression_alerts.append(
                {
                    "kind": "reward_drop",
                    "previous_mean_reward": prior_mean_reward,
                    "recent_mean_reward": recent_mean_reward,
                    "delta": reward_drop,
                    "window": max(recent_window, 1),
                }
            )
    latest_eval_pass_rate = None
    if latest_online_eval is not None:
        latest_eval_pass_rate = latest_online_eval.get("pass_rate")
    if recent_mean_pass_rate is not None and latest_eval_pass_rate is not None:
        train_eval_gap = recent_mean_pass_rate - float(latest_eval_pass_rate)
        if train_eval_gap >= 0.30:
            regression_alerts.append(
                {
                    "kind": "train_eval_gap",
                    "recent_train_pass_rate": recent_mean_pass_rate,
                    "latest_eval_pass_rate": float(latest_eval_pass_rate),
                    "delta": train_eval_gap,
                }
            )
    recent_mean_read_before_write = _mean(recent_read_before_write_rates)
    if (
        recent_mean_read_before_write is not None
        and recent_mean_read_before_write < min_read_before_write_rate
    ):
        regression_alerts.append(
            {
                "kind": "trajectory_read_before_write_drop",
                "recent_read_before_write_rate": recent_mean_read_before_write,
                "threshold": min_read_before_write_rate,
            }
        )
    recent_mean_tests_before_final = _mean(recent_tests_before_final_rates)
    if (
        recent_mean_tests_before_final is not None
        and recent_mean_tests_before_final < min_tests_before_final_rate
    ):
        regression_alerts.append(
            {
                "kind": "trajectory_tests_before_final_drop",
                "recent_tests_before_final_rate": recent_mean_tests_before_final,
                "threshold": min_tests_before_final_rate,
            }
        )
    recent_mean_no_tool_rate = _mean(recent_no_tool_rates)
    if recent_mean_no_tool_rate is not None and recent_mean_no_tool_rate > max_no_tool_rate:
        regression_alerts.append(
            {
                "kind": "trajectory_no_tool_rate_high",
                "recent_no_tool_call_rate": recent_mean_no_tool_rate,
                "threshold": max_no_tool_rate,
            }
        )

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "status": status,
        "elapsed_seconds": max(0.0, time.time() - started_at),
        "planned_steps": planned_steps,
        "world_size": world_size,
        "summary": summary,
        "recent": {
            "window": max(recent_window, 1),
            "recorded_steps": len(recent_records),
            "updated_steps": len(recent_updated),
            "mean_reward": recent_mean_reward,
            "mean_pass_rate": recent_mean_pass_rate,
            "mean_loss": _mean(recent_loss_values),
            "mean_read_before_write_rate": recent_mean_read_before_write,
            "mean_tests_before_final_rate": recent_mean_tests_before_final,
            "mean_no_tool_call_rate": recent_mean_no_tool_rate,
            "mean_think_call_rate": _mean(recent_think_rates),
            "termination_counts": dict(sorted(termination_counts.items())),
        },
        "alerts": regression_alerts,
        "last_record": records[-1] if records else None,
        "latest_checkpoint": latest_checkpoint,
        "online_eval_latest": latest_online_eval,
        "wallclock_checkpoints_saved": checkpoint_state.saved_count,
        "checkpoint_every_steps": checkpoint_state.every_steps,
        "last_checkpoint_step": checkpoint_state.last_saved_step,
    }


def build_job_health_payload(
    *,
    args: argparse.Namespace,
    output_dir: Path,
    world_size: int,
    status: str,
    started_at: float,
    records: list[dict[str, Any]],
    latest_checkpoint: dict[str, Any] | None,
) -> dict[str, Any]:
    now = time.time()
    last_record = records[-1] if records else None
    last_record_time = None
    if isinstance(last_record, dict):
        for key in ("timestamp_utc", "timestamp"):
            if isinstance(last_record.get(key), str):
                last_record_time = last_record[key]
                break
    return {
        "schema_version": 1,
        "environment": os.environ.get("HUANXIN_ENV_NAME")
        or os.environ.get("ASI1_AGENTIC_TASK_ENV")
        or "ASI1",
        "huanxin_task_name": os.environ.get("ASI1_AGENTIC_TASK_NAME"),
        "huanxin_task_id": os.environ.get("HUANXIN_TASK_ID"),
        "huanxin_task_status": status,
        "remote_path": str(output_dir),
        "model_name": args.model_name,
        "benchmark_file": args.benchmark_file,
        "online_eval_benchmark_file": args.online_eval_benchmark_file,
        "training_mode": args.training_mode,
        "world_size": world_size,
        "nproc_per_node": world_size,
        "planned_steps": args.grpo_steps,
        "recorded_steps": len(records),
        "last_record_step": int(last_record.get("step", 0))
        if isinstance(last_record, dict)
        else None,
        "last_record_timestamp_utc": last_record_time,
        "last_metric_age_sec": 0.0 if records else None,
        "checkpoint_age_sec": None if latest_checkpoint is None else 0.0,
        "latest_checkpoint_step": (latest_checkpoint or {}).get("step"),
        "latest_checkpoint_dir": (latest_checkpoint or {}).get("checkpoint_dir"),
        "pid_alive": status in {"initializing", "running"},
        "pid": os.getpid(),
        "elapsed_seconds": max(0.0, now - started_at),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def run_online_eval(
    *,
    model: Any,
    tokenizer: Any,
    eval_tasks: list[dict[str, Any]],
    device: Any,
    args: argparse.Namespace,
    research_methods: list[Any],
    step: int,
) -> dict[str, Any]:
    task_results: list[dict[str, Any]] = []
    failure_categories: Counter[str] = Counter()
    termination_counts: Counter[str] = Counter()
    sample_failures: list[str] = []
    tool_counts: Counter[str] = Counter()
    read_before_write_count = 0
    tests_before_final_count = 0
    no_tool_turn_count = 0
    total_turn_count = 0
    think_calls = 0

    for task in eval_tasks[: max(args.online_eval_max_tasks, 0)]:
        prompt = build_agentic_prompt(task, research_methods=research_methods)
        tests_py = task.get("tests_py") or task.get("meta", {}).get("tests_py")
        if not tests_py:
            raise KeyError(
                f"Online eval task {task.get('task_id', '<unknown>')} is missing tests_py"
            )
        test_harness = load_test_harness(tests_py)
        candidate_filename = task["meta"].get("candidate_file") or "candidate.py"
        trajectory = rollout_trajectory(
            model,
            tokenizer,
            task=task,
            test_harness=test_harness,
            user_prompt=prompt,
            device=device,
            max_turns=args.max_turns,
            max_new_tokens=args.max_new_tokens,
            max_seq_length=args.max_seq_length,
            temperature=args.online_eval_temperature,
            candidate_filename=candidate_filename,
            max_test_runs=args.max_test_runs,
        )
        evaluation = evaluate_candidate(
            trajectory.final_candidate,
            test_harness,
            task,
            args,
            research_methods=research_methods,
        )
        termination_counts[trajectory.terminated] += 1
        trajectory_summary = summarize_trajectory_behavior(trajectory)
        for tool_name, count in dict(trajectory_summary.get("tool_counts") or {}).items():
            tool_counts[str(tool_name)] += int(count)
        total_turn_count += int(trajectory_summary.get("turn_count", 0))
        no_tool_turn_count += int(trajectory_summary.get("no_tool_turns", 0))
        think_calls += int(trajectory_summary.get("think_calls", 0))
        if bool(trajectory_summary.get("read_before_write")):
            read_before_write_count += 1
        if bool(trajectory_summary.get("tests_before_final")):
            tests_before_final_count += 1
        details = [str(item).strip() for item in evaluation.get("details", []) if str(item).strip()]
        for detail in details[:2]:
            failure_categories[classify_failure_detail(detail)] += 1
            if len(sample_failures) < 8 and detail not in sample_failures:
                sample_failures.append(detail[:240])
        task_results.append(
            {
                "task_id": task["task_id"],
                "domain": task["meta"].get("domain"),
                "passed": bool(evaluation.get("passed")),
                "total_reward": float(evaluation.get("total_reward", 0.0)),
                "pass_reward": float(evaluation.get("pass_reward", 0.0)),
                "syntax_reward": float(evaluation.get("syntax_reward", 0.0)),
                "interface_reward": float(evaluation.get("interface_reward", 0.0)),
                "verifier_reward": float(evaluation.get("verifier_reward", 0.0)),
                "termination": trajectory.terminated,
                "test_runs": trajectory.test_runs,
                "trajectory_summary": trajectory_summary,
                "details": details[:2],
            }
        )

    pass_rates = [1.0 if result["passed"] else 0.0 for result in task_results]
    total_rewards = [float(result["total_reward"]) for result in task_results]
    syntax_rates = [float(result["syntax_reward"]) for result in task_results]
    interface_rates = [float(result["interface_reward"]) for result in task_results]
    verifier_rates = [float(result["verifier_reward"]) for result in task_results]
    domain_metrics: dict[str, dict[str, Any]] = {}
    for domain in sorted({str(result.get("domain") or "unknown") for result in task_results}):
        domain_results = [
            result for result in task_results if str(result.get("domain") or "unknown") == domain
        ]
        domain_pass_rates = [1.0 if result["passed"] else 0.0 for result in domain_results]
        domain_rewards = [float(result["total_reward"]) for result in domain_results]
        domain_metrics[domain] = {
            "task_count": len(domain_results),
            "pass_rate": _mean(domain_pass_rates),
            "mean_total_reward": _mean(domain_rewards),
        }

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "benchmark_file": args.online_eval_benchmark_file,
        "task_count": len(task_results),
        "pass_rate": _mean(pass_rates),
        "mean_total_reward": _mean(total_rewards),
        "mean_syntax_reward": _mean(syntax_rates),
        "mean_interface_reward": _mean(interface_rates),
        "mean_verifier_reward": _mean(verifier_rates),
        "domain_metrics": domain_metrics,
        "quantum_pass_rate": (domain_metrics.get("quantum") or {}).get("pass_rate"),
        "quantum_task_count": (domain_metrics.get("quantum") or {}).get("task_count", 0),
        "software_pass_rate": (domain_metrics.get("software") or {}).get("pass_rate"),
        "software_task_count": (domain_metrics.get("software") or {}).get("task_count", 0),
        "termination_counts": dict(sorted(termination_counts.items())),
        "tool_counts": dict(sorted(tool_counts.items())),
        "read_before_write_rate": read_before_write_count / max(len(task_results), 1),
        "tests_before_final_rate": tests_before_final_count / max(len(task_results), 1),
        "no_tool_call_rate": no_tool_turn_count / max(total_turn_count, 1),
        "mean_think_calls_per_trajectory": think_calls / max(len(task_results), 1),
        "failure_categories": dict(sorted(failure_categories.items())),
        "sample_failures": sample_failures,
        "tasks": task_results,
    }


def _distributed_barrier(enabled: bool) -> None:
    if enabled:
        torch.distributed.barrier()


def distributed_world_size() -> int:
    return int(os.environ.get("WORLD_SIZE", 1))


def main() -> int:
    args = parse_args()
    research_methods = load_research_methods(args.research_methods)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    step_metrics_path = output_dir / "grpo_step_metrics.jsonl"
    metrics_path = output_dir / "grpo_metrics.json"
    run_config_path = output_dir / "run_config.json"
    checkpoint_history_path = output_dir / "checkpoint_history.jsonl"
    online_eval_history_path = output_dir / "online_eval_history.jsonl"
    online_eval_latest_path = output_dir / "online_eval_latest.json"
    live_status_path = output_dir / "live_status.json"
    job_health_path = output_dir / "job_health.json"
    run_manifest_path = output_dir / "run_manifest.json"
    requested_task_ids = load_requested_task_ids(args.benchmark_file)
    online_eval_task_ids = (
        load_requested_task_ids(args.online_eval_benchmark_file)
        if args.online_eval_benchmark_file
        else None
    )
    allowed_domains = set(args.domain_filter) if args.domain_filter else None

    distributed = "RANK" in os.environ
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    rank = int(os.environ.get("RANK", 0))
    world_size = distributed_world_size()

    if distributed:
        if args.device == "npu":
            import torch_npu  # noqa: F401

            torch.npu.set_device(local_rank)
            device = torch.device(f"npu:{local_rank}")
            torch.distributed.init_process_group(backend="hccl")
        else:
            torch.cuda.set_device(local_rank)
            device = torch.device(f"cuda:{local_rank}")
            torch.distributed.init_process_group(backend="nccl")
    else:
        device = torch.device(args.device)
        if args.device == "npu":
            import torch_npu  # noqa: F401

            torch.npu.set_device(0)

    args.device = device

    resume_step = 0
    resume_metrics: list[dict[str, Any]] = []
    if args.resume_from and rank == 0:
        resume_path = Path(args.resume_from)
        resume_metrics = load_grpo_step_metrics_jsonl(resume_path)
        if resume_metrics:
            resume_step = max(int(r.get("step", 0)) for r in resume_metrics)
            print(
                json.dumps(
                    {
                        "stage": "warm_restart",
                        "resume_from": str(resume_path),
                        "resume_step": resume_step,
                        "prior_records": len(resume_metrics),
                    }
                ),
                flush=True,
            )

    if rank == 0:
        emit_training_log_event(
            "training_run_started",
            build_run_started_log_event_payload(
                args=args,
                output_dir=output_dir,
                requested_task_ids=requested_task_ids,
                online_eval_task_ids=online_eval_task_ids,
                allowed_domains=allowed_domains,
                rank=rank,
                local_rank=local_rank,
                world_size=world_size,
                research_methods=research_methods,
                resume_step=resume_step,
            ),
        )

    if rank == 0:
        if not args.resume_from:
            step_metrics_path.unlink(missing_ok=True)
        metrics_path.unlink(missing_ok=True)
        run_config_path.unlink(missing_ok=True)
        checkpoint_history_path.unlink(missing_ok=True)
        online_eval_history_path.unlink(missing_ok=True)
        online_eval_latest_path.unlink(missing_ok=True)
        live_status_path.unlink(missing_ok=True)
        job_health_path.unlink(missing_ok=True)
        run_manifest_path.unlink(missing_ok=True)
        (output_dir / "latest_checkpoint.json").unlink(missing_ok=True)
        if resume_metrics:
            for prior_record in resume_metrics:
                append_grpo_metric_jsonl(step_metrics_path, prior_record)

    tasks = discover_tasks(
        Path(args.tasks_dir),
        requested_task_ids=requested_task_ids,
        allowed_domains=allowed_domains,
    )
    if not tasks:
        raise ValueError("No agentic GRPO tasks matched the requested filters")
    if rank == 0:
        emit_training_log_event(
            "training_task_inventory",
            build_task_inventory_log_event_payload(
                tasks=tasks,
                benchmark_file=args.benchmark_file,
                online_eval_benchmark_file=args.online_eval_benchmark_file,
                allowed_domains=allowed_domains,
                research_methods=research_methods,
                args=args,
            ),
        )

    from transformers import (
        AutoConfig,
        AutoModelForCausalLM,
        AutoProcessor,
        AutoTokenizer,
        PreTrainedTokenizerFast,
    )

    if args.training_mode == "lora":
        from peft import LoraConfig, PeftModel, TaskType, get_peft_model
    else:
        LoraConfig = PeftModel = TaskType = get_peft_model = None

    try:
        model_loader, runtime_compat, model_loader_metadata = select_transformers_model_loader(
            args.model_name,
            auto_config_cls=AutoConfig,
            auto_model_for_causal_lm_cls=AutoModelForCausalLM,
            transformers_module=transformers,
        )
    except SystemExit as exc:
        runtime_compat = probe_model_runtime_compat(args.model_name, AutoConfig)
        print(
            json.dumps(
                {
                    "stage": "trainer_backend_preflight",
                    "state": "blocked",
                    "model_type": (runtime_compat or {}).get("config_model_type"),
                    "architectures": (runtime_compat or {}).get("config_architectures"),
                    "error": str(exc),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        raise
    if rank == 0:
        print(
            json.dumps(
                {"stage": "model_loader_selected", **model_loader_metadata}, ensure_ascii=False
            ),
            flush=True,
        )

    text_preprocessor = load_text_preprocessor_backend(
        args.model_name,
        AutoTokenizer,
        AutoProcessor,
        PreTrainedTokenizerFast,
    )
    tokenizer = text_preprocessor.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    if rank == 0:
        print(
            json.dumps(
                {
                    "stage": "text_preprocessor_loaded",
                    "backend_kind": text_preprocessor.backend_kind,
                    "render_backend_class": text_preprocessor.render_backend.__class__.__name__,
                    "text_backend_class": text_preprocessor.text_backend.__class__.__name__,
                    "save_backend_class": text_preprocessor.save_backend.__class__.__name__,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    for task in tasks:
        task.update(
            build_task_runtime_context(task, detail_budget_cap=args.reward_detail_budget_cap)
        )

    online_eval_tasks: list[dict[str, Any]] = []
    if online_eval_task_ids is not None:
        online_eval_tasks = discover_tasks(
            Path(args.tasks_dir),
            requested_task_ids=online_eval_task_ids,
            allowed_domains=None,
        )
        for task in online_eval_tasks:
            task.update(
                build_task_runtime_context(task, detail_budget_cap=args.reward_detail_budget_cap)
            )
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "online_eval_tasks_ready",
                        "task_count": len(online_eval_tasks),
                        "benchmark_file": args.online_eval_benchmark_file,
                    }
                ),
                flush=True,
            )

    preflight_task = tasks[0]
    preflight_task_id = preflight_task["meta"].get("id", preflight_task["task_dir"].name)
    preflight_record = {
        "example_id": f"agentic-grpo-preflight-{preflight_task_id}",
        "messages": [
            {
                "role": "system",
                "content": AGENT_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_agentic_prompt(preflight_task, research_methods=research_methods),
            },
            {
                "role": "assistant",
                "content": '{"tool": "final_answer", "content": "pass"}',
            },
        ],
    }
    preflight_example = build_supervised_text_example(
        preflight_record,
        text_preprocessor,
        args.max_seq_length,
        train_on_completions_only=True,
    )
    needs_mm_token_type_ids = str(
        runtime_compat.get("config_model_type") if runtime_compat is not None else ""
    ).startswith("gemma4")
    preflight_batch = pad_supervised_text_batch(
        [preflight_example],
        text_preprocessor.text_backend,
        torch,
        add_mm_token_type_ids=needs_mm_token_type_ids,
    )

    model = model_loader.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        torch_dtype="auto",
        local_files_only=True,
    )
    if rank == 0:
        print(
            json.dumps(
                {"stage": "model_loaded", "model_class": model.__class__.__name__},
                ensure_ascii=False,
            ),
            flush=True,
        )
    if args.adapter_init and args.training_mode != "lora":
        raise SystemExit("--adapter-init requires --training-mode lora")
    if args.adapter_init:
        model = PeftModel.from_pretrained(model, str(args.adapter_init), is_trainable=True)
        resolved_target_modules = None
    elif args.training_mode == "lora":
        resolved_target_modules = resolve_lora_target_modules(
            args.target_modules,
            model,
            args.target_module_regex,
        )
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            target_modules=resolved_target_modules,
            bias="none",
        )
        model = get_peft_model(model, lora_config)
    else:
        resolved_target_modules = None
        for parameter in model.parameters():
            parameter.requires_grad = False
        selected_name = None
        for name, parameter in reversed(list(model.named_parameters())):
            if parameter.is_floating_point() and parameter.ndim >= 1:
                parameter.requires_grad = True
                selected_name = name
                break
        if selected_name is None:
            raise SystemExit("Unable to find a floating-point parameter for native smoke training.")
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "native_training_mode_enabled",
                        "trainable_parameter": selected_name,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    if args.gradient_checkpointing:
        if hasattr(model, "config"):
            model.config.use_cache = False
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
        if hasattr(model, "gradient_checkpointing_enable"):
            model.gradient_checkpointing_enable()
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "gradient_checkpointing_enabled",
                        "use_cache": getattr(getattr(model, "config", None), "use_cache", None),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    layernorm_training = {
        "enabled": False,
        "trainable_layernorm_count": 0,
        "trainable_layernorm_parameter_count": 0,
    }
    if args.training_mode == "lora" and args.train_layernorm:
        layernorm_training = enable_layernorm_training(model)
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "layernorm_training_enabled",
                        **layernorm_training,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    selective_training = apply_selective_training_controls(
        model,
        trainable_param_regex=getattr(args, "trainable_param_regex", None),
        freeze_param_regex=getattr(args, "freeze_param_regex", None),
    )
    trainable_param_tensors, trainable_param_names, trainable_param_count = (
        collect_trainable_parameters(model)
    )
    trainable_parameter_budget = enforce_trainable_parameter_budget(
        trainable_param_count,
        args.max_trainable_parameters,
    )
    trainable_parameter_floor = enforce_min_trainable_parameters(
        trainable_param_count,
        args.min_trainable_parameters,
    )
    if rank == 0:
        print(
            json.dumps(
                {
                    "stage": "selective_training_applied",
                    **selective_training,
                    "layernorm_training": layernorm_training,
                    "trainable_parameter_budget": trainable_parameter_budget,
                    "trainable_parameter_floor": trainable_parameter_floor,
                    "trainable_parameter_count": trainable_param_count,
                    "trainable_parameter_sample": trainable_param_names[:12],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    model.to(device)
    if rank == 0:
        print(
            json.dumps({"stage": "model_on_device", "device": str(device)}, ensure_ascii=False),
            flush=True,
        )
    text_forward_preflight = run_text_forward_preflight(
        model,
        preflight_batch,
        torch_module=torch,
        device=device,
    )
    if rank == 0:
        print(
            json.dumps(
                {"stage": "text_forward_preflight", **text_forward_preflight}, ensure_ascii=False
            ),
            flush=True,
        )

    if distributed:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])
        if rank == 0:
            print(json.dumps({"stage": "ddp_wrapped"}, ensure_ascii=False), flush=True)

    optimizer = torch.optim.AdamW(trainable_param_tensors, lr=args.lr)
    metrics = list(resume_metrics)
    curriculum = TaskCurriculum(
        ema_decay=args.curriculum_ema_decay,
        min_weight=args.curriculum_min_weight,
        quantum_priority=args.quantum_priority,
        uncertainty_bonus=args.curriculum_uncertainty_bonus,
    )
    adaptive_temp = AdaptiveTemperatureState(
        base_temp=args.temperature,
        step_size=args.adaptive_temp_step,
        max_temp=args.adaptive_temp_max,
    )
    for prior in resume_metrics:
        task_name = str(prior.get("task", ""))
        mean_reward = float(prior.get("mean_reward", 0.0))
        if task_name:
            curriculum.record(task_name, mean_reward)
        if bool(prior.get("skipped")) and prior.get("reason") == "low_reward_signal":
            adaptive_temp.record_skip("low_reward_signal")
        elif not bool(prior.get("skipped")):
            adaptive_temp.record_update()

    checkpoint_state = WallClockCheckpointState(
        interval_seconds=args.checkpoint_interval_seconds,
        last_saved_at=time.time(),
        every_steps=args.checkpoint_every_steps,
        last_saved_step=resume_step,
    )
    started_at = time.time()
    latest_checkpoint_payload: dict[str, Any] | None = None
    latest_online_eval_payload: dict[str, Any] | None = None

    if rank == 0:
        run_manifest = build_run_manifest(
            run_id=output_dir.name,
            created_at_utc=datetime.now(timezone.utc).isoformat(),
            trainer="training/agentic_grpo_trainer.py",
            model_name=args.model_name,
            output_dir=str(output_dir),
            tasks_dir=args.tasks_dir,
            benchmark_file=args.benchmark_file,
            planned_steps=args.grpo_steps,
            group_size=args.group_size,
            max_turns=args.max_turns,
            max_test_runs=args.max_test_runs,
            artifact_paths={
                "run_config": str(run_config_path),
                "step_metrics_jsonl": str(step_metrics_path),
                "agentic_trace_jsonl": str(output_dir / "agentic_trace.jsonl"),
                "live_status": str(live_status_path),
                "adapter_dir": str(output_dir / "final_adapter"),
            },
            extra={
                "environment": os.environ.get("HUANXIN_ENV_NAME")
                or os.environ.get("ASI1_AGENTIC_TASK_ENV")
                or "ASI1",
                "training_mode": args.training_mode,
                "adapter_init": args.adapter_init,
                "online_eval_benchmark_file": args.online_eval_benchmark_file,
                "online_eval_every_steps": args.online_eval_every_steps,
                "online_eval_max_tasks": args.online_eval_max_tasks,
                "checkpoint_interval_seconds": args.checkpoint_interval_seconds,
                "checkpoint_every_steps": args.checkpoint_every_steps,
                "world_size": world_size,
                "lora": {
                    "rank": args.lora_rank,
                    "alpha": args.lora_alpha,
                    "target_modules": list(args.target_modules) if args.target_modules else None,
                    "target_module_regex": list(args.target_module_regex)
                    if args.target_module_regex
                    else None,
                },
                "research_methods": summarize_methods(research_methods),
                "command": " ".join(sys.argv),
            },
        )
        write_json_atomic(run_manifest_path, run_manifest)

    def persist_live_status(*, status: str) -> None:
        if rank != 0:
            return
        job_health = build_job_health_payload(
            args=args,
            output_dir=output_dir,
            world_size=world_size,
            status=status,
            started_at=started_at,
            records=metrics,
            latest_checkpoint=latest_checkpoint_payload,
        )
        payload = build_live_status_payload(
            records=metrics,
            planned_steps=args.grpo_steps,
            checkpoint_state=checkpoint_state,
            latest_checkpoint=latest_checkpoint_payload,
            latest_online_eval=latest_online_eval_payload,
            world_size=world_size,
            status=status,
            started_at=started_at,
            recent_window=args.live_status_window,
            min_read_before_write_rate=args.trajectory_health_min_read_before_write_rate,
            min_tests_before_final_rate=args.trajectory_health_min_tests_before_final_rate,
            max_no_tool_rate=args.trajectory_health_max_no_tool_rate,
        )
        payload["job_health"] = job_health
        write_json_atomic(live_status_path, payload)
        write_json_atomic(job_health_path, job_health)

    def maybe_save_checkpoint(step: int, record: dict[str, Any]) -> None:
        nonlocal latest_checkpoint_payload
        should_save = rank == 0 and checkpoint_state.due(now=time.time(), step=step)
        if distributed:
            flag = torch.tensor([1 if should_save else 0], device=device, dtype=torch.int32)
            torch.distributed.broadcast(flag, src=0)
            should_save = bool(flag.item())
        if should_save:
            checkpoint_dir = save_runtime_checkpoint(
                output_dir=output_dir,
                save_model=model.module if distributed else model,
                save_backend=text_preprocessor.save_backend,
                optimizer=optimizer,
                adaptive_temp=adaptive_temp,
                curriculum=curriculum,
                step=step,
                metrics_record=record,
                step_metrics_path=step_metrics_path,
                checkpoint_interval_seconds=args.checkpoint_interval_seconds,
            )
            checkpoint_state.mark_saved(now=time.time(), step=step)
            latest_checkpoint_payload = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "step": step,
                "checkpoint_dir": str(checkpoint_dir),
                "saved_count": checkpoint_state.saved_count,
                "checkpoint_interval_seconds": args.checkpoint_interval_seconds,
                "checkpoint_every_steps": args.checkpoint_every_steps,
                "latest_record": record,
            }
            append_grpo_metric_jsonl(checkpoint_history_path, latest_checkpoint_payload)
            write_json_atomic(output_dir / "latest_checkpoint.json", latest_checkpoint_payload)
            emit_training_log_event(
                "checkpoint_saved",
                {
                    "step": step,
                    "checkpoint_dir": str(checkpoint_dir),
                    "adapter_dir": str(checkpoint_dir / "adapter"),
                    "runtime_state_path": str(checkpoint_dir / "runtime_state.pt"),
                    "saved_count": checkpoint_state.saved_count,
                    "checkpoint_interval_seconds": args.checkpoint_interval_seconds,
                    "checkpoint_every_steps": args.checkpoint_every_steps,
                    "latest_record": safe_payload_preview(record),
                },
            )
            _distributed_barrier(distributed)
        elif distributed:
            _distributed_barrier(distributed)

    def maybe_run_online_eval(step: int) -> None:
        nonlocal latest_online_eval_payload
        should_run = (
            args.online_eval_every_steps > 0
            and bool(online_eval_tasks)
            and step % args.online_eval_every_steps == 0
        )
        if distributed:
            flag = torch.tensor(
                [1 if (rank == 0 and should_run) else 0], device=device, dtype=torch.int32
            )
            torch.distributed.broadcast(flag, src=0)
            should_run = bool(flag.item())
        if should_run:
            active_model = model.module if distributed else model
            was_training = bool(getattr(active_model, "training", False))
            active_model.eval()
            if rank == 0:
                latest_online_eval_payload = run_online_eval(
                    model=active_model,
                    tokenizer=tokenizer,
                    eval_tasks=online_eval_tasks,
                    device=device,
                    args=args,
                    research_methods=research_methods,
                    step=step,
                )
            if hasattr(active_model, "train"):
                active_model.train(was_training)
            if rank == 0 and latest_online_eval_payload is not None:
                append_grpo_metric_jsonl(online_eval_history_path, latest_online_eval_payload)
                write_json_atomic(online_eval_latest_path, latest_online_eval_payload)
                emit_training_log_event(
                    "online_eval_complete",
                    {
                        "step": step,
                        "task_count": latest_online_eval_payload.get("task_count"),
                        "pass_rate": latest_online_eval_payload.get("pass_rate"),
                        "quantum_pass_rate": latest_online_eval_payload.get("quantum_pass_rate"),
                        "software_pass_rate": latest_online_eval_payload.get("software_pass_rate"),
                        "mean_total_reward": latest_online_eval_payload.get("mean_total_reward"),
                        "domain_metrics": latest_online_eval_payload.get("domain_metrics"),
                        "termination_counts": latest_online_eval_payload.get("termination_counts"),
                        "failure_categories": latest_online_eval_payload.get("failure_categories"),
                        "sample_failures": latest_online_eval_payload.get("sample_failures"),
                    },
                )
            _distributed_barrier(distributed)
        elif distributed:
            _distributed_barrier(distributed)

    persist_live_status(status="initializing")

    random.seed(42 + rank)

    def persist_and_log_record(
        *,
        record: dict[str, Any],
        task: dict[str, Any],
        task_weight: float,
        weight_sum: float,
        effective_temperature: float,
        evaluations: list[dict[str, Any]],
        trajectory_summaries: list[dict[str, Any]],
    ) -> None:
        if rank != 0:
            return
        append_grpo_metric(metrics, record=record)
        append_grpo_metric_jsonl(step_metrics_path, record)
        emit_training_log_event(
            "training_step_summary",
            build_step_log_event_payload(
                record=record,
                task=task,
                task_weight=task_weight,
                weight_sum=weight_sum,
                group_size=args.group_size,
                world_size=world_size,
                rank=rank,
                effective_temperature=effective_temperature,
                adaptive_temp=adaptive_temp,
                evaluations=evaluations,
                trajectory_summaries=trajectory_summaries,
                checkpoint_state=checkpoint_state,
                latest_checkpoint=latest_checkpoint_payload,
                latest_online_eval=latest_online_eval_payload,
            ),
        )
        persist_live_status(status="running")

    for step in range(1, args.grpo_steps + 1):
        if step <= resume_step:
            continue

        weights = []
        for task in tasks:
            weight = curriculum.weight(task["task_id"], task["meta"].get("domain"))
            for method in research_methods:
                weight = max(0.0, float(method.adjust_task_weight(weight, task=task, stage="grpo")))
            weights.append(weight)
        weight_sum = sum(weights)
        task_index = random.choices(range(len(tasks)), weights=weights, k=1)[0]
        task = tasks[task_index]
        task_prob = weights[task_index] / weight_sum if weight_sum > 0 else 1.0 / len(tasks)
        prompt = build_agentic_prompt(task, research_methods=research_methods)
        test_harness = load_test_harness(task["tests_py"])
        candidate_filename = task["meta"].get("candidate_file") or "candidate.py"

        active_model = model.module if distributed else model
        active_model.eval()
        effective_temperature = adaptive_temp.current_temp()
        trajectories = [
            rollout_trajectory(
                active_model,
                tokenizer,
                task=task,
                test_harness=test_harness,
                user_prompt=prompt,
                device=device,
                max_turns=args.max_turns,
                max_new_tokens=args.max_new_tokens,
                max_seq_length=args.max_seq_length,
                temperature=effective_temperature,
                candidate_filename=candidate_filename,
                max_test_runs=args.max_test_runs,
            )
            for _ in range(args.group_size)
        ]

        trajectory_summaries = [
            summarize_trajectory_behavior(trajectory) for trajectory in trajectories
        ]
        evaluations = []
        for trajectory, trajectory_summary in zip(trajectories, trajectory_summaries, strict=False):
            evaluation = evaluate_candidate(
                trajectory.final_candidate,
                test_harness,
                task,
                args,
                research_methods=research_methods,
            )
            behavior_reward = trajectory_behavior_reward(
                trajectory_summary,
                terminated=trajectory.terminated,
                args=args,
            )
            evaluation = dict(evaluation)
            evaluation["base_total_reward"] = float(evaluation.get("total_reward", 0.0))
            evaluation["trajectory_behavior_reward"] = behavior_reward
            evaluation["total_reward"] = (
                float(evaluation.get("total_reward", 0.0)) + behavior_reward
            )
            evaluations.append(evaluation)
        rewards = torch.tensor(
            [float(entry["total_reward"]) for entry in evaluations], device=device
        )
        pass_rewards = torch.tensor(
            [float(entry["pass_reward"]) for entry in evaluations], device=device
        )
        syntax_rewards = torch.tensor(
            [float(entry["syntax_reward"]) for entry in evaluations], device=device
        )
        interface_rewards = torch.tensor(
            [float(entry["interface_reward"]) for entry in evaluations], device=device
        )
        verifier_rewards = torch.tensor(
            [float(entry["verifier_reward"]) for entry in evaluations], device=device
        )
        brevity_rewards = torch.tensor(
            [float(entry.get("brevity_reward", 0.0)) for entry in evaluations], device=device
        )

        with torch.no_grad():
            old_log_probs = []
            old_token_counts = []
            for trajectory in trajectories:
                old_log_prob, old_token_count = assistant_logprob_over_trajectory(
                    active_model,
                    tokenizer,
                    trajectory=trajectory,
                    device=device,
                    logit_clip=args.logit_clip,
                    max_seq_length=args.max_seq_length,
                )
                old_log_probs.append(old_log_prob.detach())
                old_token_counts.append(old_token_count.detach())
        old_log_probs_tensor = torch.stack(old_log_probs)
        old_token_counts_tensor = torch.stack(old_token_counts)

        mean_reward = rewards.mean()
        signal_stats = reward_signal_stats(
            rewards,
            pass_rewards,
            syntax_rewards,
            interface_rewards,
            verifier_rewards,
            brevity_rewards,
        )
        std_reward = rewards.std(unbiased=False)
        advantage_scale = max(signal_stats["signal_std"], float(std_reward.item()), 1e-8)
        advantages = ((rewards - mean_reward) / advantage_scale).clamp(
            -args.advantage_clip,
            args.advantage_clip,
        )
        task_state = curriculum.record(task["task_id"], float(mean_reward))

        base_record = build_grpo_step_record(
            step=step,
            task_name=task["task_dir"].name,
            domain=task["meta"].get("domain", "?"),
            mean_reward=float(mean_reward),
            signal_stats=signal_stats,
            pass_rate=float(pass_rewards.mean()),
            syntax_rate=float(syntax_rewards.mean()),
            interface_rate=float(interface_rewards.mean()),
            verifier_rate=float(verifier_rewards.mean()),
            task_prob=float(task_prob),
            task_state=task_state,
            advantage_scale=advantage_scale,
            adapter_init=args.adapter_init,
        )
        base_record["mean_turns"] = sum(len(t.turns) for t in trajectories) / max(
            len(trajectories), 1
        )
        base_record["mean_test_runs"] = sum(t.test_runs for t in trajectories) / max(
            len(trajectories), 1
        )
        base_record["termination_counts"] = dict(
            sorted(Counter(t.terminated for t in trajectories).items())
        )
        tool_counts: Counter[str] = Counter()
        read_before_write_hits = 0
        tests_before_final_hits = 0
        no_tool_turns = 0
        total_turns = 0
        think_calls = 0
        for summary in trajectory_summaries:
            for tool_name, count in dict(summary.get("tool_counts") or {}).items():
                tool_counts[str(tool_name)] += int(count)
            total_turns += int(summary.get("turn_count", 0))
            no_tool_turns += int(summary.get("no_tool_turns", 0))
            think_calls += int(summary.get("think_calls", 0))
            if bool(summary.get("read_before_write")):
                read_before_write_hits += 1
            if bool(summary.get("tests_before_final")):
                tests_before_final_hits += 1
        base_record["trajectory_tool_counts"] = dict(sorted(tool_counts.items()))
        base_record["read_before_write_rate"] = read_before_write_hits / max(
            len(trajectory_summaries), 1
        )
        base_record["tests_before_final_rate"] = tests_before_final_hits / max(
            len(trajectory_summaries), 1
        )
        base_record["no_tool_call_rate"] = no_tool_turns / max(total_turns, 1)
        base_record["think_call_rate"] = think_calls / max(len(trajectory_summaries), 1)
        base_record["training_mode"] = args.training_mode

        if signal_stats["signal_std"] < args.min_reward_std:
            adaptive_temp.record_skip("low_reward_signal")
            record = dict(base_record)
            record["skipped"] = True
            record["reason"] = "low_reward_signal"
            persist_and_log_record(
                record=record,
                task=task,
                task_weight=weights[task_index],
                weight_sum=weight_sum,
                effective_temperature=effective_temperature,
                evaluations=evaluations,
                trajectory_summaries=trajectory_summaries,
            )
            maybe_save_checkpoint(step, record)
            maybe_run_online_eval(step)
            clear_device_cache(torch, device)
            if rank == 0:
                persist_live_status(status="running")
            continue

        active_model.train()
        current_log_probs = []
        normalized_old_log_probs = []
        filtered_advantages = []
        for index, trajectory in enumerate(trajectories):
            current_log_prob, token_count = assistant_logprob_over_trajectory(
                active_model,
                tokenizer,
                trajectory=trajectory,
                device=device,
                logit_clip=args.logit_clip,
                max_seq_length=args.max_seq_length,
            )
            if token_count.item() == 0:
                continue
            current_log_probs.append(current_log_prob / token_count.clamp_min(1))
            normalized_old_log_probs.append(
                old_log_probs_tensor[index] / old_token_counts_tensor[index].clamp_min(1)
            )
            filtered_advantages.append(advantages[index])

        if not current_log_probs:
            adaptive_temp.record_skip("empty_completion_mask")
            record = dict(base_record)
            record["skipped"] = True
            record["reason"] = "empty_completion_mask"
            persist_and_log_record(
                record=record,
                task=task,
                task_weight=weights[task_index],
                weight_sum=weight_sum,
                effective_temperature=effective_temperature,
                evaluations=evaluations,
                trajectory_summaries=trajectory_summaries,
            )
            maybe_save_checkpoint(step, record)
            maybe_run_online_eval(step)
            clear_device_cache(torch, device)
            if rank == 0:
                persist_live_status(status="running")
            continue

        total_loss = grpo_loss(
            torch.stack(current_log_probs),
            torch.stack(normalized_old_log_probs),
            torch.stack(filtered_advantages),
            args.kl_coeff,
            args.ratio_clip_log_delta,
        )
        if not torch.isfinite(total_loss):
            adaptive_temp.record_skip("non_finite_loss")
            record = dict(base_record)
            record["skipped"] = True
            record["reason"] = "non_finite_loss"
            persist_and_log_record(
                record=record,
                task=task,
                task_weight=weights[task_index],
                weight_sum=weight_sum,
                effective_temperature=effective_temperature,
                evaluations=evaluations,
                trajectory_summaries=trajectory_summaries,
            )
            maybe_save_checkpoint(step, record)
            maybe_run_online_eval(step)
            clear_device_cache(torch, device)
            if rank == 0:
                persist_live_status(status="running")
            continue

        optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_param_tensors, 1.0)
        optimizer.step()
        adaptive_temp.record_update()

        record = dict(base_record)
        record["loss"] = float(total_loss.item())
        persist_and_log_record(
            record=record,
            task=task,
            task_weight=weights[task_index],
            weight_sum=weight_sum,
            effective_temperature=effective_temperature,
            evaluations=evaluations,
            trajectory_summaries=trajectory_summaries,
        )
        maybe_save_checkpoint(step, record)
        maybe_run_online_eval(step)
        clear_device_cache(torch, device)
        if rank == 0:
            persist_live_status(status="running")

    _distributed_barrier(distributed)
    if rank == 0:
        save_model = model.module if distributed else model
        adapter_dir = output_dir / "final_adapter"
        if args.training_mode == "lora":
            save_model.save_pretrained(adapter_dir)
        else:
            adapter_dir.mkdir(parents=True, exist_ok=True)
            trainable_state = {
                name: parameter.detach().cpu()
                for name, parameter in save_model.named_parameters()
                if parameter.requires_grad
            }
            torch.save(trainable_state, adapter_dir / "trainable_state.pt")
        text_preprocessor.save_backend.save_pretrained(adapter_dir)
        metrics_payload = build_grpo_metrics_payload(metrics, planned_steps=args.grpo_steps)
        metrics_path.write_text(
            json.dumps(metrics_payload, indent=2) + "\n",
            encoding="utf-8",
        )
        run_config_path.write_text(
            json.dumps(
                {
                    "model_name": args.model_name,
                    "training_mode": args.training_mode,
                    "adapter_init": args.adapter_init,
                    "resume_from": args.resume_from,
                    "resume_step": resume_step,
                    "tasks_dir": args.tasks_dir,
                    "benchmark_file": args.benchmark_file,
                    "domain_filter": args.domain_filter,
                    "group_size": args.group_size,
                    "grpo_steps": args.grpo_steps,
                    "lr": args.lr,
                    "kl_coeff": args.kl_coeff,
                    "temperature": args.temperature,
                    "adaptive_temp_step": args.adaptive_temp_step,
                    "adaptive_temp_max": args.adaptive_temp_max,
                    "adaptive_temp_state": adaptive_temp.to_dict(),
                    "max_new_tokens": args.max_new_tokens,
                    "max_seq_length": args.max_seq_length,
                    "max_turns": args.max_turns,
                    "max_test_runs": args.max_test_runs,
                    "checkpoint_interval_seconds": args.checkpoint_interval_seconds,
                    "checkpoint_every_steps": args.checkpoint_every_steps,
                    "online_eval_benchmark_file": args.online_eval_benchmark_file,
                    "online_eval_every_steps": args.online_eval_every_steps,
                    "online_eval_max_tasks": args.online_eval_max_tasks,
                    "online_eval_temperature": args.online_eval_temperature,
                    "device": str(args.device),
                    "reward_pass_weight": args.reward_pass_weight,
                    "reward_syntax_weight": args.reward_syntax_weight,
                    "reward_interface_weight": args.reward_interface_weight,
                    "reward_verifier_weight": args.reward_verifier_weight,
                    "reward_brevity_weight": args.reward_brevity_weight,
                    "reward_import_hygiene_weight": args.reward_import_hygiene_weight,
                    "brevity_target_lines": args.brevity_target_lines,
                    "reward_detail_budget_cap": args.reward_detail_budget_cap,
                    "advantage_clip": args.advantage_clip,
                    "ratio_clip_log_delta": args.ratio_clip_log_delta,
                    "logit_clip": args.logit_clip,
                    "min_reward_std": args.min_reward_std,
                    "curriculum_ema_decay": args.curriculum_ema_decay,
                    "curriculum_min_weight": args.curriculum_min_weight,
                    "curriculum_uncertainty_bonus": args.curriculum_uncertainty_bonus,
                    "quantum_priority": args.quantum_priority,
                    "research_methods": summarize_methods(research_methods),
                    "curriculum_state": curriculum.state,
                    "trajectory_health_min_read_before_write_rate": args.trajectory_health_min_read_before_write_rate,
                    "trajectory_health_min_tests_before_final_rate": args.trajectory_health_min_tests_before_final_rate,
                    "trajectory_health_max_no_tool_rate": args.trajectory_health_max_no_tool_rate,
                    "target_modules": list(args.target_modules) if args.target_modules else None,
                    "target_module_regex": list(args.target_module_regex)
                    if args.target_module_regex
                    else None,
                    "resolved_target_modules": resolved_target_modules,
                    "train_layernorm": args.train_layernorm,
                    "max_trainable_parameters": args.max_trainable_parameters,
                    "min_trainable_parameters": args.min_trainable_parameters,
                    "trainable_param_regex": list(getattr(args, "trainable_param_regex", []) or [])
                    or None,
                    "freeze_param_regex": list(getattr(args, "freeze_param_regex", []) or [])
                    or None,
                    "selective_training": selective_training,
                    "layernorm_training": layernorm_training,
                    "trainable_parameter_budget": trainable_parameter_budget,
                    "trainable_parameter_floor": trainable_parameter_floor,
                    "trainable_parameter_count": trainable_param_count,
                    "trainable_parameter_sample": trainable_param_names[:12],
                    "text_forward_preflight": text_forward_preflight,
                    "world_size": world_size,
                    "wallclock_checkpoints_saved": checkpoint_state.saved_count,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        persist_live_status(status="completed")
        emit_training_log_event(
            "training_completed",
            {
                "adapter_dir": str(adapter_dir),
                "output_dir": str(output_dir),
                "planned_steps": args.grpo_steps,
                "recorded_steps": len(metrics),
                "updated_steps": sum(1 for record in metrics if not bool(record.get("skipped"))),
                "wallclock_checkpoints_saved": checkpoint_state.saved_count,
                "latest_checkpoint_step": (latest_checkpoint_payload or {}).get("step"),
                "latest_online_eval_step": (latest_online_eval_payload or {}).get("step"),
                "final_record": safe_payload_preview(metrics[-1] if metrics else None),
            },
        )
    _distributed_barrier(distributed)

    if distributed:
        torch.distributed.destroy_process_group()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
