#!/usr/bin/env python3
"""Convenience runner for the 35B self-correcting distillation pipeline.

Wraps scripts/self_correcting_distill.py with the 35B config and the shared
question pool. Reads student API credentials from the environment.

Required env vars:
    STUDENT_35B_API_KEY   (any non-empty string accepted by the local vLLM)
    GLM52_API_BASE
    GLM52_API_KEY

Optional env vars:
    STUDENT_35B_API_BASE  (default http://127.0.0.1:8008/v1)
    WORKERS               (default 4)
    START_INDEX           (default 0)
    END_INDEX             (default 8000)
    LIMIT                 (default unset — process the whole range)
    GIT_SYNC_INTERVAL     (default 100 — commit every N processed questions)
    NO_GIT_PUSH           (default unset — set to "1" to commit without pushing)
    NO_GIT_SYNC           (default unset — set to "1" to disable git checkpoints)
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/distill/self_correcting_distill_35b_v1.json"
POOL = ROOT / "data/generated/self_correcting_distill/questions_pool.jsonl"


def main() -> int:
    missing = []
    if not os.environ.get("GLM52_API_BASE"):
        missing.append("GLM52_API_BASE")
    if not os.environ.get("GLM52_API_KEY"):
        missing.append("GLM52_API_KEY")
    if missing:
        print(f"[fatal] missing env vars: {missing}", file=sys.stderr)
        return 2

    cmd = [
        sys.executable,
        str(ROOT / "scripts/self_correcting_distill.py"),
        "--config", str(CONFIG),
        "--question-pool", str(POOL),
        "--resume",
        "--workers", os.environ.get("WORKERS", "4"),
        "--start-index", os.environ.get("START_INDEX", "0"),
        "--end-index", os.environ.get("END_INDEX", "8000"),
    ]
    if os.environ.get("LIMIT"):
        cmd.extend(["--limit", os.environ["LIMIT"]])
    if os.environ.get("GIT_SYNC_INTERVAL"):
        cmd.extend(["--git-sync-interval", os.environ["GIT_SYNC_INTERVAL"]])
    if os.environ.get("NO_GIT_PUSH") == "1":
        cmd.append("--no-git-push")
    if os.environ.get("NO_GIT_SYNC") == "1":
        cmd.append("--no-git-sync")

    print("[run_35b] " + " ".join(cmd), flush=True)
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
