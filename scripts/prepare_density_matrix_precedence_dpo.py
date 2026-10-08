#!/usr/bin/env python3
"""Prepare DPO pairs for density-matrix operator precedence (Track N7).

Targets the TypeError on DensityMatrix @ (iter-2 gap report §3 item 4).
For each density-matrix-family task, emit a DPO pair:

- chosen  = correct program using explicit DensityMatrix(...) wrappers and
  parenthesized @ chains (passes tests.py).
- rejected = the same program with one DensityMatrix() wrapper removed or
  parentheses dropped from the @ chain (TypeError-inducing).

Usage:
    python scripts/prepare_density_matrix_precedence_dpo.py \
        --tasks-dir evals/tasks/quantum \
        --output data/generated/n7_density_matrix_precedence_dpo_v1.jsonl \
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

DM_TASKS = [
    "quantum_density_matrix_partial_trace",
    "quantum_partial_trace_bipartite",
]


def load_reference_candidate(tasks_dir: Path, task_id: str) -> str | None:
    candidates = [
        tasks_dir / task_id / "candidate.py",
        tasks_dir / task_id.replace("quantum_", "", 1) / "candidate.py",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text()
    return None


def canonicalize(code: str, task_id: str) -> str:
    if not code.lstrip().startswith("#!"):
        code = CANONICAL_HEADER + "\n" + code
    return f"Here is the reference solution for `{task_id}`.\n\n```python\n{code.rstrip()}\n```\n"


def has_density_matrix_op(code: str) -> bool:
    markers = ("DensityMatrix", "density_matrix", "partial_trace", " @ ")
    return any(m in code for m in markers)


def mutate_precedence(code: str) -> str | None:
    """Apply the first matching precedence-breaking mutation.

    Returns None if no mutation applies (task not in the DM family).
    """
    lines = code.split("\n")
    # Mutation 1: remove a DensityMatrix(...) wrapper
    for i, line in enumerate(lines):
        m = re.search(r"(\w+)\s*=\s*DensityMatrix\(([^)]+)\)", line)
        if m:
            lines[i] = line.replace(
                f"{m.group(1)} = DensityMatrix({m.group(2)})",
                f"{m.group(1)} = {m.group(2)}  # TypeError: missing DensityMatrix wrapper",
            )
            return "\n".join(lines)
    # Mutation 2: drop parentheses from an @ chain: a @ (b @ c) -> a @ b @ c
    for i, line in enumerate(lines):
        if " @ (" in line and ") @" in line:
            lines[i] = re.sub(r"\s*@\s*\(([^()]+)\)\s*@", r" @ \1 @ ", line)
            lines[i] += "  # TypeError: operator precedence broken"
            return "\n".join(lines)
    # Mutation 3: use * instead of @ for matrix multiply
    for i, line in enumerate(lines):
        if " @ " in line and "=" in line:
            lines[i] = line.replace(" @ ", " * ", 1) + "  # TypeError: * is elementwise, not matmul"
            return "\n".join(lines)
    return None


def build_pair(task_id: str, tasks_dir: Path) -> dict | None:
    code = load_reference_candidate(tasks_dir, task_id)
    if code is None or not has_density_matrix_op(code):
        return None
    mutated = mutate_precedence(code)
    if mutated is None:
        return None
    chosen_text = canonicalize(code, task_id)
    rejected_text = canonicalize(mutated, task_id)
    prompt = [
        {
            "role": "system",
            "content": "You are a quantum-code assistant. When composing density-matrix operators, use explicit DensityMatrix(...) wrappers and parenthesize @ chains to avoid TypeError on operator precedence.",
        },
        {
            "role": "user",
            "content": f"Solve task `{task_id}`. Ensure all density-matrix operations use correct types and precedence.",
        },
    ]
    return {
        "prompt": prompt,
        "chosen": prompt + [{"role": "assistant", "content": chosen_text}],
        "rejected": prompt + [{"role": "assistant", "content": rejected_text}],
        "task_id": task_id,
        "failure_category": "type_error_precedence",
        "pair_id": hashlib.sha256((task_id + "dm_precedence" + chosen_text).encode()).hexdigest()[
            :16
        ],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks-dir", default="evals/tasks/quantum")
    ap.add_argument("--output", required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    tasks_dir = Path(args.tasks_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n_pairs = n_skip = 0
    # Try the named DM tasks first; fall back to scanning all tasks for DM ops.
    task_ids = list(DM_TASKS)
    for p in sorted(tasks_dir.iterdir()):
        tid = "quantum_" + p.name
        if tid not in task_ids and (p / "candidate.py").exists():
            code = (p / "candidate.py").read_text()
            if has_density_matrix_op(code):
                task_ids.append(tid)

    with out.open("w") as fw:
        for tid in task_ids:
            pair = build_pair(tid, tasks_dir)
            if pair is None:
                n_skip += 1
                continue
            fw.write(json.dumps(pair, ensure_ascii=False) + "\n")
            n_pairs += 1

    print(
        f"N7 density-matrix-precedence DPO: wrote {n_pairs} pairs, skipped {n_skip} -> {out}",
        file=sys.stderr,
    )

    if args.check:
        ok = bad = 0
        for tid in task_ids:
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
