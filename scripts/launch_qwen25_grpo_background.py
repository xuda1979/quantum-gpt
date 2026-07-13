#!/usr/bin/env python3
"""Launch a Qwen GRPO run in the background and print a JSON receipt."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", default="models/Qwen3.6-27B")
    parser.add_argument("--adapter-init", required=True)
    parser.add_argument("--benchmark-file", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--log-path", required=True)
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--nproc-per-node", type=int, default=8)
    parser.add_argument("--master-port", type=int, default=29531)
    parser.add_argument("--device", default="npu")
    parser.add_argument("--visible-devices", default="0,1,2,3,4,5,6,7")
    parser.add_argument("--group-size", type=int, default=8)
    parser.add_argument("--grpo-steps", type=int, default=8)
    parser.add_argument("--max-new-tokens", type=int, default=192)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--adaptive-temp-step", type=float, default=0.15)
    parser.add_argument("--adaptive-temp-max", type=float, default=1.4)
    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--kl-coeff", type=float, default=0.05)
    parser.add_argument("--reward-pass-weight", type=float, default=0.6)
    parser.add_argument("--reward-syntax-weight", type=float, default=0.1)
    parser.add_argument("--reward-interface-weight", type=float, default=0.15)
    parser.add_argument("--reward-verifier-weight", type=float, default=0.15)
    parser.add_argument("--reward-brevity-weight", type=float, default=0.05)
    parser.add_argument("--reward-import-hygiene-weight", type=float, default=0.05)
    parser.add_argument("--ratio-clip-log-delta", type=float, default=8.0)
    parser.add_argument("--logit-clip", type=float, default=50.0)
    parser.add_argument("--min-reward-std", type=float, default=0.02)
    parser.add_argument("--quantum-priority", type=float, default=1.5)
    parser.add_argument("--curriculum-uncertainty-bonus", type=float, default=0.35)
    parser.add_argument("--log-steps", type=int, default=1)
    parser.add_argument("--domain-filter", nargs="*", default=["quantum"])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_command(args: argparse.Namespace) -> list[str]:
    command = [
        "torchrun",
        f"--nproc_per_node={args.nproc_per_node}",
        f"--master_port={args.master_port}",
        "training/grpo_trainer.py",
        "--model-name",
        args.model_name,
        "--adapter-init",
        args.adapter_init,
        "--benchmark-file",
        args.benchmark_file,
        "--output-dir",
        args.output_dir,
        "--device",
        args.device,
        "--group-size",
        str(args.group_size),
        "--grpo-steps",
        str(args.grpo_steps),
        "--max-new-tokens",
        str(args.max_new_tokens),
        "--max-seq-length",
        str(args.max_seq_length),
        "--temperature",
        str(args.temperature),
        "--adaptive-temp-step",
        str(args.adaptive_temp_step),
        "--adaptive-temp-max",
        str(args.adaptive_temp_max),
        "--lr",
        str(args.lr),
        "--kl-coeff",
        str(args.kl_coeff),
        "--reward-pass-weight",
        str(args.reward_pass_weight),
        "--reward-syntax-weight",
        str(args.reward_syntax_weight),
        "--reward-interface-weight",
        str(args.reward_interface_weight),
        "--reward-verifier-weight",
        str(args.reward_verifier_weight),
        "--reward-brevity-weight",
        str(args.reward_brevity_weight),
        "--reward-import-hygiene-weight",
        str(args.reward_import_hygiene_weight),
        "--ratio-clip-log-delta",
        str(args.ratio_clip_log_delta),
        "--logit-clip",
        str(args.logit_clip),
        "--min-reward-std",
        str(args.min_reward_std),
        "--quantum-priority",
        str(args.quantum_priority),
        "--curriculum-uncertainty-bonus",
        str(args.curriculum_uncertainty_bonus),
        "--log-steps",
        str(args.log_steps),
    ]
    for domain in args.domain_filter:
        command.extend(["--domain-filter", domain])
    return command


def main() -> int:
    args = parse_args()
    command = build_command(args)
    cwd = Path(args.cwd).resolve()
    log_path = Path(args.log_path)
    if not log_path.is_absolute():
        log_path = cwd / log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.setdefault("PYTORCH_NPU_ALLOC_CONF", "max_split_size_mb:256")
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    env.setdefault("ASCEND_RT_VISIBLE_DEVICES", args.visible_devices)

    receipt = {
        "cwd": str(cwd),
        "log_path": str(log_path),
        "command": command,
        "env_overrides": {
            "PYTORCH_NPU_ALLOC_CONF": env["PYTORCH_NPU_ALLOC_CONF"],
            "TOKENIZERS_PARALLELISM": env["TOKENIZERS_PARALLELISM"],
            "ASCEND_RT_VISIBLE_DEVICES": env["ASCEND_RT_VISIBLE_DEVICES"],
        },
    }
    if args.dry_run:
        print(json.dumps(receipt, indent=2))
        return 0

    with log_path.open("w", encoding="utf-8") as handle:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            stdout=handle,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

    receipt["pid"] = process.pid
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
