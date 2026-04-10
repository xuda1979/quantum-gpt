#!/usr/bin/env python3
"""Render leadership-ready 8-NPU timeboxed SFT/GRPO commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


OUTPUT = Path("artifacts/timeboxed-8npu-scaleup-command-sheet.txt")
DEFAULT_REQS = "training/requirements-huanxin-cpu.txt"
GEMMA_REQS = "training/requirements-gemma4-runtime.txt"
DEFAULT_ITERATION_PROFILE = "fast"

ITERATION_PROFILES = {
    "fast": {
        "headline": "under 45 minutes per run, fast-iteration prioritized on 2 NPUs; standard 8-NPU scale-up remains available",
        "output_suffix": "-fastiter",
        "visible_devices": "6,7",
        "nproc_per_node": 2,
        "required_idle_npus": 2,
        "paper_router_max_steps": 8,
        "paper_router_eval_steps": 8,
        "paper_router_log_steps": 1,
        "sft_max_steps": 12,
        "sft_eval_steps": 6,
        "sft_log_steps": 1,
        "grpo_group_size": 2,
        "grpo_steps": 2,
        "grpo_max_new_tokens": 96,
        "grpo_max_seq_length": 1536,
        "grpo_temperature": 0.4,
        "grpo_log_steps": 1,
    },
    "standard": {
        "headline": "under 2 hours per run, leadership-facing, all 8 NPUs when available",
        "output_suffix": "",
        "visible_devices": "0,1,2,3,4,5,6,7",
        "nproc_per_node": 8,
        "required_idle_npus": 8,
        "paper_router_max_steps": 20,
        "paper_router_eval_steps": 1000,
        "paper_router_log_steps": 5,
        "sft_max_steps": 40,
        "sft_eval_steps": 1000,
        "sft_log_steps": 5,
        "grpo_group_size": 4,
        "grpo_steps": 8,
        "grpo_max_new_tokens": 128,
        "grpo_max_seq_length": 2048,
        "grpo_temperature": 0.7,
        "grpo_log_steps": 1,
    },
}

TARGET_PRESETS = {
    "omnicoder9b": {
        "bootstrap_requirements": DEFAULT_REQS,
        "model_name": "models/OmniCoder-9B",
        "train_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        "eval_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        "benchmark_file": "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        "paper_inputs": "paper",
        "paper_output_dir": "data/generated/quantum-paper-router-warmup-v1",
        "paper_dataset_name": "quantum_paper_router_warmup",
        "paper_train_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
        "paper_eval_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl",
        "paper_router_output_dir": "outputs/omnicoder9b-quantum-paper-router-warmup",
        "paper_router_target_module_regex": r"(?:^|\.)(?:router|gate)(?:$|\.)",
        "paper_router_trainable_param_regex": r"lora_",
        "paper_router_freeze_param_regex": None,
        "sft_adapter_init": "outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter",
        "grpo_adapter_init": "outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter",
        "sft_output_dir": "outputs/omnicoder9b-quantum-generalization-sft-8npu-true40",
        "grpo_output_dir": "outputs/omnicoder9b-quantum-generalization-grpo-8npu-true8",
    },
    "gemma4-e2b-it": {
        "bootstrap_requirements": GEMMA_REQS,
        "model_name": "models/gemma-4-E2B-it",
        "train_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        "eval_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        "benchmark_file": "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        "paper_inputs": "paper",
        "paper_output_dir": "data/generated/quantum-paper-router-warmup-v1",
        "paper_dataset_name": "quantum_paper_router_warmup",
        "paper_train_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
        "paper_eval_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl",
        "paper_router_output_dir": "outputs/gemma4-e2b-it-quantum-paper-router-warmup",
        "paper_router_target_module_regex": r"(?:^|\.)(?:router|gate)(?:$|\.)",
        "paper_router_trainable_param_regex": r"lora_",
        "paper_router_freeze_param_regex": None,
        "sft_adapter_init": None,
        "grpo_adapter_init": "outputs/gemma4-e2b-it-quantum-generalization-sft-8npu-true40/adapter",
        "sft_output_dir": "outputs/gemma4-e2b-it-quantum-generalization-sft-8npu-true40",
        "grpo_output_dir": "outputs/gemma4-e2b-it-quantum-generalization-grpo-8npu-true8",
    },
    "gemma4-e4b-it": {
        "bootstrap_requirements": GEMMA_REQS,
        "model_name": "models/gemma-4-E4B-it",
        "train_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        "eval_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        "benchmark_file": "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        "paper_inputs": "paper",
        "paper_output_dir": "data/generated/quantum-paper-router-warmup-v1",
        "paper_dataset_name": "quantum_paper_router_warmup",
        "paper_train_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
        "paper_eval_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl",
        "paper_router_output_dir": "outputs/gemma4-e4b-it-quantum-paper-router-warmup",
        "paper_router_target_module_regex": r"(?:^|\.)(?:router|gate)(?:$|\.)",
        "paper_router_trainable_param_regex": r"lora_",
        "paper_router_freeze_param_regex": None,
        "sft_adapter_init": None,
        "grpo_adapter_init": "outputs/gemma4-e4b-it-quantum-generalization-sft-8npu-true40/adapter",
        "sft_output_dir": "outputs/gemma4-e4b-it-quantum-generalization-sft-8npu-true40",
        "grpo_output_dir": "outputs/gemma4-e4b-it-quantum-generalization-grpo-8npu-true8",
    },
    "gemma4-26b-a4b-it": {
        "bootstrap_requirements": GEMMA_REQS,
        "model_name": "models/gemma-4-26B-A4B-it",
        "train_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        "eval_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        "benchmark_file": "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        "paper_inputs": "paper",
        "paper_output_dir": "data/generated/quantum-paper-router-warmup-v1",
        "paper_dataset_name": "quantum_paper_router_warmup",
        "paper_train_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
        "paper_eval_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl",
        "paper_router_output_dir": "outputs/gemma4-26b-a4b-it-quantum-paper-router-warmup",
        "paper_router_target_module_regex": r"(?:^|\.)(?:router|gate)(?:$|\.)",
        "paper_router_trainable_param_regex": r"lora_",
        "paper_router_freeze_param_regex": None,
        "sft_adapter_init": None,
        "grpo_adapter_init": "outputs/gemma4-26b-a4b-it-quantum-generalization-sft-8npu-true40/adapter",
        "sft_output_dir": "outputs/gemma4-26b-a4b-it-quantum-generalization-sft-8npu-true40",
        "grpo_output_dir": "outputs/gemma4-26b-a4b-it-quantum-generalization-grpo-8npu-true8",
    },
    "gemma4-31b-it": {
        "bootstrap_requirements": GEMMA_REQS,
        "model_name": "models/gemma-4-31B-it",
        "train_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl",
        "eval_file": "data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl",
        "benchmark_file": "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        "paper_inputs": "paper",
        "paper_output_dir": "data/generated/quantum-paper-router-warmup-v1",
        "paper_dataset_name": "quantum_paper_router_warmup",
        "paper_train_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
        "paper_eval_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl",
        "paper_router_output_dir": "outputs/gemma4-31b-it-quantum-paper-router-warmup",
        "paper_router_target_module_regex": r"(?:^|\.)(?:router|gate)(?:$|\.)",
        "paper_router_trainable_param_regex": r"lora_",
        "paper_router_freeze_param_regex": None,
        "sft_adapter_init": None,
        "grpo_adapter_init": "outputs/gemma4-31b-it-quantum-generalization-sft-8npu-true40/adapter",
        "sft_output_dir": "outputs/gemma4-31b-it-quantum-generalization-sft-8npu-true40",
        "grpo_output_dir": "outputs/gemma4-31b-it-quantum-generalization-grpo-8npu-true8",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=sorted(TARGET_PRESETS), default="omnicoder9b")
    parser.add_argument(
        "--iteration-profile",
        choices=sorted(ITERATION_PROFILES),
        default=DEFAULT_ITERATION_PROFILE,
    )
    parser.add_argument("--model-name")
    parser.add_argument("--train-file")
    parser.add_argument("--eval-file")
    parser.add_argument("--benchmark-file")
    parser.add_argument("--paper-inputs")
    parser.add_argument("--paper-output-dir")
    parser.add_argument("--paper-dataset-name")
    parser.add_argument("--paper-train-file")
    parser.add_argument("--paper-eval-file")
    parser.add_argument("--paper-router-output-dir")
    parser.add_argument("--paper-router-target-module-regex")
    parser.add_argument("--paper-router-trainable-param-regex")
    parser.add_argument("--paper-router-freeze-param-regex")
    parser.add_argument("--sft-adapter-init")
    parser.add_argument("--grpo-adapter-init")
    parser.add_argument("--sft-output-dir")
    parser.add_argument("--grpo-output-dir")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    return parser.parse_args()


def resolve_target_config(args: argparse.Namespace) -> dict[str, str | None]:
    config = dict(TARGET_PRESETS[args.target])
    overrides = {
        "model_name": args.model_name,
        "train_file": args.train_file,
        "eval_file": args.eval_file,
        "benchmark_file": args.benchmark_file,
        "paper_inputs": args.paper_inputs,
        "paper_output_dir": args.paper_output_dir,
        "paper_dataset_name": args.paper_dataset_name,
        "paper_train_file": args.paper_train_file,
        "paper_eval_file": args.paper_eval_file,
        "paper_router_output_dir": args.paper_router_output_dir,
        "paper_router_target_module_regex": args.paper_router_target_module_regex,
        "paper_router_trainable_param_regex": args.paper_router_trainable_param_regex,
        "paper_router_freeze_param_regex": args.paper_router_freeze_param_regex,
        "sft_adapter_init": args.sft_adapter_init,
        "grpo_adapter_init": args.grpo_adapter_init,
        "sft_output_dir": args.sft_output_dir,
        "grpo_output_dir": args.grpo_output_dir,
    }
    for key, value in overrides.items():
        if value is not None:
            config[key] = value
    profile = ITERATION_PROFILES[args.iteration_profile]
    config["iteration_profile"] = args.iteration_profile
    config["profile_headline"] = str(profile["headline"])
    config["visible_devices"] = str(profile["visible_devices"])
    config["nproc_per_node"] = str(profile["nproc_per_node"])
    config["required_idle_npus"] = str(profile["required_idle_npus"])
    config["paper_router_max_steps"] = str(profile["paper_router_max_steps"])
    config["paper_router_eval_steps"] = str(profile["paper_router_eval_steps"])
    config["paper_router_log_steps"] = str(profile["paper_router_log_steps"])
    config["sft_max_steps"] = str(profile["sft_max_steps"])
    config["sft_eval_steps"] = str(profile["sft_eval_steps"])
    config["sft_log_steps"] = str(profile["sft_log_steps"])
    config["grpo_group_size"] = str(profile["grpo_group_size"])
    config["grpo_steps"] = str(profile["grpo_steps"])
    config["grpo_max_new_tokens"] = str(profile["grpo_max_new_tokens"])
    config["grpo_max_seq_length"] = str(profile["grpo_max_seq_length"])
    config["grpo_temperature"] = str(profile["grpo_temperature"])
    config["grpo_log_steps"] = str(profile["grpo_log_steps"])
    suffix = str(profile["output_suffix"])
    if suffix:
        if args.paper_router_output_dir is None:
            config["paper_router_output_dir"] = f"{config['paper_router_output_dir']}{suffix}"
        if args.sft_output_dir is None:
            config["sft_output_dir"] = f"{config['sft_output_dir']}{suffix}"
        if args.grpo_output_dir is None:
            config["grpo_output_dir"] = f"{config['grpo_output_dir']}{suffix}"
    return config


def render_command(lines: list[str]) -> str:
    return " \\\n".join(lines)


def build_sft_command(config: dict[str, str | None]) -> str:
    lines = [
        "PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
        "TOKENIZERS_PARALLELISM=false",
        f"ASCEND_RT_VISIBLE_DEVICES={config['visible_devices']}",
        f"torchrun --nproc_per_node={config['nproc_per_node']} training/qwen_sft_peft.py",
        f"  --model-name {config['model_name']}",
    ]
    if config.get("sft_adapter_init"):
        lines.append(f"  --adapter-init {config['sft_adapter_init']}")
    lines.extend(
        [
            f"  --train-file {config['train_file']}",
            f"  --eval-file {config['eval_file']}",
            f"  --output-dir {config['sft_output_dir']}",
            "  --device npu",
            "  --max-length 512",
            "  --per-device-batch-size 1",
            "  --gradient-accumulation-steps 2",
            "  --learning-rate 2e-4",
            "  --num-epochs 1",
            f"  --max-steps {config['sft_max_steps']}",
            f"  --eval-steps {config['sft_eval_steps']}",
            f"  --log-steps {config['sft_log_steps']}",
            "  --train-on-completions-only",
            "  --research-methods verifier_guided_repair_curriculum ast_anchor_interface_grounding",
        ]
    )
    return render_command(lines)


def build_grpo_command(config: dict[str, str | None]) -> str:
    lines = [
        "PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
        "TOKENIZERS_PARALLELISM=false",
        f"ASCEND_RT_VISIBLE_DEVICES={config['visible_devices']}",
        f"torchrun --nproc_per_node={config['nproc_per_node']} --master_port=29531 training/grpo_trainer.py",
        f"  --model-name {config['model_name']}",
    ]
    if config.get("grpo_adapter_init"):
        lines.append(f"  --adapter-init {config['grpo_adapter_init']}")
    lines.extend(
        [
            f"  --benchmark-file {config['benchmark_file']}",
            "  --domain-filter quantum",
            f"  --output-dir {config['grpo_output_dir']}",
            "  --device npu",
            f"  --group-size {config['grpo_group_size']}",
            f"  --grpo-steps {config['grpo_steps']}",
            f"  --max-new-tokens {config['grpo_max_new_tokens']}",
            f"  --max-seq-length {config['grpo_max_seq_length']}",
            f"  --temperature {config['grpo_temperature']}",
            "  --lr 5e-6",
            "  --kl-coeff 0.05",
            "  --reward-pass-weight 0.6",
            "  --reward-syntax-weight 0.1",
            "  --reward-interface-weight 0.15",
            "  --reward-verifier-weight 0.15",
            "  --ratio-clip-log-delta 4.0",
            "  --logit-clip 30.0",
            "  --min-reward-std 0.02",
            "  --curriculum-ema-decay 0.8",
            "  --curriculum-min-weight 0.1",
            "  --quantum-priority 1.1",
            "  --curriculum-uncertainty-bonus 0.2",
            f"  --log-steps {config['grpo_log_steps']}",
            "  --research-methods clause_aware_verifier_reward ast_anchor_interface_grounding",
        ]
    )
    return render_command(lines)


def build_paper_dataset_command(config: dict[str, str | None]) -> str:
    return render_command(
        [
            "python3 scripts/build_paper_sft_dataset.py",
            f"  {config['paper_inputs']}",
            f"  --output-dir {config['paper_output_dir']}",
            f"  --dataset-name {config['paper_dataset_name']}",
        ]
    )


def build_paper_router_warmup_command(config: dict[str, str | None]) -> str:
    lines = [
        "PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
        "TOKENIZERS_PARALLELISM=false",
        f"ASCEND_RT_VISIBLE_DEVICES={config['visible_devices']}",
        f"torchrun --nproc_per_node={config['nproc_per_node']} training/qwen_sft_peft.py",
        f"  --model-name {config['model_name']}",
        f"  --train-file {config['paper_train_file']}",
    ]
    if config.get("paper_eval_file"):
        lines.append(f"  --eval-file {config['paper_eval_file']}")
    lines.extend(
        [
            f"  --output-dir {config['paper_router_output_dir']}",
            "  --device npu",
            "  --max-length 1024",
            "  --per-device-batch-size 1",
            "  --gradient-accumulation-steps 2",
            "  --learning-rate 1e-4",
            "  --num-epochs 1",
            f"  --max-steps {config['paper_router_max_steps']}",
            f"  --eval-steps {config['paper_router_eval_steps']}",
            f"  --log-steps {config['paper_router_log_steps']}",
            "  --train-on-completions-only",
        ]
    )
    if config.get("paper_router_target_module_regex"):
        lines.append(f"  --target-module-regex '{config['paper_router_target_module_regex']}'")
    if config.get("paper_router_trainable_param_regex"):
        lines.append(f"  --trainable-param-regex '{config['paper_router_trainable_param_regex']}'")
    if config.get("paper_router_freeze_param_regex"):
        lines.append(f"  --freeze-param-regex '{config['paper_router_freeze_param_regex']}'")
    return render_command(lines)


def build_bootstrap_command(config: dict[str, str | None]) -> str:
    requirements = str(config["bootstrap_requirements"])
    return "\n".join(
        [
            "python3 -m pip install --upgrade pip",
            f"python3 -m pip install -r {requirements}",
        ]
    )


def main() -> int:
    args = parse_args()
    config = resolve_target_config(args)
    bootstrap_command = build_bootstrap_command(config)
    paper_dataset_command = build_paper_dataset_command(config)
    paper_router_warmup_command = build_paper_router_warmup_command(config)
    sft_command = build_sft_command(config)
    grpo_command = build_grpo_command(config)
    payload = {
        "target": args.target,
        "resolved_config": config,
        "bootstrap": bootstrap_command,
        "paper_dataset": paper_dataset_command,
        "paper_router_warmup": paper_router_warmup_command,
        "sft": sft_command,
        "grpo": grpo_command,
        "papers": [
            "research/papers/timeboxed_eight_npu_sft/paper.md",
            "research/papers/timeboxed_eight_npu_grpo/paper.md",
            "research/papers/verifier_guided_repair_curriculum/paper.md",
            "research/papers/clause_aware_verifier_reward/paper.md",
            "research/papers/ast_anchor_interface_grounding/paper.md",
            "research/papers/self_consistency_verifier_routing/paper.md",
            "research/papers/uncertainty_triggered_repair_replay/paper.md",
            "research/papers/gemma4_26b_a4b_weekend_demo/paper.md",
        ],
    }
    text = "\n".join(
        [
            "# Timeboxed 8-NPU Scale-Up Command Sheet",
            f"# target: {args.target}",
            f"# iteration_profile: {args.iteration_profile}",
            f"# target: {config['profile_headline']}",
            "",
            "## Bootstrap",
            bootstrap_command,
            "",
            "## Paper Dataset",
            paper_dataset_command,
            "",
            "## Paper Router Warmup",
            paper_router_warmup_command,
            "",
            "## SFT",
            sft_command,
            "",
            "## GRPO",
            grpo_command,
            "",
            "## JSON",
            json.dumps(payload, indent=2),
            "",
        ]
    )
    args.output.write_text(text, encoding="utf-8")
    print(json.dumps({"output": str(args.output.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
