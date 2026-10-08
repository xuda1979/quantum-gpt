"""C-0024 freeze-integrity: canonical sha256 manifest + fail-closed eval-leg check.

The 18-task SAPO promotion holdout (evals/benchmarks/sapo_promotion_holdout_v1_18.txt)
plus its 18x(task.json, tests.py) and the scorer chain drifted between eval legs with
nothing detecting it (beats_base.py hash moved 3x in 21min on 2026-09-16). This pins
the whole set behind a committed manifest and forces every eval leg to verify it
fail-closed before scoring.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_RELPATH = "evals/benchmarks/sapo_promotion_holdout_v1_18.sha256"
BENCH_RELPATH = "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
RUNNER_RELPATH = "scripts/run_asi2_base_adapter_rubric_eval.py"

SCORER_CHAIN = (
    "evals/runner/single_candidate_eval.py",
    "scripts/run_asi2_base_adapter_rubric_eval.py",
    "evals/runner/candidate_sanitize.py",
    "harness/beats_base.py",
)

TASK_DIRS = (
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
)


def _required_paths():
    from evals.runner.holdout_freeze import required_paths

    return list(required_paths())


def test_module_task_ids_match_bench_txt_order():
    from evals.runner.holdout_freeze import bench_task_ids

    bench_ids = [
        ln.strip()
        for ln in (ROOT / BENCH_RELPATH).read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert len(bench_ids) == 18
    assert bench_task_ids() == bench_ids


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_tracked(relpath):
    proc = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relpath],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0


def test_manifest_exists_and_core_files_are_git_tracked():
    assert (ROOT / MANIFEST_RELPATH).is_file(), "missing " + MANIFEST_RELPATH
    assert _git_tracked(MANIFEST_RELPATH), MANIFEST_RELPATH + " not git-tracked"
    assert _git_tracked(BENCH_RELPATH), BENCH_RELPATH + " not git-tracked"
    assert _git_tracked(
        "evals/runner/single_candidate_eval.py"
    ), "evals/runner/single_candidate_eval.py not git-tracked"


def test_manifest_covers_full_required_set():
    from evals.runner.holdout_freeze import load_manifest

    entries = load_manifest(ROOT / MANIFEST_RELPATH)
    covered = set(rel for rel, _ in entries)
    required = set(_required_paths())
    missing = sorted(required - covered)
    assert not missing, "manifest does not cover: " + repr(missing)


def test_manifest_hashes_match_disk():
    from evals.runner.holdout_freeze import load_manifest

    for rel, digest in load_manifest(ROOT / MANIFEST_RELPATH):
        actual = _sha256(ROOT / rel)
        assert actual == digest, rel + ": manifest " + digest + " != disk " + actual


def test_verify_passes_on_current_tree():
    from evals.runner.holdout_freeze import verify_holdout_freeze

    verify_holdout_freeze(ROOT)


def _make_fake_tree(tmp_path):
    root = tmp_path / "repo"
    for rel in _required_paths():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("content-of-" + rel + "\n", encoding="utf-8")
    return root


def _write_manifest(root):
    from evals.runner.holdout_freeze import MANIFEST_RELPATH as rel
    from evals.runner.holdout_freeze import compute_manifest

    entries = compute_manifest(root)
    lines = [digest + "  " + r for r, digest in entries]
    out = root / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_verify_rejects_drifted_file(tmp_path):
    from evals.runner.holdout_freeze import HoldoutFreezeError, verify_holdout_freeze

    root = _make_fake_tree(tmp_path)
    _write_manifest(root)
    victim = root / SCORER_CHAIN[-1]
    victim.write_text(victim.read_text(encoding="utf-8") + "# drifted\n", encoding="utf-8")
    with pytest.raises(HoldoutFreezeError):
        verify_holdout_freeze(root)


def test_verify_rejects_missing_file(tmp_path):
    from evals.runner.holdout_freeze import HoldoutFreezeError, verify_holdout_freeze

    root = _make_fake_tree(tmp_path)
    _write_manifest(root)
    (root / BENCH_RELPATH).unlink()
    with pytest.raises(HoldoutFreezeError):
        verify_holdout_freeze(root)


def test_verify_rejects_missing_manifest(tmp_path):
    from evals.runner.holdout_freeze import HoldoutFreezeError, verify_holdout_freeze

    root = _make_fake_tree(tmp_path)
    with pytest.raises(HoldoutFreezeError):
        verify_holdout_freeze(root)


def test_verify_rejects_incomplete_coverage(tmp_path):
    from evals.runner.holdout_freeze import HoldoutFreezeError, verify_holdout_freeze

    root = _make_fake_tree(tmp_path)
    _write_manifest(root)
    manifest = root / "evals/benchmarks/sapo_promotion_holdout_v1_18.sha256"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    removed = [ln for ln in lines if SCORER_CHAIN[0] in ln]
    assert len(removed) == 1
    manifest.write_text("\n".join(ln for ln in lines if ln not in removed) + "\n", encoding="utf-8")
    with pytest.raises(HoldoutFreezeError):
        verify_holdout_freeze(root)


def test_eval_leg_runner_wires_failclosed_freeze_check():
    text = (ROOT / RUNNER_RELPATH).read_text(encoding="utf-8")
    assert "verify_holdout_freeze" in text, "runner does not call verify_holdout_freeze"
    assert (
        "from evals.runner.holdout_freeze import" in text
        or "from evals.runner import holdout_freeze" in text
    ), "runner does not import the freeze module"
    assert "HoldoutFreezeError" in text, "runner does not handle HoldoutFreezeError"
