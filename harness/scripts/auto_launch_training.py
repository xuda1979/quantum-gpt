#!/usr/bin/env python3
"""auto_launch_training.py — wait for box ready window, launch training automatically.

Polls ASI3 health. When ready, launches training with setsid + boot-verifies.
Writes progress to harness/state/auto_launch.json for fast feedback.

Usage:
    nohup python3 harness/scripts/auto_launch_training.py &
    # check: cat harness/state/auto_launch.json
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from push_to_box import _exec  # noqa: E402

STATE_FILE = REPO / "harness" / "state" / "auto_launch.json"
PORT = 20653
TRAIN_CMD = (
    "cd /root/work && mkdir -p /vllm-workspace/sapo-27b-auto-$(date +%Y%m%dT%H%M%S) && "
    "RUN_DIR=/vllm-workspace/sapo-27b-auto-$(date +%Y%m%dT%H%M%S) && "
    "setsid nohup python3 training/grpo_trainer.py "
    "--benchmark evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt "
    "--output_dir $RUN_DIR "
    "> $RUN_DIR/training.log 2>&1 & echo LAUNCHED pid=$!"
)


def write_state(state: dict) -> None:
    """<4 lines."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def health_ok() -> bool:
    """Check ASI3 ready. <10 lines."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=5) as r:
            d = json.loads(r.read())
            return d.get("startupState") == "ready"
    except Exception:
        return False


def wait_and_launch(max_wait_min: int = 60) -> dict:
    """Wait for ready window, launch. <15 lines."""
    state = {"phase": "waiting", "started": time.strftime("%H:%M:%S")}
    write_state(state)
    deadline = time.time() + max_wait_min * 60
    while time.time() < deadline:
        if health_ok():
            state["phase"] = "launching"
            state["ready_at"] = time.strftime("%H:%M:%S")
            write_state(state)
            result = _exec("ASI3", TRAIN_CMD, timeout=20)
            state["launch_result"] = result
            state["phase"] = "launched" if result.get("status") == "PASS" else "launch_failed"
            write_state(state)
            return state
        time.sleep(10)
    state["phase"] = "timeout"
    write_state(state)
    return state


def main() -> None:
    """<3 lines."""
    result = wait_and_launch()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
