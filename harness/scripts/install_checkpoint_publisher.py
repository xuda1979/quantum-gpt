#!/usr/bin/env python3
"""install_checkpoint_publisher.py — install + start the checkpoint publisher ON ASI3.

Pushes checkpoint_publisher.py + harness_config.py to ASI3 /vllm-workspace/harness/,
then starts it detached (setsid nohup, 60s cycle). Idempotent (pgrep guard).

Publisher runs box-local on the trainer: checkpoints flow
/vllm-workspace/{run}/{step} -> /root/work/ckpt_bus/{run}/{step} (NAS),
where the ASI2 eval watcher picks them up. No daemon in the data path.

Usage:
    python3 harness/scripts/install_checkpoint_publisher.py
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

BOX = "ASI3"
REMOTE_DIR = "/vllm-workspace/harness"
BUS = get("ckpt_bus.nas_root")
STATE_ON_NAS = f"{BUS}/checkpoint_publisher_state.json"


def install(box: str = BOX) -> dict:
    """Push files + start daemon. <12 lines."""
    pushes = {
        "checkpoint_publisher.py": (REPO / "harness/scripts/checkpoint_publisher.py", f"{REMOTE_DIR}/checkpoint_publisher.py"),
        "harness_config.py": (REPO / "harness/harness_config.py", f"{REMOTE_DIR}/harness_config.py"),
    }
    for name, (local, remote) in pushes.items():
        r = push(box, str(local), remote)
        if r.get("status") != "PASS":
            return {"status": "FAIL", "step": f"push:{name}", "detail": str(r)[:200]}
    start_cmd = (
        f"cd {REMOTE_DIR} && "
        "pgrep -f 'checkpoint_publisher.py --loop' >/dev/null || "
        f"setsid nohup python3 {REMOTE_DIR}/checkpoint_publisher.py --loop "
        f"> {REMOTE_DIR}/publisher.log 2>&1 & echo STARTED"
    )
    r = run_box(box, start_cmd, timeout=30)
    return {"status": r.get("status"), "detail": (r.get("stdout", "") or r.get("stderr", ""))[-200:]}


def read_status() -> dict:
    """Read publisher state from NAS. <6 lines."""
    r = run_box(BOX, f"cat {STATE_ON_NAS}", timeout=30)
    try:
        return json.loads(r.get("stdout", "").strip())
    except json.JSONDecodeError:
        return {"status": "NO_STATE", "raw": r.get("stdout", "")[:100]}


def main() -> None:
    """Dispatch. <8 lines."""
    ap = argparse.ArgumentParser(description="Install + start checkpoint publisher on ASI3")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.status:
        print(json.dumps(read_status(), indent=2))
        return
    print(json.dumps(install(), indent=2))


if __name__ == "__main__":
    main()
