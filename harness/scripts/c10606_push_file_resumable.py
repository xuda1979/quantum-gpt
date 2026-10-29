#!/usr/bin/env python3
"""C-10606: resumable file push to a box via daemon exec base64.

push_to_box.py restarts from byte 0 on every daemon drop; over a flapping
daemon a 2.5MB file never completes. This variant:
  - probes the remote file's current size (append offset)
  - pushes CHUNK raw bytes per exec (base64 +, and verifies the final sha256.
"""

from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import time
from pathlib import Path

CHUNK = 24 * 1024  # 24KB raw → 32KB base64, under the 50KB exec limit


def box_exec(box: str, cmd: str, timeout: int = 60) -> tuple[bool, str]:
    full = 'python3 harness/scripts/run_and_report.py --timeout %d --box-exec %s "%s" 2>&1' % (
        timeout,
        box,
        cmd.replace('"', '\\"'),
    )
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=timeout + 30)
    out = (r.stdout or "") + (r.stderr or "")
    return (r.returncode == 0 and "STATUS: PASS" in out), out


def heal(box: str) -> None:
    subprocess.run(
        ["python3", "harness/scripts/daemon_reconciler.py", "--box", box],
        capture_output=True,
        text=True,
        timeout=180,
    )


def remote_size(box: str, path: str) -> int:
    ok, out = box_exec(box, f"wc -c {path} 2>/dev/null || echo MISSING")
    if not ok:
        return -1
    for ln in out.splitlines():
        ln = ln.strip()
        if ln == "MISSING":
            return 0
        parts = ln.split()
        if len(parts) == 2 and parts[0].isdigit():
            return int(parts[0])
    return 0


def push(local: str, box: str, remote: str) -> int:
    data = Path(local).read_bytes()
    total = len(data)
    sha = hashlib.sha256(data).hexdigest()
    print(f"total={total} sha256={sha}")

    # wait for daemon health
    for _ in range(20):
        ok, _ = box_exec(box, "echo alive", 30)
        if ok:
            break
        heal(box)
        time.sleep(10)
    else:
        print("box unreachable after 20 heal attempts")
        return 1

    off = remote_size(box, remote)
    if off < 0:
        off = 0
    print(f"resuming from offset {off}")

    n_drops = 0
    while off < total:
        chunk = data[off : off + CHUNK]
        b64 = base64.b64encode(chunk).decode()
        if off == 0:
            cmd = f"mkdir -p $(dirname {remote}) && echo {b64} | base64 -d > {remote} && wc -c {remote}"
        else:
            cmd = f"echo {b64} | base64 -d >> {remote} && wc -c {remote}"
        ok, out = box_exec(box, cmd, 90)
        if not ok:
            n_drops += 1
            print(f"  drop #{n_drops} at offset {off}; healing...")
            heal(box)
            for _ in range(10):
                ok2, _ = box_exec(box, "echo alive", 30)
                if ok2:
                    break
                heal(box)
                time.sleep(8)
            off = remote_size(box, remote)
            if off < 0:
                off = 0
            print(f"  resumed at offset {off}")
            continue
        for ln in out.splitlines():
            parts = ln.strip().split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1] == remote:
                off = int(parts[0])
                break
        else:
            off = remote_size(box, remote)
            if off < 0:
                off = 0
        if off % (CHUNK * 10) < CHUNK:
            print(f"  {off}/{total} ({100 * off // total}%)")

    # final verify
    ok, out = box_exec(box, f"sha256sum {remote}", 120)
    remote_sha = ""
    for ln in out.splitlines():
        parts = ln.split()
        if len(parts) == 2 and parts[1] == remote:
            remote_sha = parts[0]
    print(f"remote sha256={remote_sha}")
    if remote_sha == sha:
        print("VERIFY: MATCH")
        return 0
    print("VERIFY: MISMATCH")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: c10606_push_file_resumable.py <local> <box> <remote>")
        sys.exit(2)
    sys.exit(push(sys.argv[1], sys.argv[2], sys.argv[3]))
