#!/usr/bin/env python3
"""C-10605 pull the big leg log (part names via two-column tee pattern to stay under cap)."""

from __future__ import annotations

import base64
import gzip
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/daxu/software/quantum-gpt")
BOX = "ASI1"
BOUT = "/root/work/quantum-gpt/outputs/eval_leg1_c10605/sft-27b-q38-c10599-bump-20261021T220345Z"
LOCAL = REPO / "outputs" / "eval_leg1_c10605_full" / "sft-27b-q38-c10599-bump-20261021T220345Z"
FN = "leg1_step-final-c10605.log"

import time as _t


def box(cmd, timeout=240):
    for attempt in range(4):
        try:
            r = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "harness/scripts/run_and_report.py"),
                    "--box-exec",
                    BOX,
                    cmd,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except Exception as e:
            print("BOX_EXC", e)
            _t.sleep(5)
            continue
        out = r.stdout or ""
        if "STATUS: PASS" in out:
            return out.split("STDOUT:", 1)[-1].strip()
        print("BOX_FAIL(attempt %d)" % attempt, (out or "")[-200:])
        if "BOX_DOWN" in out or "500" in out or "TimeoutExpired" in out:
            _t.sleep(5 + 5 * attempt)
            continue
        return None
    return None


prep = box(
    "gzip -c "
    + BOUT
    + "/"
    + FN
    + " | base64 -w0 > /tmp/cl10605.b64; rm -f /tmp/cl10605_part_*; split -b 1800 /tmp/cl10605.b64 /tmp/cl10605_part_; ls -d /tmp/cl10605_part_* | wc -l"
)
print("prep:", prep)
n_parts = int(prep.strip().splitlines()[-1])
print("n_parts=", n_parts)
# get names via two-stage: store list to file on box and read pages
box("ls -d /tmp/cl10605_part_* | sed 's#.*part_##' | tr '\n' ' ' > /tmp/cl10605_names.txt")
# count chars
ln = box("wc -c /tmp/cl10605_names.txt")
print("names file size:", ln)
name = box("cat /tmp/cl10605_names.txt")
print("names len:", len(name))
parts = name.split()
print("parts cnt from cat:", len(parts))
chunks = []
for nm in parts:
    part = box("cat /tmp/cl10605_part_" + nm)
    if not part:
        print("FAIL part", nm)
        sys.exit(2)
    chunks.append("".join(part.split()))
data = gzip.decompress(base64.b64decode("".join(chunks)))
md = box("md5sum " + BOUT + "/" + FN + " | cut -d' ' -f1").strip().split()[0]
local_md5 = hashlib.md5(data).hexdigest()
print("md5_match=", local_md5 == md, "len=", len(data))
LOCAL.mkdir(parents=True, exist_ok=True)
(LOCAL / FN).write_bytes(data)
print("WROTE", LOCAL / FN, "match=" + str(local_md5 == md))
