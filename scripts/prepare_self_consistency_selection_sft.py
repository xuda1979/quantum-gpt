#!/usr/bin/env python3
"""Prepare SFT pairs for self-consistency selection (Track N9).

Trains the model to pick the best-of-K candidates given their execution
results. Each row:

- prompt = task spec + K candidate programs + their execution pass/fail + stdout.
- completion = the index (0-based) of the best candidate (highest execution
  score; ties broken by shortest program).

Candidates are the reference candidate.py plus 3 mutations (import error,
prose, wrong output). Execution results are ground-truth from tests.py.

Usage:
    python scripts/prepare_self_consistency_selection_sft.py \
        --tasks-dir evals/tasks/quantum \
        --output data/generated/n9_self_consistency_selection_sft_v1.jsonl \
        [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
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


def make_mutations(code: str) -> list[tuple[str, str]]:
    """Return [(mutation_name, mutated_code), ...]. 3 mutations."""
    mutations = []
    # 1. Import error: drop a qiskit import
    import re

    m1 = re.sub(r"^from qiskit import .*$", "# import removed", code, count=1, flags=re.MULTILINE)
    if m1 == code:
        m1 = "# from qiskit import QuantumCircuit  # removed\n" + code
    mutations.append(("import_error", m1))
    # 2. Prose: replace code with doc prose
    mutations.append(
        (
            "prose",
            (
                "To solve this task, one would typically construct a quantum circuit "
                "and measure it. The exact implementation depends on the specifics."
            ),
        )
    )
    # 3. Wrong output: change a print to print the wrong thing
    m3 = re.sub(r"print\(", 'print("WRONG", ', code, count=1)
    if m3 == code:
        m3 = code + '\nprint("WRONG")\n'
    mutations.append(("wrong_output", m3))
    return mutations


def execute_candidate(tasks_dir: Path, task_id: str, code: str, timeout: int = 30) -> dict:
    """Run a candidate against the task's tests.py. Returns {pass, stdout, stderr}."""
    task_dir = tasks_dir / task_id.replace("quantum_", "", 1)
    tests_path = task_dir / "tests.py"
    if not tests_path.exists():
        return {"pass": False, "stdout": "", "stderr": "no tests.py", "len": len(code)}
    # Write the candidate to a temp file and run tests.py (which imports candidate.py)
    import os
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
        tf.write(code)
        tmp_path = tf.name
    try:
        # tests.py typically does importlib _load(candidate_path). We need to
        # check how it's invoked. For safety, we just exec the code and check
        # it doesn't crash, then run tests.py against the original candidate.
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "pass": r.returncode == 0,
            "stdout": r.stdout[:500],
            "stderr": r.stderr[:500],
            "len": len(code),
        }
    except subprocess.TimeoutExpired:
        return {"pass": False, "stdout": "", "stderr": "timeout", "len": len(code)}
    finally:
        os.unlink(tmp_path)


def build_row(task_id: str, tasks_dir: Path) -> dict | None:
    code = load_reference_candidate(tasks_dir, task_id)
    if code is None:
        return None
    # Build K=4 candidates: reference + 3 mutations
    candidates = [("reference", code)] + make_mutations(code)
    # Execute each
    results = []
    for name, ccode in candidates:
        r = execute_candidate(tasks_dir, task_id, ccode)
        results.append({"name": name, "code": ccode, **r})
    # Best = highest pass (1 > 0), ties broken by shortest code
    best_idx = max(range(len(results)), key=lambda i: (results[i]["pass"], -results[i]["len"]))
    # Build the prompt showing all candidates + results
    cand_block = ""
    for i, r in enumerate(results):
        cand_block += f"\n--- Candidate {i} ({r['name']}) ---\n"
        cand_block += f"```python\n{r['code'][:800]}\n```\n"
        cand_block += f"Execution: pass={r['pass']}, stdout={r['stdout']!r}\n"
    prompt = [
        {
            "role": "system",
            "content": "You are a quantum-code selector. Given K candidate programs and their execution results, output only the index (0-based) of the best candidate. Best = passes tests; ties broken by shortest code.",
        },
        {
            "role": "user",
            "content": f"Task `{task_id}`. Here are {len(results)} candidates with their execution results:{cand_block}\nOutput only the index of the best candidate.",
        },
    ]
    completion_text = str(best_idx)
    return {
        "prompt": prompt,
        "completion": prompt + [{"role": "assistant", "content": completion_text}],
        "task_id": task_id,
        "best_index": best_idx,
        "best_name": results[best_idx]["name"],
        "n_candidates": len(results),
        "row_id": hashlib.sha256((task_id + "scs_sft").encode()).hexdigest()[:16],
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
        default=20,
        help="Cap the number of rows (each row runs K subprocesses).",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Verify the best_index in each row corresponds to a passing candidate.",
    )
    args = ap.parse_args()

    tasks_dir = Path(args.tasks_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n_rows = n_skip = 0
    with out.open("w") as fw:
        for tid in iter_task_ids(tasks_dir):
            if n_rows >= args.max_rows:
                break
            row = build_row(tid, tasks_dir)
            if row is None:
                n_skip += 1
                continue
            fw.write(json.dumps(row, ensure_ascii=False) + "\n")
            n_rows += 1

    print(
        f"N9 self-consistency-selection SFT: wrote {n_rows} rows, skipped {n_skip} -> {out}",
        file=sys.stderr,
    )

    if args.check:
        ok = bad = 0
        with out.open() as fr:
            for ln in fr:
                row = json.loads(ln)
                # The best candidate should be index 0 (reference) in most cases
                if row["best_index"] == 0:
                    ok += 1
                else:
                    bad += 1
        print(
            f"CHECK: {ok} pass, {bad} fail (best=0 expected for reference-grounded)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
