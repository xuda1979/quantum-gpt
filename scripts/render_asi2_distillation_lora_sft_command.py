#!/usr/bin/env python3
"""Render ASI2 Qwen3.6-35B-A3B LoRA/QLoRA distillation SFT commands."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any

DEFAULT_REMOTE_ROOT = "/root/software/quantum-gpt"
DEFAULT_MODEL = "/root/work/filestorage/Qwen3.6-35B-A3B"
DEFAULT_SPLIT_DIR = "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft"
DEFAULT_OUTPUT_DIR = "outputs/qwen36-35b-a3b-distill-uniform-lora-asi2-allnpu-r64-broad-ln-l512-s40"
DEFAULT_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote-root", default=DEFAULT_REMOTE_ROOT)
    parser.add_argument("--model-name", default=DEFAULT_MODEL)
    parser.add_argument("--split-dir", default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--mode", choices=["lora", "qlora"], default="lora")
    parser.add_argument("--device", default="npu")
    parser.add_argument("--nproc-per-node", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--max-steps", type=int, default=40)
    parser.add_argument("--num-epochs", type=int, default=3)
    parser.add_argument("--per-device-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
    parser.add_argument("--learning-rate", default="5e-5")
    parser.add_argument("--eval-steps", type=int, default=10)
    parser.add_argument("--log-steps", type=int, default=5)
    parser.add_argument("--lora-rank", type=int, default=64)
    parser.add_argument("--lora-alpha", type=int, default=128)
    parser.add_argument("--lora-dropout", default="0.0")
    parser.add_argument("--train-layernorm", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--max-trainable-parameters", type=int, default=1_000_000_000)
    parser.add_argument("--min-trainable-parameters", type=int, default=200_000_000)
    parser.add_argument("--target-modules", nargs="*", default=DEFAULT_TARGET_MODULES)
    parser.add_argument("--completion-only", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--gradient-checkpointing", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("artifacts/asi2-distillation-lora-sft-command.json"),
    )
    return parser.parse_args()


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def build_command(args: argparse.Namespace) -> dict[str, Any]:
    train_file = f"{args.split_dir.rstrip('/')}/train_chatml.jsonl"
    eval_file = f"{args.split_dir.rstrip('/')}/eval_chatml.jsonl"
    trainer_args = [
        "training/qwen_sft_peft.py",
        "--model-name",
        args.model_name,
        "--train-file",
        train_file,
        "--eval-file",
        eval_file,
        "--output-dir",
        args.output_dir,
        "--device",
        args.device,
        "--max-length",
        str(args.max_length),
        "--max-steps",
        str(args.max_steps),
        "--num-epochs",
        str(args.num_epochs),
        "--per-device-batch-size",
        str(args.per_device_batch_size),
        "--gradient-accumulation-steps",
        str(args.gradient_accumulation_steps),
        "--learning-rate",
        str(args.learning_rate),
        "--eval-steps",
        str(args.eval_steps),
        "--log-steps",
        str(args.log_steps),
        "--lora-rank",
        str(args.lora_rank),
        "--lora-alpha",
        str(args.lora_alpha),
        "--lora-dropout",
        str(args.lora_dropout),
    ]
    if args.target_modules:
        trainer_args.append("--target-modules")
        trainer_args.extend(args.target_modules)
    if args.completion_only:
        trainer_args.append("--train-on-completions-only")
    if args.gradient_checkpointing:
        trainer_args.append("--gradient-checkpointing")
    if args.train_layernorm:
        trainer_args.append("--train-layernorm")
    if args.max_trainable_parameters is not None:
        trainer_args.extend(["--max-trainable-parameters", str(args.max_trainable_parameters)])
    if args.min_trainable_parameters is not None:
        trainer_args.extend(["--min-trainable-parameters", str(args.min_trainable_parameters)])
    if args.mode == "qlora":
        trainer_args.append("--load-in-8bit")

    launch = [
        "set -euo pipefail",
        f"cd {shlex.quote(args.remote_root)}",
        "python3 scripts/preflight_qwen36_ascend_hf_training.py "
        f"--model-name {shlex.quote(args.model_name)} --device {shlex.quote(args.device)} --json",
        "mkdir -p logs",
        "export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
        f"torchrun --nproc_per_node={args.nproc_per_node} {shell_join(trainer_args)} "
        f"2>&1 | tee {shlex.quote('logs/asi2_distillation_lora_sft.log')}",
    ]
    return {
        "ok": True,
        "mode": args.mode,
        "adapter_strategy": "QLoRA" if args.mode == "qlora" else "LoRA",
        "remote_root": args.remote_root,
        "model_name": args.model_name,
        "train_file": train_file,
        "eval_file": eval_file,
        "output_dir": args.output_dir,
        "uses_lora": True,
        "uses_qlora": args.mode == "qlora",
        "uniform_lora_policy": "all matching transformer layers, shared rank, attention plus mlp projection targets",
        "train_layernorm": bool(args.train_layernorm),
        "max_trainable_parameters": args.max_trainable_parameters,
        "min_trainable_parameters": args.min_trainable_parameters,
        "command": "\n".join(launch),
    }


def main() -> int:
    args = parse_args()
    payload = build_command(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
