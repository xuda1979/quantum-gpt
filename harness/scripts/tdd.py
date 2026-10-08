#!/usr/bin/env python3
"""tdd.py — TDD cycle runner. Write test → run → deterministic output.

Usage:
    python3 harness/scripts/tdd.py red --test <path>
    python3 harness/scripts/tdd.py green --test <path>
    python3 harness/scripts/tdd.py last-fail
    python3 harness/scripts/tdd.py last
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


def _parse_counts(output: str) -> tuple[int, int, int]:
    """Extract pass/fail/error counts from pytest output. <10 lines."""
    for line in output.splitlines():
        if line.startswith("TESTSUITE_COUNTS"):
            m = re.search(r"passed=(\d+).*?failed=(\d+).*?errors=(\d+)", line)
            if m:
                return int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = re.search(r"(\d+) passed(?:.*?(\d+) failed)?(?:.*?(\d+) errors)?", output)
    if m:
        return int(m.group(1)), int(m.group(2) or 0), int(m.group(3) or 0)
    return 0, 0, 0


def _extract_failures(output: str) -> list[str]:
    """Extract failed test names from pytest output. <8 lines."""
    return [
        line.strip()
        for line in output.splitlines()
        if "FAILED" in line and ("::" in line or "_" in line)
    ][:20]


def _build_result(
    target: str, name: str, proc: subprocess.CompletedProcess, elapsed: float
) -> dict:
    """Build structured result dict from pytest run. <15 lines."""
    output = proc.stdout + "\n" + proc.stderr
    passed, failed, errors = _parse_counts(output)
    return {
        "target": target,
        "name": name or "all",
        "exit_code": proc.returncode,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "failed_names": _extract_failures(output),
        "elapsed_s": round(elapsed, 1),
        "output_tail": "\n".join(output.splitlines()[-30:]),
    }


def run_pytest(target: str, name: str | None = None, timeout: int = 120) -> dict:
    """Run pytest, return structured result. <20 lines."""
    cmd = [sys.executable, "-m", "pytest", target, "-v", "--tb=short", "--no-header"]
    if name:
        cmd[3:3] = ["-k", name]
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO))
        result = _build_result(target, name, proc, time.time() - start)
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
    rid = str(int(time.time()))
    (STATE_DIR / f"run_{rid}.json").write_text(json.dumps(result, indent=2))
    (STATE_DIR / "last_run.json").write_text(json.dumps(result, indent=2))
    return result


def print_result(r: dict):
    """Print deterministic result. <12 lines."""
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
        print(f"\n--- OUTPUT TAIL ---\n{r['output_tail']}")


def _cmd_red(args):
    """Red phase: test should fail. <10 lines."""
    r = run_pytest(args.test, args.name)
    print_result(r)
    if r["failed"] == 0 and r["exit_code"] == 0:
        print("\nNOTE: test already passes — write the test FIRST.")
    else:
        print("\nRED confirmed — now write the implementation.")


def _cmd_green(args):
    """Green phase: test should pass. <10 lines."""
    r = run_pytest(args.test, args.name, args.timeout)
    print_result(r)
    print(
        "\nGREEN — all tests pass."
        if r["failed"] == 0 and r["errors"] == 0
        else "\nRED — fix the code."
    )


def _cmd_last_fail():
    """Show last run failures. <8 lines."""
    last = STATE_DIR / "last_run.json"
    if not last.exists():
        print("No previous run found.")
        return
    r = json.loads(last.read_text())
    for fn in r.get("failed_names", []) or ["No failures in last run."]:
        print(fn)


def _cmd_last():
    """Show last run result. <6 lines."""
    last = STATE_DIR / "last_run.json"
    if not last.exists():
        print("No previous run found.")
        return
    print_result(json.loads(last.read_text()))


def main():
    """Argparse dispatch. <15 lines."""
    ap = argparse.ArgumentParser(description="TDD cycle runner")
    sub = ap.add_subparsers(dest="cmd")
    p_red = sub.add_parser("red")
    p_red.add_argument("--test", required=True)
    p_red.add_argument("--name")
    p_green = sub.add_parser("green")
    p_green.add_argument("--test", required=True)
    p_green.add_argument("--name")
    p_green.add_argument("--timeout", type=int, default=120)
    sub.add_parser("last-fail")
    sub.add_parser("last")
    args = ap.parse_args()
    dispatch = {
        "red": _cmd_red,
        "green": _cmd_green,
        "last-fail": _cmd_last_fail,
        "last": _cmd_last,
    }
    handler = dispatch.get(args.cmd)
    if handler:
        handler(args) if args.cmd in ("red", "green") else handler()
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
