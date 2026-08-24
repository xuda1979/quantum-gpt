"""Eval-lane repair regression tests (2026-08-24, SAPO loop).

Four scorer tasks previously raised NoneType runner-exception tracebacks when
a candidate returned ``None`` instead of the expected structure:

  - density_matrix_partial_trace          (``_mat_close``: len(None))
  - quantum_error_correction_shor_9qubit  (``len(encoded_0)`` on None)
  - trotterized_hamiltonian_evolution     (``result[0][0]`` on None)
  - quantum_channel_depolarizing          (``abs(None - b)`` in ``_close``)

These tests pin the repaired contract: the scorer must return a pass/fail
verdict with details -- never a traceback -- for both the reference solution
and a broken (None-returning) candidate, and the harness must classify the
broken candidate as a clean assertion failure (never ``runner_exception``).
"""

from __future__ import annotations

import ast
import importlib.util
import json
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "evals" / "tasks" / "quantum"

REPAIR_TASK_IDS = [
    "density_matrix_partial_trace",
    "quantum_error_correction_shor_9qubit",
    "trotterized_hamiltonian_evolution",
    "quantum_channel_depolarizing",
    "cirq_qaoa_line",
]

# Functions the scorer cannot work without; a candidate missing one is broken
# and must score a clean assertion failure (base-model candidates omitted
# exactly these: purity / apply_x_error / trotter_evolve / best_maxcut_value).
REQUIRED_FUNCTIONS = {
    "density_matrix_partial_trace": [
        "density_from_state",
        "tensor_product",
        "partial_trace",
        "purity",
    ],
    "quantum_error_correction_shor_9qubit": ["shor_encode", "apply_x_error", "shor_decode"],
    "trotterized_hamiltonian_evolution": ["pauli_matrix", "matrix_exp_hermitian", "trotter_evolve"],
    "quantum_channel_depolarizing": [
        "depolarizing_channel",
        "amplitude_damping_channel",
        "channel_fidelity",
    ],
    "cirq_qaoa_line": [
        "maxcut_line_edges",
        "best_maxcut_value",
        "maxcut_value",
        "qaoa_line_circuit",
        "measure_bitstrings",
    ],
}


def _load_test_module(task_id: str):
    test_path = TASKS / task_id / "tests.py"
    spec = importlib.util.spec_from_file_location(f"tests_{task_id}", test_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _public_function_names(candidate_path: Path) -> list[str]:
    tree = ast.parse(candidate_path.read_text(encoding="utf-8"))
    return [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and not node.name.startswith("_")
    ]


def _write_none_stub(candidate_path: Path, tmpdir: Path) -> Path:
    """Broken candidate: every public function returns ``None``.

    Built from the reference candidate's function names so the stub always
    exposes the same API surface the hidden scorer calls.
    """
    names = _public_function_names(candidate_path)
    body = "\n".join(f"def {name}(*args, **kwargs):\n    return None\n" for name in names)
    stub = tmpdir / "broken_candidate.py"
    stub.write_text(textwrap.dedent(body))
    return stub


def _write_missing_function_candidate(candidate_path: Path, omit: str, tmpdir: Path) -> Path:
    """Broken candidate: exposes every public function except ``omit``.

    Matches the real failure mode of the cached base-model candidates, which
    omit required functions entirely (e.g. ``purity``, ``apply_x_error``,
    ``trotter_evolve``).
    """
    names = [n for n in _public_function_names(candidate_path) if n != omit]
    body = "\n".join(f"def {name}(*args, **kwargs):\n    return None\n" for name in names)
    stub = tmpdir / "broken_candidate_missing_fn.py"
    stub.write_text(textwrap.dedent(body))
    return stub


@pytest.mark.parametrize("task_id", REPAIR_TASK_IDS)
def test_reference_solution_passes_without_traceback(task_id: str):
    module = _load_test_module(task_id)
    result = module.run_tests(str(TASKS / task_id / "candidate.py"))
    assert result["passed"] is True
    assert result["details"]


@pytest.mark.parametrize("task_id", REPAIR_TASK_IDS)
def test_none_returning_candidate_scores_clean_fail(task_id: str, tmp_path: Path):
    module = _load_test_module(task_id)
    stub = _write_none_stub(TASKS / task_id / "candidate.py", tmp_path)
    result = module.run_tests(str(stub))  # must not raise
    assert result["passed"] is False
    assert result["details"], "scorer must record failure details, not raise"


@pytest.mark.parametrize("task_id", REPAIR_TASK_IDS)
def test_harness_classifies_none_candidate_as_assertion(task_id: str, tmp_path: Path):
    """Through the real harness path (run_eval.run_task) the None-returning
    candidate must be a clean assertion failure -- never a runner_exception."""
    from evals.runner.run_eval import run_task

    task_json = TASKS / task_id / "task.json"
    task_id_in_manifest = json.loads(task_json.read_text())["id"]
    stub = _write_none_stub(TASKS / task_id / "candidate.py", tmp_path)
    result = run_task(task_json, {task_id_in_manifest: stub})
    assert result["passed"] is False
    assert (
        result["error_type"] is None
    ), f"expected clean fail, got runner exception: {result['details'][:3]}"
    assert result["failure_category"] == "assertion"


@pytest.mark.parametrize("task_id", REPAIR_TASK_IDS)
def test_missing_function_candidate_scores_clean_fail(task_id: str, tmp_path: Path):
    """A candidate omitting a required function (the real base-model failure
    mode) must score a clean assertion failure, never a runner_exception."""
    from evals.runner.run_eval import run_task

    task_json = TASKS / task_id / "task.json"
    task_id_in_manifest = json.loads(task_json.read_text())["id"]
    omit = REQUIRED_FUNCTIONS[task_id][0]
    stub = _write_missing_function_candidate(TASKS / task_id / "candidate.py", omit, tmp_path)
    result = run_task(task_json, {task_id_in_manifest: stub})
    assert result["passed"] is False
    assert (
        result["error_type"] is None
    ), f"expected clean fail, got runner exception: {result['details'][:3]}"
    assert result["failure_category"] == "assertion"
