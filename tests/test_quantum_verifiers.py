"""Tests for typed quantum-semantic verifiers (review 2026-08-05 #6).

Uses real qiskit quantum_info (Statevector, state_fidelity, Operator,
process_fidelity). Requires qiskit installed; skipped when unavailable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

qiskit = pytest.importorskip("qiskit")

from training.quantum_verifiers import (  # noqa: E402
    run_typed_verifier,
    score_from_typed_verifier,
)


def _make_task(tmp_path: Path, reference_code: str, verifier_type: str, entry: str) -> Path:
    task_dir = tmp_path / "evals" / "tasks" / "quantum" / "typed_task"
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "candidate.py").write_text(reference_code, encoding="utf-8")
    (task_dir / "task.json").write_text(
        json.dumps(
            {
                "id": "quantum_typed_task",
                "domain": "quantum",
                "category": "typed",
                "candidate_file": "candidate.py",
                "verifier_type": verifier_type,
                "verifier_entry": entry,
            }
        ),
        encoding="utf-8",
    )
    return task_dir


BELL_REFERENCE = """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def build_state():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return Statevector(qc)
"""


def test_state_preparation_fidelity_correct_and_wrong(tmp_path: Path) -> None:
    task_dir = _make_task(tmp_path, BELL_REFERENCE, "state_preparation", "build_state")
    correct = """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def build_state():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return Statevector(qc)
"""
    result = run_typed_verifier(
        correct, task_dir, {"verifier_type": "state_preparation", "verifier_entry": "build_state"}
    )
    assert result is not None
    assert abs(result["score"] - 1.0) < 1e-9

    wrong = """from qiskit.quantum_info import Statevector

def build_state():
    return Statevector([1, 0, 0, 0])  # |00>
"""
    result = run_typed_verifier(
        wrong, task_dir, {"verifier_type": "state_preparation", "verifier_entry": "build_state"}
    )
    assert result is not None
    assert result["score"] < 0.5


def test_state_preparation_ignores_global_phase(tmp_path: Path) -> None:
    task_dir = _make_task(tmp_path, BELL_REFERENCE, "state_preparation", "build_state")
    phase_flipped = """from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import cmath

def build_state():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    sv = Statevector(qc)
    # global phase -i: equivalent state
    return Statevector([cmath.exp(-1j * cmath.pi / 2) * a for a in sv.data])
"""
    result = run_typed_verifier(
        phase_flipped,
        task_dir,
        {"verifier_type": "state_preparation", "verifier_entry": "build_state"},
    )
    assert result is not None
    assert abs(result["score"] - 1.0) < 1e-6  # |<psi|phi>|^2 ignores global phase


def test_distribution_verifier_total_variation(tmp_path: Path) -> None:
    reference = """from qiskit import QuantumCircuit

def run_distribution():
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()
    # analytic probabilities for H|0>
    return {"0": 0.5, "1": 0.5}
"""
    task_dir = _make_task(tmp_path, reference, "distribution", "run_distribution")
    exact = 'def run_distribution():\n    return {"0": 0.5, "1": 0.5}\n'
    result = run_typed_verifier(
        exact, task_dir, {"verifier_type": "distribution", "verifier_entry": "run_distribution"}
    )
    assert result is not None
    assert abs(result["score"] - 1.0) < 1e-9

    biased = 'def run_distribution():\n    return {"0": 0.9, "1": 0.1}\n'
    result = run_typed_verifier(
        biased, task_dir, {"verifier_type": "distribution", "verifier_entry": "run_distribution"}
    )
    assert result is not None
    # TVD = 0.4 -> score 0.6
    assert abs(result["score"] - 0.6) < 1e-9


def test_process_fidelity_gate_synthesis(tmp_path: Path) -> None:
    reference = """from qiskit import QuantumCircuit

def build_gate():
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.h(0)
    return qc
"""
    task_dir = _make_task(tmp_path, reference, "process_fidelity", "build_gate")
    # Same unitary via a different but equivalent decomposition (CNOT + H is
    # its own inverse here; use an equivalent: H on 0 then CNOT in reverse
    # order is NOT the same; use the exact same circuit for fidelity 1).
    identical = """from qiskit import QuantumCircuit

def build_gate():
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.h(0)
    return qc
"""
    result = run_typed_verifier(
        identical, task_dir, {"verifier_type": "process_fidelity", "verifier_entry": "build_gate"}
    )
    assert result is not None
    assert abs(result["score"] - 1.0) < 1e-9

    different = """from qiskit import QuantumCircuit

def build_gate():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc  # H then CNOT: different unitary
"""
    result = run_typed_verifier(
        different, task_dir, {"verifier_type": "process_fidelity", "verifier_entry": "build_gate"}
    )
    assert result is not None
    assert result["score"] < 1.0


def test_untyped_task_falls_back_to_generic(tmp_path: Path) -> None:
    task_dir = _make_task(tmp_path, BELL_REFERENCE, "state_preparation", "build_state")
    score, info = score_from_typed_verifier(
        "def build_state():\n    return None\n",
        task_dir,
        {"verifier_type": None},
    )
    assert info is None  # untyped -> caller falls back to the generic fraction
    assert score == 0.0
    # Unknown verifier_type -> fallback too.
    score, info = score_from_typed_verifier(
        "def build_state():\n    return None\n",
        task_dir,
        {"verifier_type": "unknown_type"},
    )
    assert info is None
