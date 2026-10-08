#!/usr/bin/env python3
"""Prepare DPO pairs targeting import-path failures (Track N3).

For each task in evals/tasks/quantum/ whose candidate.py imports a quantum
SDK, emit a DPO pair:

- chosen  = the reference candidate, canonicalized (passes tests.py).
- rejected = the reference candidate with exactly one import line mutated
  to a known-bad path (ImportError-inducing).

The rejected side is *constructed to fail* on the import axis, so the DPO
signal is corruption-proof.

Usage:
    python scripts/prepare_import_path_dpo.py \
        --tasks-dir evals/tasks/quantum \
        --output data/generated/n3_import_path_dpo_v1.jsonl \
        [--mutations configs/dpo/import_path_mutations_v1.json] \
        [--check]

Output: JSONL, one DPO pair per line (schema matches prepare_universal_failure_dpo.py).
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

# Known-bad import mutations: (regex matching a real import line, replacement).
# Each replacement is an import that will raise ImportError on a standard
# Qiskit / Cirq / PennyLane / Braket install.
DEFAULT_MUTATIONS = [
    # Qiskit: algorithms moved to qiskit_algorithms
    (
        r"^(\s*)from qiskit\.algorithms import (.*)$",
        r"\1from qiskit.algorithms.optimizers import \2  # ImportError: moved to qiskit_algorithms",
    ),
    # Qiskit: aqua fully removed
    (
        r"^(\s*)from qiskit\.aqua import (.*)$",
        r"\1from qiskit.aqua.components import \2  # ImportError: aqua removed",
    ),
    # Cirq: simulators path drift
    (
        r"^(\s*)from cirq\.sim import (.*)$",
        r"\1from cirq.simulators.sim import \2  # ImportError: wrong module",
    ),
    # PennyLane: qml vs pennylane
    (
        r"^(\s*)import pennylane as qml$",
        r"\1import pennylane_qml as qml  # ImportError: no module 'pennylane_qml'",
    ),
    # Braket: devices vs tasks
    (
        r"^(\s*)from braket\.devices import (.*)$",
        r"\1from braket.tasks import \2  # ImportError: wrong submodule",
    ),
    # Generic: drop the import entirely (NameError downstream)
    (r"^(\s*)from qiskit import QuantumCircuit$", r"\1# import removed — will raise NameError"),
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


def canonicalize_candidate(code: str, task_id: str) -> str:
    if not code.lstrip().startswith("#!"):
        code = CANONICAL_HEADER + "\n" + code
    return f"Here is the reference solution for `{task_id}`.\n\n```python\n{code.rstrip()}\n```\n"


def has_quantum_import(code: str) -> bool:
    markers = ("qiskit", "cirq", "pennylane", "braket", "pyquil", "qutip")
    return any(m in code for m in markers)


def mutate_imports(code: str, mutations: list) -> str | None:
    """Apply the first matching mutation. Returns None if no import line matched."""
    lines = code.split("\n")
    for i, line in enumerate(lines):
        for pattern, repl in mutations:
            if re.match(pattern, line):
                lines[i] = re.sub(pattern, repl, line)
                return "\n".join(lines)
    return None


def build_pair(task_id: str, tasks_dir: Path, mutations: list) -> dict | None:
    code = load_reference_candidate(tasks_dir, task_id)
    if code is None or not has_quantum_import(code):
        return None
    mutated = mutate_imports(code, mutations)
    if mutated is None:
        return None
    chosen_text = canonicalize_candidate(code, task_id)
    rejected_text = canonicalize_candidate(mutated, task_id)
    prompt = [
        {
            "role": "system",
            "content": 'You are a quantum-code assistant. Output a full Python program with def main() and the if __name__ == "__main__" guard. Use correct, current import paths for the quantum SDK.',
        },
        {
            "role": "user",
            "content": f"Solve task `{task_id}`. Ensure all imports resolve on a standard Qiskit/Cirq/PennyLane/Braket install.",
        },
    ]
    return {
        "prompt": prompt,
        "chosen": prompt + [{"role": "assistant", "content": chosen_text}],
        "rejected": prompt + [{"role": "assistant", "content": rejected_text}],
        "task_id": task_id,
        "failure_category": "import_error",
        "pair_id": hashlib.sha256((task_id + "import_path" + chosen_text).encode()).hexdigest()[
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
        "--mutations",
        default=None,
        help="JSON file with a list of [regex, replacement] pairs. Defaults to built-in set.",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Run each task's tests.py against the chosen candidate (slow, verifies ground truth).",
    )
    args = ap.parse_args()

    mutations = DEFAULT_MUTATIONS
    if args.mutations:
        with open(args.mutations) as f:
            raw = json.load(f)
        mutations = [(m[0], m[1]) for m in raw]

    tasks_dir = Path(args.tasks_dir)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    n_pairs = 0
    n_skip = 0
    with out.open("w") as fw:
        for tid in iter_task_ids(tasks_dir):
            pair = build_pair(tid, tasks_dir, mutations)
            if pair is None:
                n_skip += 1
                continue
            fw.write(json.dumps(pair, ensure_ascii=False) + "\n")
            n_pairs += 1

    print(
        f"N3 import-path DPO: wrote {n_pairs} pairs, skipped {n_skip} tasks "
        f"(no quantum import or no mutable line) -> {out}",
        file=sys.stderr,
    )

    if args.check:
        ok = bad = 0
        for tid in iter_task_ids(tasks_dir):
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
                print(f"CHECK FAIL {tid}: {r.stderr[:200]}", file=sys.stderr)
        print(f"CHECK: {ok} pass, {bad} fail", file=sys.stderr)


if __name__ == "__main__":
    main()
