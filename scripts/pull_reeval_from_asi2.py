#!/usr/bin/env python3
"""pull_reeval_from_asi2.py — chunked base64 download of the re-eval results.

ASI2 has no working S3 write path, so we pull the gzipped tarball through the
webshell in ~3.8K base64 chunks (the daemon output cap is ~4.3K).
"""

import json
import re
import subprocess
import sys

REMOTE_B64 = "/tmp/reeval100.b64"
LOCAL_B64 = "/tmp/reeval100_local.b64"
N_CHUNKS = int(sys.argv[1]) if len(sys.argv) > 1 else 400


def shell(cmd):
    r = subprocess.run(
        ["bash", "scripts/huanxin_shell.sh", "ASI2", cmd],
        capture_output=True,
        text=True,
        timeout=180,
    )
    return r.stdout


def get_chunk(n):
    out = shell(f"sed -n '{n}p' {REMOTE_B64}")
    m = re.search(r'"output": "(.*?)",\n  "commandStatus"', out, re.DOTALL)
    if not m:
        return None
    try:
        raw = json.loads('"' + m.group(1) + '"')
    except Exception:
        return None
    # The terminal wraps long lines; base64 is whitespace-free, so strip all
    # whitespace and anything after the daemon's RUN marker.
    cut = raw.split("__ASI2_RUN")[0]
    return re.sub(r"\s+", "", cut)


def main():
    with open(LOCAL_B64, "a") as fh:
        for n in range(1, N_CHUNKS + 1):
            line = get_chunk(n)
            if line is None or not line.strip():
                print(f"chunk {n}: empty, retrying", flush=True)
                line = get_chunk(n)
            if line is None or not line.strip():
                print(f"chunk {n}: FAILED", flush=True)
                continue
            fh.write(line)
            if n % 10 == 0:
                print(f"chunk {n}/{N_CHUNKS}", flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
