#!/usr/bin/env python3
"""Execute every code answer in the curated quantum-algorithm-coding dataset.

Each answer embeds a single fenced ```python block that is a self-contained,
self-checking program (it ends with assertions and a print). This validator
extracts that block, runs it in a subprocess, and reports pass/fail so the
dataset can guarantee that every high-quality answer actually executes and is
numerically correct.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CODE_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)
DEFAULT_DATASET = Path("data/curated/quantum_algorithm_coding_100_v1.jsonl")


def extract_code(response: str) -> str:
    blocks = CODE_BLOCK.findall(response)
    if not blocks:
        raise ValueError("no python code block found in response")
    return blocks[-1]


def run_one(code: str, python: str, timeout: int) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(code)
        path = fh.name
    try:
        proc = subprocess.run([python, path], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"
    finally:
        Path(path).unlink(missing_ok=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip().splitlines()[-1:][0] if (
            proc.stderr or proc.stdout
        ).strip() else "non-zero exit"
    return True, proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--only", default=None, help="substring filter on example_id")
    args = parser.parse_args()

    rows = [json.loads(l) for l in args.dataset.read_text().splitlines() if l.strip()]
    failures = []
    for i, row in enumerate(rows, 1):
        eid = row.get("example_id", f"row{i}")
        if args.only and args.only not in eid:
            continue
        code = extract_code(row["response"])
        ok, msg = run_one(code, args.python, args.timeout)
        status = "PASS" if ok else "FAIL"
        print(f"[{i:3d}/{len(rows)}] {status}  {eid}: {msg}")
        if not ok:
            failures.append((eid, msg))

    print("\n" + "=" * 60)
    print(f"TOTAL: {len(rows)}  PASS: {len(rows) - len(failures)}  FAIL: {len(failures)}")
    for eid, msg in failures:
        print(f"  FAIL {eid}: {msg}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
