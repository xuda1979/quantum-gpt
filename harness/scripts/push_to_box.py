#!/usr/bin/env python3
"""push_to_box.py — push a local file to a box via daemon exec base64.

Handles large files by chunking. Each chunk <50KB base64.

Usage:
    python3 harness/scripts/push_to_box.py ASI3 training/grpo_utils.py /root/work/training/grpo_utils.py
"""

from __future__ import annotations

import base64
import json
import sys
import sys as _sys
import time
import urllib.request
from pathlib import Path
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from harness_config import get  # noqa: E402

BOX_PORTS = get("box_ports")  # single source: harness_config.py
CHUNK_SIZE = 32 * 1024  # 32KB raw → ~43KB base64, safe for exec


def _exec(box: str, cmd: str, timeout: int = 30) -> dict:
    """Single exec call. <10 lines."""
    port = BOX_PORTS.get(box.upper())
    if not port:
        return {"status": "FAIL", "error": f"unknown box {box}"}
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
                "status": "PASS" if d.get("commandOk") else "FAIL",
                "output": (d.get("output") or "")[:200],
            }
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def push(box: str, local: str, remote: str) -> dict:
    """Push file in chunks. <20 lines."""
    data = Path(local).read_bytes()
    # Create remote file with first chunk, append rest
    for i in range(0, len(data), CHUNK_SIZE):
        chunk = data[i : i + CHUNK_SIZE]
        b64 = base64.b64encode(chunk).decode()
        if i == 0:
            cmd = f"mkdir -p $(dirname {remote}) && echo '{b64}' | base64 -d > {remote}"
        else:
            cmd = f"echo '{b64}' | base64 -d >> {remote}"
        result = _exec(box, cmd)
        if result["status"] != "PASS":
            return {"status": "FAIL", "error": f"chunk {i} failed: {result}", "bytes_sent": i}
        time.sleep(0.2)
    # Verify size
    verify = _exec(box, f"wc -c {remote}")
    return {"status": "PASS", "total_bytes": len(data), "verify": verify.get("output", "").strip()}


def main():
    """<8 lines."""
    if len(sys.argv) != 4:
        print("Usage: push_to_box.py <box> <local_path> <remote_path>")
        sys.exit(1)
    result = push(sys.argv[1], sys.argv[2], sys.argv[3])
    print(f"STATUS: {result['status']}")
    if result.get("total_bytes"):
        print(f"BYTES: {result['total_bytes']}")
    if result.get("verify"):
        print(f"VERIFY: {result['verify']}")
    if result.get("error"):
        print(f"ERROR: {result['error']}")


if __name__ == "__main__":
    main()
