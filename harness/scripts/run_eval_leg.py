#!/usr/bin/env python3
"""run_eval_leg.py — run a single eval leg with timeout + fail-closed markers.

The old approach let eval legs run indefinitely, stalling on ASI2 transport
wedges. This script enforces a hard timeout and reports adapter markers.

Usage:
    python3 harness/scripts/run_eval_leg.py --dry-run
    python3 harness/scripts/run_eval_leg.py --box ASI2 --adapter step_000035 --timeout 600
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


def _eval_cmd(adapter: str, task_start: int, task_count: int) -> str:
    """Build the eval command. <8 lines."""
    return (
        f"cd /vllm-workspace && python3 run_asi2_base_adapter_rubric_eval.py "
        f"--adapter {adapter} --task-start {task_start} --task-count {task_count} "
        f"2>&1 | tee /tmp/eval_leg_{adapter}.log"
    )


def _check_markers(output: str) -> dict:
    """Check for fail-closed markers in eval output. <10 lines."""
    return {
        "adapter_applied": "adapter_applied" in output or "adapter=True" in output,
        "probe_differs": "probe_differs" in output or "differs=True" in output,
        "has_results": "pass" in output.lower() and "fail" in output.lower(),
    }


def run_leg(box: str, adapter: str, timeout: int, task_start: int, task_count: int) -> dict:
    """Run one eval leg with timeout. <15 lines."""
    cmd = _eval_cmd(adapter, task_start, task_count)
    start = time.time()
    result = run_box(box, cmd, timeout=timeout)
    elapsed = time.time() - start
    markers = _check_markers(result.get("stdout", ""))
    return {
        "box": box,
        "adapter": adapter,
        "elapsed_s": round(elapsed, 1),
        "status": result.get("status"),
        "timed_out": elapsed >= timeout,
        "markers": markers,
        "output_tail": result.get("stdout", "")[-500:],
    }


def main():
    """Dispatch. <15 lines."""
    ap = argparse.ArgumentParser(description="Run eval leg with timeout + markers")
    ap.add_argument("--box", default="ASI2")
    ap.add_argument("--adapter", default="step_000035")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--task-start", type=int, default=0)
    ap.add_argument("--task-count", type=int, default=18)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        cmd = _eval_cmd(args.adapter, args.task_start, args.task_count)
        print(f"DRY RUN — would execute on {args.box}:")
        print(f"  command: {cmd}")
        print(f"  timeout: {args.timeout}s")
        print("  markers: adapter_applied, probe_differs")
        print("  output: JSON with elapsed_s, status, timed_out, markers")
    else:
        result = run_leg(args.box, args.adapter, args.timeout, args.task_start, args.task_count)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
