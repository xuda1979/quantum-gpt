#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex


def export_line(name: str, value: str | int | float) -> str:
    return f"export {name}={shlex.quote(str(value))}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-root", default="/root/work/quantum-gpt")
    parser.add_argument("--model-name", default="/root/work/filestorage/Qwen3.6-27B")
    parser.add_argument(
        "--benchmark-file", default="evals/benchmarks/agentic_coding_trajectory_training_v1.txt"
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--log-path", required=True)
    parser.add_argument("--visible-devices", default="0,1,2,3,4,5,6,7")
    parser.add_argument("--nproc-per-node", type=int, default=8)
    parser.add_argument("--group-size", type=int, default=2)
    parser.add_argument("--grpo-steps", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=32)
    parser.add_argument("--max-seq-length", type=int, default=512)
    parser.add_argument("--max-turns", type=int, default=2)
    parser.add_argument("--online-eval-every-steps", type=int, default=1)
    parser.add_argument("--online-eval-max-tasks", type=int, default=2)
    parser.add_argument(
        "--online-eval-benchmark-file",
        default="evals/benchmarks/quantum_generalization_holdout_v2_hard.txt",
    )
    parser.add_argument("--checkpoint-interval-seconds", type=int, default=3600)
    parser.add_argument("--checkpoint-every-steps", type=int, default=1)
    parser.add_argument("--training-mode", choices=["native", "lora"], default="native")
    args = parser.parse_args()

    lines = [
        "set -euo pipefail",
        f"cd {shlex.quote(args.remote_root)}",
        export_line("ASI1_AGENTIC_TASK_MODEL_NAME", args.model_name),
        export_line("ASI1_AGENTIC_TASK_BENCHMARK_FILE", args.benchmark_file),
        export_line("ASI1_AGENTIC_TASK_OUTPUT_DIR", args.output_dir),
        export_line("ASI1_AGENTIC_TASK_LOG_PATH", args.log_path),
        export_line("ASI1_AGENTIC_TASK_VISIBLE_DEVICES", args.visible_devices),
        export_line("ASI1_AGENTIC_TASK_NPROC_PER_NODE", args.nproc_per_node),
        export_line("ASI1_AGENTIC_TASK_GROUP_SIZE", args.group_size),
        export_line("ASI1_AGENTIC_TASK_GRPO_STEPS", args.grpo_steps),
        export_line("ASI1_AGENTIC_TASK_MAX_NEW_TOKENS", args.max_new_tokens),
        export_line("ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH", args.max_seq_length),
        export_line("ASI1_AGENTIC_TASK_MAX_TURNS", args.max_turns),
        export_line("ASI1_AGENTIC_TASK_ONLINE_EVAL_EVERY_STEPS", args.online_eval_every_steps),
        export_line("ASI1_AGENTIC_TASK_ONLINE_EVAL_MAX_TASKS", args.online_eval_max_tasks),
        export_line(
            "ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE", args.online_eval_benchmark_file
        ),
        export_line(
            "ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS", args.checkpoint_interval_seconds
        ),
        export_line("ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS", args.checkpoint_every_steps),
        export_line("ASI1_AGENTIC_TASK_TRAINING_MODE", args.training_mode),
        "bash scripts/run_asi1_agentic_grpo_from_env.sh",
    ]
    command = "\n".join(lines)
    print(
        json.dumps(
            {
                "environment": "ASI1",
                "remote_root": args.remote_root,
                "output_dir": args.output_dir,
                "log_path": args.log_path,
                "job_name": "asi1-agentic-grpo-runner",
                "remote_command": command,
                "execution_command": command,
                "compact_command": "runner",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
