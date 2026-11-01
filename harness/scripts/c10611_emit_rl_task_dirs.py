#!/usr/bin/env python3
"""C-10611 — emit the 28 qg_* tasks as SAPO RL task dirs under
evals/tasks/quantum/ (task #11), then hand off to admission (task #10).

Layout per task dir (matches evals/tasks/quantum/* conventions):
  task.json     — id/domain/category/framework/task_prompt/candidate_file/test_file
  candidate.py  — the verified reference solution (exec-green, G5)
  tests.py      — run_tests(candidate_path) -> {"passed": bool} harness
                  wrapping the corpus builder's `check(candidate)` suite

Contract alignment (verified before writing):
  - admission (training/task_admission.py): discovers task.json+tests.py,
    requires domain, task_prompt|description, reference_file (candidate.py),
    mutatable return; _RUNNER imports tests.py and calls run_tests(candidate).
  - RL trainers (training/grpo_trainer.py, agentic_grpo_trainer.py): discover
    <domain_dir>/<task_dir>/{task.json,tests.py,candidate.py}; scoring goes
    through evals/runner/single_candidate_eval.py -> tests.run_tests().
  - holdout safety: task prompts are the builder's docstrings, already
    G2-leak-checked against the IBM Qiskit HumanEval 139 freeze.

This script only EMITS files; admission itself runs via
scripts/verify_sapo_tasks.py in the sandbox (fail-closed doctrine).
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "harness" / "scripts" / "c10611_build_ibm_track_corpus.py"
TARGET = REPO / "evals" / "tasks" / "quantum"

# module -> category (RL task.json "category" field; informative, admission
# only requires domain)
CATEGORY_BY_MODULE = {
    "qiskit.quantum_info": "quantum_info",
    "qiskit.circuit": "circuit_construction",
    "qiskit.transpiler": "transpilation",
    "qiskit_aer": "aer_simulation",
    "qiskit.primitives": "primitives",
    "qiskit.circuit.library": "circuit_library",
    "qiskit.dagcircuit": "dagcircuit",
    "qiskit.qpy": "serialization",
    "qiskit.qasm2": "serialization",
    "qiskit.synthesis": "synthesis",
    "qiskit_aer.noise": "noise_modeling",
}

TESTS_TEMPLATE = '''"""SAPO RL harness for {tid} (C-10611 v26 corpus task).

Contract: run_tests(candidate_path) -> {{"passed": bool, "details": [str]}}.
The check suite is the corpus builder's `check(candidate)` (G5-verified).
"""
import importlib.util


def _load(candidate_path):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    try:
        check(module.{entry})
    except AssertionError as exc:
        return {{"passed": False, "details": [f"check failed: {{exc}}"]}}
    except Exception as exc:  # noqa: BLE001 — candidate errors are task signal
        return {{"passed": False, "details": [f"{{type(exc).__name__}}: {{exc}}"]}}
    return {{"passed": True, "details": ["ok"]}}


{check_src}
'''


def load_builder():
    spec = importlib.util.spec_from_file_location("c10611_builder", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = load_builder()
    tasks = mod.author_tasks()
    if len(tasks) != 28:
        print(f"FATAL: expected 28 author tasks, got {len(tasks)}", file=sys.stderr)
        return 2

    emitted = []
    for t in tasks:
        tid = t["id"]
        task_dir = TARGET / tid
        if task_dir.exists():
            print(f"SKIP (exists): {tid}")
            continue

        check_src = t["tests"].rstrip()
        if not re.search(r"^def check\(", check_src, flags=re.M):
            print(f"FATAL: {tid} tests lack check()", file=sys.stderr)
            return 2

        task_prompt = t["docstring"].strip() + (
            f"\nYou must implement this using a function named `{t['entry']}` taking no arguments."
        )

        meta = {
            "id": tid,
            "name": tid.replace("qg_", "").replace("_", " "),
            "domain": "quantum",
            "category": CATEGORY_BY_MODULE.get(t["module"], "qiskit_generalization"),
            "framework": "qiskit",
            "task_prompt": task_prompt,
            "candidate_file": "candidate.py",
            "test_file": "tests.py",
        }

        task_dir.mkdir(parents=True)
        (task_dir / "task.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (task_dir / "candidate.py").write_text(t["solution"].rstrip() + "\n", encoding="utf-8")
        (task_dir / "tests.py").write_text(
            TESTS_TEMPLATE.format(tid=tid, entry=t["entry"], check_src=check_src),
            encoding="utf-8",
        )
        emitted.append(tid)

    print(json.dumps({"emitted": emitted, "count": len(emitted)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
