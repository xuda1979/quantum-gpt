# C-9668 (2026-09-23): reproducible per-task scorer freeze.
#
# The frozen 18-task holdout scorer chain (single_candidate_eval + task
# tests.py/seed + typed verifier) must be byte-for-byte reproducible so the
# independent second reconfirmation leg matches leg1 exactly. This locks the
# guarantee: two fresh-interpreter runs of single_candidate_eval on the same
# frozen task inputs must produce the identical per-task score JSON (sha256-
# equal). A drifted/mutated candidate MUST be detected (fail-closed).

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "evals" / "runner" / "single_candidate_eval.py"

# (bench task id, resolved task dir) in bench order -- mirrors holdout_freeze.BENCH_TASKS.
TASKS = [
    ("quantum_gate_alias_normalization", "gate_alias_normalization"),
    ("quantum_phase_estimation_circuit", "phase_estimation_circuit"),
    ("quantum_qaoa_maxcut", "qaoa_maxcut"),
    ("quantum_superdense_coding", "superdense_coding"),
    ("quantum_grover_oracle_diffusion", "grover_oracle_diffusion"),
    ("quantum_density_matrix_partial_trace", "density_matrix_partial_trace"),
    ("quantum_error_correction_shor_9qubit", "quantum_error_correction_shor_9qubit"),
    ("quantum_trotterized_hamiltonian_evolution", "trotterized_hamiltonian_evolution"),
    ("quantum_channel_depolarizing", "quantum_channel_depolarizing"),
    ("quantum_ghz_state_witness", "ghz_state_witness"),
    ("quantum_pennylane_vqe_h2", "pennylane_vqe_h2"),
    ("quantum_cirq_qaoa_line", "cirq_qaoa_line"),
    ("quantum_braket_bell_state", "braket_bell_state"),
    ("quantum_qiskit_qft_entangled", "qiskit_qft_entangled"),
    ("quantum_qiskit_stabilizer_5qubit_code", "qiskit_stabilizer_5qubit_code"),
    ("quantum_pennylane_qml_iris_classification", "pennylane_qml_iris_classification"),
    ("quantum_phase_register_roundtrip", "phase_register_roundtrip"),
    ("quantum_binary_measurement_decoder", "binary_measurement_decoder"),
]


def _task_dir(task_id):
    return ROOT / "evals" / "tasks" / "quantum" / task_id


def _run_scorer(task_dir):
    cand = task_dir / "candidate.py"
    tests = task_dir / "tests.py"
    proc = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--candidate",
            str(cand),
            "--tests",
            str(tests),
            "--task-dir",
            str(task_dir),
            "--timeout",
            "200",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=260,
    )
    out = proc.stdout.strip()
    assert out, f"scorer produced no stdout for {task_dir.name}: {proc.stderr[-300:]}"
    return out.splitlines()[-1]  # last JSON line is the per-task score


@pytest.mark.parametrize("task_id", [t for _, t in TASKS])
def test_independent_runs_byte_identical_per_task_score(task_id):
    td = _task_dir(task_id)
    assert (td / "candidate.py").is_file(), f"{task_id} missing candidate.py"
    r1 = _run_scorer(td)
    r2 = _run_scorer(td)  # independent fresh-interpreter run
    h1 = hashlib.sha256(r1.encode()).hexdigest()
    h2 = hashlib.sha256(r2.encode()).hexdigest()
    msg = f"{task_id}: per-task score NOT reproducible across independent runs"
    msg += f"\n  run1 sha={h1} {r1[:120]}"
    msg += f"\n  run2 sha={h2} {r2[:120]}"
    assert h1 == h2, msg


def test_non_reproducible_score_is_detected_red(tmp_path):
    # RED side of the determinism guarantee: when two runs WOULD produce
    # different per-task scores, the equality check must flag it (fail-
    # closed). We mutate the frozen candidate so it raises at runtime,
    # which the scorer grades as a distinct FAIL -- proving the
    # byte-identical assertion is not vacuous.
    td = _task_dir("quantum_channel_depolarizing")
    crash = tmp_path / "candidate_crash.py"
    crash.write_text(
        "def depolarizing_channel(*a):\n    raise RuntimeError('boom')\n"
        "def amplitude_damping_channel(*a):\n    return None\n"
        "def channel_fidelity(*a):\n    return 0.0\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--candidate",
            str(crash),
            "--tests",
            str(td / "tests.py"),
            "--task-dir",
            str(td),
            "--timeout",
            "200",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=260,
    )
    out = proc.stdout.strip()
    assert out, f"no stdout: {proc.stderr[-300:]}"
    crash_score = out.splitlines()[-1]
    base_score = _run_scorer(td)
    h_crash = hashlib.sha256(crash_score.encode()).hexdigest()
    h_base = hashlib.sha256(base_score.encode()).hexdigest()
    assert h_crash != h_base, (
        "drifted candidate produced identical per-task score; equality check vacuous\n"
        f"  base_sha={h_base} {base_score[:120]}\n"
        f"  crash_sha={h_crash} {crash_score[:120]}"
    )
