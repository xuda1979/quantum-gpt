#!/usr/bin/env python3
"""C-10605 clean re-pull of leg1 artifacts from ASI1 (c10434 chunked pattern)."""

from __future__ import annotations

import base64
import gzip
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/daxu/software/quantum-gpt")
OUT = REPO / "outputs"
BOX = "ASI1"
BOUT = "/root/work/quantum-gpt/outputs/eval_leg1_c10605/sft-27b-q38-c10599-bump-20261021T220345Z"
LOCAL = OUT / "eval_leg1_c10605_full" / "sft-27b-q38-c10599-bump-20261021T220345Z"
PULL_TMP = "c10605_pull"


def box(cmd, timeout=240):
    r = subprocess.run(
        [sys.executable, str(REPO / "harness/scripts/run_and_report.py"), "--box-exec", BOX, cmd],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    out = r.stdout or ""
    if "STATUS: PASS" not in out:
        print("BOX_FAIL", (out or "")[-400:], (r.stderr or "")[-200:])
        return None
    return out.split("STDOUT:", 1)[-1].strip()


def pull_file(box_path, local_name):
    prep = box(
        "gzip -c " + box_path + " | base64 -w0 > /tmp/%s.b64; "
        "rm -f /tmp/%s_part_*; "
        "split -b 1800 /tmp/%s.b64 /tmp/%s_part_; "
        "ls -d /tmp/%s_part_* 2>/dev/null | wc -l" % ((PULL_TMP,) * 5)
    )
    if not prep:
        return False, "prepare-failed"
    n_parts = int(prep.strip().splitlines()[-1])
    ls = box(f"ls -d /tmp/{PULL_TMP}_part_* 2>/dev/null | sed 's#.*part_##'")
    if not ls:
        return False, "parts-ls-failed"
    part_names = ls.split()
    if len(part_names) != n_parts:
        return False, "part-count-mismatch %d!=%d" % (len(part_names), n_parts)
    chunks = []
    for nm in part_names:
        part = box(f"cat /tmp/{PULL_TMP}_part_{nm}")
        if not part:
            return False, f"part-{nm}-failed"
        chunks.append("".join(part.split()))
    data = gzip.decompress(base64.b64decode("".join(chunks)))
    md = box("md5sum " + box_path + " | cut -d' ' -f1")
    if not md:
        return False, "md5-unreadable"
    box_md5 = md.strip().split()[0]
    local_md5 = hashlib.md5(data).hexdigest()
    LOCAL.mkdir(parents=True, exist_ok=True)
    (LOCAL / local_name).write_bytes(data)
    print("PULLED", local_name, len(data), "bytes", "md5_match=" + str(local_md5 == box_md5))
    return (local_md5 == box_md5), None


def main():
    files = [
        "holdout_leg1_step-final-c10605.json",
        "leg1_step-final-c10605_scores.json",
        "leg1_step-final-c10605.log",
        "leg1_step-final-c10605_slice0_scores.json",
        "leg1_step-final-c10605_slice1_scores.json",
        "leg1_step-final-c10605_slice2_scores.json",
        "dispatch.log",
    ]
    rc = 0
    for fn in files:
        ok, err = pull_file(BOUT + "/" + fn, fn)
        print(fn, "OK" if ok else "FAIL", err or "")
        if not ok:
            rc = 1
    print("PULL_OK" if rc == 0 else "PULL_FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
