#!/usr/bin/env python3
"""Prepare DPO pairs for error-message-grounded repair (Track N10).

Each pair:

- prompt   = task spec + a failing program + its real traceback (captured
  by running the mutated program against the task's tests.py).
- chosen   = the corrected (reference) program, verified to pass tests.py.
- rejected = the original failing program (unchanged).

The rejected side is the *exact program that produced the traceback*, so the
DPO signal is corruption-proof.

Usage:
    python scripts/prepare_traceback_repair_dpo.py \
        --tasks-dir evals/tasks/quantum \
        --output data/generated/n10_traceback_repair_dpo_v1.jsonl \
        [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

CANONICAL_HEADER = "#!/usr/bin/env python3"


def load_reference_candidate(tasks_dir: Path, task_id: str) -> str | None:
    candidates = [
        tasks_dir / task_id / "candidate.py",
        tasks_dir / task_id.replace("quantum_", "", 1) / "candidate.py",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text()
    return None


def make_failing_variant(code: str) -> str | None:
    """Produce a failing variant by applying a mutation. Returns None if no mutation applies."""
    # 1. Drop a qiskit import -> NameError
    m1 = re.sub(r"^from qiskit import .*$", "# import removed", code, count=1, flags=re.MULTILINE)
    if m1 != code:
        return m1
    # 2. Change a print to wrong output -> assertion failure
    m2 = re.sub(r"print\(", 'print("WRONG", ', code, count=1)
    if m2 != code:
        return m2
    # 3. Remove a def body -> SyntaxError or NameError
    m3 = re.sub(r"(def \w+\([^)]*\):\s*\n)(    [^\n]+\n)", r"\1    pass\n", code, count=1)
    if m3 != code:
        return m3
    return None


def capture_traceback(code: str, timeout: int = 30) -> str:
    """Run the code and return the stderr (traceback) if it fails, else empty string."""
    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return "TimeoutExpired"
    if r.returncode == 0:
        return ""
    return r.stderr[-1500:]  # last 1500 chars to keep the payload bounded


def canonicalize(code: str, task_id: str) -> str:
    if not code.lstrip().startswith("#!"):
        code = CANONICAL_HEADER + "\n" + code
    return f"Here is the corrected solution for `{task_id}`.\n\n```python\n{code.rstrip()}\n```\n"


def build_pair(task_id: str, tasks_dir: Path) -> dict | None:
    ref_code = load_reference_candidate(tasks_dir, task_id)
    if ref_code is None:
        return None
    failing_code = make_failing_variant(ref_code)
    if failing_code is None:
        return None
    traceback = capture_traceback(failing_code)
    if not traceback:
        return None  # mutation didn't actually fail; skip
    chosen_text = canonicalize(ref_code, task_id)
    rejected_text = canonicalize(failing_code, task_id)
    prompt = [
        {
            "role": "system",
            "content": "You are a quantum-code repair assistant. Given a failing program and its traceback, output the corrected full program. Read the error type and message to determine the fix.",
        },
        {
            "role": "user",
            "content": (
                f"Solve task `{task_id}`. The following program fails:\n\n"
                f"```python\n{failing_code.rstrip()}\n```\n\n"
                f"Traceback:\n```\n{traceback.rstrip()}\n```\n\n"
                f'Output the corrected full program with def main() and the if __name__ == "__main__" guard.'
            ),
        },
    ]
    return {
        "prompt": prompt,
        "chosen": prompt + [{"role": "assistant", "content": chosen_text}],
        "rejected": prompt + [{"role": "assistant", "content": rejected_text}],
        "task_id": task_id,
        "failure_category": "traceback_repair",
        "traceback_tail": traceback[-200:],
        "pair_id": hashlib.sha256((task_id + "tr_dpo" + traceback[-200:]).encode()).hexdigest()[
            :16
        ],
    }


def iter_task_ids(tasks_dir: Path):
    for p in sorted(tasks_dir.iterdir()):
        if p.is_dir() and (p / "candidate.py").exists():
            yield "quantum_" + p.name


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks-dir", default="evals/tasks/quantum")
    ap.add_argument("--output", required=True)
    ap.add_argument(
        "--max-rows",
        type=int,
        default=30,
        help="Cap the number of pairs (each pair runs a subprocess to capture traceback).",
    )
    ap.add_argument(
        "--check", action="store_true", help="Verify the chosen side passes the task's tests.py."
    )
    args = ap.parse_args()

    tasks_dir = Path(args.tasks_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n_pairs = n_skip = 0
    with out.open("w") as fw:
        for tid in iter_task_ids(tasks_dir):
            if n_pairs >= args.max_rows:
                break
            pair = build_pair(tid, tasks_dir)
            if pair is None:
                n_skip += 1
                continue
            fw.write(json.dumps(pair, ensure_ascii=False) + "\n")
            n_pairs += 1

    print(
        f"N10 traceback-repair DPO: wrote {n_pairs} pairs, skipped {n_skip} -> {out}",
        file=sys.stderr,
    )

    if args.check:
        ok = bad = 0
        with out.open() as fr:
            for ln in fr:
                row = json.loads(ln)
                tid = row["task_id"]
                task_dir = tasks_dir / tid.replace("quantum_", "", 1)
                if not (task_dir / "tests.py").exists():
                    continue
                r = subprocess.run(
                    [sys.executable, str(task_dir / "tests.py")],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if r.returncode == 0:
                    ok += 1
                else:
                    bad += 1
        print(f"CHECK: {ok} pass, {bad} fail", file=sys.stderr)


if __name__ == "__main__":
    main()
