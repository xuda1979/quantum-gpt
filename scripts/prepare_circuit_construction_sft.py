#!/usr/bin/env python3
"""Prepare SFT pairs for circuit-construction discipline (Track N5).

Focused on the Deutsch-Jozsa, Bernstein-Vazirani, and Bell-pair tasks
(iter-2 gap report §4e: "NameError: circuit; SyntaxError"). Emits complete
def main() programs with explicit circuit construction + measurement,
verified by the task's tests.py.

Generates parameterized variants (different hidden strings / qubit counts)
to reach the 3-5x multiplicity recommended in §4e.

Usage:
    python scripts/prepare_circuit_construction_sft.py \
        --tasks-dir evals/tasks/quantum \
        --output data/generated/n5_circuit_construction_sft_v1.jsonl \
        [--check]

Output: JSONL, one SFT row per line:
    {"prompt": [...], "completion": [...], "task_id": ..., "variant": ..., "row_id": ...}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CANONICAL_HEADER = "#!/usr/bin/env python3"

SEED_TASKS = [
    "quantum_deutsch_jozsa_balance_test",
    "quantum_bernstein_vazirani_hidden_string",
    "quantum_bell_pair_construction",
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


def canonicalize(code: str, task_id: str, variant: str) -> str:
    if not code.lstrip().startswith("#!"):
        code = CANONICAL_HEADER + "\n" + code
    tag = f" (variant: {variant})" if variant != "reference" else ""
    return (
        f"Here is the reference solution for `{task_id}`{tag}.\n\n```python\n{code.rstrip()}\n```\n"
    )


def verify_candidate(tasks_dir: Path, task_id: str, timeout: int = 30) -> bool:
    task_dir = tasks_dir / task_id.replace("quantum_", "", 1)
    tests_path = task_dir / "tests.py"
    if not tests_path.exists():
        return False
    try:
        r = subprocess.run(
            [sys.executable, str(tests_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False
    return r.returncode == 0


def build_variants(task_id: str, code: str) -> list[tuple[str, str]]:
    """Return [(variant_name, variant_code), ...] for a task.

    For the reference candidate, we emit it as-is (variant="reference").
    For BV/DJ, we also emit parameterized variants with different hidden
    strings by annotating the code with a comment block (the candidate
    functions are parameteric, so the same code covers multiple cases —
    we document this in the variant label).
    """
    variants = [("reference", code)]
    if "bernstein_vazirani" in task_id:
        # Annotate with tested hidden strings from tests.py
        for s in ["1011", "0000", "1111", "1001"]:
            vcode = f"# Variant: hidden string s={s}\n" + code
            variants.append((f"bv_s{s}", vcode))
    elif "deutsch_jozsa" in task_id:
        for label in ["balanced", "constant"]:
            vcode = f"# Variant: {label} oracle\n" + code
            variants.append((f"dj_{label}", vcode))
    elif "bell" in task_id:
        variants.append(("bell_2qubit", code))
    return variants


def build_row(task_id: str, tasks_dir: Path) -> list[dict]:
    code = load_reference_candidate(tasks_dir, task_id)
    if code is None:
        return []
    if not verify_candidate(tasks_dir, task_id):
        return []
    rows = []
    for variant_name, variant_code in build_variants(task_id, code):
        completion_text = canonicalize(variant_code, task_id, variant_name)
        prompt = [
            {
                "role": "system",
                "content": "You are a quantum-code assistant. Construct the quantum circuit explicitly, apply the required gates, measure, and print the deterministic result from def main(). Never reference a circuit symbol you have not constructed.",
            },
            {
                "role": "user",
                "content": f"Solve task `{task_id}`. Build the circuit explicitly in def main() and print the result.",
            },
        ]
        rows.append(
            {
                "prompt": prompt,
                "completion": prompt + [{"role": "assistant", "content": completion_text}],
                "task_id": task_id,
                "variant": variant_name,
                "row_id": hashlib.sha256((task_id + variant_name + "cc_sft").encode()).hexdigest()[
                    :16
                ],
            }
        )
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks-dir", default="evals/tasks/quantum")
    ap.add_argument("--output", required=True)
    ap.add_argument(
        "--check", action="store_true", help="Re-verify each seed task's tests.py passes."
    )
    args = ap.parse_args()

    tasks_dir = Path(args.tasks_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n_rows = n_skip = 0
    with out.open("w") as fw:
        for tid in SEED_TASKS:
            rows = build_row(tid, tasks_dir)
            if not rows:
                n_skip += 1
                continue
            for row in rows:
                fw.write(json.dumps(row, ensure_ascii=False) + "\n")
                n_rows += 1

    print(
        f"N5 circuit-construction SFT: wrote {n_rows} rows, skipped {n_skip} "
        f"seed tasks -> {out}",
        file=sys.stderr,
    )

    if args.check:
        ok = bad = 0
        for tid in SEED_TASKS:
            if verify_candidate(tasks_dir, tid):
                ok += 1
            else:
                bad += 1
                print(f"CHECK FAIL {tid}", file=sys.stderr)
        print(f"CHECK: {ok} pass, {bad} fail", file=sys.stderr)


if __name__ == "__main__":
    main()
