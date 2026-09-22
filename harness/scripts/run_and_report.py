#!/usr/bin/env python3
"""run_and_report.py — run a command, produce deterministic structured output.

Every harness agent uses this instead of running commands conversationally.
The output is ALWAYS structured: exit code, stdout, stderr, timing, pass/fail.

Usage:
    python3 harness/scripts/run_and_report.py <command...>
    python3 harness/scripts/run_and_report.py --json <command...>
    python3 harness/scripts/run_and_report.py --check-file <path>  # verify file exists + non-empty
    python3 harness/scripts/run_and_report.py --box-exec ASI3 "command"  # exec on a box
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
BOX_PORTS = {"ASI1": 20646, "ASI2": 19004, "ASI3": 20653}


def run_local(cmd: list[str], timeout: int = 60) -> dict:
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO))
        elapsed = time.time() - start
        return {
            "command": " ".join(cmd),
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-2000:] if len(proc.stdout) > 2000 else proc.stdout,
            "stderr": proc.stderr[-2000:] if len(proc.stderr) > 2000 else proc.stderr,
            "elapsed_s": round(elapsed, 2),
            "status": "PASS" if proc.returncode == 0 else "FAIL",
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(cmd),
            "exit_code": -1,
            "stdout": "",
            "stderr": f"TIMEOUT after {timeout}s",
            "elapsed_s": timeout,
            "status": "TIMEOUT",
        }


def run_box(box: str, command: str, timeout: int = 30) -> dict:
    port = BOX_PORTS.get(box.upper())
    if not port:
        return {"status": "FAIL", "error": f"unknown box {box}"}
    payload = json.dumps({"command": command}).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/exec",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            d = json.loads(resp.read().decode())
            elapsed = time.time() - start
            return {
                "box": box,
                "command": command,
                "exit_code": d.get("commandStatus", d.get("exitCode", -1)),
                "stdout": (d.get("output") or d.get("stdout") or "")[-2000:],
                "stderr": (d.get("stderr") or "")[-2000:],
                "elapsed_s": round(elapsed, 2),
                "status": "PASS"
                if (d.get("commandOk") or d.get("commandStatus", d.get("exitCode", -1)) == 0)
                else "FAIL",
            }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return {
            "box": box,
            "command": command,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "elapsed_s": round(time.time() - start, 2),
            "status": "BOX_DOWN",
        }


def check_file(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"path": path, "exists": False, "status": "FAIL", "reason": "not found"}
    if p.stat().st_size == 0:
        return {"path": path, "exists": True, "size": 0, "status": "FAIL", "reason": "empty"}
    return {"path": path, "exists": True, "size": p.stat().st_size, "status": "PASS"}


def main():
    ap = argparse.ArgumentParser(description="Run command → deterministic output")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--check-file", help="verify file exists and non-empty")
    ap.add_argument("--box-exec", help="box name (ASI1/ASI2/ASI3) to exec on")
    ap.add_argument("command", nargs="*", help="command to run")
    args = ap.parse_args()

    if args.check_file:
        result = check_file(args.check_file)
    elif args.box_exec:
        if not args.command:
            print("error: --box-exec requires a command", file=sys.stderr)
            sys.exit(1)
        result = run_box(args.box_exec, " ".join(args.command), args.timeout)
    elif args.command:
        result = run_local(args.command, args.timeout)
    else:
        ap.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"STATUS: {result['status']}")
        if "exit_code" in result:
            print(f"EXIT: {result['exit_code']}  TIME: {result.get('elapsed_s', '?')}s")
        if result.get("stdout"):
            print(f"STDOUT:\n{result['stdout']}")
        if result.get("stderr"):
            print(f"STDERR:\n{result['stderr']}")


if __name__ == "__main__":
    main()
