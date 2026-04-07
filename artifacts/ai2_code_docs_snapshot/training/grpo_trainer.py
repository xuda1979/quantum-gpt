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
)
from training.grpo_utils import (  # noqa: E402
    TaskCurriculum,
    build_reward_breakdown,
    estimate_detail_budget,
    stable_grpo_loss,
    stable_token_log_probs,
    summarize_python_interface,
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
    p.add_argument("--max-new-tokens", type=int, default=2048)
    p.add_argument("--max-seq-length", type=int, default=4096)
    p.add_argument("--log-steps", type=int, default=5)
    p.add_argument("--lora-rank", type=int, default=8)
    p.add_argument("--lora-alpha", type=int, default=16)
    p.add_argument("--reward-pass-weight", type=float, default=0.6)
    p.add_argument("--reward-syntax-weight", type=float, default=0.1)
    p.add_argument("--reward-interface-weight", type=float, default=0.15)
    p.add_argument("--reward-verifier-weight", type=float, default=0.15)
    p.add_argument("--reward-detail-budget-cap", type=int, default=8)
    p.add_argument("--advantage-clip", type=float, default=2.5)
    p.add_argument("--ratio-clip-log-delta", type=float, default=8.0)
    p.add_argument("--logit-clip", type=float, default=50.0)
    p.add_argument("--min-reward-std", type=float, default=0.05)
    p.add_argument("--curriculum-ema-decay", type=float, default=0.9)
    p.add_argument("--curriculum-min-weight", type=float, default=0.05)
    p.add_argument("--curriculum-uncertainty-bonus", type=float, default=0.35)
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
    hints: list[str] = []
    for raw_line in tests_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# Test "):
            comment = line.lstrip("#").strip()
            if len(comment) >= 12:
                hints.append(comment)
            continue
        marker = None
        if "failures.append(" in line:
            marker = "failures.append("
        elif "details.append(" in line:
            marker = "details.append("
        if marker is None:
            continue
        expr = line.split(marker, 1)[1].rstrip(")")
        try:
            value = eval(expr, {"__builtins__": {}}, {})
        except Exception:
            continue
        if not isinstance(value, str) or not value:
            continue
        normalized = " ".join(value.split())
        if normalized not in hints:
            hints.append(normalized)
        if len(hints) >= 6:
            break
    return hints


def summarize_candidate_interface(candidate_path: Path) -> list[str]:
    if not candidate_path.exists():
        return []
    return summarize_python_interface(candidate_path.read_text(encoding="utf-8"))


def build_prompt(task: dict) -> str:
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
    return "\n\n".join(parts)


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


def evaluate_candidate(code: str, test_harness, task: dict, args) -> dict[str, Any]:
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
    )
    reward["details"] = result.get("details", []) if isinstance(result, dict) else []
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


def generate_group(model, backend: TextPreprocessorBackend, prompt: str, args) -> tuple[list[str], torch.Tensor, torch.Tensor, str]:
    """Generate a group of solutions and return (codes, log_probs, token_counts, prompt_text)."""
    text = render_generation_prompt(backend.render_backend, prompt)
    inputs = move_batch_to_device(backend.text_backend(text, return_tensors="pt"), args.device)

    codes = []
    all_log_probs = []
    token_counts = []

    for _ in range(args.group_size):
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                do_sample=True,
                return_dict_in_generate=True,
                output_scores=True,
            )

        # Compute log probs of generated tokens
        gen_ids = outputs.sequences[0, inputs["input_ids"].shape[1]:]
        scores = torch.stack(outputs.scores, dim=0)  # (seq_len, vocab)
        token_log_probs = stable_token_log_probs(scores, gen_ids, args.logit_clip)
        seq_log_prob = token_log_probs.sum()

        response = backend.text_backend.decode(gen_ids, skip_special_tokens=True)
        codes.append(extract_code(response))
        all_log_probs.append(seq_log_prob)
        token_counts.append(torch.tensor(max(len(gen_ids), 1), device=seq_log_prob.device))

    return codes, torch.stack(all_log_probs), torch.stack(token_counts), text


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
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
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
    else:
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=0.05,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            bias="none",
        )
        model = get_peft_model(model, lora_config)
    model.to(device)

    if distributed:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    metrics = []
    curriculum = TaskCurriculum(
        ema_decay=args.curriculum_ema_decay,
        min_weight=args.curriculum_min_weight,
        quantum_priority=args.quantum_priority,
        uncertainty_bonus=args.curriculum_uncertainty_bonus,
    )

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
        weights = [curriculum.weight(task["task_id"], task["meta"].get("domain")) for task in tasks]
        weight_sum = sum(weights)
        task_index = random.choices(range(len(tasks)), weights=weights, k=1)[0]
        task = tasks[task_index]
        task_prob = weights[task_index] / weight_sum if weight_sum > 0 else 1.0 / len(tasks)
        prompt = build_prompt(task)
        test_harness = load_test_harness(task["tests_py"])

        # Generate group of solutions
        active_model = model.module if distributed else model
        active_model.eval()
        codes, old_log_probs, old_token_counts, prompt_text = generate_group(active_model, text_preprocessor, prompt, args)

        # Score each solution with verifier-aware shaped rewards.
        evaluations = [evaluate_candidate(c, test_harness, task, args) for c in codes]
        rewards = torch.tensor([float(entry["total_reward"]) for entry in evaluations], device=device)
        pass_rewards = torch.tensor([float(entry["pass_reward"]) for entry in evaluations], device=device)
        syntax_rewards = torch.tensor([float(entry["syntax_reward"]) for entry in evaluations], device=device)
        interface_rewards = torch.tensor([float(entry["interface_reward"]) for entry in evaluations], device=device)
        verifier_rewards = torch.tensor([float(entry["verifier_reward"]) for entry in evaluations], device=device)

        # Compute group-relative advantages (GRPO core idea)
        mean_reward = rewards.mean()
        std_reward = rewards.std(unbiased=False)
        advantages = ((rewards - mean_reward) / (std_reward + 1e-8)).clamp(
            -args.advantage_clip,
            args.advantage_clip,
        )
        task_state = curriculum.record(task["task_id"], float(mean_reward))

        # Skip if all same reward (no signal)
        if std_reward.item() < args.min_reward_std:
            if rank == 0 and step % args.log_steps == 0:
                print(json.dumps({
                    "step": step,
                    "task": task["task_dir"].name,
                    "mean_reward": float(mean_reward),
                    "pass_rate": float(pass_rewards.mean()),
                    "syntax_rate": float(syntax_rewards.mean()),
                    "interface_rate": float(interface_rewards.mean()),
                    "verifier_rate": float(verifier_rewards.mean()),
                    "curriculum_prob": float(task_prob),
                    "task_ema_reward": float(task_state["ema_reward"]),
                    "skipped": True,
                }))
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
            if rank == 0 and step % args.log_steps == 0:
                print(json.dumps({
                    "step": step,
                    "task": task["task_dir"].name,
                    "mean_reward": float(mean_reward),
                    "curriculum_prob": float(task_prob),
                    "task_ema_reward": float(task_state["ema_reward"]),
                    "skipped": True,
                    "reason": "empty_completion_mask",
                }))
            continue

        total_loss = grpo_loss(
            torch.stack(current_log_probs),
            torch.stack(normalized_old_log_probs),
            torch.stack(filtered_advantages),
            args.kl_coeff,
            args.ratio_clip_log_delta,
        )
        if not torch.isfinite(total_loss):
            if rank == 0 and step % args.log_steps == 0:
                print(json.dumps({
                    "step": step,
                    "task": task["task_dir"].name,
                    "mean_reward": float(mean_reward),
                    "pass_rate": float(pass_rewards.mean()),
                    "syntax_rate": float(syntax_rewards.mean()),
                    "interface_rate": float(interface_rewards.mean()),
                    "verifier_rate": float(verifier_rewards.mean()),
                    "curriculum_prob": float(task_prob),
                    "task_ema_reward": float(task_state["ema_reward"]),
                    "skipped": True,
                    "reason": "non_finite_loss",
                }))
            continue
        optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(active_model.parameters(), 1.0)
        optimizer.step()

        if rank == 0 and step % args.log_steps == 0:
            record = {
                "step": step,
                "task": task["task_dir"].name,
                "domain": task["meta"].get("domain", "?"),
                "mean_reward": float(mean_reward),
                "pass_rate": float(pass_rewards.mean()),
                "syntax_rate": float(syntax_rewards.mean()),
                "interface_rate": float(interface_rewards.mean()),
                "verifier_rate": float(verifier_rewards.mean()),
                "curriculum_prob": float(task_prob),
                "task_ema_reward": float(task_state["ema_reward"]),
                "task_seen": int(task_state["seen"]),
                "loss": float(total_loss.item()),
                "adapter_init": args.adapter_init,
            }
            metrics.append(record)
            print(json.dumps(record))

    # Save
    if rank == 0:
        save_model = model.module if distributed else model
        adapter_dir = output_dir / "adapter"
        save_model.save_pretrained(adapter_dir)
        tokenizer.save_pretrained(adapter_dir)
        (output_dir / "grpo_metrics.json").write_text(
            json.dumps({"metrics": metrics}, indent=2) + "\n"
        )
        (output_dir / "run_config.json").write_text(
            json.dumps(
                {
                    "model_name": args.model_name,
                    "adapter_init": args.adapter_init,
                    "tasks_dir": args.tasks_dir,
                    "benchmark_file": args.benchmark_file,
                    "domain_filter": args.domain_filter,
                    "group_size": args.group_size,
                    "grpo_steps": args.grpo_steps,
                    "lr": args.lr,
                    "kl_coeff": args.kl_coeff,
                    "temperature": args.temperature,
                    "max_new_tokens": args.max_new_tokens,
                    "max_seq_length": args.max_seq_length,
                    "device": str(args.device),
                    "reward_pass_weight": args.reward_pass_weight,
                    "reward_syntax_weight": args.reward_syntax_weight,
                    "reward_interface_weight": args.reward_interface_weight,
                    "reward_verifier_weight": args.reward_verifier_weight,
                    "reward_detail_budget_cap": args.reward_detail_budget_cap,
                    "advantage_clip": args.advantage_clip,
                    "ratio_clip_log_delta": args.ratio_clip_log_delta,
                    "logit_clip": args.logit_clip,
                    "min_reward_std": args.min_reward_std,
                    "curriculum_ema_decay": args.curriculum_ema_decay,
                    "curriculum_min_weight": args.curriculum_min_weight,
                    "curriculum_uncertainty_bonus": args.curriculum_uncertainty_bonus,
                    "quantum_priority": args.quantum_priority,
                    "curriculum_state": curriculum.state,
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
