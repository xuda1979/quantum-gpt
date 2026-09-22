#!/usr/bin/env python3
"""tdd.py — TDD cycle runner for harness agents.

Every agent that touches code MUST use this. The cycle is:
  1. write test (red)  → tdd.py red   --test <path> --name <test_name>
  2. write code        → (agent writes the implementation)
  3. run test (green)  → tdd.py green --test <path> --name <test_name>
  4. show result       → tdd.py result <run_id>

This script produces DETERMINISTIC output: pass/fail counts, error messages,
diff. No eyeballing, no conversational analysis.

Usage:
    python3 harness/scripts/tdd.py red --test tests/test_my_fix.py
    python3 harness/scripts/tdd.py green --test tests/test_my_fix.py
    python3 harness/scripts/tdd.py green --suite tests/  # full suite
    python3 harness/scripts/tdd.py last-fail            # show last failures
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE_DIR = REPO / "harness" / "state" / "tdd"
STATE_DIR.mkdir(parents=True, exist_ok=True)


def run_pytest(target: str, name: str | None = None, timeout: int = 120) -> dict:
    """Run pytest deterministically, return structured result."""
    cmd = [sys.executable, "-m", "pytest", target, "-v", "--tb=short", "--no-header"]
    if name:
        cmd[3:3] = ["-k", name]
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO))
        elapsed = time.time() - start
        # Parse output for pass/fail counts — prefer TESTSUITE_COUNTS line,
        # fall back to summary line, then to per-test verbose markers.
        output = proc.stdout + "\n" + proc.stderr
        passed = failed = errors = 0
        # Method 1: TESTSUITE_COUNTS line (emitted by our pytest config)
        for line in output.splitlines():
            if line.startswith("TESTSUITE_COUNTS"):
                m = re.search(r"passed=(\d+).*?failed=(\d+).*?errors=(\d+)", line)
                if m:
                    passed = int(m.group(1))
                    failed = int(m.group(2))
                    errors = int(m.group(3))
                break
        # Method 2: summary line "N passed, M failed, E errors"
        if passed == 0 and failed == 0 and errors == 0:
            m = re.search(r"(\d+) passed(?:.*?(\d+) failed)?(?:.*?(\d+) errors)?", output)
            if m:
                passed = int(m.group(1))
                failed = int(m.group(2) or 0)
                errors = int(m.group(3) or 0)
        # Extract failed test names
        failed_names = []
        for line in output.splitlines():
            if "FAILED" in line and ("::" in line or "_" in line):
                failed_names.append(line.strip())
        result = {
            "target": target,
            "name": name or "all",
            "exit_code": proc.returncode,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "failed_names": failed_names[:20],
            "elapsed_s": round(elapsed, 1),
            "output_tail": "\n".join(output.splitlines()[-30:]),
        }
    except subprocess.TimeoutExpired:
        result = {
            "target": target,
            "name": name or "all",
            "exit_code": -1,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "failed_names": [],
            "elapsed_s": timeout,
            "output_tail": f"TIMEOUT after {timeout}s",
        }
    # Persist result
    run_id = str(int(time.time()))
    (STATE_DIR / f"run_{run_id}.json").write_text(json.dumps(result, indent=2))
    (STATE_DIR / "last_run.json").write_text(json.dumps(result, indent=2))
    return result


def print_result(r: dict):
    """Print deterministic result line."""
    status = "GREEN" if r["failed"] == 0 and r["errors"] == 0 and r["exit_code"] == 0 else "RED"
    print(f"STATUS: {status}")
    print(
        f"PASSED: {r['passed']}  FAILED: {r['failed']}  ERRORS: {r['errors']}  TIME: {r['elapsed_s']}s"
    )
    if r["failed_names"]:
        print("FAILURES:")
        for fn in r["failed_names"]:
            print(f"  {fn}")
    if status == "RED":
        print("\n--- OUTPUT TAIL ---")
        print(r["output_tail"])


def main():
    ap = argparse.ArgumentParser(description="TDD cycle runner")
    sub = ap.add_subparsers(dest="cmd")

    p_red = sub.add_parser("red", help="run test, expect failure (red phase)")
    p_red.add_argument("--test", required=True, help="test file path")
    p_red.add_argument("--name", help="test name filter (-k)")

    p_green = sub.add_parser("green", help="run test, expect pass (green phase)")
    p_green.add_argument("--test", required=True, help="test file or dir")
    p_green.add_argument("--name", help="test name filter (-k)")
    p_green.add_argument("--timeout", type=int, default=120)

    sub.add_parser("last-fail", help="show last run failures")
    sub.add_parser("last", help="show last run result")

    args = ap.parse_args()

    if args.cmd == "red":
        r = run_pytest(args.test, args.name)
        print_result(r)
        if r["failed"] == 0 and r["exit_code"] == 0:
            print("\nNOTE: test already passes — RED phase expects failure. Write the test FIRST.")
        else:
            print("\nRED confirmed — test fails as expected. Now write the implementation.")

    elif args.cmd == "green":
        r = run_pytest(args.test, args.name, args.timeout)
        print_result(r)
        if r["failed"] == 0 and r["errors"] == 0:
            print("\nGREEN — all tests pass.")
        else:
            print("\nRED — tests still failing. Fix the code.")

    elif args.cmd == "last-fail":
        last = STATE_DIR / "last_run.json"
        if last.exists():
            r = json.loads(last.read_text())
            if r["failed_names"]:
                for fn in r["failed_names"]:
                    print(fn)
            else:
                print("No failures in last run.")
        else:
            print("No previous run found.")

    elif args.cmd == "last":
        last = STATE_DIR / "last_run.json"
        if last.exists():
            r = json.loads(last.read_text())
            print_result(r)
        else:
            print("No previous run found.")
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
