from __future__ import annotations

import importlib.util
from pathlib import Path

TASKS = [
    "gate_alias_casefold_barrier",
    "phase_measurement_register",
    "bitstring_maxcut_landscape",
    "superdense_pauli_router",
]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_targeted_support_candidates_pass_their_tests() -> None:
    base_dir = Path("evals/tasks/quantum")
    for task_name in TASKS:
        task_dir = base_dir / task_name
        tests_module = _load_module(task_dir / "tests.py", f"{task_name}_tests")
        result = tests_module.run_tests(str(task_dir / "candidate.py"))
        assert result["passed"], f"{task_name} failed: {result['details']}"
