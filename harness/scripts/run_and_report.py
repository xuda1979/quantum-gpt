#!/usr/bin/env python3
"""run_and_report.py — run command → deterministic PASS/FAIL output.

Usage:
    python3 harness/scripts/run_and_report.py <command...>
    python3 harness/scripts/run_and_report.py --json <command...>
    python3 harness/scripts/run_and_report.py --check-file <path>
    python3 harness/scripts/run_and_report.py --box-exec ASI3 "command"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
BOX_PORTS = {"ASI1": 20646, "ASI2": 19004, "ASI3": 20653}


def run_local(cmd: list[str], timeout: int = 60) -> dict:
    """Run local command. <15 lines."""
    start = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO))
        return _result(
            " ".join(cmd), proc.returncode, proc.stdout, proc.stderr, time.time() - start
        )
    except subprocess.TimeoutExpired:
        return _result(" ".join(cmd), -1, "", f"TIMEOUT after {timeout}s", timeout)


def _result(cmd: str, exit_code: int, stdout: str, stderr: str, elapsed: float) -> dict:
    """Build result dict. <8 lines."""
    return {
        "command": cmd,
        "exit_code": exit_code,
        "stdout": stdout[-2000:],
        "stderr": stderr[-2000:],
        "elapsed_s": round(elapsed, 2),
        "status": "PASS" if exit_code == 0 else "FAIL",
    }


def run_box(box: str, command: str, timeout: int = 30) -> dict:
    """Exec on a box via daemon. <20 lines."""
    port = BOX_PORTS.get(box.upper())
    if not port:
        return {"box": box, "status": "FAIL", "error": f"unknown box {box}"}
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
            d = json.loads(resp.read())
            ok = d.get("commandOk") or d.get("commandStatus", d.get("exitCode", -1)) == 0
            return {
                "box": box,
                "command": command,
                "exit_code": d.get("commandStatus", d.get("exitCode", -1)),
                "stdout": (d.get("output") or d.get("stdout") or "")[-2000:],
                "stderr": (d.get("stderr") or "")[-2000:],
                "elapsed_s": round(time.time() - start, 2),
                "status": "PASS" if ok else "FAIL",
            }
    except Exception as e:
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
    """Verify file exists and non-empty. <6 lines."""
    p = Path(path)
    if not p.exists():
        return {"path": path, "exists": False, "status": "FAIL", "reason": "not found"}
    if p.stat().st_size == 0:
        return {"path": path, "exists": True, "size": 0, "status": "FAIL", "reason": "empty"}
    return {"path": path, "exists": True, "size": p.stat().st_size, "status": "PASS"}


def _print(result: dict):
    """Print human-readable result. <8 lines."""
    print(f"STATUS: {result['status']}")
    if "exit_code" in result:
        print(f"EXIT: {result['exit_code']}  TIME: {result.get('elapsed_s', '?')}s")
    if result.get("stdout"):
        print(f"STDOUT:\n{result['stdout']}")
    if result.get("stderr"):
        print(f"STDERR:\n{result['stderr']}")


def main():
    """Dispatch. <15 lines."""
    ap = argparse.ArgumentParser(description="Run command → deterministic output")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--check-file")
    ap.add_argument("--box-exec")
    ap.add_argument("command", nargs="*")
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

    print(json.dumps(result, indent=2)) if args.json else _print(result)


if __name__ == "__main__":
    main()
