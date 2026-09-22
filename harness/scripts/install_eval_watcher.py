#!/usr/bin/env python3
"""install_eval_watcher.py — install + start the eval watcher daemon ON ASI2.

Pushes eval_watcher.py + harness_config.py to ASI2 /vllm-workspace/harness/,
then starts it detached (setsid nohup, 60s poll loop). Idempotent: a running
watcher is NOT double-started (pgrep guard).

The watcher then runs entirely box-local (NAS is local on ASI2): eval never
rides the daemon transport, never depends on ASI3 liveness.

Usage:
    python3 harness/scripts/install_eval_watcher.py            # install + start
    python3 harness/scripts/install_eval_watcher.py --status   # read NAS state
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness"))
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from harness_config import get  # noqa: E402
from push_to_box import push  # noqa: E402
from run_and_report import run_box  # noqa: E402

BOX = "ASI2"
REMOTE_DIR = "/vllm-workspace/harness"
BUS = get("ckpt_bus.nas_root")
STATE_ON_NAS = f"{BUS}/eval_watcher_state.json"


def install(box: str = BOX) -> dict:
    """Push files + start daemon. <15 lines."""
    pushes = {
        "eval_watcher.py": (REPO / "harness/scripts/eval_watcher.py", f"{REMOTE_DIR}/eval_watcher.py"),
        "harness_config.py": (REPO / "harness/harness_config.py", f"{REMOTE_DIR}/harness_config.py"),
    }
    for name, (local, remote) in pushes.items():
        r = push(box, str(local), remote)
        if r.get("status") != "PASS":
            return {"status": "FAIL", "step": f"push:{name}", "detail": str(r)[:200]}
    start_cmd = (
        f"cd {REMOTE_DIR} && "
        "pgrep -f 'eval_watcher.py --loop' >/dev/null || "
        f"setsid nohup python3 {REMOTE_DIR}/eval_watcher.py --loop "
        f"> {REMOTE_DIR}/watcher.log 2>&1 & echo STARTED"
    )
    r = run_box(box, start_cmd, timeout=30)
    return {"status": r.get("status"), "detail": (r.get("stdout", "") or r.get("stderr", ""))[-200:]}


def read_status() -> dict:
    """Read watcher state from NAS. <6 lines."""
    r = run_box(BOX, f"cat {STATE_ON_NAS}", timeout=30)
    try:
        return json.loads(r.get("stdout", "").strip())
    except json.JSONDecodeError:
        return {"status": "NO_STATE", "raw": r.get("stdout", "")[:100]}


def main() -> None:
    """Dispatch. <8 lines."""
    ap = argparse.ArgumentParser(description="Install + start eval watcher on ASI2")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.status:
        print(json.dumps(read_status(), indent=2))
        return
    print(json.dumps(install(), indent=2))


if __name__ == "__main__":
    main()
