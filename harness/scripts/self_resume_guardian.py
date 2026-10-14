#!/usr/bin/env python3
"""self_resume_guardian.py — tests green + trainer down => resume training. Standing.

The closing practice (item 12): zero downtime between "tests green" and
"training running". This guardian watches the canonical training thread; if
the trainer dies while the harness is healthy (boxes up, compile gate open,
tests green), it resumes from the latest checkpoint via resume_training.py —
the same gate chain a human or agent would run, but within seconds.

C-10112 (deadlock fix): the decision logic lives in decide(); once() passes
confirmed=(down_polls >= confirm window) AND persists the down counter across
process restarts (C-10133). A RESUMED last-status (a SUCCESS) still honours the
down-window, so a resumed trainer that later dies is treated as a NEW death and
is not relaunched into a still-rising process; RECOVERABLE_DEAD statuses (the
previous launch itself failed) retry immediately at any confirm state.

Deliberately conservative (a wrong resume costs GPU-hours):
  - waits TRAIN_DOWN_CONFIRM_S of continuous trainer-down before acting
  - never resumes when the box daemon is down (can't verify anything)
  - never resumes when a compile gate blocks (training tree broken)
  - never resumes when tests are red (C-10372: TESTS_RED_NO_RELAUNCH)
  - one exclusive resume-lease holder at a time (harness_lib lock)
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
import harness_lib  # noqa: E402
from resume_training import compile_gate, find_latest_checkpoint, resume, trainer_running  # noqa: E402

STATE = REPO / "harness" / "state" / "self_resume_guardian.json"
RESUME_STATE = REPO / "harness" / "state" / "resume_training.json"
LOCK_PATH = REPO / "harness" / "state" / "locks" / "resume.lock"
POLL_S = 60
TRAIN_DOWN_CONFIRM_S = 180  # 3 consecutive down-polls before resuming

RECOVERABLE_DEAD = frozenset(
    {"NO_CHECKPOINT", "BOX_DOWN", "SKIP_TRAINER_ALREADY_RUNNING",
     "BLOCKED_COMPILE_GATE", "BOOT_FAILED", "RESUME_FAILED"}
)


def now() -> str:
    """ISO now. <3 lines."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_last_status():
    """Last resume_training.json status, or None when unreadable. <5 lines."""
    try:
        return json.loads(RESUME_STATE.read_text()).get("status")
    except (OSError, ValueError):
        return None


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


def acquire_resume_lock():
    """One exclusive resume-lease holder at a time. <3 lines."""
    return harness_lib.acquire_lock(str(LOCK_PATH))


def release_resume_lock(token):
    """Release the lease iff it is still ours. <3 lines."""
    return harness_lib.release_lock(str(LOCK_PATH), token)


def _dispatch_resume():
    """Run the gated resume_training.launch. <3 lines."""
    out = resume()
    launched = bool(out.get("launch") == "PASS" and out.get("boot", {}).get("alive"))
    return {"launched": launched, "result": out}


def decide(status, running, up, has_ckpt, compile_ok, tests_ok, dispatch,
           confirmed) -> str:
    """C-10112 deadlock-free decision. <20 lines.

    A live trainer never evicts. A box that is unreachable never relaunches.
    Busy-wait in TRAINER_DOWN_CONFIRMING until the persisted down-window
    elapses (confirmed=True), then gate on checkpoint/compile/tests fail-closed
    and relaunch. RECOVERABLE_DEAD last statuses skip the wait (the previous
    launch already failed on its own).
    """
    if running:
        return "NO_RELAUNCH_ALIVE"
    if not up:
        return "BOX_DOWN"
    if status in RECOVERABLE_DEAD:
        confirmed = True
    if not confirmed:
        return "TRAINER_DOWN_CONFIRMING"
    if not has_ckpt:
        return "NO_CHECKPOINT"
    if not compile_ok:
        return "COMPILE_GATE_BLOCKED"
    if not tests_ok:
        return "TESTS_RED_NO_RELAUNCH"
    tok = acquire_resume_lock()
    if tok is None:
        return "RESUME_LOCK_BUSY"
    try:
        dispatch()
    finally:
        release_resume_lock(tok)
    return "RELAUNCHED"


def _confirmed_at_or_after(n: int) -> bool:
    """True once the down-poll count reached the confirm window. <2 lines."""
    return n >= TRAIN_DOWN_CONFIRM_S // POLL_S


def once(down_count: dict) -> dict:
    """One guardian cycle. <20 lines."""
    running, up = trainer_running()
    if not up:
        down_count["n"] = 0
        return write({"ts": now(), "status": "BOX_DOWN", "acted": False})
    if running:
        down_count["n"] = 0
        return write({"ts": now(), "status": "TRAINER_RUNNING", "acted": False})

    persisted = _read_down_polls()
    down_count["n"] = persisted + 1
    write({"down_polls": down_count["n"]})

    last_status = read_last_status()
    confirmed = _confirmed_at_or_after(down_count["n"])
    verdict = decide(
        last_status, running, up,
        has_ckpt=bool(find_latest_checkpoint()),
        compile_ok=compile_gate()[0], tests_ok=run_tests(),
        dispatch=_dispatch_resume, confirmed=confirmed,
    )
    if verdict in ("RELAUNCHED", "RESUME_LOCK_BUSY"):
        down_count["n"] = 0
        write({"down_polls": 0})
    return write({
        "ts": now(), "status": verdict,
        "down_polls": down_count["n"],
        "acted": verdict == "RELAUNCHED",
    })


def _read_down_polls() -> int:
    """Persisted down-poll counter (0 when absent/unreadable). <4 lines."""
    try:
        v = json.loads(STATE.read_text()).get("down_polls")
        return int(v) if v is not None else 0
    except (OSError, ValueError):
        return 0


def write(state: dict) -> dict:
    """Write + return state (plain replace). <4 lines."""
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
