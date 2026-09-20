#!/usr/bin/env python3
"""build_grpo_v9_manifest.py — regenerate the SAPO RL v9 training manifest
(quantum_grpo_training_v9_rl_questions_v2.txt) from the materialized
waves of quantum_rl_questions_v2.jsonl tasks.

v9 = 44 task dirs under evals/tasks/quantum/quantum_rl_v2_* (waves
1+2+3 plus the wave-2 QML/QEC-focus extension),
each with
the full jsonl question text as task_prompt, a reference candidate, and a
shaped-details tests.py harness. The header follows the v7/v8 conventions:

  # source=quantum_rl_questions_v2.jsonl sha256=<sha256 of the jsonl bytes>
  # task_contract_sha256=<hash of sorted task.json + tests.py bytes>

The task_contract_hash() is reused verbatim from build_grpo_v8_manifest.py
(same separator scheme, sorted task ids). Deterministic: running it
reproduces the checked-in manifest byte-for-byte.

Usage:
  python3 scripts/build_grpo_v9_manifest.py [--output PATH] [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SOURCES_JSONL = ROOT / "quantum_rl_questions_v2.jsonl"
OUTPUT = ROOT / "evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt"

from scripts.build_grpo_v8_manifest import task_contract_hash  # noqa: E402

# Wave 1 (12 tasks): the same competence classes as the frozen holdout
# failures (partial trace/entropy x2, Shor order finding, Trotter,
# depolarizing x2, VQE, QAOA landscape, Bell basis/CHSH, QFT, stabilizers,
# error correction). Wave 2 (12 more tasks, 2026-08-31): teleportation,
# Grover with oracles x2, coined quantum walks x2, phase estimation x2,
# canonical amplitude estimation, QML variational classifier, readout
# error mitigation, measurement-helper repair, Phi+ CHSH evaluation.
# Wave 3 (12 more tasks, 2026-08-31): under-covered classes -- GHZ/MABK
# witnesses x2, zero-noise extrapolation, Fermi-Hubbard Jordan-Wigner
# spectra x2, Heisenberg/TFIM second-order Trotter evolution, QFT matrix
# construction + QFT repair, StatePreparation x2, SWAP test. Wave 2
# extension (8 more tasks, 2026-08-31, QML/QEC-focus lane): QML class
# (kernel matrix R3, RX/RY Jacobian, x1>0 variational classifier),
# stabilizer work beyond bit-flip (binary A-G tableau, 6-qubit graph
# state, phase-flip channel Kraus), Grover 5-qubit Qiskit variant and
# canonical amplitude estimation for A=RY(0.6) with 3 evaluation qubits.
# All locally executable (qiskit/cirq/pennylane/stim/openfermion;
# braket/tket deferred — no local SDK).
NEW_TASK_IDS: list[str] = [
    # wave 1
    "quantum_rl_v2_ry_cx_entropy",
    "quantum_rl_v2_w_state_entropy",
    "quantum_rl_v2_shor_order_finding",
    "quantum_rl_v2_trotter_suzuki_1qubit",
    "quantum_rl_v2_depolarizing_kraus",
    "quantum_rl_v2_depolarizing_bell_mixed",
    "quantum_rl_v2_vqe_penny_energy",
    "quantum_rl_v2_qaoa_p2_maxcut",
    "quantum_rl_v2_bell_chsh",
    "quantum_rl_v2_phase_encode_decode",
    "quantum_rl_v2_stim_cluster_tableau",
    "quantum_rl_v2_bitflip_code_ancilla",
    # wave 2
    "quantum_rl_v2_teleport_rz_ry",
    "quantum_rl_v2_grover_cirq_1000",
    "quantum_rl_v2_walk_cycle16_7step",
    "quantum_rl_v2_walk_cycle4_3step",
    "quantum_rl_v2_qml_classifier_x0x1",
    "quantum_rl_v2_readout_mitigation",
    "quantum_rl_v2_qpe_cirq_0125",
    "quantum_rl_v2_measure_helper_5q",
    "quantum_rl_v2_chsh_phiplus_estimator",
    "quantum_rl_v2_grover_qiskit_101",
    "quantum_rl_v2_amplitude_estimation",
    "quantum_rl_v2_qpe_qiskit_0375",
    # wave 3
    "quantum_rl_v2_ghz_mabk_witness",
    "quantum_rl_v2_ghz_mabk_4party",
    "quantum_rl_v2_zne_richardson_zz",
    "quantum_rl_v2_hubbard_jw_2x1",
    "quantum_rl_v2_hubbard_jw_3x1",
    "quantum_rl_v2_heisenberg_trotter_3q",
    "quantum_rl_v2_tfim_trotter_3q",
    "quantum_rl_v2_qft_matrix_5q",
    "quantum_rl_v2_qft_repair_2q",
    "quantum_rl_v2_stateprep_amplitudes",
    "quantum_rl_v2_stateprep_2q",
    "quantum_rl_v2_swap_test_ry",
    # wave 2 extension (QML/QEC-focus lane, 8 more tasks; question
    # indices 517, 84, 32, 27, 266, 17, 100, 597 — disjoint from the
    # waves above and from the frozen holdout)
    "quantum_rl_v2_amplitude_estimation_ry",
    "quantum_rl_v2_binary_stabilizer_tableau",
    "quantum_rl_v2_graph_state_stabilizers_6q",
    "quantum_rl_v2_grover_qiskit_10111",
    "quantum_rl_v2_phase_flip_channel_kraus",
    "quantum_rl_v2_qml_jacobian_rx_ry",
    "quantum_rl_v2_qml_kernel_ring_r3",
    "quantum_rl_v2_qml_vc_sign_x1",
    # waves 4-6 gap-fill lineage (gate-alias registry, amplitude-damping
    # Kraus, GHZ/MABK witness, phase round-trip, gate-alias sequence,
    # channel damping fidelity, register phase round-trip, alias phase
    # drill, bare-file gate norm, statevector fidelity check, circuit
    # construct+measure, compact phase round-trip). Restored 2026-09-20:
    # the builder had lost this wave section and re-rendered only 44 of
    # the checked-in 56 tasks -- regeneration silently DROPPED 12 training
    # tasks whose dirs exist and whose contracts verify.
    "quantum_rl_v4_gapfill_gate_alias_registry",
    "quantum_rl_v4_gapfill_amplitude_damping_kraus",
    "quantum_rl_v4_gapfill_ghz_mabk_witness",
    "quantum_rl_v4_gapfill_phase_roundtrip",
    "quantum_rl_v5_gapfill_gate_alias_sequence",
    "quantum_rl_v5_gapfill_channel_damping_fidelity",
    "quantum_rl_v5_gapfill_register_phase_roundtrip",
    "quantum_rl_v5_gapfill_alias_phase_drill",
    "quantum_rl_v6_gapfill_bare_file_gate_norm",
    "quantum_rl_v6_gapfill_statevector_fidelity_check",
    "quantum_rl_v6_gapfill_circuit_construct_measure",
    "quantum_rl_v6_gapfill_compact_phase_roundtrip",
]


def manifest_ids(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def render() -> str:
    ids = list(NEW_TASK_IDS)
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate task id in v9 manifest")
    for task_id in ids:
        task_dir = ROOT / "evals/tasks" / "quantum" / task_id
        for name in ("task.json", "tests.py", "candidate.py"):
            if not (task_dir / name).is_file():
                raise SystemExit(f"missing v9 task artifact: {task_dir / name}")
    source_hash = hashlib.sha256(SOURCES_JSONL.read_bytes()).hexdigest()
    contract_hash = task_contract_hash(ids)
    lines = [
        f"# SAPO RL training from quantum_rl_questions_v2.jsonl: waves 1-6 gap-fill lineage = {len(ids)} tasks.",
        f"# source={SOURCES_JSONL.relative_to(ROOT)} sha256={source_hash}",
        f"# task_contract_sha256={contract_hash}",
        f"# targeted={len(ids)} deterministic=0 semantic=0",
        "# required_import_roots=",
        "# reference_execution_verified=true runs=3",
        "# Wave 1 (2026-08-31): frozen-holdout competence classes (partial",
        "# trace/entropy, Shor, Trotter, depolarizing, VQE, QAOA landscape,",
        "# Bell basis, QFT, stabilizers/tableau, error-correcting codes).",
        "# Wave 2/3 (2026-08-31): teleportation, Grover oracles, quantum walks,",
        "# QPE variants, amplitude estimation, QML classifier, readout",
        "# mitigation, measurement helper, GHZ/MABK witnesses, ZNE, Hubbard",
        "# Jordan-Wigner, Heisenberg/TFIM Trotter, QFT matrix/repair,",
        "# StatePreparation, SWAP test.",
        "# Wave 2 extension (2026-08-31): QML kernel matrix R3, RX/RY",
        "# Jacobian, x1>0 variational classifier, binary A-G stabilizer",
        "# tableau, 6-qubit graph state, phase-flip channel Kraus, Grover",
        "# 5-qubit Qiskit variant, canonical amplitude estimation RY(0.6).",
        "# Each task_prompt is the verbatim quantum_rl_questions_v2.jsonl",
        "# question text; all instances disjoint between waves and from the",
        "# frozen holdout sapo_promotion_holdout_v1_18.txt (read-only).",
        "# braket/tket jsonl questions deferred (no local SDK); PyMatching",
        "# decoding questions skipped (stochastic/fragile).",
        *ids,
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the output differs from the checked-in file",
    )
    args = parser.parse_args()

    text = render()
    if args.check:
        if not args.output.is_file():
            raise SystemExit(f"missing manifest: {args.output}")
        if args.output.read_text(encoding="utf-8") != text:
            raise SystemExit(f"manifest drift: {args.output} is stale (re-run builder)")
        print(f"OK {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"wrote {args.output} ({len(manifest_ids(args.output))} tasks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
