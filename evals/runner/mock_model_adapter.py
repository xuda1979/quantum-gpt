#!/usr/bin/env python3
"""Minimal model-adapter seam for prepared eval runs.

This adapter is intentionally conservative: it defines a stable interface between
`execute_run.py` and any future real model backend. For now it supports:

- `reference-copy`: copy the task's bundled reference candidate
- `echo-prompt`: emit the prompt text (useful for smoke testing logs)

The point is to make the adapter boundary explicit so a real OpenAI/OpenClaw or
local-runtime backend can be dropped in without changing run packaging.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = ROOT / "evals" / "tasks"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["reference-copy", "echo-prompt"], default="reference-copy")
    parser.add_argument("--task-id", default=None, help="Optional explicit task id. Falls back to EVAL_TASK_ID env var usage upstream.")
    parser.add_argument("--prompt-path", type=Path, default=None, help="Optional prompt file path for echo-prompt backend.")
    return parser.parse_args()



def load_task_metadata(task_id: str) -> tuple[dict[str, Any], Path]:
    for task_json in sorted(TASKS_ROOT.glob("*/*/task.json")):
        payload = json.loads(task_json.read_text())
        if payload.get("id") == task_id:
            return payload, task_json.parent
    raise SystemExit(f"Unknown task id: {task_id}")



def run_reference_copy(task_id: str) -> int:
    metadata, task_dir = load_task_metadata(task_id)
    candidate_path = task_dir / metadata["candidate_file"]
    sys.stdout.write(candidate_path.read_text())
    return 0



def run_echo_prompt(prompt_path: Path | None) -> int:
    if prompt_path is None or not prompt_path.exists():
        raise SystemExit("--prompt-path is required for echo-prompt backend")
    sys.stdout.write(prompt_path.read_text())
    return 0



if __name__ == "__main__":
    args = parse_args()
    if args.backend == "reference-copy":
        if not args.task_id:
            raise SystemExit("--task-id is required for reference-copy backend")
        raise SystemExit(run_reference_copy(args.task_id))
    if args.backend == "echo-prompt":
        raise SystemExit(run_echo_prompt(args.prompt_path))
    raise SystemExit(f"Unsupported backend: {args.backend}")
