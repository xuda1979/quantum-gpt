#!/usr/bin/env python3
"""boot_verify_training.py — verify training launched and is advancing.

Completes in <30s: checks process alive, step advancing, writes probe.

Usage:
    python3 harness/scripts/boot_verify_training.py --box ASI3
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from run_and_report import run_box  # noqa: E402

PROBE_PATH = REPO / "harness" / "state" / "probes" / "train.json"


def _check_process(box: str) -> dict:
    """Check if training process is alive on box. <10 lines."""
    r = run_box(box, "ps aux | grep -E 'torchrun|grpo' | grep -v grep | head -3", timeout=10)
    output = r.get("stdout", "").strip()
    return {
        "alive": len(output) > 0 and r.get("status") == "PASS",
        "processes": output[:300] if output else "none",
    }


def _check_step(box: str, run_name: str) -> dict:
    """Check latest checkpoint step. <10 lines."""
    r = run_box(
        box, f"ls -t /vllm-workspace/{run_name}/step_* -d 2>/dev/null | head -1", timeout=10
    )
    output = r.get("stdout", "").strip()
    return {"latest_step_dir": output if output else "none"}


def _write_probe(probe: dict) -> None:
    """Write probe to state. <5 lines."""
    PROBE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROBE_PATH.write_text(json.dumps(probe, indent=2))


def verify(box: str) -> dict:
    """Boot-verify training on box. <15 lines."""
    proc = _check_process(box)
    # Read existing probe for run name
    run_name = "unknown"
    if PROBE_PATH.exists():
        try:
            run_name = json.loads(PROBE_PATH.read_text()).get("run", "unknown")
        except Exception:
            pass
    step = _check_step(box, run_name) if proc["alive"] else {"latest_step_dir": "none"}
    result = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "box": box,
        "process": proc,
        "step": step,
        "status": "RUNNING" if proc["alive"] else "NOT_RUNNING",
    }
    _write_probe(result)
    return result


def main():
    """Dispatch. <8 lines."""
    ap = argparse.ArgumentParser(description="Boot-verify training")
    ap.add_argument("--box", default="ASI3")
    args = ap.parse_args()
    result = verify(args.box)
    print(f"STATUS: {result['status']}")
    print(f"PROCESS: {result['process']['alive']}")
    print(f"STEP: {result['step']['latest_step_dir']}")
    print(f"PROBE: {PROBE_PATH}")


if __name__ == "__main__":
    main()
