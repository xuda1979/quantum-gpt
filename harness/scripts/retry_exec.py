#!/usr/bin/env python3
"""retry_exec.py — exec on a box with retries. Handles flaky daemon sessions.

Usage:
    python3 harness/scripts/retry_exec.py ASI3 "command" [--retries 5] [--wait 5]
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request

BOX_PORTS = {"ASI1": 20646, "ASI2": 19004, "ASI3": 20653}


def exec_once(box: str, cmd: str, timeout: int = 20) -> dict:
    """One exec attempt. <10 lines."""
    port = BOX_PORTS.get(box.upper())
    if not port:
        return {"ok": False, "error": f"unknown box {box}"}
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/exec",
            data=json.dumps({"command": cmd}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
            return {
                "ok": d.get("commandOk") is True,
                "output": (d.get("output") or "").strip(),
                "raw_ok": d.get("commandOk"),
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def exec_retry(box: str, cmd: str, retries: int, wait: int) -> dict:
    """Exec with retries. <12 lines."""
    last = {}
    for attempt in range(1, retries + 1):
        last = exec_once(box, cmd)
        if last.get("ok"):
            last["attempts"] = attempt
            return last
        time.sleep(wait)
    last["attempts"] = retries
    return last


def main():
    """<10 lines."""
    ap = argparse.ArgumentParser()
    ap.add_argument("box")
    ap.add_argument("command")
    ap.add_argument("--retries", type=int, default=5)
    ap.add_argument("--wait", type=int, default=5)
    args = ap.parse_args()
    result = exec_retry(args.box, args.command, args.retries, args.wait)
    print(f"OK: {result.get('ok')} attempts={result.get('attempts')}")
    if result.get("output"):
        print(f"OUTPUT: {result['output']}")


if __name__ == "__main__":
    main()
