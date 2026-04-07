#!/usr/bin/env python3
"""GRPO (Group Relative Policy Optimization) trainer for code generation.

Samples N solutions per prompt, scores them with test harnesses,
and updates the policy using relative advantage within each group.

Usage:
    torchrun --nproc_per_node=2 training/grpo_trainer.py \
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
import uuid
from pathlib import Path
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.qwen_sft_peft import (  # noqa: E402
    TextPreprocessorBackend,
    load_text_preprocessor_backend,
    resolve_lora_target_modules,
)
from training.grpo_utils import (  # noqa: E402
    AdaptiveTemperatureState,
    TaskCurriculum,
    append_grpo_metric,
    append_grpo_metric_jsonl,
    build_grpo_metrics_payload,
    build_grpo_step_record,
    build_reward_breakdown,
    estimate_detail_budget,
    extract_behavior_hints_from_test_source,
    load_grpo_step_metrics_jsonl,
    reward_signal_stats,
    stable_grpo_loss,
    stable_token_log_probs,
    summarize_python_interface,
)
from training.research_plugins import load_research_methods, summarize_methods  # noqa: E402


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
    p.add_argument("--grpo-steps", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--kl-coeff", type=float, default=0.05, help="KL penalty coefficient")
    p.add_argument("--temperature", type=float, default=0.8)
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
    p.add_argument("--log-steps", type=int, default=5)
    p.add_argument("--lora-rank", type=int, default=8)
    p.add_argument("--lora-alpha", type=int, default=16)
    p.add_argument(
        "--target-modules",
        nargs="*",
        default=None,
        help="Optional explicit LoRA target module suffixes. Defaults to auto-discovery from the loaded model.",
    )
    p.add_argument("--reward-pass-weight", type=float, default=0.6)
    p.add_argument("--reward-syntax-weight", type=float, default=0.1)
    p.add_argument("--reward-interface-weight", type=float, default=0.15)
    p.add_argument("--reward-verifier-weight", type=float, default=0.15)
    p.add_argument("--reward-brevity-weight", type=float, default=0.0,
                   help="Weight for brevity reward; set >0 to break flat-reward deadlocks.")
    p.add_argument("--brevity-target-lines", type=int, default=40,
                   help="Target line count for full brevity reward.")
    p.add_argument("--reward-detail-budget-cap", type=int, default=8)
    p.add_argument("--advantage-clip", type=float, default=2.5)
    p.add_argument("--ratio-clip-log-delta", type=float, default=8.0)
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


def discover_tasks(tasks_dir: Path, requested_task_ids: set[str] | None = None, allowed_domains: set[str] | None = None) -> list[dict]:
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
    parts.append(f"Domain: {meta.get('domain', 'unknown')}\nCategory: {meta.get('category', 'unknown')}")

    candidate_file = meta.get("candidate_file")
    if candidate_file:
        interface_lines = task.get("required_interface") or summarize_candidate_interface(task["task_dir"] / candidate_file)
        if interface_lines:
            parts.append("Required interface:\n" + "\n".join(f"- {line}" for line in interface_lines))

    behavior_hints = task.get("behavior_hints") or extract_behavior_hints(task["tests_py"])
    if behavior_hints:
        parts.append("Behavioral requirements:\n" + "\n".join(f"- {line}" for line in behavior_hints))

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


def evaluate_candidate(code: str, test_harness, task: dict, args, research_methods: list[Any] | None = None) -> dict[str, Any]:
    """Run tests and return a shaped reward breakdown."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir=str(task["task_dir"])) as f:
        f.write(code)
        f.flush()
        path = f.name
    try:
        result = test_harness.run_tests(path)
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
    finally:
        Path(path).unlink(missing_ok=True)

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
    )
    reward["details"] = result.get("details", []) if isinstance(result, dict) else []
    for method in research_methods or []:
        reward = method.adjust_reward_breakdown(
            reward,
            code=code,
            result=result,
            task=task,
            stage="grpo",
        )
    return reward


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
            return render_backend.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return "\n\n".join(f"{message['role'].upper()}: {message['content']}" for message in messages)


def move_batch_to_device(batch: dict[str, torch.Tensor], device: Any) -> dict[str, torch.Tensor]:
    return {name: tensor.to(device) for name, tensor in batch.items()}


def generate_group(model, backend: TextPreprocessorBackend, prompt: str, args, *, temperature: float | None = None) -> tuple[list[str], str]:
    """Generate a group of solutions and return (codes, prompt_text).

    Args:
        temperature: Override the base sampling temperature.  When adaptive
            temperature escalation is active, pass the escalated value here.
            Falls back to ``args.temperature`` if not specified.
    """
    text = render_generation_prompt(backend.render_backend, prompt)
    inputs = move_batch_to_device(backend.text_backend(text, return_tensors="pt"), args.device)
    effective_temp = temperature if temperature is not None else args.temperature

    codes = []

    for _ in range(args.group_size):
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=effective_temp,
                do_sample=True,
                return_dict_in_generate=True,
                output_scores=True,
            )

        gen_ids = outputs.sequences[0, inputs["input_ids"].shape[1]:]
        response = backend.text_backend.decode(gen_ids, skip_special_tokens=True)
        codes.append(extract_code(response))

    return codes, text


def compute_completion_log_prob(
    model,
    tokenizer,
    prompt_text: str,
    completion_text: str,
    device: Any,
    max_seq_length: int,
    logit_clip: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    prompt_inputs = tokenizer(prompt_text, return_tensors="pt", truncation=True, max_length=max_seq_length)
    full_inputs = tokenizer(prompt_text + completion_text, return_tensors="pt", truncation=True, max_length=max_seq_length)
    full_inputs = move_batch_to_device(full_inputs, device)
    prompt_len = min(prompt_inputs["input_ids"].shape[1], full_inputs["input_ids"].shape[1])

    outputs = model(**full_inputs)
    logits = outputs.logits[:, :-1, :]
    target_ids = full_inputs["input_ids"][:, 1:]
    token_log_probs = stable_token_log_probs(logits, target_ids, logit_clip)

    completion_mask = torch.zeros_like(target_ids, dtype=torch.bool)
    completion_start = max(prompt_len - 1, 0)
    completion_mask[:, completion_start:] = True
    attention_mask = full_inputs.get("attention_mask")
    if attention_mask is not None:
        completion_mask &= attention_mask[:, 1:].bool()
    token_count = completion_mask.sum()
    if token_count.item() == 0:
        return token_log_probs.new_tensor(0.0), token_count
    seq_log_prob = token_log_probs.masked_select(completion_mask).sum()
    return seq_log_prob, token_count


def grpo_loss(log_probs: torch.Tensor, old_log_probs: torch.Tensor,
              advantages: torch.Tensor, kl_coeff: float,
              ratio_clip_log_delta: float) -> torch.Tensor:
    """GRPO loss: policy gradient with group-relative advantages + KL penalty."""
    return stable_grpo_loss(
        log_probs=log_probs,
        old_log_probs=old_log_probs,
        advantages=advantages,
        kl_coeff=kl_coeff,
        ratio_clip_log_delta=ratio_clip_log_delta,
    )


def main() -> int:
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
    distributed = "RANK" in os.environ
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    rank = int(os.environ.get("RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))

    if distributed:
        if args.device == "npu":
            import torch_npu
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
            import torch_npu
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
            print(json.dumps({"stage": "warm_restart", "resume_from": str(resume_path), "resume_step": resume_step, "prior_records": len(resume_metrics)}))

    if rank == 0:
        if not args.resume_from:
            step_metrics_path.unlink(missing_ok=True)
        metrics_path.unlink(missing_ok=True)
        run_config_path.unlink(missing_ok=True)
        # When resuming, seed the JSONL with prior records
        if resume_metrics:
            for prior_record in resume_metrics:
                append_grpo_metric_jsonl(step_metrics_path, prior_record)

    tasks = discover_tasks(Path(args.tasks_dir), requested_task_ids=requested_task_ids, allowed_domains=allowed_domains)
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
    from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast
    from peft import LoraConfig, PeftModel, TaskType, get_peft_model

    text_preprocessor = load_text_preprocessor_backend(args.model_name, AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast)
    tokenizer = text_preprocessor.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        torch_dtype="auto",
    )
    if args.adapter_init:
        model = PeftModel.from_pretrained(model, str(args.adapter_init), is_trainable=True)
        resolved_target_modules = None
    else:
        resolved_target_modules = resolve_lora_target_modules(args.target_modules, model)
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=0.05,
            target_modules=resolved_target_modules,
            bias="none",
        )
        model = get_peft_model(model, lora_config)
    model.to(device)

    if distributed:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
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
    # Replay curriculum state from resumed records
    for prior in resume_metrics:
        task_name = str(prior.get("task", ""))
        mr = float(prior.get("mean_reward", 0.0))
        if task_name:
            curriculum.record(task_name, mr)
        if bool(prior.get("skipped")) and prior.get("reason") == "low_reward_signal":
            adaptive_temp.record_skip("low_reward_signal")
        elif not bool(prior.get("skipped")):
            adaptive_temp.record_update()

    for task in tasks:
        task_id = task["meta"].get("id", task["task_dir"].name)
        candidate_file = task["meta"].get("candidate_file")
        required_interface = summarize_candidate_interface(task["task_dir"] / candidate_file) if candidate_file else []
        behavior_hints = extract_behavior_hints(task["tests_py"])
        test_source = task["tests_py"].read_text(encoding="utf-8")
        detail_budget = max(
            estimate_detail_budget(test_source, cap=args.reward_detail_budget_cap),
            min(args.reward_detail_budget_cap, max(1, len(behavior_hints))) if behavior_hints else 1,
        )
        task["task_id"] = task_id
        task["required_interface"] = required_interface
        task["behavior_hints"] = behavior_hints
        task["detail_budget"] = detail_budget

    random.seed(42 + rank)

    for step in range(1, args.grpo_steps + 1):
        # Skip steps already covered by warm restart
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
        prompt = build_prompt(task, research_methods=research_methods)
        test_harness = load_test_harness(task["tests_py"])

        # Generate group of solutions (adaptive temperature escalation on repeated low-signal skips)
        active_model = model.module if distributed else model
        active_model.eval()
        effective_temperature = adaptive_temp.current_temp()
        codes, prompt_text = generate_group(active_model, text_preprocessor, prompt, args, temperature=effective_temperature)

        consistent_old_log_probs = []
        consistent_old_token_counts = []
        with torch.no_grad():
            for code in codes:
                old_log_prob, old_token_count = compute_completion_log_prob(
                    active_model,
                    tokenizer,
                    prompt_text,
                    code,
                    device,
                    args.max_seq_length,
                    args.logit_clip,
                )
                consistent_old_log_probs.append(old_log_prob.detach())
                consistent_old_token_counts.append(old_token_count.detach())
        old_log_probs = torch.stack(consistent_old_log_probs)
        old_token_counts = torch.stack(consistent_old_token_counts)

        # Score each solution with verifier-aware shaped rewards.
        evaluations = [evaluate_candidate(c, test_harness, task, args, research_methods=research_methods) for c in codes]
        rewards = torch.tensor([float(entry["total_reward"]) for entry in evaluations], device=device)
        pass_rewards = torch.tensor([float(entry["pass_reward"]) for entry in evaluations], device=device)
        syntax_rewards = torch.tensor([float(entry["syntax_reward"]) for entry in evaluations], device=device)
        interface_rewards = torch.tensor([float(entry["interface_reward"]) for entry in evaluations], device=device)
        verifier_rewards = torch.tensor([float(entry["verifier_reward"]) for entry in evaluations], device=device)
        brevity_rewards = torch.tensor([float(entry.get("brevity_reward", 0.0)) for entry in evaluations], device=device)

        # Compute group-relative advantages (GRPO core idea)
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

        # Skip only when both total and component reward signals are flat.
        if signal_stats["signal_std"] < args.min_reward_std:
            adaptive_temp.record_skip("low_reward_signal")
            if rank == 0:
                record = build_grpo_step_record(
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
                    skipped=True,
                    reason="low_reward_signal",
                )
                append_grpo_metric(metrics, record=record)
                append_grpo_metric_jsonl(step_metrics_path, record)
                if step % args.log_steps == 0:
                    print(json.dumps(record))
            continue

        # Forward pass to get current completion-only log probs and apply GRPO loss.
        active_model.train()
        current_log_probs = []
        normalized_old_log_probs = []
        filtered_advantages = []
        for idx, code in enumerate(codes):
            current_log_prob, token_count = compute_completion_log_prob(
                active_model,
                tokenizer,
                prompt_text,
                code,
                device,
                args.max_seq_length,
                args.logit_clip,
            )
            if token_count.item() == 0:
                continue
            current_log_probs.append(current_log_prob / token_count.clamp_min(1))
            normalized_old_log_probs.append(old_log_probs[idx] / old_token_counts[idx].clamp_min(1))
            filtered_advantages.append(advantages[idx])

        if not current_log_probs:
            adaptive_temp.record_skip("empty_completion_mask")
            if rank == 0:
                record = build_grpo_step_record(
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
                    skipped=True,
                    reason="empty_completion_mask",
                )
                append_grpo_metric(metrics, record=record)
                append_grpo_metric_jsonl(step_metrics_path, record)
                if step % args.log_steps == 0:
                    print(json.dumps(record))
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
            if rank == 0:
                record = build_grpo_step_record(
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
                    skipped=True,
                    reason="non_finite_loss",
                )
                append_grpo_metric(metrics, record=record)
                append_grpo_metric_jsonl(step_metrics_path, record)
                if step % args.log_steps == 0:
                    print(json.dumps(record))
            continue
        optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(active_model.parameters(), 1.0)
        optimizer.step()
        adaptive_temp.record_update()

        if rank == 0:
            record = build_grpo_step_record(
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
                loss=float(total_loss.item()),
                adapter_init=args.adapter_init,
            )
            append_grpo_metric(metrics, record=record)
            append_grpo_metric_jsonl(step_metrics_path, record)
            if step % args.log_steps == 0:
                print(json.dumps(record))

    # Save
    if rank == 0:
        save_model = model.module if distributed else model
        adapter_dir = output_dir / "adapter"
        save_model.save_pretrained(adapter_dir)
        tokenizer.save_pretrained(adapter_dir)
        (output_dir / "grpo_metrics.json").write_text(
            json.dumps(build_grpo_metrics_payload(metrics, planned_steps=args.grpo_steps), indent=2) + "\n"
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
                    "logit_clip": args.logit_clip,
                    "min_reward_std": args.min_reward_std,
                    "curriculum_ema_decay": args.curriculum_ema_decay,
                    "curriculum_min_weight": args.curriculum_min_weight,
                    "curriculum_uncertainty_bonus": args.curriculum_uncertainty_bonus,
                    "quantum_priority": args.quantum_priority,
                    "research_methods": summarize_methods(research_methods),
                    "curriculum_state": curriculum.state,
                    "target_modules": list(args.target_modules) if args.target_modules else None,
                    "resolved_target_modules": resolved_target_modules,
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
