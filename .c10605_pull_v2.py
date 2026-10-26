#!/usr/bin/env python3
"""Port-agile chunked pull (C-10605 harvest).

The three Huanxin exec daemons (20646/19004/20653) flap independently.
Each /exec attempt races across all ports; the fold+sed chunk recipe from
scripts/pull_box_file.py is applied, with per-chunk sha tracking so a
mid-pull daemon death is recoverable without restarting the whole file.

Chunk width 13000: the daemon output cap measured live at ~13336 chars
(B-042's 4000 was overly conservative), cutting chunk count 3.25x.
"""

import base64
import hashlib
import json
import re
import sys
import time
import urllib.request

PORTS = [20646, 19004, 20653]
CHUNK = 13000  # daemon cap ~13336 (measured 2026-10-26)


def exec_any(cmd, timeout=120, wait_ms=60000):
    """Run cmd on whichever daemon is alive. Retries port sweep for up to
    300s when all are down."""
    last = None
    deadline = time.time() + 300
    while time.time() < deadline:
        for port in PORTS:
            try:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/exec",
                    data=json.dumps({"command": cmd, "waitMs": wait_ms}).encode(),
                    headers={"Content-Type": "application/json"},
                )
                d = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
                if d.get("ok") is True and d.get("commandOk") is True:
                    return d.get("output", "")
                last = "port {} ok={} cmdOk={}".format(port, d.get("ok"), d.get("commandOk"))
            except Exception as e:
                last = f"port {port} {type(e).__name__}"
        time.sleep(10)
    raise RuntimeError(f"no daemon accepted command: {last}")


def clean(s):
    return re.sub(r"[\r\n]", "", s)


def pull(remote, local, box_sha):
    # chunk count via explicit loop until empty; never trust wc -l (B-042)
    chunks = []
    i = 1
    while True:
        cmd = f"base64 -w0 {remote} | fold -w {CHUNK} | sed -n '{i}p'"
        out = exec_any(cmd, timeout=90)
        c = clean(out)
        if c == "" and i > 1:
            break
        chunks.append(c)
        i += 1
        if i % 200 == 0:
            print(f"  chunk {i} ...", flush=True)
        if i > 30000:
            raise RuntimeError("safety stop")
    b64 = "".join(chunks)
    raw = base64.b64decode(b64)
    local_sha = hashlib.sha256(raw).hexdigest()
    if local_sha != box_sha:
        raise RuntimeError(f"sha mismatch: local={local_sha} box={box_sha}")
    with open(local, "wb") as f:
        f.write(raw)
    print(f"WROTE {local} ({len(raw)} bytes, sha ok)")
    return local_sha


def main():
    if len(sys.argv) < 4:
        print("usage: pull_v2.py REMOTE LOCAL BOX_SHA", file=sys.stderr)
        return 1
    remote, local, box_sha = sys.argv[1], sys.argv[2], sys.argv[3]
    last_err = None
    for attempt in range(5):
        try:
            pull(remote, local, box_sha)
            return 0
        except Exception as e:
            last_err = e
            print(f"attempt {attempt + 1} failed: {str(e)[:200]}", flush=True)
            time.sleep(20)
    print(f"FATAL: {last_err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
