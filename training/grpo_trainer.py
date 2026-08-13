#!/usr/bin/env python3
"""GRPO (Group Relative Policy Optimization) trainer for code generation.

Samples N solutions per prompt, scores them with test harnesses,
and updates the policy using relative advantage within each group.

Usage:
    torchrun --nproc_per_node=8 training/grpo_trainer.py \
        --model-name models/Qwen2.5-1.5B-Instruct \
        --tasks-dir evals/tasks \
        --output-dir outputs/grpo-v1 \
        --device npu \
        --group-size 8 \
        --grpo-steps 100
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import random
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_utils import (  # noqa: E402
    INVALID_OR_NOISY,
    MASTERED_REPLAY,
    MODEL_JUDGE_DIMENSIONS,
    REPAIR_SFT,
    RL_ROUTES,
    AdaptiveKLState,
    AdaptiveTemperatureState,
    CircuitBreakerState,
    FrontierRouter,
    RunningMAD,
    TaskCurriculum,
    append_grpo_metric,
    append_grpo_metric_jsonl,
    append_repair_queue_record,
    blend_comprehensive_reward,
    build_grpo_metrics_payload,
    build_grpo_step_record,
    build_judge_diagnostics_record,
    build_mixture_weights,
    build_reward_breakdown,
    chunked_log_probs_and_entropy,
    count_repair_conversions,
    estimate_detail_budget,
    extract_behavior_hints_from_test_source,
    leave_one_out_advantages,
    load_grpo_step_metrics_jsonl,
    reward_signal_stats,
    sequence_ratio_stats,
    stable_grpo_loss,
    stable_gspo_loss_metrics,
    summarize_python_interface,
)
from training.model_backend import run_text_forward_preflight  # noqa: E402
from training.model_family_preflight import trainer_backend_preflight_block  # noqa: E402
from training.quantum_verifiers import score_from_typed_verifier  # noqa: E402
from training.qwen_sft_peft import (  # noqa: E402
    TextPreprocessorBackend,
    _visible_npu_indices,
    apply_selective_training_controls,
    build_balanced_npu_layer_device_map,
    collect_trainable_parameters,
    load_text_preprocessor_backend,
    probe_model_runtime_compat,
    resolve_lora_target_modules,
)
from training.research_plugins import load_research_methods, summarize_methods  # noqa: E402
from training.teacher_free_repair import (  # noqa: E402
    teacher_free_self_repair,
)
from training.text_preprocessor_backend import (  # noqa: E402
    build_supervised_text_example,
    pad_supervised_text_batch,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-name", required=True)
    p.add_argument(
        "--adapter-init",
        default=None,
        help="Optional PEFT adapter directory to continue from before GRPO updates.",
    )
    p.add_argument("--tasks-dir", default="evals/tasks")
    p.add_argument(
        "--resume-from",
        default=None,
        help="Path to a previous grpo_step_metrics.jsonl to resume from (warm restart).",
    )
    p.add_argument(
        "--benchmark-file",
        default=None,
        help="Optional text file with task ids to include; '#' comments are ignored.",
    )
    p.add_argument(
        "--domain-filter",
        nargs="*",
        default=None,
        help="Optional domain allowlist, for example --domain-filter quantum.",
    )
    p.add_argument("--output-dir", default="outputs/grpo-v1")
    p.add_argument("--device", default="cpu")
    p.add_argument("--group-size", type=int, default=8, help="Solutions per prompt")
    p.add_argument(
        "--max-adaptive-group",
        type=int,
        default=8,
        help="Cap on the posterior router's recommended group size (16 was the ASI2 stall trigger).",
    )
    p.add_argument("--grpo-steps", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--kl-coeff", type=float, default=0.05, help="KL penalty coefficient")
    p.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Sampling temperature. NOTE: with temperature != 1.0 the loss must "
        "compute ratios under the transformed behavior policy, otherwise the "
        "policy-gradient estimate is biased (review finding 2026-08-05).",
    )
    p.add_argument(
        "--adaptive-temp-step",
        type=float,
        default=0.15,
        help="Per-skip temperature escalation factor. Effective temp = min(base * (1 + step * consecutive_skips), max).",
    )
    p.add_argument(
        "--adaptive-temp-max",
        type=float,
        default=1.4,
        help="Maximum sampling temperature after adaptive escalation.",
    )
    p.add_argument("--max-new-tokens", type=int, default=2048)
    p.add_argument("--max-seq-length", type=int, default=4096)
    p.add_argument(
        "--npu-device-map",
        choices=["auto", "balanced-layers"],
        default="auto",
        help="Shard model layers across the rank's visible NPUs (single-process launch); required for 27B+ on 60GB 910B cards.",
    )
    p.add_argument(
        "--npu-max-memory-gib",
        type=int,
        default=54,
        help="Per-NPU max_memory GiB with --npu-device-map balanced-layers.",
    )
    p.add_argument("--log-steps", type=int, default=5)
    p.add_argument("--lora-rank", type=int, default=8)
    p.add_argument("--lora-alpha", type=int, default=16)
    p.add_argument(
        "--target-modules",
        nargs="*",
        default=None,
        help="Optional explicit LoRA target module suffixes. Defaults to auto-discovery from the loaded model.",
    )
    p.add_argument(
        "--target-module-regex",
        nargs="*",
        default=None,
        help="Optional regex patterns matched against full module names for router-only or expert-specific LoRA targeting.",
    )
    p.add_argument(
        "--trainable-param-regex",
        nargs="*",
        default=None,
        help="Optional regex allowlist for trainable parameter names. Non-matching trainable params are frozen.",
    )
    p.add_argument(
        "--freeze-param-regex",
        nargs="*",
        default=None,
        help="Optional regex denylist for parameter names to freeze after allowlist filtering.",
    )
    p.add_argument("--reward-pass-weight", type=float, default=0.6)
    p.add_argument("--reward-syntax-weight", type=float, default=0.1)
    p.add_argument("--reward-interface-weight", type=float, default=0.15)
    p.add_argument("--reward-verifier-weight", type=float, default=0.15)
    p.add_argument(
        "--reward-brevity-weight",
        type=float,
        default=0.0,
        help="Weight for brevity reward; set >0 to break flat-reward deadlocks.",
    )
    p.add_argument(
        "--reward-import-hygiene-weight",
        type=float,
        default=0.05,
        help="Penalty weight for invented non-stdlib imports on single-file tasks.",
    )
    p.add_argument(
        "--brevity-target-lines",
        type=int,
        default=40,
        help="Target line count for full brevity reward.",
    )
    p.add_argument("--reward-detail-budget-cap", type=int, default=8)
    p.add_argument("--advantage-clip", type=float, default=2.5)
    p.add_argument("--ratio-clip-log-delta", type=float, default=8.0)
    p.add_argument(
        "--top-p",
        type=float,
        default=1.0,
        help="Nucleus sampling threshold. Default 1.0 for sampling-policy "
        "consistency with the loss's raw-model ratios (review finding 2026-08-05).",
    )
    p.add_argument(
        "--overwrite-output-dir",
        action="store_true",
        default=False,
        help="Allow overwriting an existing output dir with prior step metrics.",
    )
    # ── FV-GSPO (frontier-verifier GSPO): see docs/frontier-verifier-gspo-design-2026-08-04.md ──
    p.add_argument(
        "--loss-mode",
        choices=["grpo", "gspo", "gspo_ln"],
        default="gspo",
        help="'grpo' keeps the old unclipped sequence-ratio loss (ablation baseline); "
        "'gspo' uses the GSPO sequence-level clipped proximal objective; "
        "'gspo_ln' is the LUSPO-style length-neutral variant (review 2026-08-05 #3): "
        "each surrogate is multiplied by w_i = min(|y_i|/L_reference, w_max) to "
        "neutralize the length bias of the sequence-mean ratio.",
    )
    p.add_argument(
        "--ln-reference-length",
        type=float,
        default=256.0,
        help="L_reference for the length-neutral surrogate weight.",
    )
    p.add_argument(
        "--ln-max-weight",
        type=float,
        default=4.0,
        help="w_max cap on the length multiplier (prevents one very long "
        "candidate from dominating).",
    )
    p.add_argument(
        "--gspo-clip-low",
        type=float,
        default=3e-4,
        help="Lower GSPO sequence-ratio clip (27B sweep 1e-4..1e-3; 35B start 3e-4). "
        "GSPO ratios differ by orders of magnitude from token PPO ratios, so do NOT "
        "copy DAPO's 0.2/0.28 values.",
    )
    p.add_argument(
        "--gspo-clip-high",
        type=float,
        default=4e-4,
        help="Upper GSPO sequence-ratio clip (default 1.3 * gspo-clip-low; 35B start 4e-4).",
    )
    p.add_argument(
        "--numerical-log-ratio-clip",
        type=float,
        default=8.0,
        help="Wide log-ratio clamp kept only for finite exponentiation; the proximal "
        "objective is controlled by gspo-clip-low/high, not by this value.",
    )
    # ── trust region (review 2026-08-05, Design B) ──
    # In the synchronous one-rollout-per-step implementation the pre-update
    # sequence ratio is 1 by construction, so GSPO clipping cannot constrain
    # the update. Instead the update is taken, the post-update ratio/KL is
    # measured on the same rollouts, and the update is rejected (or the LR
    # scaled) when the trust region is violated.
    p.add_argument(
        "--no-trust-region",
        action="store_false",
        dest="trust_region_enabled",
        default=True,
        help="Disable the post-update trust-region check (kept for ablations).",
    )
    p.add_argument("--trust-region-max-seq-kl", type=float, default=0.05)
    p.add_argument("--trust-region-max-clip-fraction", type=float, default=0.50)
    p.add_argument(
        "--trust-region-on-violation",
        choices=["reject", "scale_lr"],
        default="reject",
        help="'reject' restores the pre-update parameters and optimizer state; "
        "'scale_lr' keeps the update but halves the learning rate.",
    )
    p.add_argument(
        "--advantage-mode",
        choices=["loo", "group_std"],
        default="loo",
        help="'loo' is the FV-GSPO Dr.GRPO leave-one-out advantage (no per-task "
        "std normalization); 'group_std' reproduces the legacy per-group "
        "normalization for the ablation baseline.",
    )
    p.add_argument(
        "--loo-advantage-scale",
        choices=["none", "shared_mad"],
        default="none",
        help="Dr.GRPO leave-one-out advantages without per-task standard-deviation "
        "normalization. 'shared_mad' optionally divides by one fixed running MAD "
        "shared across tasks; 'none' keeps raw leave-one-out advantages.",
    )
    p.add_argument("--frontier-threshold", type=float, default=0.10)
    p.add_argument("--mastered-threshold", type=float, default=0.95)
    p.add_argument("--mix-targeted", type=float, default=0.5)
    p.add_argument("--mix-neighbor", type=float, default=0.25)
    p.add_argument("--mix-replay", type=float, default=0.25)
    p.add_argument(
        "--adaptive-mixture",
        action="store_true",
        default=False,
        help="Adapt mixture masses to router state (review 2026-08-05 #11): "
        "targeted mass rises with frontier yield (0.25-0.75), replay mass "
        "shrinks when mastered tasks repeatedly produce flat groups.",
    )
    p.add_argument("--neighbor-window", type=int, default=10)
    p.add_argument(
        "--repair-queue-path",
        default=None,
        help="JSONL queue for all-fail groups (execution-grounded repair candidates). "
        "Defaults to <output-dir>/repair_queue.jsonl.",
    )
    p.add_argument(
        "--repair-converted-jsonl",
        default=None,
        help="Optional JSONL written by the repair SFT/DPO stage recording verified "
        "conversions; used by the all-fail-without-repair circuit breaker.",
    )
    p.add_argument(
        "--coverage-json",
        default=None,
        help="Optional JSON mapping task_id -> coverage need from the training-only "
        "skill/failure inventory (WeaknessReport-style cells).",
    )
    p.add_argument(
        "--circuit-breaker-window",
        type=int,
        default=10,
        help="Steps per evaluation window for circuit breakers; a breaker trips only "
        "after persisting across two windows.",
    )
    # ── adaptive KL controller (design §4: capability preservation) ──
    p.add_argument(
        "--adaptive-kl",
        action="store_true",
        default=False,
        help="Adapt the KL penalty beta from measured sequence KL: rise when KL "
        "drifts beyond target, fall when far below. Keeps the policy close to "
        "the anchor (accepted checkpoint) until regression gates pass.",
    )
    p.add_argument("--kl-target", type=float, default=0.05)
    p.add_argument("--kl-up-rate", type=float, default=1.2)
    p.add_argument("--kl-down-rate", type=float, default=0.9)
    p.add_argument("--kl-min", type=float, default=1e-4)
    p.add_argument("--kl-max", type=float, default=0.5)
    p.add_argument("--kl-beta-init", type=float, default=0.005)
    p.add_argument(
        "--no-stop-on-severe-breaker",
        action="store_false",
        dest="stop_on_severe_breaker",
        default=True,
        help="Do not halt training when a severe in-loop circuit breaker trips "
        "(non-finite loss, clip fraction above 50 percent, entropy collapse, "
        "all-fail without repair).",
    )
    p.add_argument("--logit-clip", type=float, default=50.0)
    p.add_argument(
        "--min-reward-std",
        type=float,
        default=0.05,
        help="Minimum standard deviation across total or component rewards required to update.",
    )
    p.add_argument("--curriculum-ema-decay", type=float, default=0.9)
    p.add_argument("--curriculum-min-weight", type=float, default=0.05)
    p.add_argument("--curriculum-uncertainty-bonus", type=float, default=0.35)
    p.add_argument("--research-methods", nargs="*", default=[])
    p.add_argument(
        "--quantum-priority",
        type=float,
        default=1.5,
        help="Sampling multiplier for quantum tasks in the adaptive curriculum.",
    )
    # ── self-evaluation: the model judges its own generated code ──
    p.add_argument(
        "--self-evaluation-enabled",
        action="store_true",
        default=False,
        help="Enable self-evaluation: the model judges its own generated code samples.",
    )
    p.add_argument(
        "--reward-self-eval-weight",
        type=float,
        default=0.25,
        help="Weight for the self-evaluation reward component.",
    )
    p.add_argument(
        "--self-eval-judge-temperature",
        type=float,
        default=0.3,
        help="Temperature for the self-judge generation.",
    )
    p.add_argument(
        "--self-eval-judge-max-tokens",
        type=int,
        default=512,
        help="Max tokens for the self-judge response.",
    )
    # ── comprehensive frozen-judge scoring (base model / older adapters) ──
    p.add_argument(
        "--model-judge-enabled",
        action="store_true",
        default=False,
        help="Enable per-dimension comprehensive scoring by a FROZEN judge: the base "
        "model (or an older accepted adapter via --judge-adapter-path), never the "
        "current training policy. Reward weights stay zero until calibration passes.",
    )
    p.add_argument(
        "--judge-model-path",
        default=None,
        help="Frozen judge base model. Defaults to the training model path.",
    )
    p.add_argument(
        "--judge-adapter-path",
        default=None,
        help="Optional OLDER accepted adapter checkpoint to evaluate samples with "
        "(frozen; do not use the current training adapter as its own judge).",
    )
    p.add_argument(
        "--judge-device",
        default="cpu",
        help="Device for the frozen judge (cpu by default; a spare npu card when "
        "available, e.g. npu:2 on a 4-card env).",
    )
    p.add_argument(
        "--model-judge-max-tokens",
        type=int,
        default=256,
        help="Max tokens for one judge evaluation.",
    )
    p.add_argument(
        "--model-judge-temperature",
        type=float,
        default=0.0,
        help="Judge sampling temperature (greedy default for stability).",
    )
    p.add_argument(
        "--judge-calibration",
        default=None,
        help="Path to judge_calibration.json (from scripts/calibrate_model_judge.py): "
        "enables per-dimension reward weights only for dimensions whose agreement "
        "with executable anchors passed calibration. Until then weights are zero.",
    )
    p.add_argument(
        "--judge-diagnostics-path",
        default=None,
        help="Per-candidate judge diagnostics JSONL (executable anchors + judge "
        "dimension scores) consumed by scripts/calibrate_model_judge.py. Defaults "
        "to <output-dir>/judge_diagnostics.jsonl when the judge is enabled.",
    )
    # ── reward composition (user decision 2026-08-05: not executable-dominated) ──
    p.add_argument(
        "--reward-mode",
        choices=["p_dominant", "comprehensive", "tiered"],
        default="p_dominant",
        help="'p_dominant' keeps executable tests authoritative (P clamps failing "
        "candidates below every passing one; FV-GSPO default and ablation "
        "baseline). 'comprehensive' makes the reward the comprehensive score "
        "R = w_P*P + w_S*S + w_J*J with configurable masses below — the pass "
        "term no longer dominates, and the frozen judge contributes its mass "
        "once any dimension passes calibration. 'tiered' (review 2026-08-05 #5, "
        "recommended) uses the constrained hierarchy "
        "R = (1-P)*min(0.95, Q_progress) + P*(1 + alpha*Q_efficiency + gamma*Q_quality): "
        "any passer outranks any failure (execution authoritative), failures stay "
        "learnable via Q_progress, and passers are differentiated by efficiency/"
        "quality (judge dims, calibration-gated).",
    )
    p.add_argument("--reward-pass-mass", type=float, default=0.40)
    p.add_argument("--reward-shaped-mass", type=float, default=0.35)
    p.add_argument("--reward-judge-mass", type=float, default=0.25)
    p.add_argument("--tiered-alpha", type=float, default=0.10)
    p.add_argument("--tiered-gamma", type=float, default=0.10)
    # ── teacher-free self-repair rollout (Teacher-Free FV-GSPO plan §3/§8) ──
    # Failed candidates + real harness error logs feed a new rollout round using
    # the policy model itself (no reference/teacher model). 0 disables.
    p.add_argument(
        "--self-repair-rounds",
        type=int,
        default=0,
        help="Teacher-free self-repair rounds per failed candidate (plan §8: use "
        "2). 0 disables. When >0, a failing code is re-rolled by the policy with "
        "its exact harness errors appended and accepted only if it passes the "
        "hidden tests, else the original failed sample is retained for GRPO.",
    )
    # ── checkpoint interval (periodic adapter save to disk) ──
    p.add_argument(
        "--checkpoint-interval-seconds",
        type=int,
        default=7200,
        help="Save adapter checkpoint to disk every N seconds (0 = only at end).",
    )
    return p.parse_args()


def load_requested_task_ids(path: str | None) -> set[str] | None:
    if not path:
        return None
    task_ids = set()
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        task_ids.add(line)
    if not task_ids:
        raise ValueError(f"No task ids found in {path}")
    return task_ids


def discover_tasks(
    tasks_dir: Path,
    requested_task_ids: set[str] | None = None,
    allowed_domains: set[str] | None = None,
) -> list[dict]:
    tasks = []
    for domain_dir in sorted(tasks_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            task_json = task_dir / "task.json"
            tests_py = task_dir / "tests.py"
            if task_json.exists() and tests_py.exists():
                with open(task_json) as f:
                    meta = json.load(f)
                task_id = meta.get("id", task_dir.name)
                domain = meta.get("domain")
                if requested_task_ids is not None and task_id not in requested_task_ids:
                    continue
                if allowed_domains is not None and domain not in allowed_domains:
                    continue
                tasks.append({"meta": meta, "task_dir": task_dir, "tests_py": tests_py})
    return tasks


def load_test_harness(tests_py: Path):
    spec = importlib.util.spec_from_file_location(f"tests_{uuid.uuid4().hex[:6]}", str(tests_py))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def extract_behavior_hints(tests_path: Path) -> list[str]:
    if not tests_path.exists():
        return []
    return extract_behavior_hints_from_test_source(tests_path.read_text(encoding="utf-8"), cap=6)


def summarize_candidate_interface(candidate_path: Path) -> list[str]:
    if not candidate_path.exists():
        return []
    return summarize_python_interface(candidate_path.read_text(encoding="utf-8"))


def build_task_runtime_context(task: dict, *, detail_budget_cap: int) -> dict[str, Any]:
    """Derive runtime-only task fields once so reward and prompt code share the same view."""
    meta = task["meta"]
    task_id = meta.get("id", task["task_dir"].name)
    candidate_file = meta.get("candidate_file")
    required_interface = (
        summarize_candidate_interface(task["task_dir"] / candidate_file) if candidate_file else []
    )
    behavior_hints = extract_behavior_hints(task["tests_py"])
    test_source = task["tests_py"].read_text(encoding="utf-8")
    detail_budget = max(
        estimate_detail_budget(test_source, cap=detail_budget_cap),
        min(detail_budget_cap, max(1, len(behavior_hints))) if behavior_hints else 1,
    )
    raw_allowed_import_roots = meta.get("allowed_import_roots", [])
    allowed_import_roots = [
        root.strip() for root in raw_allowed_import_roots if isinstance(root, str) and root.strip()
    ]
    candidate_files = meta.get("candidate_files")
    if candidate_files is None and candidate_file:
        candidate_files = [candidate_file]
    return {
        "task_id": task_id,
        "required_interface": required_interface,
        "behavior_hints": behavior_hints,
        "detail_budget": detail_budget,
        "single_file_expected": len(candidate_files or []) <= 1,
        "allowed_import_roots": allowed_import_roots,
    }


def build_prompt(task: dict, research_methods: list[Any] | None = None) -> str:
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
        interface_lines = task.get("required_interface") or summarize_candidate_interface(
            task["task_dir"] / candidate_file
        )
        if interface_lines:
            parts.append(
                "Required interface:\n" + "\n".join(f"- {line}" for line in interface_lines)
            )

    behavior_hints = task.get("behavior_hints") or extract_behavior_hints(task["tests_py"])
    if behavior_hints:
        parts.append(
            "Behavioral requirements:\n" + "\n".join(f"- {line}" for line in behavior_hints)
        )

    if task.get("single_file_expected", False):
        parts.append(
            "Implementation constraints:\n"
            "- Keep the answer self-contained in one Python file.\n"
            "- Do not depend on repository-local helpers or invent non-standard modules."
        )

    parts.append("Return only the final Python code.")
    prompt = "\n\n".join(parts)
    for method in research_methods or []:
        prompt = method.augment_grpo_prompt(prompt, task=task, stage="grpo")
    return prompt


SYSTEM_PROMPT = (
    "You are a careful coding assistant focused on correctness, clear reasoning, "
    "and maintainable Python code. Return only the final code."
)


def extract_code(response: str) -> str:
    if "```python" in response:
        parts = response.split("```python")
        if len(parts) > 1:
            return parts[1].split("```")[0].strip()
    if "```" in response:
        parts = response.split("```")
        if len(parts) > 2:
            return parts[1].strip()
    return response.strip()


SELF_EVAL_JUDGE_PROMPT = """You are a quantum computing code reviewer. Evaluate the following code solution
against these criteria on a scale of 0-10 (0 = completely wrong/fails, 10 = perfect):

1. Correctness: Does the algorithm produce the right quantum state / result?
2. Runnability: Will the code execute without errors in a standard quantum SDK environment?
3. Efficiency: Is the circuit depth / gate count / resource usage reasonable for the problem?
4. Code quality: Is it well-structured, readable, and uses proper quantum computing patterns?

First, analyze the code briefly. Then output ONLY a single JSON object with this format:
{"score": <float 0-10>, "analysis": "<one-line summary>"}

CODE TO EVALUATE:
```python
{code}
```

TASK CONTEXT:
{task_context}

EVALUATION:"""


def _self_evaluate_code(code: str, task: dict, model, backend, args, device) -> float:
    """Ask the model to judge its own generated code and return a score 0-1."""
    task_desc = task.get("meta", {}).get(
        "description",
        task.get("meta", {}).get("name", str(task.get("task_dir", task.get("task_id", "unknown")))),
    )
    prompt = SELF_EVAL_JUDGE_PROMPT.format(code=code, task_context=task_desc)

    with torch.no_grad():
        # Tokenize
        messages = [
            {"role": "user", "content": prompt},
        ]
        if hasattr(backend, "tokenizer"):
            tokenized_inputs = backend.tokenizer.apply_chat_template(
                messages, tokenize=True, return_tensors="pt", add_generation_prompt=True
            ).to(device)
            input_len = tokenized_inputs.shape[1]
        elif hasattr(backend, "encode_chat"):
            tokenized_ids = backend.encode_chat(messages, add_generation_prompt=True)
            tokenized_inputs = torch.tensor([tokenized_ids], dtype=torch.long, device=device)
            input_len = tokenized_inputs.shape[1]
        else:
            return 0.0

        # Generate judgement
        try:
            outputs = model.generate(
                input_ids=tokenized_inputs,
                max_new_tokens=args.self_eval_judge_max_tokens,
                temperature=args.self_eval_judge_temperature,
                top_p=0.95,
                do_sample=True,
                pad_token_id=backend.tokenizer.pad_token_id
                if hasattr(backend, "tokenizer")
                else getattr(backend, "pad_token_id", 0),
            )
            response_ids = outputs[0][input_len:]
            if hasattr(backend, "tokenizer"):
                response_text = backend.tokenizer.decode(response_ids, skip_special_tokens=True)
            else:
                response_text = backend.decode(response_ids.tolist())
        except Exception:
            return 0.0

    # Parse the score from JSON response
    score = _parse_self_eval_score(response_text)
    return score


COMPREHENSIVE_JUDGE_PROMPT = """You are a strict code evaluator. Score the candidate solution on five dimensions, each a float 0.0-1.0. Use the executable evidence below as the authoritative anchor — do not contradict it.

Dimensions:
- correctness: does the algorithm's logic produce the right result (0.0 if tests fail)?
- runnability: would the code execute without syntax/import/runtime errors?
- result_correctness: do the actual outputs match the expected values?
- efficiency: is runtime / circuit depth / gate count / resource use reasonable for the problem?
- quality: is the code well-structured, readable, and maintainable?

CODE TO EVALUATE:
```python
{code}
```

EXECUTABLE EVIDENCE (authoritative):
{evidence}

TASK CONTEXT:
{task_context}

Output ONLY a JSON object:
{{"correctness": 0.0-1.0, "runnability": 0.0-1.0, "result_correctness": 0.0-1.0, "efficiency": 0.0-1.0, "quality": 0.0-1.0, "evidence": "one line"}}"""


def _parse_model_dim_scores(text: str) -> dict[str, float | None] | None:
    """Parse the judge's JSON response into per-dimension scores (0-1)."""
    import re

    try:
        match = re.search(r"\{[^}]+\}", text or "")
        if not match:
            return None
        data = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        return None
    scores: dict[str, float | None] = {}
    for dim in MODEL_JUDGE_DIMENSIONS:
        raw = data.get(dim)
        if isinstance(raw, int | float) and not isinstance(raw, bool):
            scores[dim] = min(1.0, max(0.0, float(raw)))
        else:
            scores[dim] = None
    if all(value is None for value in scores.values()):
        return None
    return scores


def _model_comprehensive_scores(
    code: str,
    task: dict,
    executable_evidence: str,
    judge_model,
    backend,
    args,
    device,
) -> dict[str, float | None] | None:
    """Frozen-judge per-dimension scores (correctness..quality) for one sample.

    The judge is the base model (or an older accepted adapter) — never the
    current training policy — so the reward model cannot be gamed by policy
    drift. Runs greedily and returns None when the judge output is unusable
    (recorded as missing; excluded from calibration).
    """
    task_desc = task.get("meta", {}).get(
        "description",
        task.get("meta", {}).get("name", str(task.get("task_dir", task.get("task_id", "unknown")))),
    )
    prompt = COMPREHENSIVE_JUDGE_PROMPT.format(
        code=code, evidence=executable_evidence, task_context=task_desc
    )
    messages = [{"role": "user", "content": prompt}]
    try:
        if hasattr(backend, "tokenizer"):
            tokenized = backend.tokenizer.apply_chat_template(
                messages, tokenize=True, return_tensors="pt", add_generation_prompt=True
            ).to(device)
            input_len = tokenized.shape[1]
        elif hasattr(backend, "encode_chat"):
            tokenized_ids = backend.encode_chat(messages, add_generation_prompt=True)
            tokenized = torch.tensor([tokenized_ids], dtype=torch.long, device=device)
            input_len = tokenized.shape[1]
        else:
            return None
        with torch.no_grad():
            outputs = judge_model.generate(
                input_ids=tokenized,
                max_new_tokens=getattr(args, "model_judge_max_tokens", 256),
                temperature=getattr(args, "model_judge_temperature", 0.0),
                top_p=1.0,
                do_sample=False,
                pad_token_id=backend.tokenizer.pad_token_id
                if hasattr(backend, "tokenizer")
                else getattr(backend, "pad_token_id", 0),
            )
            response_ids = outputs[0][input_len:]
            response_text = backend.tokenizer.decode(response_ids, skip_special_tokens=True)
    except Exception:
        return None

    return _parse_model_dim_scores(response_text)


def _parse_self_eval_score(text: str) -> float:
    """Extract score 0-10 from model's judge response, normalize to 0-1."""
    import re

    try:
        # Try to find JSON block
        json_match = re.search(r"\{[^}]+\}", text)
        if json_match:
            data = json.loads(json_match.group(0))
            raw = float(data.get("score", 5.0))
        else:
            # Fallback: look for "score: X" or "X/10"
            score_match = re.search(
                r"(?:score[:\s]*)?(\d+(?:\.\d+)?)\s*(?:/\s*10|out of 10)?", text
            )
            if score_match:
                raw = float(score_match.group(1))
            else:
                return 0.5  # neutral default
    except (json.JSONDecodeError, ValueError, KeyError):
        return 0.5

    # Normalize: clamp to [0, 10], then divide to [0, 1]
    raw = max(0.0, min(10.0, raw))
    return raw / 10.0


def evaluate_candidate(
    code: str,
    test_harness,
    task: dict,
    args,
    research_methods: list[Any] | None = None,
    model=None,
    backend=None,
    device=None,
    judge_model=None,
    judge_weights: dict[str, float] | None = None,
    judge_diagnostics_path: Path | None = None,
    step: int | None = None,
) -> dict[str, Any]:
    """Run tests and return a shaped reward breakdown.

    When self_evaluation is enabled, also evaluates the code by asking the model
    to judge its own output against quality criteria (correctness, runnability,
    efficiency, code quality).

    When ``judge_model`` is provided (frozen base model / older accepted
    adapter), per-dimension comprehensive scores are produced and blended with
    the executable reward via ``blend_comprehensive_reward``: P (full test
    pass) always dominates; judge mass comes out of the shaped term only.
    """
    # Review finding 2026-08-05 (#10): candidates must NOT be written into the
    # task directory, which also contains tests.py and the reference solution.
    # Candidates are executed from an isolated temp dir (harnesses load the
    # candidate by absolute path). Full container-level isolation remains a
    # deployment requirement.
    with tempfile.TemporaryDirectory(prefix="fv_gspo_candidate_") as candidate_dir:
        candidate_path = Path(candidate_dir) / "candidate.py"
        candidate_path.write_text(code, encoding="utf-8")
        try:
            result = test_harness.run_tests(str(candidate_path))
            if not isinstance(result, dict):
                result = {
                    "passed": False,
                    "details": [f"Unexpected harness return type: {type(result).__name__}"],
                }
        except Exception as exc:
            result = {
                "passed": False,
                "details": [f"{type(exc).__name__}: {exc}"],
            }

    reward = build_reward_breakdown(
        code=code,
        result=result,
        required_interface=task.get("required_interface", []),
        detail_budget=int(task.get("detail_budget", 1)),
        pass_weight=args.reward_pass_weight,
        syntax_weight=args.reward_syntax_weight,
        interface_weight=args.reward_interface_weight,
        verifier_weight=args.reward_verifier_weight,
        brevity_weight=args.reward_brevity_weight,
        brevity_target_lines=args.brevity_target_lines,
        import_hygiene_weight=args.reward_import_hygiene_weight,
        single_file_expected=bool(task.get("single_file_expected", False)),
        allowed_import_roots=task.get("allowed_import_roots", []),
    )
    reward["details"] = result.get("details", []) if isinstance(result, dict) else []
    # Typed quantum-semantic verifier (review 2026-08-05 #6): a continuous
    # semantic score (state/process fidelity, distribution distance) replaces
    # the generic verifier fraction when the task declares a verifier_type.
    # tests.py remains the authoritative pass gate.
    typed_score, typed_info = score_from_typed_verifier(
        code, task["task_dir"], task.get("meta", {})
    )
    if typed_info is not None:
        reward["verifier_reward"] = typed_score
        reward["typed_verifier"] = str(task.get("meta", {}).get("verifier_type"))
    for method in research_methods or []:
        reward = method.adjust_reward_breakdown(
            reward,
            code=code,
            result=result,
            task=task,
            stage="grpo",
        )

    # ── self-evaluation: ask the model to judge its own generated code ──
    if args.self_evaluation_enabled and model is not None and backend is not None:
        self_eval_score = _self_evaluate_code(code, task, model, backend, args, device)
        reward["self_eval_reward"] = self_eval_score * args.reward_self_eval_weight
        reward["self_eval_raw_score"] = self_eval_score
    else:
        reward["self_eval_reward"] = 0.0
        reward["self_eval_raw_score"] = 0.0

    # ── comprehensive frozen-judge scoring (base model / older adapters) ──
    reward["model_dim_scores"] = {}
    if args.model_judge_enabled and judge_model is not None and backend is not None:
        evidence_parts = [f"tests passed: {bool(result.get('passed'))}"]
        raw_details = result.get("details") or []
        evidence_parts.append(
            "failures: " + ("; ".join(str(d)[:200] for d in raw_details[:5]) or "none")
        )
        scores = _model_comprehensive_scores(
            code, task, "\n".join(evidence_parts), judge_model, backend, args, device
        )
        if scores is not None:
            reward["model_dim_scores"] = scores
            if judge_diagnostics_path is not None:
                append_grpo_metric_jsonl(
                    judge_diagnostics_path,
                    build_judge_diagnostics_record(
                        task_id=task.get("task_id", "?"),
                        passed=bool(reward.get("passed")),
                        syntax_ok=bool(
                            reward.get("syntax_reward") and reward["syntax_reward"] >= 1.0
                        ),
                        verifier_rate=float(reward.get("verifier_reward") or 0.0),
                        model_dim_scores=scores,
                        step=step,
                    ),
                )
            valid = {dim: value for dim, value in scores.items() if value is not None}
            shaped_mass = (
                args.reward_syntax_weight
                + args.reward_interface_weight
                + args.reward_verifier_weight
                + args.reward_brevity_weight
                + args.reward_import_hygiene_weight
            )
            shaped_reward = (
                args.reward_syntax_weight * reward["syntax_reward"]
                + args.reward_interface_weight * reward["interface_reward"]
                + args.reward_verifier_weight * reward["verifier_reward"]
                + args.reward_brevity_weight * reward["brevity_reward"]
                + args.reward_import_hygiene_weight * reward["import_hygiene_reward"]
            ) / max(shaped_mass, 1e-8)
            if args.reward_mode == "tiered":
                # tiered alpha/gamma are small multipliers on passing rewards
                # (efficiency/quality bonuses), not linear masses.
                blend_pass_mass = args.tiered_alpha
                blend_shaped_mass = args.tiered_gamma
            else:
                blend_pass_mass = args.reward_pass_mass
                blend_shaped_mass = args.reward_shaped_mass
            reward["total_reward"] = blend_comprehensive_reward(
                pass_reward=reward["pass_reward"],
                shaped_reward=shaped_reward,
                model_dim_scores=valid,
                dim_weights=judge_weights or {},
                mode=args.reward_mode,
                pass_mass=blend_pass_mass,
                shaped_mass=blend_shaped_mass,
                judge_mass=args.reward_judge_mass,
            )
    return reward


def _run_harness_for_code(
    test_harness,
    code: str,
) -> dict[str, Any]:
    """Run a candidate code string against the hidden-test harness in isolation.

    Mirrors the isolation mechanics of ``evaluate_candidate`` (review 2026-08-05
    #10): the candidate is written into a throwaway temp dir, never into the
    task directory that also holds tests.py / the reference solution. Returns a
    ``{passed: bool, details: list[str]}`` result dict for teacher-free
    self-repair verification.
    """
    with tempfile.TemporaryDirectory(prefix="tf_repair_candidate_") as candidate_dir:
        candidate_path = Path(candidate_dir) / "candidate.py"
        candidate_path.write_text(code, encoding="utf-8")
        try:
            result = test_harness.run_tests(str(candidate_path))
            if not isinstance(result, dict):
                result = {
                    "passed": False,
                    "details": [f"Unexpected harness return type: {type(result).__name__}"],
                }
        except Exception as exc:  # noqa: BLE001 - a repair op must not kill the step
            result = {
                "passed": False,
                "details": [f"{type(exc).__name__}: {exc}"],
            }
    passed = bool(result.get("passed"))
    details = [str(d) for d in (result.get("details") or [])] if isinstance(result, dict) else []
    return {"passed": passed, "details": details}


def _self_repair_failing_candidate(
    *,
    model,
    text_preprocessor,
    device: Any,
    test_harness,
    task: dict,
    code: str,
    task_prompt: str,
    result: dict[str, Any],
    args,
    max_rounds: int,
    temperature: float | None = None,
) -> dict[str, Any]:
    """Teacher-free self-repair rollout for a single failing candidate.

    Implements the plan's 无教师自修复 (no teacher model): the failing code plus
    its real harness error logs are fed back to the *policy model itself* to
    produce a repair, re-scored against the hidden tests, up to ``max_rounds``
    rounds (plan §8 recommends 2). Only an independently-passing repair replaces
    the original; otherwise the failed sample is retained so the group's GRPO
    relative-advantage stays well-defined on the behavior samples.

    Returns the module's result dict (see teacher_free_repair.teacher_free_self_repair).
    """
    backend = text_preprocessor

    def _repair(prompt_text: str) -> str:
        text = render_generation_prompt(backend.render_backend, prompt_text)
        inputs = move_batch_to_device(backend.text_backend(text, return_tensors="pt"), device)
        effective_temp = temperature if temperature is not None else args.temperature
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=effective_temp,
                top_p=args.top_p,
                do_sample=True,
            )
        gen_ids = outputs.sequences[0, inputs["input_ids"].shape[1] :]
        response = backend.text_backend.decode(gen_ids, skip_special_tokens=True)
        return extract_code(response)

    meta = task.get("meta", {})
    interface_lines = task.get("required_interface") or (
        summarize_candidate_interface(task["task_dir"] / meta["candidate_file"])
        if meta.get("candidate_file")
        else []
    )
    behavior_hints = task.get("behavior_hints") or extract_behavior_hints(task["tests_py"])

    return teacher_free_self_repair(
        task_prompt=task_prompt,
        failing_code=code,
        correctness=result,
        repair=_repair,
        verify=lambda c: _run_harness_for_code(test_harness, c),
        max_rounds=max_rounds,
        interface_lines=interface_lines or None,
        behavior_hints=behavior_hints or None,
    )


def render_generation_prompt(render_backend: Any, prompt: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    if hasattr(render_backend, "apply_chat_template"):
        try:
            return render_backend.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            return render_backend.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
    return "\n\n".join(f"{message['role'].upper()}: {message['content']}" for message in messages)


def move_batch_to_device(batch: dict[str, torch.Tensor], device: Any) -> dict[str, torch.Tensor]:
    return {name: tensor.to(device) for name, tensor in batch.items()}


def _release_device_cache(torch_module: Any) -> None:
    """Release NPU/CUDA allocator cache between phases.

    Long sharded 27B runs fragment device memory across rollouts; freeing the
    allocator cache between phases keeps peak allocation low. Safe no-op on
    backends without an empty_cache API.
    """
    for backend_name in ("npu", "cuda", "mps"):
        backend = getattr(torch_module, backend_name, None)
        if backend is not None and hasattr(backend, "empty_cache"):
            try:
                backend.empty_cache()
            except Exception:
                pass


def generate_group(
    model,
    backend: TextPreprocessorBackend,
    prompt: str,
    args,
    *,
    temperature: float | None = None,
    count: int | None = None,
) -> tuple[list[str], str]:
    """Generate a group of solutions and return (codes, prompt_text).

    Args:
        temperature: Override the base sampling temperature.  When adaptive
            temperature escalation is active, pass the escalated value here.
            Falls back to ``args.temperature`` if not specified.
        count: Number of solutions to generate. Defaults to ``args.group_size``;
            the posterior router may recommend 4/8/16 adaptively (review
            2026-08-05 #4).
    """
    text = render_generation_prompt(backend.render_backend, prompt)
    inputs = move_batch_to_device(backend.text_backend(text, return_tensors="pt"), args.device)
    effective_temp = temperature if temperature is not None else args.temperature
    group_size = count if count is not None else args.group_size

    codes = []

    for _ in range(group_size):
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=effective_temp,
                top_p=args.top_p,
                do_sample=True,
                return_dict_in_generate=True,
                output_scores=True,
            )

        gen_ids = outputs.sequences[0, inputs["input_ids"].shape[1] :]
        response = backend.text_backend.decode(gen_ids, skip_special_tokens=True)
        codes.append(extract_code(response))
        # Long rollout groups fragment NPU memory across sequential generations;
        # free the allocator cache between rollouts (p15: group-16 rollout hang).
        _release_device_cache(torch)

    return codes, text


def compute_completion_log_prob(
    model,
    tokenizer,
    prompt_text: str,
    completion_text: str,
    device: Any,
    max_seq_length: int,
    logit_clip: float,
    *,
    add_mm_token_type_ids: bool = False,
    return_entropy: bool = False,
) -> tuple[torch.Tensor, torch.Tensor] | tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    prompt_inputs = tokenizer(
        prompt_text, return_tensors="pt", truncation=True, max_length=max_seq_length
    )
    full_inputs = tokenizer(
        prompt_text + completion_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_seq_length,
    )
    if add_mm_token_type_ids:
        full_inputs["mm_token_type_ids"] = torch.zeros_like(full_inputs["input_ids"])
    full_inputs = move_batch_to_device(full_inputs, device)
    prompt_len = min(prompt_inputs["input_ids"].shape[1], full_inputs["input_ids"].shape[1])

    outputs = model(**full_inputs)
    logits = outputs.logits[:, :-1, :]
    target_ids = full_inputs["input_ids"][:, 1:]

    completion_mask = torch.zeros_like(target_ids, dtype=torch.bool)
    completion_start = max(prompt_len - 1, 0)
    completion_mask[:, completion_start:] = True
    attention_mask = full_inputs.get("attention_mask")
    if attention_mask is not None:
        completion_mask &= attention_mask[:, 1:].bool()
    token_count = completion_mask.sum()
    if token_count.item() == 0:
        zero = logits.new_tensor(0.0)
        if return_entropy:
            return zero, token_count, zero
        return zero, token_count
    # Chunked-vocab pass: full-vocab fp32 logits/softmax spike multiple GB on the
    # lm_head NPU of the sharded 27B (the ASI2 stall zone) — chunked avoids it.
    result = chunked_log_probs_and_entropy(
        logits, target_ids, logit_clip, return_entropy=return_entropy
    )
    if return_entropy:
        token_log_probs, entropy_per_pos = result
        seq_log_prob = token_log_probs.masked_select(completion_mask).sum()
        masked_entropy = entropy_per_pos.masked_select(completion_mask)
        entropy = masked_entropy.mean() if masked_entropy.numel() else logits.new_tensor(0.0)
        return seq_log_prob, token_count, entropy
    token_log_probs = result
    seq_log_prob = token_log_probs.masked_select(completion_mask).sum()
    return seq_log_prob, token_count


def grpo_loss(
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    kl_coeff: float,
    ratio_clip_log_delta: float,
) -> torch.Tensor:
    """GRPO loss: policy gradient with group-relative advantages + KL penalty."""
    return stable_grpo_loss(
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=advantages,
        kl_coeff=kl_coeff,
        ratio_clip_log_delta=ratio_clip_log_delta,
    )


def compute_dr_pair_loss(
    *,
    research_methods: list[Any],
    rewards: torch.Tensor,
    codes: list[str],
    current_log_probs: list[torch.Tensor],
    old_log_probs: list[torch.Tensor],
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Compute the doubly-robust DPO pair loss when the plugin is enabled.

    Returns (loss, info) where `loss` is a scalar tensor (zero if the
    plugin is disabled or no pair was mined) and `info` is a dict with
    debugging fields (`dr_pair_mined`, `dr_pair_reward_gap`,
    `dr_pair_loss_value`).

    This is a no-op when no research method matches
    `doubly_robust_quantum_grpo`. The pair loss is weighted by
    `dr_pair_loss_weight` (default 0.3) read from the plugin's
    `extra_run_config()`.
    """
    info: dict[str, Any] = {
        "dr_pair_mined": False,
        "dr_pair_reward_gap": 0.0,
        "dr_pair_loss_value": 0.0,
        "dr_pair_loss_weight": 0.0,
    }
    if not research_methods:
        zero = rewards.new_tensor(0.0) if rewards is not None else None
        if zero is None:
            import torch as _torch

            zero = _torch.zeros((), dtype=_torch.float32)
        return zero, info

    method = next(
        (m for m in research_methods if m.method_id == "doubly_robust_quantum_grpo"),
        None,
    )
    if method is None:
        zero = rewards.new_tensor(0.0) if rewards is not None else None
        if zero is None:
            import torch as _torch

            zero = _torch.zeros((), dtype=_torch.float32)
        return zero, info

    cfg = method.extra_run_config().get("doubly_robust_quantum_grpo", {})
    beta = float(cfg.get("dr_dpo_beta", 0.07))
    min_gap = float(cfg.get("dr_pair_min_reward_gap", 0.4))
    max_pairs = int(cfg.get("dr_pair_max_per_step", 1))
    weight = float(cfg.get("dr_pair_loss_weight", 0.3))
    info["dr_pair_loss_weight"] = weight
    if weight <= 0.0 or max_pairs <= 0:
        zero = rewards.new_tensor(0.0)
        return zero, info

    # Lazy import so the trainer does not hard-depend on the plugin module.
    try:
        import importlib.util
        import sys as _sys

        plugin_root = (
            Path(__file__).resolve().parents[1]
            / "research"
            / "papers"
            / "doubly_robust_quantum_grpo"
            / "code"
        )
        spec = importlib.util.spec_from_file_location(
            "dr_pair_loss_mod", plugin_root / "dr_pair_loss.py"
        )
        if spec is None or spec.loader is None:
            zero = rewards.new_tensor(0.0)
            return zero, info
        mod = importlib.util.module_from_spec(spec)
        # Register the module in sys.modules before exec so that
        # @dataclass(frozen=True) inside the plugin can resolve the
        # module namespace.
        _sys.modules["dr_pair_loss_mod"] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            _sys.modules.pop("dr_pair_loss_mod", None)
            raise
    except Exception:
        zero = rewards.new_tensor(0.0)
        return zero, info

    pairs = mod.build_dr_pairs(
        rewards=rewards,
        codes=codes,
        min_reward_gap=min_gap,
        max_pairs=max_pairs,
    )
    if not pairs:
        zero = rewards.new_tensor(0.0)
        return zero, info

    info["dr_pair_mined"] = True
    info["dr_pair_reward_gap"] = float(pairs[0].reward_gap)

    log_probs_tensor = torch.stack(current_log_probs)
    ref_log_probs_tensor = torch.stack(old_log_probs).detach()
    pair_loss = mod.dr_pair_loss(
        log_probs=log_probs_tensor,
        ref_log_probs=ref_log_probs_tensor,
        pairs=pairs,
        beta=beta,
        device=log_probs_tensor.device,
    )
    if not torch.isfinite(pair_loss):
        zero = rewards.new_tensor(0.0)
        return zero, info

    weighted = weight * pair_loss
    info["dr_pair_loss_value"] = float(pair_loss.item())
    return weighted, info


def compute_dr_variance_correction(
    *,
    research_methods: list[Any],
    log_probs: torch.Tensor,
    old_log_probs: torch.Tensor,
    advantages: torch.Tensor,
    ratio_clip_log_delta: float,
    current_step: int | None = None,
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Compute the doubly-robust PPO-side variance correction.

    The DR estimator is

        L_DR = L_PPO + psi * E[ (r - 1) * A ]

    where `r = exp(log_probs - old_log_probs)` is the PPO importance
    ratio and `A` is the (detached) group-relative advantage. The
    correction has zero mean under the behavior policy but reduces
    variance when the behavior policy is close to the target, which is
    the "doubly robust" guarantee (see paper.md §2 and
    arXiv:2506.01183).

    Returns (correction_term, info). The correction term is added to
    `total_loss` by the caller. When the `doubly_robust_quantum_grpo`
    plugin is absent or `dr_psi_init == 0`, returns a zero tensor so
    this is safe for base GRPO.
    """
    info: dict[str, Any] = {
        "dr_variance_correction_value": 0.0,
        "dr_psi": 0.0,
    }
    if not research_methods:
        zero = log_probs.new_tensor(0.0) if log_probs is not None else None
        if zero is None:
            import torch as _torch

            zero = _torch.zeros((), dtype=_torch.float32)
        return zero, info

    method = None
    for m in research_methods:
        if getattr(m, "method_id", "") == "doubly_robust_quantum_grpo":
            method = m
            break
    if method is None:
        zero = log_probs.new_tensor(0.0)
        return zero, info

    cfg = method.extra_run_config().get("doubly_robust_quantum_grpo", {})
    psi_init = float(cfg.get("dr_psi_init", 0.0))
    warmup_steps = int(float(cfg.get("dr_psi_warmup_steps", 0)))
    # Linear psi warmup: psi ramps 0 -> psi_init over the first
    # `dr_psi_warmup_steps` training steps, then holds at psi_init.
    # Matches the paper's "tune psi after warmup" guidance and reduces
    # early-step variance. When warmup_steps == 0 (default), psi is
    # constant — preserves the pre-warmup behavior.
    if warmup_steps > 0 and current_step is not None and current_step < warmup_steps:
        psi = psi_init * (float(current_step) / float(warmup_steps))
    else:
        psi = psi_init
    info["dr_psi"] = psi
    info["dr_psi_init"] = psi_init
    info["dr_psi_warmup_steps"] = warmup_steps
    info["dr_psi_current_step"] = int(current_step) if current_step is not None else None
    if psi == 0.0:
        zero = log_probs.new_tensor(0.0)
        return zero, info

    # Reuse the plugin helper if importable; fall back to inline math.
    try:
        import sys as _sys

        plugin_root = Path(__file__).resolve().parent.parent / (
            "research/papers/doubly_robust_quantum_grpo/code"
        )
        spec = importlib.util.spec_from_file_location(
            "dr_pair_loss_mod_v2", plugin_root / "dr_pair_loss.py"
        )
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            _sys.modules["dr_pair_loss_mod_v2"] = mod
            try:
                spec.loader.exec_module(mod)
            except Exception:
                _sys.modules.pop("dr_pair_loss_mod_v2", None)
                raise
            log_ratio = (log_probs - old_log_probs.detach()).clamp(
                -ratio_clip_log_delta, ratio_clip_log_delta
            )
            ppo_ratio = torch.exp(log_ratio)
            correction = mod.dr_variance_correction(
                ppo_loss=log_probs.new_tensor(0.0),  # unused; helper adds to ppo_loss
                ppo_ratio=ppo_ratio,
                advantages=advantages.detach(),
                psi=psi,
            )
            # dr_variance_correction returns ppo_loss + psi*((r-1)*A).mean();
            # subtract the unused ppo_loss (0.0) so we isolate the correction.
            correction = correction - 0.0
            if not torch.isfinite(correction):
                zero = log_probs.new_tensor(0.0)
                return zero, info
            info["dr_variance_correction_value"] = float(correction.item())
            return correction, info
    except Exception:
        pass

    # Inline fallback (matches dr_variance_correction math).
    log_ratio = (log_probs - old_log_probs.detach()).clamp(
        -ratio_clip_log_delta, ratio_clip_log_delta
    )
    ppo_ratio = torch.exp(log_ratio)
    correction = psi * ((ppo_ratio - 1.0) * advantages.detach()).mean()
    if not torch.isfinite(correction):
        zero = log_probs.new_tensor(0.0)
        return zero, info
    info["dr_variance_correction_value"] = float(correction.item())
    return correction, info


def observe_and_evaluate_breakers(
    breaker: CircuitBreakerState,
    *,
    step: int,
    route: str,
    non_finite: bool,
    clip_fraction: float,
    entropy_mean: float | None,
    repair_queued: bool,
    repair_converted_jsonl: str | None,
    all_fail: bool,
) -> list[dict[str, Any]]:
    """Feed one step's facts to the circuit-breaker monitor and close a window.

    Returns newly tripped breaker events (see ``CircuitBreakerState.evaluate``).
    """
    breaker.observe_step(
        step=step,
        route=route,
        non_finite=non_finite,
        clip_fraction=clip_fraction,
        entropy=entropy_mean,
        repair_queued=repair_queued,
        repair_converted=count_repair_conversions(repair_converted_jsonl),
        all_fail_share=1.0 if all_fail else 0.0,
    )
    return breaker.evaluate(step=step)


def maybe_stop_for_breaker(
    breaker: CircuitBreakerState,
    args: argparse.Namespace,
    rank: int,
    trips: list[dict[str, Any]],
) -> bool:
    """Log newly tripped breakers; return True when the run must halt.

    A severe in-loop breaker (non-finite, clip fraction, entropy collapse,
    all-fail without repair) that persists across two evaluation windows stops
    the run so NPU-hours are not burned on a broken policy.
    """
    if trips and rank == 0:
        print(
            json.dumps({"stage": "circuit_breaker_trip", "trips": trips}, ensure_ascii=False),
            flush=True,
        )
    if breaker.should_stop and args.stop_on_severe_breaker:
        if rank == 0:
            print(
                json.dumps(
                    {"stage": "circuit_breaker_stop", "trips": breaker.tripped},
                    ensure_ascii=False,
                ),
                flush=True,
            )
        return True
    return False


def emit_step_record(
    *,
    rank: int,
    metrics: list[dict[str, Any]],
    step_metrics_path: Path,
    log_steps: int,
    ctx: dict[str, Any],
    skipped: bool,
    reason: str | None = None,
    loss: float | None = None,
    trips: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> dict[str, Any] | None:
    """Persist one step record (skipped or updated) on rank 0.

    ``ctx`` carries the step-scoped record fields (built once per step in
    ``main``); ``extra`` fields are merged into the record (e.g. GSPO loss
    statistics).
    """
    if rank != 0:
        return None
    record = build_grpo_step_record(
        step=int(ctx["step"]),
        task_name=str(ctx["task_name"]),
        domain=str(ctx["domain"]),
        mean_reward=float(ctx["mean_reward"]),
        signal_stats=ctx["signal_stats"],
        pass_rate=ctx.get("pass_rate"),
        syntax_rate=ctx.get("syntax_rate"),
        interface_rate=ctx.get("interface_rate"),
        verifier_rate=ctx.get("verifier_rate"),
        task_prob=float(ctx["task_prob"]),
        task_state=ctx["task_state"],
        advantage_scale=ctx.get("advantage_scale"),
        skipped=skipped,
        reason=reason,
        loss=loss,
        adapter_init=ctx.get("adapter_init"),
        route=ctx.get("route"),
        entropy_mean=ctx.get("entropy_mean"),
        generation_tokens=ctx.get("generation_tokens"),
        repair_queued=ctx.get("repair_queued"),
        all_fail=ctx.get("all_fail"),
        frontier_fraction=ctx.get("frontier_fraction"),
        breaker_trips=trips,
        model_dim_scores=ctx.get("model_dim_scores"),
        model_judge_enabled=ctx.get("model_judge_enabled"),
        posterior_lower=ctx.get("posterior_lower"),
        posterior_upper=ctx.get("posterior_upper"),
        flaky=ctx.get("flaky"),
        group_size=ctx.get("group_size"),
        **extra,
    )
    append_grpo_metric(metrics, record=record)
    append_grpo_metric_jsonl(step_metrics_path, record)
    if int(ctx["step"]) % max(1, log_steps) == 0:
        print(json.dumps(record))
    return record


def main() -> int:
    # The trainer's stdout is redirected to the run log; block buffering would
    # swallow every phase marker if the container is killed mid-stall. Line-buffer
    # so each stage print lands immediately (NPU-hang diagnostics).
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(line_buffering=True)
        except Exception:
            pass
    args = parse_args()
    research_methods = load_research_methods(args.research_methods)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    step_metrics_path = output_dir / "grpo_step_metrics.jsonl"
    metrics_path = output_dir / "grpo_metrics.json"
    run_config_path = output_dir / "run_config.json"
    requested_task_ids = load_requested_task_ids(args.benchmark_file)
    allowed_domains = set(args.domain_filter) if args.domain_filter else None

    # DDP setup
    # With --npu-device-map balanced-layers the model spans multiple NPUs and
    # must NOT be DDP-wrapped; treat it as a non-distributed single process.
    distributed = "RANK" in os.environ and args.npu_device_map != "balanced-layers"
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    rank = int(os.environ.get("RANK", 0))

    if distributed:
        if args.device == "npu":
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
            torch.npu.set_device(0)

    args.device = device

    # Warm restart: load prior metrics and curriculum state from a previous JSONL.
    resume_step = 0
    resume_metrics: list[dict] = []
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
                )
            )

    if rank == 0:
        if not args.resume_from:
            if step_metrics_path.exists() and not args.overwrite_output_dir:
                raise SystemExit(
                    f"Output dir already contains {step_metrics_path.name}; pass "
                    "--overwrite-output-dir to start fresh."
                )
            step_metrics_path.unlink(missing_ok=True)
        metrics_path.unlink(missing_ok=True)
        run_config_path.unlink(missing_ok=True)
        # When resuming, seed the JSONL with prior records
        if resume_metrics:
            for prior_record in resume_metrics:
                append_grpo_metric_jsonl(step_metrics_path, prior_record)

    tasks = discover_tasks(
        Path(args.tasks_dir), requested_task_ids=requested_task_ids, allowed_domains=allowed_domains
    )
    if not tasks:
        raise ValueError("No GRPO tasks matched the requested filters")
    if rank == 0:
        print(
            json.dumps(
                {
                    "stage": "tasks_ready",
                    "task_count": len(tasks),
                    "group_size": args.group_size,
                    "steps": args.grpo_steps,
                    "benchmark_file": args.benchmark_file,
                    "domain_filter": sorted(allowed_domains) if allowed_domains else None,
                    "research_methods": summarize_methods(research_methods),
                }
            )
        )

    # Load model with LoRA
    from peft import LoraConfig, PeftModel, TaskType, get_peft_model
    from transformers import (
        AutoConfig,
        AutoModelForCausalLM,
        AutoProcessor,
        AutoTokenizer,
        PreTrainedTokenizerFast,
    )

    runtime_compat = probe_model_runtime_compat(args.model_name, AutoConfig)
    if runtime_compat is not None:
        backend_blocker = trainer_backend_preflight_block(
            str(runtime_compat.get("config_model_type") or ""),
            [str(item) for item in (runtime_compat.get("config_architectures") or [])],
        )
        if backend_blocker is not None:
            print(
                json.dumps(
                    {
                        "stage": "trainer_backend_preflight",
                        "state": "blocked",
                        "model_type": runtime_compat.get("config_model_type"),
                        "architectures": runtime_compat.get("config_architectures"),
                        "error": backend_blocker,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            raise SystemExit(backend_blocker)

    text_preprocessor = load_text_preprocessor_backend(
        args.model_name, AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast
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
            )
        )

    preflight_task = tasks[0]
    preflight_task_id = preflight_task["meta"].get("id", preflight_task["task_dir"].name)
    preflight_record = {
        "example_id": f"grpo-preflight-{preflight_task_id}",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_prompt(preflight_task, research_methods=research_methods),
            },
            {"role": "assistant", "content": "pass"},
        ],
    }
    preflight_example = build_supervised_text_example(
        preflight_record,
        text_preprocessor,
        args.max_seq_length,
        train_on_completions_only=True,
    )
    _needs_mm_token_type_ids = str(
        runtime_compat.get("config_model_type") if runtime_compat is not None else ""
    ).startswith("gemma4")
    preflight_batch = pad_supervised_text_batch(
        [preflight_example],
        text_preprocessor.text_backend,
        torch,
        add_mm_token_type_ids=_needs_mm_token_type_ids,
    )

    model_config = AutoConfig.from_pretrained(args.model_name, trust_remote_code=True)
    model_kwargs: dict[str, Any] = {
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "torch_dtype": "auto",
    }
    npu_device_map: dict[str, str] | None = None
    if args.npu_device_map == "balanced-layers":
        visible_npus = _visible_npu_indices()
        npu_device_map = build_balanced_npu_layer_device_map(model_config, visible_npus)
        model_kwargs["device_map"] = npu_device_map
        model_kwargs["max_memory"] = {
            f"npu:{idx}": f"{args.npu_max_memory_gib}GiB" for idx in range(len(visible_npus))
        }
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "npu_device_map",
                        "visible_npus": visible_npus,
                        "layers": len(npu_device_map),
                        "max_memory_gib": args.npu_max_memory_gib,
                    },
                    ensure_ascii=False,
                )
            )
    model = AutoModelForCausalLM.from_pretrained(args.model_name, **model_kwargs)
    if rank == 0:
        print(
            json.dumps(
                {"stage": "model_loaded", "model_class": model.__class__.__name__},
                ensure_ascii=False,
            )
        )
    if args.adapter_init:
        model = PeftModel.from_pretrained(model, str(args.adapter_init), is_trainable=True)
        resolved_target_modules = None
    else:
        resolved_target_modules = resolve_lora_target_modules(
            args.target_modules,
            model,
            args.target_module_regex,
        )
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=0.05,
            target_modules=resolved_target_modules,
            bias="none",
        )
        model = get_peft_model(model, lora_config)
    selective_training = apply_selective_training_controls(
        model,
        trainable_param_regex=getattr(args, "trainable_param_regex", None),
        freeze_param_regex=getattr(args, "freeze_param_regex", None),
    )
    trainable_param_tensors, trainable_param_names, trainable_param_count = (
        collect_trainable_parameters(model)
    )
    if rank == 0:
        print(
            json.dumps(
                {
                    "stage": "selective_training_applied",
                    **selective_training,
                    "trainable_parameter_count": trainable_param_count,
                    "trainable_parameter_sample": trainable_param_names[:12],
                },
                ensure_ascii=False,
            )
        )
    if npu_device_map is None:
        model.to(device)
        if rank == 0:
            print(
                json.dumps({"stage": "model_on_device", "device": str(device)}, ensure_ascii=False)
            )
    elif rank == 0:
        print(
            json.dumps(
                {"stage": "model_sharded_on_npus", "map_size": len(npu_device_map)},
                ensure_ascii=False,
            )
        )

    # ── frozen comprehensive judge (base model / older accepted adapter) ──
    # The judge is NEVER the current training policy: it is the base model,
    # optionally with an OLDER accepted adapter (accepted checkpoints from the
    # eval gate). Its reward weight stays zero until scripts/calibrate_model_judge.py
    # confirms per-dimension agreement with executable anchors.
    judge_model = None
    judge_weights: dict[str, float] = {}
    judge_diagnostics_path = (
        Path(args.judge_diagnostics_path)
        if args.judge_diagnostics_path
        else (output_dir / "judge_diagnostics.jsonl" if args.model_judge_enabled else None)
    )
    if args.model_judge_enabled:
        judge_path = args.judge_model_path or args.model_name
        judge_model = AutoModelForCausalLM.from_pretrained(
            judge_path,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            torch_dtype="auto",
        )
        if args.judge_adapter_path:
            judge_model = PeftModel.from_pretrained(
                judge_model, str(args.judge_adapter_path), is_trainable=False
            )
        judge_model.to(args.judge_device)
        judge_model.eval()
        if args.judge_calibration:
            cal_path = Path(args.judge_calibration)
            if cal_path.is_file():
                calibration = json.loads(cal_path.read_text(encoding="utf-8"))
                judge_weights = {
                    str(dim): float(weight)
                    for dim, weight in (calibration.get("enabled_dims") or {}).items()
                    if float(weight) > 0.0
                }
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "comprehensive_judge_loaded",
                        "judge_model_path": judge_path,
                        "judge_adapter_path": args.judge_adapter_path,
                        "judge_device": str(args.judge_device),
                        "judge_weights": judge_weights,
                    },
                    ensure_ascii=False,
                )
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
            )
        )

    if distributed and npu_device_map is None:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])
        if rank == 0:
            print(json.dumps({"stage": "ddp_wrapped"}, ensure_ascii=False))

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
    # ── FV-GSPO: frontier router, mixture sampling, circuit breakers ──
    router = FrontierRouter(
        frontier_threshold=args.frontier_threshold,
        mastered_threshold=args.mastered_threshold,
    )
    if args.coverage_json:
        coverage_path = Path(args.coverage_json)
        if coverage_path.exists():
            try:
                router.load_coverage_map(json.loads(coverage_path.read_text(encoding="utf-8")))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid --coverage-json {coverage_path}: {exc}")
    breaker = CircuitBreakerState(window_size=args.circuit_breaker_window)
    running_mad = RunningMAD()
    kl_state = (
        AdaptiveKLState(
            target_kl=args.kl_target,
            up_rate=args.kl_up_rate,
            down_rate=args.kl_down_rate,
            min_kl=args.kl_min,
            max_kl=args.kl_max,
            beta=args.kl_beta_init,
        )
        if args.adaptive_kl
        else None
    )
    repair_queue_path = (
        Path(args.repair_queue_path)
        if args.repair_queue_path
        else output_dir / "repair_queue.jsonl"
    )
    recent_frontier: list[str] = []
    total_probes = 0
    # Replay curriculum state from resumed records
    for prior in resume_metrics:
        task_name = str(prior.get("task", ""))
        mr = float(prior.get("mean_reward", 0.0))
        if task_name:
            curriculum.record(task_name, mr)
            pass_rate = prior.get("pass_rate")
            shaped_std = max(
                [
                    float(prior.get(key, 0.0))
                    for key in (
                        "reward_std",
                        "pass_std",
                        "syntax_std",
                        "interface_std",
                        "verifier_std",
                    )
                ]
            )
            if pass_rate is not None:
                router.probe_record(
                    task_name, int(prior.get("step", 0)), float(pass_rate), shaped_std
                )
                total_probes += 1
        if bool(prior.get("skipped")) and prior.get("reason") == "low_reward_signal":
            adaptive_temp.record_skip("low_reward_signal")
        elif not bool(prior.get("skipped")):
            adaptive_temp.record_update()

    for task in tasks:
        task.update(
            build_task_runtime_context(task, detail_budget_cap=args.reward_detail_budget_cap)
        )

    random.seed(42 + rank)
    _last_checkpoint_time = time.time()

    for step in range(1, args.grpo_steps + 1):
        # Skip steps already covered by warm restart
        if step <= resume_step:
            continue
        # FV-GSPO mixture sampling: 50% targeted frontier/repair, 25% neighboring
        # variants, 25% replay (see docs/frontier-verifier-gspo-design-2026-08-04.md §6).
        weights = build_mixture_weights(
            router,
            tasks,
            step,
            mix_targeted=args.mix_targeted,
            mix_neighbor=args.mix_neighbor,
            mix_replay=args.mix_replay,
            recent_frontier=recent_frontier,
            neighbor_window=args.neighbor_window,
            adaptive=args.adaptive_mixture,
        )
        for index, task in enumerate(tasks):
            if weights[index] <= 0.0:
                continue
            for method in research_methods:
                weights[index] = max(
                    0.0,
                    float(method.adjust_task_weight(weights[index], task=task, stage="grpo")),
                )
        weight_sum = sum(weights)
        task_index = random.choices(range(len(tasks)), weights=weights, k=1)[0]
        task = tasks[task_index]
        task_prob = weights[task_index] / weight_sum if weight_sum > 0 else 1.0 / len(tasks)
        prompt = build_prompt(task, research_methods=research_methods)
        test_harness = load_test_harness(task["tests_py"])

        # Generate group of solutions (adaptive temperature escalation on repeated low-signal skips;
        # adaptive group size from the posterior router — review 2026-08-05 #4)
        active_model = model.module if distributed else model
        active_model.eval()
        effective_temperature = adaptive_temp.current_temp()
        effective_g = min(router.recommended_group_size(task["task_id"]), args.max_adaptive_group)
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "step_begin",
                        "step": step,
                        "task": task["task_id"],
                        "temperature": effective_temperature,
                        "group_size": effective_g,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        codes, prompt_text = generate_group(
            active_model,
            text_preprocessor,
            prompt,
            args,
            temperature=effective_temperature,
            count=effective_g,
        )
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "generation_done",
                        "step": step,
                        "n_codes": len(codes),
                        "max_code_chars": max((len(code) for code in codes), default=0),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        _release_device_cache(torch)

        consistent_old_log_probs = []
        consistent_old_token_counts = []
        consistent_entropies = []
        with torch.no_grad():
            for code in codes:
                old_log_prob, old_token_count, entropy = compute_completion_log_prob(
                    active_model,
                    tokenizer,
                    prompt_text,
                    code,
                    device,
                    args.max_seq_length,
                    args.logit_clip,
                    add_mm_token_type_ids=_needs_mm_token_type_ids,
                    return_entropy=True,
                )
                consistent_old_log_probs.append(old_log_prob.detach())
                consistent_old_token_counts.append(old_token_count.detach())
                consistent_entropies.append(entropy.detach())
                # Release the allocator cache between per-completion forwards:
                # long sequential forward runs are the ASI2 27B stall trigger.
                _release_device_cache(torch)
        old_log_probs = torch.stack(consistent_old_log_probs)
        old_token_counts = torch.stack(consistent_old_token_counts)
        entropy_values = [float(value.item()) for value in consistent_entropies]
        entropy_mean = float(sum(entropy_values) / len(entropy_values)) if entropy_values else None
        generation_tokens = int(old_token_counts.sum().item())
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "logprob_done",
                        "step": step,
                        "generation_tokens": generation_tokens,
                        "entropy_mean": entropy_mean,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        _release_device_cache(torch)

        # Score each solution with verifier-aware shaped rewards + optional self-evaluation.
        judge_enabled = bool(args.model_judge_enabled and judge_model is not None)
        evaluations = []
        self_repair_summary: dict[str, Any] = {
            "enabled": int(args.self_repair_rounds > 0),
            "max_rounds": args.self_repair_rounds,
            "candidates_repaired": 0,
            "repairs_passed": 0,
            "total_repair_rounds": 0,
        }
        for c in codes:
            entry = evaluate_candidate(
                c,
                test_harness,
                task,
                args,
                research_methods=research_methods,
                model=active_model if args.self_evaluation_enabled else None,
                backend=text_preprocessor
                if (args.self_evaluation_enabled or judge_enabled)
                else None,
                device=device if (args.self_evaluation_enabled or judge_enabled) else None,
                judge_model=judge_model if judge_enabled else None,
                judge_weights=judge_weights if judge_enabled else None,
                judge_diagnostics_path=(
                    judge_diagnostics_path if (judge_enabled and rank == 0) else None
                ),
                step=step,
            )
            # Teacher-free self-repair (plan §8): a failing candidate is re-rolled
            # by the policy itself with its exact harness errors appended, up to
            # `--self-repair-rounds` rounds. Only an independently-passing repair
            # replaces the original behavior sample, so the GRPO relative
            # advantage stays well-defined on the policy's own outputs.
            if args.self_repair_rounds > 0 and float(entry.get("pass_reward", 0.0)) <= 0.0:
                repair_ctx = _self_repair_failing_candidate(
                    model=active_model,
                    text_preprocessor=text_preprocessor,
                    device=device,
                    test_harness=test_harness,
                    task=task,
                    code=c,
                    task_prompt=prompt,
                    result={
                        "passed": bool(entry.get("pass_reward", 0.0) > 0.0),
                        "details": entry.get("details", []),
                    },
                    args=args,
                    max_rounds=args.self_repair_rounds,
                    temperature=effective_temperature,
                )
                self_repair_summary["total_repair_rounds"] += len(repair_ctx.get("attempted", []))
                if repair_ctx.get("passed"):
                    # Accept the passing repair: suffuse its rewards into the entry.
                    repaired_code = repair_ctx["code"]
                    repaired_entry = evaluate_candidate(
                        repaired_code,
                        test_harness,
                        task,
                        args,
                        research_methods=research_methods,
                        model=active_model if args.self_evaluation_enabled else None,
                        backend=text_preprocessor
                        if (args.self_evaluation_enabled or judge_enabled)
                        else None,
                        device=device if (args.self_evaluation_enabled or judge_enabled) else None,
                        judge_model=judge_model if judge_enabled else None,
                        judge_weights=judge_weights if judge_enabled else None,
                        judge_diagnostics_path=None,
                        step=step,
                    )
                    self_repair_summary["repairs_passed"] += 1
                    # Reuse the original code for logprob/consistency tracking but
                    # adopt the repair's (higher) executable rewards so the policy
                    # gets credit for the improvement.
                    entry["pass_reward"] = repaired_entry.get("pass_reward", entry["pass_reward"])
                    entry["total_reward"] = repaired_entry.get(
                        "total_reward", entry["total_reward"]
                    )
                    entry["self_repair_passed"] = True
                    entry["self_repair_round"] = repair_ctx.get("best_round", 0)
                else:
                    entry["self_repair_passed"] = False
                    entry["self_repair_best_round"] = repair_ctx.get("best_round", 0)
                self_repair_summary["candidates_repaired"] += 1
            evaluations.append(entry)
        # Incorporate self-eval reward into total
        for entry in evaluations:
            entry["total_reward"] = entry.get("total_reward", entry.get("reward", 0.0))
            entry["total_reward"] = entry["total_reward"] + entry.get("self_eval_reward", 0.0)
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "eval_done",
                        "step": step,
                        "n_candidates": len(evaluations),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        _release_device_cache(torch)

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
        self_eval_rewards = torch.tensor(
            [float(entry.get("self_eval_reward", 0.0)) for entry in evaluations], device=device
        )

        # Compute group-relative rewards.
        mean_reward = rewards.mean()
        signal_stats = reward_signal_stats(
            rewards,
            pass_rewards,
            syntax_rewards,
            interface_rewards,
            verifier_rewards,
            brevity_rewards,
        )
        task_state = curriculum.record(task["task_id"], float(mean_reward))

        # Aggregate frozen-judge dimension scores across the group for metrics.
        model_dim_means: dict[str, float] = {}
        if judge_enabled:
            for dim in MODEL_JUDGE_DIMENSIONS:
                values = [
                    float(entry["model_dim_scores"][dim])
                    for entry in evaluations
                    if isinstance(entry.get("model_dim_scores", {}).get(dim), int | float)
                ]
                if values:
                    model_dim_means[dim] = sum(values) / len(values)

        # ── FV-GSPO: probe the group and route it (frontier router) ──
        pass_rate = float(pass_rewards.mean().item())
        probe = router.probe_record(
            task["task_id"],
            step,
            pass_rate,
            signal_stats["signal_std"],
            group_size=effective_g,
        )
        route = str(probe["route"])
        total_probes += 1
        all_fail = pass_rate == 0.0
        frontier_fraction = router.frontier_fraction()
        if route in RL_ROUTES:
            recent_frontier.append(task["task_id"])
            del recent_frontier[: -args.neighbor_window]

        # ── FV-GSPO: leave-one-out advantages (Dr.GRPO) ──
        # No per-task standard-deviation normalization; optional shared running
        # MAD is the only allowed batch-level scaling.
        if args.advantage_mode == "group_std":
            # Ablation baseline: reproduce the legacy per-group normalized advantage.
            std_reward = rewards.std(unbiased=False)
            advantage_scale = max(signal_stats["signal_std"], float(std_reward.item()), 1e-8)
            advantages = ((rewards - mean_reward) / advantage_scale).clamp(
                -args.advantage_clip,
                args.advantage_clip,
            )
        else:  # loo (FV-GSPO default)
            advantages = leave_one_out_advantages(rewards)
            if args.loo_advantage_scale == "shared_mad":
                running_mad.update(advantages)
                advantages = advantages / running_mad.scale
            advantage_scale = (
                running_mad.scale if args.loo_advantage_scale == "shared_mad" else None
            )
            advantages = advantages.clamp(-args.advantage_clip, args.advantage_clip)

        repair_queued = False
        step_ctx: dict[str, Any] = {
            "step": step,
            "task_name": task["task_dir"].name,
            "domain": task["meta"].get("domain", "?"),
            "mean_reward": float(mean_reward),
            "signal_stats": signal_stats,
            "pass_rate": pass_rate,
            "syntax_rate": float(syntax_rewards.mean()),
            "interface_rate": float(interface_rewards.mean()),
            "verifier_rate": float(verifier_rewards.mean()),
            "task_prob": float(task_prob),
            "task_state": task_state,
            "advantage_scale": advantage_scale,
            "adapter_init": args.adapter_init,
            "route": route,
            "entropy_mean": entropy_mean,
            "generation_tokens": generation_tokens,
            "repair_queued": repair_queued,
            "all_fail": all_fail,
            "frontier_fraction": frontier_fraction,
            "model_dim_scores": model_dim_means or None,
            "model_judge_enabled": judge_enabled or None,
            "posterior_lower": probe.get("posterior_lower"),
            "posterior_upper": probe.get("posterior_upper"),
            "flaky": bool(probe.get("flaky")),
            "group_size": effective_g,
            "teacher_free_self_repair": self_repair_summary,
        }

        # ── Route the group ──
        # All-fail groups with no shaped variation are NOT RL batches: they go to
        # the execution-verified repair lane (repair SFT/DPO queue) instead.
        if route in (REPAIR_SFT, INVALID_OR_NOISY):
            if route == REPAIR_SFT:
                best_index = max(
                    range(len(evaluations)),
                    key=lambda idx: (
                        float(evaluations[idx].get("verifier_reward", 0.0)),
                        float(evaluations[idx].get("total_reward", 0.0)),
                    ),
                )
                best = evaluations[best_index]
                failures = [str(detail) for detail in (best.get("details") or [])]
                append_repair_queue_record(
                    repair_queue_path,
                    {
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "step": step,
                        "task_id": task["task_id"],
                        "domain": task["meta"].get("domain", "?"),
                        "category": task["meta"].get("category", "?"),
                        "best_code": codes[best_index],
                        "failures": failures[:8],
                        "pass_rate": pass_rate,
                        "verifier_rate": float(verifier_rewards[best_index].item()),
                    },
                )
                repair_queued = True
                step_ctx["repair_queued"] = True
            trips = observe_and_evaluate_breakers(
                breaker,
                step=step,
                route=route,
                non_finite=False,
                clip_fraction=0.0,
                entropy_mean=entropy_mean,
                repair_queued=repair_queued,
                repair_converted_jsonl=args.repair_converted_jsonl,
                all_fail=all_fail,
            )
            emit_step_record(
                rank=rank,
                metrics=metrics,
                step_metrics_path=step_metrics_path,
                log_steps=args.log_steps,
                ctx=step_ctx,
                skipped=True,
                reason=f"{route}_queued",
                trips=trips,
            )
            if maybe_stop_for_breaker(breaker, args, rank, trips):
                break
            continue

        # Skip flat mastered groups: keep a small replay quota but do not burn
        # an optimizer step on a group whose leave-one-out advantages are ~0.
        if route == MASTERED_REPLAY and signal_stats["signal_std"] < args.min_reward_std:
            trips = observe_and_evaluate_breakers(
                breaker,
                step=step,
                route=route,
                non_finite=False,
                clip_fraction=0.0,
                entropy_mean=entropy_mean,
                repair_queued=repair_queued,
                repair_converted_jsonl=args.repair_converted_jsonl,
                all_fail=all_fail,
            )
            emit_step_record(
                rank=rank,
                metrics=metrics,
                step_metrics_path=step_metrics_path,
                log_steps=args.log_steps,
                ctx=step_ctx,
                skipped=True,
                reason="mastered_replay_flat",
                trips=trips,
            )
            if maybe_stop_for_breaker(breaker, args, rank, trips):
                break
            continue

        # Skip only when both total and component reward signals are flat on an
        # RL route (adaptive temperature escalation applies here).
        if route in RL_ROUTES and signal_stats["signal_std"] < args.min_reward_std:
            adaptive_temp.record_skip("low_reward_signal")
            trips = observe_and_evaluate_breakers(
                breaker,
                step=step,
                route=route,
                non_finite=False,
                clip_fraction=0.0,
                entropy_mean=entropy_mean,
                repair_queued=repair_queued,
                repair_converted_jsonl=args.repair_converted_jsonl,
                all_fail=all_fail,
            )
            emit_step_record(
                rank=rank,
                metrics=metrics,
                step_metrics_path=step_metrics_path,
                log_steps=args.log_steps,
                ctx=step_ctx,
                skipped=True,
                reason="low_reward_signal",
                trips=trips,
            )
            if maybe_stop_for_breaker(breaker, args, rank, trips):
                break
            continue

        # Forward pass to get current completion-only log probs and apply GRPO loss.
        active_model.train()
        current_log_probs = []
        normalized_old_log_probs = []
        filtered_advantages = []
        filtered_token_counts = []
        for idx, code in enumerate(codes):
            current_log_prob, token_count = compute_completion_log_prob(
                active_model,
                tokenizer,
                prompt_text,
                code,
                device,
                args.max_seq_length,
                args.logit_clip,
                add_mm_token_type_ids=_needs_mm_token_type_ids,
            )
            # Release the allocator cache between per-completion forwards:
            # p16 hung right here (group-8 train-logprob, 8 grad-enabled
            # forwards with full-vocab logits) after 41 min of silence.
            _release_device_cache(torch)
            if token_count.item() == 0:
                continue
            current_log_probs.append(current_log_prob / token_count.clamp_min(1))
            normalized_old_log_probs.append(old_log_probs[idx] / old_token_counts[idx].clamp_min(1))
            filtered_advantages.append(advantages[idx])
            filtered_token_counts.append(old_token_counts[idx].float())

        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "train_logprob_done",
                        "step": step,
                        "n_current": len(current_log_probs),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        _release_device_cache(torch)
        if not current_log_probs:
            adaptive_temp.record_skip("empty_completion_mask")
            trips = observe_and_evaluate_breakers(
                breaker,
                step=step,
                route=route,
                non_finite=False,
                clip_fraction=0.0,
                entropy_mean=entropy_mean,
                repair_queued=repair_queued,
                repair_converted_jsonl=args.repair_converted_jsonl,
                all_fail=all_fail,
            )
            emit_step_record(
                rank=rank,
                metrics=metrics,
                step_metrics_path=step_metrics_path,
                log_steps=args.log_steps,
                ctx=step_ctx,
                skipped=True,
                reason="empty_completion_mask",
                trips=trips,
            )
            if maybe_stop_for_breaker(breaker, args, rank, trips):
                break
            continue

        # ── FV-GSPO: sequence-level clipped objective (GSPO) or legacy ablation ──
        # Adaptive KL: measure the batch's sequence KL and adjust beta before
        # the loss so the penalty reflects current drift from the anchor.
        effective_kl = args.kl_coeff
        if kl_state is not None:
            with torch.no_grad():
                seq_kl_now = float(
                    (torch.stack(normalized_old_log_probs) - torch.stack(current_log_probs))
                    .mean()
                    .item()
                )
            effective_kl = kl_state.update(seq_kl_now)
        gspo_stats: dict[str, float] | None = None
        length_weights: torch.Tensor | None = None
        if args.loss_mode == "gspo_ln":
            # LUSPO-style length neutralization: w_i = min(|y_i|/L_ref, w_max).
            counts = torch.stack(filtered_token_counts)
            length_weights = torch.clamp(
                counts / max(args.ln_reference_length, 1.0), max=args.ln_max_weight
            )
        if args.loss_mode in ("gspo", "gspo_ln"):
            total_loss, gspo_stats = stable_gspo_loss_metrics(
                torch.stack(current_log_probs),
                torch.stack(normalized_old_log_probs),
                torch.stack(filtered_advantages),
                clip_low=args.gspo_clip_low,
                clip_high=args.gspo_clip_high,
                kl_coeff=effective_kl,
                numerical_log_ratio_clip=args.numerical_log_ratio_clip,
                length_weights=length_weights,
            )
        else:
            total_loss = grpo_loss(
                torch.stack(current_log_probs),
                torch.stack(normalized_old_log_probs),
                torch.stack(filtered_advantages),
                effective_kl,
                args.ratio_clip_log_delta,
            )
        # Doubly-Robust DPO pair loss (only active when the
        # doubly_robust_quantum_grpo research method is enabled).
        # The helper is a no-op (returns zero) when the plugin is
        # absent or no pair is mined, so this is safe for base GRPO.
        dr_pair_loss_term, dr_pair_info = compute_dr_pair_loss(
            research_methods=research_methods,
            rewards=rewards,
            codes=codes,
            current_log_probs=current_log_probs,
            old_log_probs=normalized_old_log_probs,
        )
        if torch.isfinite(dr_pair_loss_term) and float(dr_pair_loss_term.item()) != 0.0:
            total_loss = total_loss + dr_pair_loss_term
        # Doubly-Robust PPO-side variance correction (psi * E[(r-1)*A]).
        # Only active when the doubly_robust_quantum_grpo plugin is
        # enabled and dr_psi_init > 0. Safe no-op for base GRPO.
        dr_variance_term, dr_variance_info = compute_dr_variance_correction(
            research_methods=research_methods,
            log_probs=torch.stack(current_log_probs),
            old_log_probs=torch.stack(normalized_old_log_probs),
            advantages=torch.stack(filtered_advantages),
            ratio_clip_log_delta=args.ratio_clip_log_delta,
            current_step=step,
        )
        if torch.isfinite(dr_variance_term) and float(dr_variance_term.item()) != 0.0:
            total_loss = total_loss + dr_variance_term
        if not torch.isfinite(total_loss):
            adaptive_temp.record_skip("non_finite_loss")
            trips = observe_and_evaluate_breakers(
                breaker,
                step=step,
                route=route,
                non_finite=True,
                clip_fraction=0.0,
                entropy_mean=entropy_mean,
                repair_queued=repair_queued,
                repair_converted_jsonl=args.repair_converted_jsonl,
                all_fail=all_fail,
            )
            emit_step_record(
                rank=rank,
                metrics=metrics,
                step_metrics_path=step_metrics_path,
                log_steps=args.log_steps,
                ctx=step_ctx,
                skipped=True,
                reason="non_finite_loss",
                trips=trips,
            )
            if maybe_stop_for_breaker(breaker, args, rank, trips):
                break
            continue
        optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_param_tensors, 1.0)
        if rank == 0:
            print(
                json.dumps(
                    {
                        "stage": "backward_done",
                        "step": step,
                        "loss": float(total_loss.detach().item()),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        _release_device_cache(torch)

        # ── trust region (review 2026-08-05, Design B) ──
        # The pre-update ratio is 1 by construction in the synchronous
        # one-rollout-per-step implementation, so GSPO clipping cannot
        # constrain this update. Take the update, then measure the post-update
        # sequence ratio and KL on the same rollouts and reject (or scale LR
        # for) violations.
        saved_params: list[torch.Tensor] | None = None
        saved_optim: dict | None = None
        if args.trust_region_enabled:
            saved_params = [p.detach().clone() for p in trainable_param_tensors]
            saved_optim = optimizer.state_dict()
        optimizer.step()
        adaptive_temp.record_update()
        router.record_rl_update(task["task_id"])

        trust_region_violated = False
        ratio_after_update = 0.0
        clip_fraction_after_update = 0.0
        seq_kl_after = 0.0
        if args.trust_region_enabled and saved_params is not None and current_log_probs:
            active_model.eval()
            with torch.no_grad():
                post_log_probs: list[torch.Tensor] = []
                for code in codes:
                    post_log_prob, post_token_count = compute_completion_log_prob(
                        active_model,
                        tokenizer,
                        prompt_text,
                        code,
                        device,
                        args.max_seq_length,
                        args.logit_clip,
                        add_mm_token_type_ids=_needs_mm_token_type_ids,
                    )
                    if post_token_count.item() > 0:
                        post_log_probs.append(post_log_prob / post_token_count.clamp_min(1))
            if post_log_probs:
                trust_stats = sequence_ratio_stats(
                    torch.stack(post_log_probs),
                    torch.stack(normalized_old_log_probs),
                    clip_low=args.gspo_clip_low,
                    clip_high=args.gspo_clip_high,
                    numerical_log_ratio_clip=args.numerical_log_ratio_clip,
                )
                ratio_after_update = trust_stats["ratio_after_update"]
                clip_fraction_after_update = trust_stats["clip_fraction_after_update"]
                seq_kl_after = trust_stats["seq_kl_after"]
                trust_region_violated = (
                    seq_kl_after > args.trust_region_max_seq_kl
                    or clip_fraction_after_update > args.trust_region_max_clip_fraction
                )
                if trust_region_violated:
                    if args.trust_region_on_violation == "reject":
                        for param, saved in zip(trainable_param_tensors, saved_params, strict=True):
                            param.data.copy_(saved)
                        optimizer.load_state_dict(saved_optim)
                    else:  # scale_lr
                        for group in optimizer.param_groups:
                            group["lr"] *= 0.5

        clip_fraction = (
            float(gspo_stats.get("clip_total_fraction", 0.0)) if gspo_stats is not None else 0.0
        )
        trips = observe_and_evaluate_breakers(
            breaker,
            step=step,
            route=route,
            non_finite=False,
            clip_fraction=clip_fraction,
            entropy_mean=entropy_mean,
            repair_queued=repair_queued,
            repair_converted_jsonl=args.repair_converted_jsonl,
            all_fail=all_fail,
        )
        record = emit_step_record(
            rank=rank,
            metrics=metrics,
            step_metrics_path=step_metrics_path,
            log_steps=args.log_steps,
            ctx=step_ctx,
            skipped=False,
            loss=float(total_loss.item()),
            trips=trips,
            ratio_mean=float(gspo_stats.get("ratio_mean", 0.0)) if gspo_stats is not None else None,
            clip_low_fraction=float(gspo_stats.get("clip_low_fraction", 0.0))
            if gspo_stats is not None
            else None,
            clip_high_fraction=float(gspo_stats.get("clip_high_fraction", 0.0))
            if gspo_stats is not None
            else None,
            seq_kl=float(gspo_stats.get("seq_kl", 0.0)) if gspo_stats is not None else None,
            self_eval_rate=float(self_eval_rewards.mean())
            if args.self_evaluation_enabled
            else None,
        )
        if record is not None:
            if kl_state is not None:
                record["kl_beta"] = kl_state.beta
            record["trust_region_violated"] = bool(trust_region_violated)
            record["ratio_after_update"] = ratio_after_update
            record["clip_fraction_after_update"] = clip_fraction_after_update
            record["seq_kl_after"] = seq_kl_after
            record["old_policy_age"] = 1
            record["optimizer_substeps_per_rollout"] = 1
            record["mean_response_length"] = float(old_token_counts.mean().item())
            record["truncation_rate"] = float(
                (old_token_counts >= args.max_new_tokens).float().mean().item()
            )
            if dr_pair_info:
                record["dr_pair_mined"] = bool(dr_pair_info.get("dr_pair_mined"))
                record["dr_pair_reward_gap"] = float(dr_pair_info.get("dr_pair_reward_gap", 0.0))
                record["dr_pair_loss_value"] = float(dr_pair_info.get("dr_pair_loss_value", 0.0))
                record["dr_pair_loss_weight"] = float(dr_pair_info.get("dr_pair_loss_weight", 0.0))
            if dr_variance_info:
                record["dr_variance_correction_value"] = float(
                    dr_variance_info.get("dr_variance_correction_value", 0.0)
                )
                record["dr_psi"] = float(dr_variance_info.get("dr_psi", 0.0))
                record["dr_psi_init"] = float(dr_variance_info.get("dr_psi_init", 0.0))
                record["dr_psi_warmup_steps"] = int(dr_variance_info.get("dr_psi_warmup_steps", 0))
                record["dr_psi_current_step"] = dr_variance_info.get("dr_psi_current_step")
        if maybe_stop_for_breaker(breaker, args, rank, trips):
            break

            # ── Periodic checkpoint: save adapter every checkpoint_interval_seconds ──
            if args.checkpoint_interval_seconds > 0 and rank == 0:
                now = time.time()
                if now - _last_checkpoint_time >= args.checkpoint_interval_seconds:
                    _last_checkpoint_time = now
                    ckpt_dir = output_dir / f"step_{step:06d}_adapter"
                    save_model = model.module if distributed else model
                    save_model.save_pretrained(ckpt_dir)
                    text_preprocessor.save_backend.save_pretrained(ckpt_dir)
                    # Also update the main adapter dir (for sync daemon)
                    main_adapter = output_dir / "adapter"
                    save_model.save_pretrained(main_adapter)
                    text_preprocessor.save_backend.save_pretrained(main_adapter)
                    print(f"[checkpoint] saved adapter at step {step} to {ckpt_dir}")

    # Save final
    if rank == 0:
        save_model = model.module if distributed else model
        adapter_dir = output_dir / "adapter"
        save_model.save_pretrained(adapter_dir)
        text_preprocessor.save_backend.save_pretrained(adapter_dir)
        (output_dir / "grpo_metrics.json").write_text(
            json.dumps(build_grpo_metrics_payload(metrics, planned_steps=args.grpo_steps), indent=2)
            + "\n"
        )
        (output_dir / "run_config.json").write_text(
            json.dumps(
                {
                    "model_name": args.model_name,
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
                    "device": str(args.device),
                    "reward_pass_weight": args.reward_pass_weight,
                    "reward_syntax_weight": args.reward_syntax_weight,
                    "reward_interface_weight": args.reward_interface_weight,
                    "reward_verifier_weight": args.reward_verifier_weight,
                    "reward_brevity_weight": args.reward_brevity_weight,
                    "brevity_target_lines": args.brevity_target_lines,
                    "reward_detail_budget_cap": args.reward_detail_budget_cap,
                    "advantage_clip": args.advantage_clip,
                    "ratio_clip_log_delta": args.ratio_clip_log_delta,
                    "top_p": args.top_p,
                    "logit_clip": args.logit_clip,
                    "min_reward_std": args.min_reward_std,
                    "curriculum_ema_decay": args.curriculum_ema_decay,
                    "curriculum_min_weight": args.curriculum_min_weight,
                    "curriculum_uncertainty_bonus": args.curriculum_uncertainty_bonus,
                    "quantum_priority": args.quantum_priority,
                    "loss_mode": args.loss_mode,
                    "gspo_clip_low": args.gspo_clip_low,
                    "gspo_clip_high": args.gspo_clip_high,
                    "numerical_log_ratio_clip": args.numerical_log_ratio_clip,
                    "ln_reference_length": args.ln_reference_length,
                    "ln_max_weight": args.ln_max_weight,
                    "advantage_mode": args.advantage_mode,
                    "loo_advantage_scale": args.loo_advantage_scale,
                    "frontier_threshold": args.frontier_threshold,
                    "mastered_threshold": args.mastered_threshold,
                    "mix_targeted": args.mix_targeted,
                    "mix_neighbor": args.mix_neighbor,
                    "mix_replay": args.mix_replay,
                    "neighbor_window": args.neighbor_window,
                    "repair_queue_path": str(repair_queue_path),
                    "repair_converted_jsonl": args.repair_converted_jsonl,
                    "coverage_json": args.coverage_json,
                    "stop_on_severe_breaker": args.stop_on_severe_breaker,
                    "model_judge_enabled": bool(args.model_judge_enabled),
                    "judge_model_path": args.judge_model_path,
                    "judge_adapter_path": args.judge_adapter_path,
                    "judge_device": str(args.judge_device),
                    "judge_weights": judge_weights,
                    "judge_diagnostics_path": str(judge_diagnostics_path)
                    if judge_diagnostics_path
                    else None,
                    "reward_mode": args.reward_mode,
                    "reward_masses": {
                        "pass": args.reward_pass_mass,
                        "shaped": args.reward_shaped_mass,
                        "judge": args.reward_judge_mass,
                    },
                    "trust_region_enabled": bool(args.trust_region_enabled),
                    "trust_region_max_seq_kl": args.trust_region_max_seq_kl,
                    "trust_region_max_clip_fraction": args.trust_region_max_clip_fraction,
                    "trust_region_on_violation": args.trust_region_on_violation,
                    "research_methods": summarize_methods(research_methods),
                    "curriculum_state": curriculum.state,
                    "frontier_router_state": router.state,
                    "frontier_fraction": router.frontier_fraction(),
                    "circuit_breaker_state": breaker.to_dict(),
                    "running_mad_scale": running_mad.scale,
                    "total_probes": total_probes,
                    "adaptive_kl": bool(args.adaptive_kl),
                    "kl_state": kl_state.to_dict() if kl_state is not None else None,
                    "target_modules": list(args.target_modules) if args.target_modules else None,
                    "target_module_regex": list(args.target_module_regex)
                    if args.target_module_regex
                    else None,
                    "resolved_target_modules": resolved_target_modules,
                    "trainable_param_regex": list(getattr(args, "trainable_param_regex", []) or [])
                    or None,
                    "freeze_param_regex": list(getattr(args, "freeze_param_regex", []) or [])
                    or None,
                    "selective_training": selective_training,
                    "trainable_parameter_count": trainable_param_count,
                    "trainable_parameter_sample": trainable_param_names[:12],
                    "text_forward_preflight": text_forward_preflight,
                },
                indent=2,
            )
            + "\n"
        )
        print(f"\nSaved adapter to {adapter_dir}")

    if distributed:
        torch.distributed.destroy_process_group()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
