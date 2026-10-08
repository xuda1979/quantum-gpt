"""C-0024: canonical sha256 freeze manifest for the 18-task SAPO promotion holdout.

Pins the bench task-id file, every task.json/tests.py of the 18 holdout tasks, and
the scorer chain (single_candidate_eval.py, the asi2 rubric eval runner,
candidate_sanitize.py, beats_base.py) behind a committed manifest, and verifies it
fail-closed at eval-leg start. Drift, missing files, or a missing manifest all
raise HoldoutFreezeError. Regenerate ONLY deliberately, via compute_manifest().

Dir names below are the RESOLVED layout (find_task strips the leading quantum_
prefix; quantum_error_correction_shor_9qubit and quantum_channel_depolarizing
keep it). Verify the id->dir mapping before editing.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

MANIFEST_RELPATH = "evals/benchmarks/sapo_promotion_holdout_v1_18.sha256"
BENCH_RELPATH = "evals/benchmarks/sapo_promotion_holdout_v1_18.txt"

# (bench task id, task dir under evals/tasks/quantum/), in bench order.
BENCH_TASKS = (
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

SCORER_CHAIN = (
    "evals/runner/single_candidate_eval.py",
    "scripts/run_asi2_base_adapter_rubric_eval.py",
    "evals/runner/candidate_sanitize.py",
    "harness/beats_base.py",
)


class HoldoutFreezeError(RuntimeError):
    pass


def bench_task_ids():
    return [task_id for task_id, _ in BENCH_TASKS]


def required_paths():
    paths = [BENCH_RELPATH]
    for _, task_dir in BENCH_TASKS:
        paths.append("evals/tasks/quantum/" + task_dir + "/task.json")
        paths.append("evals/tasks/quantum/" + task_dir + "/tests.py")
    paths.extend(SCORER_CHAIN)
    return paths


def default_repo_root():
    return Path(__file__).resolve().parents[2]


def compute_manifest(root):
    entries = []
    for rel in required_paths():
        p = Path(root) / rel
        if not p.is_file():
            raise HoldoutFreezeError("cannot compute manifest, missing file: " + rel)
        entries.append((rel, hashlib.sha256(p.read_bytes()).hexdigest()))
    return entries


def load_manifest(path):
    out = []
    for lineno, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise HoldoutFreezeError("malformed manifest line " + str(lineno) + " in " + str(path))
        out.append((parts[1].strip(), parts[0].lower()))
    if not out:
        raise HoldoutFreezeError("empty manifest: " + str(path))
    return out


def verify_holdout_freeze(repo_root=None, manifest_path=None):
    """Fail-closed verify. Returns the verified entries; raises HoldoutFreezeError
    on missing manifest, missing covered file, hash drift, duplicate entries, or
    incomplete coverage of the required set."""
    root = Path(repo_root) if repo_root is not None else default_repo_root()
    mpath = Path(manifest_path) if manifest_path is not None else root / MANIFEST_RELPATH
    if not mpath.is_file():
        raise HoldoutFreezeError("freeze manifest missing: " + str(mpath))
    entries = load_manifest(mpath)
    covered = set()
    for rel, digest in entries:
        if rel in covered:
            raise HoldoutFreezeError("duplicate manifest entry: " + rel)
        covered.add(rel)
        p = root / rel
        if not p.is_file():
            raise HoldoutFreezeError("manifest covers a missing file: " + rel)
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != digest:
            raise HoldoutFreezeError(
                "FREEZE DRIFT " + rel + ": manifest " + digest + " != disk " + actual
            )
    missing = sorted(set(required_paths()) - covered)
    if missing:
        raise HoldoutFreezeError("manifest does not cover required files: " + ", ".join(missing))
    return entries


def main(argv=None):
    try:
        entries = verify_holdout_freeze()
    except HoldoutFreezeError as exc:
        print("[freeze] FAIL-CLOSED: " + str(exc), file=sys.stderr)
        return 2
    print("[freeze] OK: " + str(len(entries)) + " files verified against " + MANIFEST_RELPATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
