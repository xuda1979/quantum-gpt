#!/usr/bin/env python3
"""Render concrete commands for the strict unseen quantum generalization loop."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_MODEL = "models/OmniCoder-9B"
DEFAULT_TRAIN_FILE = "data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl"
DEFAULT_EVAL_FILE = "data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl"
DEFAULT_EVAL_RUN_DIR = "evals/runs/omnicoder-quantum-generalization-holdout-v1-clean"
DEFAULT_BENCHMARK_FILE = "evals/benchmarks/quantum_generalization_holdout_v1.txt"
DEFAULT_SFT_OUTPUT = "outputs/omnicoder9b-quantum-generalization-sft-v1"
DEFAULT_GRPO_OUTPUT = "outputs/omnicoder9b-quantum-generalization-grpo-v2"
DEFAULT_DEVICE = "npu"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    parser.add_argument(
        "--adapter-init",
        default=None,
        help="Optional adapter path for continuation SFT or GRPO warm start.",
    )
    parser.add_argument("--train-file", default=DEFAULT_TRAIN_FILE)
    parser.add_argument("--eval-file", default=DEFAULT_EVAL_FILE)
    parser.add_argument("--eval-run-dir", default=DEFAULT_EVAL_RUN_DIR)
    parser.add_argument("--benchmark-file", default=DEFAULT_BENCHMARK_FILE)
    parser.add_argument("--sft-output-dir", default=DEFAULT_SFT_OUTPUT)
    parser.add_argument("--grpo-output-dir", default=DEFAULT_GRPO_OUTPUT)
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    parser.add_argument("--grpo-steps", type=int, default=16)
    parser.add_argument("--group-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--max-seq-length", type=int, default=4096)
    parser.add_argument("--reward-pass-weight", type=float, default=0.6)
    parser.add_argument("--reward-syntax-weight", type=float, default=0.1)
    parser.add_argument("--reward-interface-weight", type=float, default=0.15)
    parser.add_argument("--reward-verifier-weight", type=float, default=0.15)
    parser.add_argument("--ratio-clip-log-delta", type=float, default=8.0)
    parser.add_argument("--logit-clip", type=float, default=50.0)
    parser.add_argument("--quantum-priority", type=float, default=1.5)
    parser.add_argument("--curriculum-uncertainty-bonus", type=float, default=0.35)
    parser.add_argument("--output", type=Path, default=None, help="Optional file to write the rendered command sheet to.")
    return parser.parse_args()


def q(value: str) -> str:
    return shlex.quote(value)


def build_text(args: argparse.Namespace) -> str:
    sft_parts = [
        "python3 training/qwen_sft_peft.py",
        f"--model-name {q(args.base_model)}",
        f"--train-file {q(args.train_file)}",
        f"--eval-file {q(args.eval_file)}",
        f"--output-dir {q(args.sft_output_dir)}",
        f"--device {q(args.device)}",
        "--max-steps 40",
        "--num-epochs 2",
        "--per-device-batch-size 1",
        "--gradient-accumulation-steps 8",
        "--learning-rate 2e-4",
        "--train-on-completions-only",
    ]
    if args.adapter_init:
        sft_parts.insert(2, f"--adapter-init {q(args.adapter_init)}")

    eval_adapter = args.adapter_init or f"{args.sft_output_dir}/adapter"
    eval_parts = [
        "python3 scripts/run_hf_pass1_eval.py",
        f"--run-dir {q(args.eval_run_dir)}",
        f"--base-model {q(args.base_model)}",
        f"--adapter {q(eval_adapter)}",
        f"--device {q(args.device)}",
        "--score",
    ]

    grpo_parts = [
        "python3 training/grpo_trainer.py",
        f"--model-name {q(args.base_model)}",
        f"--adapter-init {q(eval_adapter)}",
        f"--benchmark-file {q(args.benchmark_file)}",
        "--domain-filter quantum",
        f"--output-dir {q(args.grpo_output_dir)}",
        f"--device {q(args.device)}",
        f"--group-size {args.group_size}",
        f"--grpo-steps {args.grpo_steps}",
        f"--max-new-tokens {args.max_new_tokens}",
        f"--max-seq-length {args.max_seq_length}",
        f"--reward-pass-weight {args.reward_pass_weight}",
        f"--reward-syntax-weight {args.reward_syntax_weight}",
        f"--reward-interface-weight {args.reward_interface_weight}",
        f"--reward-verifier-weight {args.reward_verifier_weight}",
        f"--ratio-clip-log-delta {args.ratio_clip_log_delta}",
        f"--logit-clip {args.logit_clip}",
        f"--quantum-priority {args.quantum_priority}",
        f"--curriculum-uncertainty-bonus {args.curriculum_uncertainty_bonus}",
        "--temperature 0.8",
    ]

    payload = {
        "strict_dataset": {
            "train_file": args.train_file,
            "eval_file": args.eval_file,
        },
        "strict_benchmark": {
            "run_dir": args.eval_run_dir,
            "benchmark_file": args.benchmark_file,
        },
        "commands": {
            "sft": " \\\n  ".join(sft_parts),
            "unseen_eval": " \\\n  ".join(eval_parts),
            "grpo": " \\\n  ".join(grpo_parts),
        },
        "grpo_method": {
            "policy_update": "completion_only_grpo_with_length_normalized_logprobs",
            "reward": {
                "pass_weight": args.reward_pass_weight,
                "syntax_weight": args.reward_syntax_weight,
                "interface_weight": args.reward_interface_weight,
                "verifier_weight": args.reward_verifier_weight,
                "ratio_clip_log_delta": args.ratio_clip_log_delta,
                "logit_clip": args.logit_clip,
            },
            "curriculum": {
                "quantum_priority": args.quantum_priority,
                "uncertainty_bonus": args.curriculum_uncertainty_bonus,
            },
        },
    }

    lines = [
        "# Strict unseen quantum generalization command sheet",
        f"# dataset train: {args.train_file}",
        f"# dataset eval: {args.eval_file}",
        f"# benchmark: {args.benchmark_file}",
        "",
        "## SFT",
        payload["commands"]["sft"],
        "",
        "## Unseen Eval",
        payload["commands"]["unseen_eval"],
        "",
        "## GRPO",
        payload["commands"]["grpo"],
        "",
        "## JSON",
        json.dumps(payload, indent=2),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    text = build_text(args)
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
        print(json.dumps({"output": str(args.output.resolve())}, indent=2))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
