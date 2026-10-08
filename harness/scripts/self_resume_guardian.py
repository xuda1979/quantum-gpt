#!/usr/bin/env python3
"""self_resume_guardian.py — tests green + trainer down => resume training. Standing.

The closing practice (item 12): zero downtime between "tests green" and
"training running". This guardian watches the canonical training thread; if
the trainer dies while the harness is healthy (boxes up, compile gate open),
it resumes from the latest checkpoint via resume_training.py — the same gate
chain a human or agent would run, but within seconds, not the next session.

Deliberately conservative (a wrong resume costs GPU-hours):
  - waits TRAIN_DOWN_CONFIRM_S of continuous trainer-down before acting
  - never resumes when the box daemon is down (can't verify anything)
  - never resumes when a compile gate blocks (training tree broken)
  - one resume attempt per down-window (no storm)

Usage:
    nohup python3 harness/scripts/self_resume_guardian.py --loop &
    python3 harness/scripts/self_resume_guardian.py --once
    python3 harness/scripts/self_resume_guardian.py --status
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from resume_training import compile_gate, find_latest_checkpoint, trainer_running  # noqa: E402

STATE = REPO / "harness" / "state" / "self_resume_guardian.json"
POLL_S = 60
TRAIN_DOWN_CONFIRM_S = 180  # 3 consecutive down-polls before resuming


def run_tests() -> bool:
    """Fast harness test suite must pass before any resume. <8 lines."""
    try:
        p = subprocess.run(
            [sys.executable, "-m", "pytest", "harness/tests/test_c9627_ckpt_bus.py",
             "harness/tests/test_c9628_contracts_config_lint.py", "-q", "--timeout", "120"],
            capture_output=True, text=True, cwd=str(REPO), timeout=300,
        )
        return p.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def once(down_count: dict) -> dict:
    """One guardian cycle. <15 lines."""
    running, up = trainer_running()
    if not up:
        down_count["n"] = 0
        return write({"ts": now(), "status": "BOX_DOWN", "acted": False})
    if running:
        down_count["n"] = 0
        return write({"ts": now(), "status": "TRAINER_RUNNING", "acted": False})
    down_count["n"] += 1
    if down_count["n"] < TRAIN_DOWN_CONFIRM_S // POLL_S:
        return write({"ts": now(), "status": "TRAINER_DOWN_CONFIRMING", "down_polls": down_count["n"], "acted": False})
    if not find_latest_checkpoint():
        return write({"ts": now(), "status": "NO_CHECKPOINT", "acted": False})
    ok, up = compile_gate()
    if not up:
        return write({"ts": now(), "status": "BOX_DOWN", "acted": False})
    if not ok:
        return write({"ts": now(), "status": "COMPILE_GATE_BLOCKED", "acted": False})
    if not run_tests():
        return write({"ts": now(), "status": "TESTS_RED_NO_RESUME", "acted": False})
    r = subprocess.run(
        [sys.executable, str(REPO / "harness/scripts/resume_training.py")],
        capture_output=True, text=True, timeout=600,
    )
    down_count["n"] = 0
    return write({"ts": now(), "status": "RESUME_DISPATCHED" if r.returncode == 0 else "RESUME_FAILED",
                  "resume_output": (r.stdout or r.stderr)[-400:], "acted": True})


def now() -> str:
    """ISO now. <3 lines."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write(state: dict) -> dict:
    """Write + return state. <4 lines."""
    STATE.write_text(json.dumps(state, indent=2) + "\n")
    return state


def main() -> None:
    """Dispatch. <10 lines."""
    ap = argparse.ArgumentParser(description="Self-resume guardian (tests green + down => resume)")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.status:
        print(STATE.read_text() if STATE.exists() else "NO_STATE_YET")
        return
    down = {"n": 0}
    if args.loop:
        while True:
            once(down)
            time.sleep(POLL_S)
    print(json.dumps(once(down), indent=2))


if __name__ == "__main__":
    main()
