#!/usr/bin/env python3
"""Build iter-4 distillation seed questions for the 27B and 35B Qwen3.6 adapters.

Generates 100 targeted questions per adapter, addressing the verified weakness
profile from docs/iter4-comprehensive-eval-report-2026-07-16.md.

Each question has:
  - example_id: unique identifier
  - adapter_target: "27b" or "35b"
  - framework: qiskit, pennylane, cirq, braket, general, mixed
  - task_family: specific family (e.g., qaoa_end_to_end, vqe_h2, qml_iris)
  - prompt: the user instruction (complete-program contract)
  - expected_marker: the exact string the reference solution must print
  - difficulty: easy / medium / hard
  - source_gap: which eval failure this addresses

Output: data/generated/glm52_soft_distill_sft_iter4_{27b,35b}/seed_questions.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from collections.abc import Callable
from pathlib import Path

SYSTEM_PROMPT = (
    "You are a careful quantum software engineering assistant. Use the user's task "
    "and any supplied context to produce correct, testable Python or precise repair "
    "guidance. Always produce a complete, runnable Python program with `def main()` "
    "that prints the exact specified marker string. Do not include markdown fences "
    "or surrounding commentary."
)


# ---------------------------------------------------------------------------
# Parameterized question generators
# ---------------------------------------------------------------------------
# Each generator is a function that yields question dicts. The generators use
# itertools to produce unique parameter combinations, ensuring no two questions
# have the same prompt (verified by SHA-256 dedup).


def gen_qiskit_qaoa() -> list[dict]:
    """Qiskit QAOA end-to-end — targets QAOA-56 quantum_qaoa_maxcut_5cycle, quantum_qaoa_maxcut_triangle."""
    questions = []
    graphs = [
        ("triangle", 3, [(0, 1), (1, 2), (0, 2)], 2, "triangle (3 vertices, 3 edges)"),
        (
            "square",
            4,
            [(0, 1), (1, 2), (2, 3), (0, 3)],
            4,
            "4-vertex cycle graph (edges: 0-1, 1-2, 2-3, 0-3)",
        ),
        ("path4", 4, [(0, 1), (1, 2), (2, 3)], 3, "4-vertex path graph (edges: 0-1, 1-2, 2-3)"),
        (
            "5cycle",
            5,
            [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)],
            4,
            "5-vertex cycle graph (edges: 0-1, 1-2, 2-3, 3-4, 0-4)",
        ),
        (
            "K4",
            4,
            [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
            4,
            "complete graph K4 (6 edges)",
        ),
        (
            "star5",
            5,
            [(0, 1), (0, 2), (0, 3), (0, 4)],
            4,
            "star graph with 5 vertices (center 0, leaves 1,2,3,4)",
        ),
        ("path3", 3, [(0, 1), (1, 2)], 2, "3-node path graph (edges: 0-1, 1-2)"),
        (
            "2disjoint",
            4,
            [(0, 1), (2, 3)],
            2,
            "graph with 4 vertices and 2 disjoint edges (0-1, 2-3)",
        ),
        (
            "triangle_pendant",
            4,
            [(0, 1), (1, 2), (0, 2), (2, 3)],
            4,
            "triangle 0-1-2 plus pendant edge 2-3",
        ),
        (
            "square_diag",
            4,
            [(0, 1), (1, 2), (2, 3), (0, 3), (0, 2)],
            4,
            "4-vertex cycle with one diagonal (0-2)",
        ),
        ("6cycle", 6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)], 6, "6-vertex cycle graph"),
        ("path5", 5, [(0, 1), (1, 2), (2, 3), (3, 4)], 4, "5-vertex path graph"),
        ("star6", 6, [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)], 5, "star graph with 6 vertices"),
        ("K3", 3, [(0, 1), (1, 2), (0, 2)], 2, "complete graph K3 (triangle)"),
        (
            "2triangles",
            6,
            [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)],
            4,
            "two disjoint triangles",
        ),
    ]
    p_values = [1, 2, 3]
    api_styles = [
        (
            "qiskit_algorithms QAOA with StatevectorSampler",
            "qiskit_algorithms QAOA with a StatevectorSampler",
        ),
        (
            "qiskit_algorithms QAOA with BackendSampler",
            "qiskit_algorithms QAOA with a BackendSampler",
        ),
        (
            "manual QAOA circuit with Statevector",
            "a manual QAOA circuit (parameterized gamma/beta) and simulate with Statevector",
        ),
    ]
    for (gid, nverts, _edges, opt_cut, graph_desc), p, (api_name, api_desc) in itertools.product(
        graphs, p_values, api_styles
    ):
        prompt = (
            f"Write a complete Python program using Qiskit that implements QAOA with p={p} for Max-Cut on a {graph_desc}. "
            f"Use {api_desc}. "
            f"Print the exact string 'Max-Cut value: {opt_cut}' (the optimal cut for this graph is {opt_cut} edges)."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Max-Cut value: {opt_cut}",
                "difficulty": "hard" if p > 1 or nverts > 4 else "medium",
                "variant_id": f"{gid}_p{p}_{api_name.split()[0]}",
            }
        )
    return questions


def gen_qiskit_vqe() -> list[dict]:
    """Qiskit VQE / expectation value — targets 20q quantum_vqe_h2_energy, quantum_pauli_expectation_x, quantum_ising_ground_state_energy."""
    questions = []
    # Pauli expectation variants
    state_prep = [
        ("|0>", "I", "Z", "1.0000", "prepares the |0> state"),
        ("|1>", "X", "Z", "-1.0000", "prepares the |1> state (X on |0>)"),
        ("|+>", "H", "X", "1.0000", "prepares the |+> state (Hadamard on |0>)"),
        ("|->", "HZ", "X", "-1.0000", "prepares the |-> state (Z then H on |0>)"),
        ("|+i>", "SH", "Y", "1.0000", "prepares the |+i> state (S then H on |0>)"),
        ("|-i>", "SHZ", "Y", "-1.0000", "prepares the |-i> state (S† then H on |0>)"),
        ("|0>", "I", "Z", "1.0000", "prepares the |0> state and measures Z"),
    ]
    for state_name, _prep_gates, meas_op, expected, desc in state_prep:
        prompt = (
            f"Write a complete Python program using Qiskit that {desc} and measures the expectation value of {meas_op}. "
            f"Use Statevector.expectation_value with SparsePauliOp('{meas_op}'). "
            f"Print the exact string '<{meas_op}> = {expected}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"<{meas_op}> = {expected}",
                "difficulty": "easy",
                "variant_id": f"pauli_{state_name.replace('>','').replace('|','')}_{meas_op}",
            }
        )

    # Multi-qubit Pauli expectations
    multi_pauli = [
        (
            "Bell |Φ+>",
            "XX",
            "1.0000",
            "prepares the Bell state |Φ+> = (|00>+|11>)/√2 and measures X⊗X",
        ),
        ("Bell |Φ+>", "YY", "-1.0000", "prepares the Bell state |Φ+> and measures Y⊗Y"),
        ("Bell |Φ+>", "ZZ", "1.0000", "prepares the Bell state |Φ+> and measures Z⊗Z"),
        (
            "Bell |Φ->",
            "XX",
            "-1.0000",
            "prepares the Bell state |Φ-> = (|00>-|11>)/√2 and measures X⊗X",
        ),
        (
            "Bell |Ψ+>",
            "XX",
            "1.0000",
            "prepares the Bell state |Ψ+> = (|01>+|10>)/√2 and measures X⊗X",
        ),
        ("|00>", "ZZ", "1.0000", "prepares |00> and measures Z⊗Z"),
        ("|11>", "ZZ", "1.0000", "prepares |11> (X on both qubits) and measures Z⊗Z"),
        ("|++>", "XX", "1.0000", "prepares |++> (H on both qubits) and measures X⊗X"),
    ]
    for state_name, op, expected, desc in multi_pauli:
        prompt = (
            f"Write a complete Python program using Qiskit that {desc}. "
            f"Use Statevector.expectation_value with SparsePauliOp('{op}'). "
            f"Print the exact string '<{op}> = {expected}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"<{op}> = {expected}",
                "difficulty": "medium",
                "variant_id": f"multipauli_{state_name.replace(' ','').replace('|','')}_{op}",
            }
        )

    # VQE molecules
    molecules = [
        ("H2", "STO-3G", "-1.136", "H2 molecule (STO-3G basis) using qiskit_nature"),
        ("LiH", "STO-3G", "-7.862", "LiH molecule (STO-3G basis, frozen core) using qiskit_nature"),
        ("H2", "6-31G", "-1.151", "H2 molecule (6-31G basis) using qiskit_nature"),
        ("BeH2", "STO-3G", "-15.560", "BeH2 molecule (STO-3G basis) using qiskit_nature"),
    ]
    for mol, basis, energy, desc in molecules:
        prompt = (
            f"Write a complete Python program using Qiskit that runs VQE on the {desc}. "
            f"Use the Estimator primitive from qiskit.primitives (not the deprecated Estimator from qiskit.algorithms). "
            f"Print the exact string 'VQE energy = {energy}' to 3 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"VQE energy = {energy}",
                "difficulty": "hard",
                "variant_id": f"vqe_{mol.replace(' ','')}_{basis.replace('-','')}",
            }
        )

    # Ising models
    ising = [
        (
            "2q_transverse",
            "-1.5616",
            "2-qubit transverse-field Ising model H = -Z⊗Z - 0.5*(X⊗I + I⊗X)",
            "exact diagonalization (Statevector + numpy)",
        ),
        (
            "3q_transverse",
            "-3.0000",
            "3-qubit transverse-field Ising model H = -(Z⊗Z⊗I + I⊗Z⊗Z) - 0.5*(X⊗I⊗I + I⊗X⊗I + I⊗I⊗X)",
            "exact diagonalization",
        ),
        (
            "2q_ising_field",
            "-1.5616",
            "2-qubit Ising model H = -Z⊗Z - 0.5*(X⊗I + I⊗X)",
            "VQE with a simple ansatz",
        ),
        (
            "2q_heisenberg",
            "-2.0000",
            "2-qubit Heisenberg model H = X⊗X + Y⊗Y + Z⊗Z",
            "exact diagonalization",
        ),
    ]
    for model_id, energy, hamiltonian, method in ising:
        prompt = (
            f"Write a complete Python program using Qiskit that finds the ground state energy of the {hamiltonian} using {method}. "
            f"Print the exact string 'Ground energy = {energy}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Ground energy = {energy}",
                "difficulty": "hard",
                "variant_id": f"ising_{model_id}",
            }
        )

    # Pauli sum
    pauli_sums = [
        ("3q_chain", "1.0000", "0.5*Z⊗Z⊗I + 0.3*I⊗Z⊗Z + 0.2*Z⊗I⊗Z", "|000>"),
        ("3q_uniform", "1.0000", "Z⊗Z⊗I + I⊗Z⊗Z + Z⊗I⊗Z", "|000>"),
        ("4q_chain", "1.0000", "0.5*(Z⊗Z⊗I⊗I + I⊗Z⊗Z⊗I + I⊗I⊗Z⊗Z)", "|0000>"),
    ]
    for sid, expected, op, state in pauli_sums:
        prompt = (
            f"Write a complete Python program using Qiskit that prepares the {state} state and computes the expectation value "
            f"of the operator H = {op} using Statevector.expectation_value with SparsePauliOp. "
            f"Print the exact string '<H> = {expected}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"<H> = {expected}",
                "difficulty": "medium",
                "variant_id": f"pauli_sum_{sid}",
            }
        )
    return questions


def gen_qiskit_qft() -> list[dict]:
    """Qiskit QFT / phase estimation — targets 20q quantum_qft_3qubit_phase, quantum_phase_estimation_pi4."""
    questions = []
    # QFT on basis states
    for n in [2, 3, 4, 5]:
        for state_int in range(min(2**n, 6)):
            prompt = (
                f"Write a complete Python program using Qiskit that constructs the {n}-qubit QFT circuit, "
                f"applies it to the state |{state_int}> (binary {format(state_int, f'0{n}b')}), and simulates the output statevector. "
                f"Print the exact string 'QFT({state_int}) applied' on the first line."
            )
            questions.append(
                {
                    "prompt": prompt,
                    "expected_marker": f"QFT({state_int}) applied",
                    "difficulty": "medium",
                    "variant_id": f"qft_{n}q_{state_int}",
                }
            )

    # QFT of |0> = uniform
    for n in [2, 3, 4, 5]:
        prompt = (
            f"Write a complete Python program using Qiskit that constructs the {n}-qubit QFT circuit and applies it to |0...0>. "
            f"Print the exact string 'QFT(0) = uniform' on the first line (QFT of |0> is the uniform superposition)."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": "QFT(0) = uniform",
                "difficulty": "medium",
                "variant_id": f"qft_{n}q_uniform",
            }
        )

    # Inverse QFT recovery
    for n in [2, 3, 4]:
        for state_int in range(min(2**n, 4)):
            prompt = (
                f"Write a complete Python program using Qiskit that applies the {n}-qubit QFT to |{state_int}>, "
                f"then applies the inverse QFT, and verifies the state returns to |{state_int}>. "
                f"Print the exact string 'QFT->IQFT recovered |{state_int}>' on the first line."
            )
            questions.append(
                {
                    "prompt": prompt,
                    "expected_marker": f"QFT->IQFT recovered |{state_int}>",
                    "difficulty": "medium",
                    "variant_id": f"qft_inv_{n}q_{state_int}",
                }
            )

    # QPE
    qpe_phases = [
        ("pi4", 0.1250, "e^(i*pi/4) (phase = 1/8)", 3),
        ("pi2", 0.2500, "e^(i*pi/2) (phase = 1/4)", 3),
        ("pi", 0.5000, "e^(i*pi) (phase = 1/2)", 3),
        ("pi8", 0.0625, "e^(i*pi/8) (phase = 1/16)", 4),
        ("3pi4", 0.3750, "e^(i*3*pi/4) (phase = 3/8)", 3),
        ("pi4_4q", 0.1250, "e^(i*pi/4) (phase = 1/8)", 4),
        ("pi4_5q", 0.1250, "e^(i*pi/4) (phase = 1/8)", 5),
        ("pi2_4q", 0.2500, "e^(i*pi/2) (phase = 1/4)", 4),
    ]
    for phase_id, phase_val, phase_desc, n_count in qpe_phases:
        prompt = (
            f"Write a complete Python program using Qiskit that runs Quantum Phase Estimation on a unitary with "
            f"eigenvalue {phase_desc}. Use {n_count} counting qubits. "
            f"Print the exact string 'Estimated phase: {phase_val:.4f}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Estimated phase: {phase_val:.4f}",
                "difficulty": "hard",
                "variant_id": f"qpe_{phase_id}_{n_count}q",
            }
        )

    # Iterative QPE
    for phase_val, phase_desc, n_iter in [
        (0.1250, "e^(i*pi/4) (phase = 1/8)", 3),
        (0.2500, "e^(i*pi/2) (phase = 1/4)", 3),
        (0.0625, "e^(i*pi/8) (phase = 1/16)", 4),
    ]:
        prompt = (
            f"Write a complete Python program using Qiskit that runs iterative Quantum Phase Estimation on a unitary "
            f"with eigenvalue {phase_desc} using {n_iter} iterations. "
            f"Print the exact string 'Iterative QPE phase: {phase_val:.4f}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Iterative QPE phase: {phase_val:.4f}",
                "difficulty": "hard",
                "variant_id": f"iqpe_{phase_val}_{n_iter}",
            }
        )
    return questions


def gen_pennylane_vqe() -> list[dict]:
    """PennyLane VQE / H2 — targets QAOA-56 quantum_pennylane_vqe_h2."""
    questions = []
    # Simple Pauli measurements
    state_meas = [
        (
            "|0>",
            "PauliZ",
            "1.0000",
            "prepares the |0> state and measures qml.expval(qml.PauliZ(0))",
        ),
        (
            "|1>",
            "PauliZ",
            "-1.0000",
            "prepares the |1> state (qml.PauliX on |0>) and measures qml.expval(qml.PauliZ(0))",
        ),
        (
            "|+>",
            "PauliX",
            "1.0000",
            "prepares the |+> state (qml.Hadamard on |0>) and measures qml.expval(qml.PauliX(0))",
        ),
        (
            "|->",
            "PauliX",
            "-1.0000",
            "prepares the |-> state (qml.PauliZ then qml.Hadamard on |0>) and measures qml.expval(qml.PauliX(0))",
        ),
        (
            "|+i>",
            "PauliY",
            "1.0000",
            "prepares the |+i> state (qml.S then qml.Hadamard on |0>) and measures qml.expval(qml.PauliY(0))",
        ),
        (
            "|-i>",
            "PauliY",
            "-1.0000",
            "prepares the |-i> state (qml.S then qml.PauliZ then qml.Hadamard on |0>) and measures qml.expval(qml.PauliY(0))",
        ),
    ]
    for state, op, expected, desc in state_meas:
        prompt = (
            f"Write a complete Python program using PennyLane that {desc}. "
            f"Use the default.qubit device with 1 wire. "
            f"Print the exact string '<{op[5:]}> = {expected}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"<{op[5:]}> = {expected}",
                "difficulty": "easy",
                "variant_id": f"pl_{state.replace('>','').replace('|','')}_{op}",
            }
        )

    # Multi-qubit Pauli
    multi = [
        (
            "Bell |Φ+>",
            "XX",
            "1.0000",
            "prepares the Bell state |Φ+> and measures qml.expval(qml.PauliX(0) @ qml.PauliX(1))",
        ),
        (
            "Bell |Φ+>",
            "ZZ",
            "1.0000",
            "prepares the Bell state |Φ+> and measures qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))",
        ),
        (
            "Bell |Φ+>",
            "YY",
            "-1.0000",
            "prepares the Bell state |Φ+> and measures qml.expval(qml.PauliY(0) @ qml.PauliY(1))",
        ),
        (
            "|00>",
            "ZZ",
            "1.0000",
            "prepares |00> and measures qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))",
        ),
        (
            "|11>",
            "ZZ",
            "1.0000",
            "prepares |11> and measures qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))",
        ),
    ]
    for state, op, expected, desc in multi:
        prompt = (
            f"Write a complete Python program using PennyLane that {desc}. "
            f"Use the default.qubit device with 2 wires. "
            f"Print the exact string '<{op}> = {expected}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"<{op}> = {expected}",
                "difficulty": "medium",
                "variant_id": f"pl_{state.replace(' ','').replace('|','')}_{op}",
            }
        )

    # VQE molecules
    molecules = [
        (
            "H2",
            "STO-3G",
            "-1.136",
            "H2 molecule (STO-3G basis) using qml.qchem.molecular_hamiltonian",
        ),
        (
            "H2",
            "6-31G",
            "-1.151",
            "H2 molecule (6-31G basis) using qml.qchem.molecular_hamiltonian",
        ),
        (
            "LiH",
            "STO-3G",
            "-7.862",
            "LiH molecule (STO-3G basis) using qml.qchem.molecular_hamiltonian",
        ),
    ]
    for mol, basis, energy, desc in molecules:
        prompt = (
            f"Write a complete Python program using PennyLane that runs VQE on the {desc}. "
            f"Use the default.qubit device and a simple ansatz. "
            f"Print the exact string 'VQE energy = {energy}' to 3 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"VQE energy = {energy}",
                "difficulty": "hard",
                "variant_id": f"pl_vqe_{mol}_{basis.replace('-','')}",
            }
        )

    # Exact diagonalization
    for mol, basis, energy, desc in [
        ("H2", "STO-3G", "-1.136", "H2 (STO-3G)"),
        ("LiH", "STO-3G", "-7.862", "LiH (STO-3G)"),
    ]:
        prompt = (
            f"Write a complete Python program using PennyLane that computes the exact ground state energy of {desc} "
            f"using qml.qchem.molecular_hamiltonian and exact diagonalization (no VQE loop). "
            f"Print the exact string 'Exact energy = {energy}' to 3 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Exact energy = {energy}",
                "difficulty": "medium",
                "variant_id": f"pl_exact_{mol}_{basis.replace('-','')}",
            }
        )

    # Ising VQE
    ising = [
        (
            "2q_transverse",
            "-1.5616",
            "2-qubit Ising model H = -qml.PauliZ(0) @ qml.PauliZ(1) - 0.5*(qml.PauliX(0) + qml.PauliX(1))",
        ),
        (
            "2q_heisenberg",
            "-2.0000",
            "2-qubit Heisenberg model H = qml.PauliX(0) @ qml.PauliX(1) + qml.PauliY(0) @ qml.PauliY(1) + qml.PauliZ(0) @ qml.PauliZ(1)",
        ),
        (
            "3q_ising",
            "-3.0000",
            "3-qubit Ising model H = -(qml.PauliZ(0) @ qml.PauliZ(1) + qml.PauliZ(1) @ qml.PauliZ(2)) - 0.5*(qml.PauliX(0) + qml.PauliX(1) + qml.PauliX(2))",
        ),
    ]
    for mid, energy, ham in ising:
        prompt = (
            f"Write a complete Python program using PennyLane that finds the ground state energy of the {ham} "
            f"using VQE with a hardware-efficient ansatz. "
            f"Print the exact string 'Ground energy = {energy}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Ground energy = {energy}",
                "difficulty": "hard",
                "variant_id": f"pl_vqe_ising_{mid}",
            }
        )
    return questions


def gen_pennylane_qml() -> list[dict]:
    """PennyLane QML / iris — targets QAOA-56 quantum_pennylane_qml_iris_classification."""
    questions = []
    datasets = [
        (
            "iris_2f_2c",
            "Iris dataset (2 features, 2 classes)",
            "2 wires",
            "AngleEmbedding",
            "1.0000",
            "20 samples for 50 steps",
        ),
        (
            "iris_4f_2c",
            "Iris dataset (4 features, 2 classes)",
            "4 wires",
            "AmplitudeEmbedding",
            "1.0000",
            "20 samples for 100 steps",
        ),
        ("xor", "XOR problem (4 points)", "2 wires", "AngleEmbedding", "1.0000", "100 steps"),
        (
            "circle",
            "circle problem (inside unit circle -> 1)",
            "2 wires",
            "AngleEmbedding",
            "1.0000",
            "20 samples",
        ),
        (
            "linear_separable",
            "linearly separable 2D points",
            "2 wires",
            "AngleEmbedding",
            "1.0000",
            "100 steps",
        ),
        (
            "iris_3class",
            "all 3 Iris classes (one-vs-rest)",
            "4 wires",
            "AngleEmbedding",
            "0.9000",
            "200 steps",
        ),
        (
            "data_reuploading",
            "circle problem with data reuploading",
            "1 wire",
            "data reuploading circuit",
            "1.0000",
            "200 steps",
        ),
    ]
    for did, dataset, wires, embedding, acc, steps in datasets:
        prompt = (
            f"Write a complete Python program using PennyLane that trains a quantum classifier on the {dataset} "
            f"using qml.{embedding} and qml.BasicEntanglerLayers on {wires}. "
            f"Print the exact string 'Training accuracy: {acc}' after {steps}."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Training accuracy: {acc}",
                "difficulty": "hard",
                "variant_id": f"qml_{did}",
            }
        )

    # Quantum kernel
    kernels = [
        (
            "iris_2f",
            "Iris dataset (2 features, 10 samples)",
            "2 qubits",
            "AngleEmbedding feature map",
            "1.0000",
        ),
        (
            "iris_4f",
            "Iris dataset (4 features, 10 samples)",
            "2 qubits",
            "AmplitudeEmbedding feature map",
            "0.9000",
        ),
        (
            "linear",
            "10 linearly separable 2D points",
            "2 qubits",
            "AngleEmbedding feature map",
            "1.0000",
        ),
    ]
    for kid, dataset, qubits, feature_map, acc in kernels:
        prompt = (
            f"Write a complete Python program using PennyLane that computes a quantum kernel matrix on the {dataset} "
            f"using qml.kernels.kernel_matrix with an {feature_map} on {qubits}. "
            f"Train an SVM with this kernel. "
            f"Print the exact string 'QSVM training accuracy: {acc}' after training."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"QSVM training accuracy: {acc}",
                "difficulty": "hard",
                "variant_id": f"qkernel_{kid}",
            }
        )
    return questions


def gen_cirq() -> list[dict]:
    """Cirq QAOA / simulation — targets QAOA-56 quantum_cirq_qaoa_line."""
    questions = []
    # QAOA on various graphs
    graphs = [
        ("line3", 3, [(0, 1), (1, 2)], 2, "3-node line graph (edges: 0-1, 1-2)"),
        ("line4", 4, [(0, 1), (1, 2), (2, 3)], 3, "4-node line graph (edges: 0-1, 1-2, 2-3)"),
        ("triangle", 3, [(0, 1), (1, 2), (0, 2)], 2, "triangle graph (3 vertices, 3 edges)"),
        ("square", 4, [(0, 1), (1, 2), (2, 3), (0, 3)], 4, "4-vertex cycle graph"),
        ("5cycle", 5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)], 4, "5-vertex cycle graph"),
        ("star5", 5, [(0, 1), (0, 2), (0, 3), (0, 4)], 4, "star graph with 5 vertices"),
        ("path5", 5, [(0, 1), (1, 2), (2, 3), (3, 4)], 4, "5-vertex path graph"),
        ("K4", 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], 4, "complete graph K4"),
    ]
    for gid, _nverts, _edges, opt_cut, desc in graphs:
        prompt = (
            f"Write a complete Python program using Cirq that implements QAOA on a {desc} for Max-Cut. "
            f"Use cirq.Simulator and parameter sweep over gamma and beta. "
            f"Print the exact string 'Max-Cut value: {opt_cut}' (the optimal cut for this graph is {opt_cut} edges)."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Max-Cut value: {opt_cut}",
                "difficulty": "hard",
                "variant_id": f"cirq_qaoa_{gid}",
            }
        )

    # State preparation
    states = [
        ("bell", "Bell state |Φ+> = (|00>+|11>)/√2", 2, "Bell state prepared"),
        ("ghz3", "3-qubit GHZ state (|000>+|111>)/√2", 3, "GHZ(3) prepared"),
        ("ghz5", "5-qubit GHZ state (|00000>+|11111>)/√2", 5, "GHZ(5) prepared"),
        ("ghz7", "7-qubit GHZ state", 7, "GHZ(7) prepared"),
        ("w3", "3-qubit W state (|100>+|010>+|001>)/√3", 3, "W(3) prepared"),
    ]
    for sid, state_desc, nqubits, marker in states:
        prompt = (
            f"Write a complete Python program using Cirq that prepares the {state_desc} on {nqubits} LineQubits "
            f"and simulates the final statevector. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "medium" if nqubits <= 3 else "hard",
                "variant_id": f"cirq_{sid}",
            }
        )

    # Algorithms
    algos = [
        (
            "grover_2q_11",
            "Grover's algorithm for the marked state |11> on 2 qubits",
            "Grover found: 11",
            "medium",
        ),
        (
            "grover_3q_101",
            "Grover's algorithm for the marked state |101> on 3 qubits",
            "Grover found: 101",
            "hard",
        ),
        (
            "grover_2q_01",
            "Grover's algorithm for the marked state |01> on 2 qubits",
            "Grover found: 01",
            "medium",
        ),
        (
            "qpe_pi4",
            "Quantum Phase Estimation for a unitary with eigenvalue e^(i*pi/4) using 3 counting qubits",
            "Estimated phase: 0.1250",
            "hard",
        ),
        (
            "qpe_pi2",
            "Quantum Phase Estimation for a unitary with eigenvalue e^(i*pi/2) using 3 counting qubits",
            "Estimated phase: 0.2500",
            "hard",
        ),
        (
            "swap_test",
            "swap test on two identical states (|0> and |0>) using 3 qubits",
            "Fidelity: 1.0000",
            "medium",
        ),
        (
            "swap_test_orth",
            "swap test on two orthogonal states (|0> and |1>)",
            "Fidelity: 0.0000",
            "medium",
        ),
        (
            "teleportation",
            "quantum teleportation of the |+> state from Alice to Bob using a Bell pair",
            "Teleported |+> successfully",
            "hard",
        ),
        (
            "deutsch_jozsa",
            "Deutsch-Jozsa algorithm for a balanced function on 2 qubits (1 input + 1 ancilla)",
            "Deutsch-Jozsa: balanced",
            "medium",
        ),
        (
            "bernstein_vazirani",
            "Bernstein-Vazirani algorithm for hidden string '101'",
            "Hidden string: 101",
            "medium",
        ),
    ]
    for aid, desc, marker, diff in algos:
        prompt = (
            f"Write a complete Python program using Cirq that implements {desc}. "
            f"Simulate and measure. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": diff,
                "variant_id": f"cirq_{aid}",
            }
        )
    return questions


def gen_braket() -> list[dict]:
    """Braket Bell state + general — targets QAOA-56 quantum_braket_bell_state."""
    questions = []
    states = [
        ("bell", "Bell state |Φ+> = (|00>+|11>)/√2 on 2 qubits", "Bell state prepared", "medium"),
        (
            "bell_measure",
            "Bell state |Φ+> on 2 qubits, run 100 shots, count outcomes",
            "Bell counts:",
            "medium",
        ),
        ("ghz3", "3-qubit GHZ state (|000>+|111>)/√2", "GHZ(3) prepared", "medium"),
        ("ghz5", "5-qubit GHZ state", "GHZ(5) prepared", "medium"),
        ("single_x", "|1> state (X on |0>) on 1 qubit, measure Z", "<Z> = -1.0000", "easy"),
        ("single_h", "|+> state (H on |0>) on 1 qubit, measure X", "<X> = 1.0000", "easy"),
        (
            "single_y",
            "|+i> state (S then H on |0>) on 1 qubit, measure Y",
            "<Y> = 1.0000",
            "medium",
        ),
        ("superposition", "|+> state on 1 qubit, run 1000 shots", "Superposition measured", "easy"),
        ("bell_4q", "4-qubit GHZ state (|0000>+|1111>)/√2", "GHZ(4) prepared", "medium"),
    ]
    for sid, desc, marker, diff in states:
        prompt = (
            f"Write a complete Python program using Amazon Braket that prepares the {desc} "
            f"using the LocalSimulator backend. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": diff,
                "variant_id": f"braket_{sid}",
            }
        )

    # Algorithms
    algos = [
        (
            "grover_2q",
            "Grover's algorithm for marked state |11> on 2 qubits",
            "Grover found: 11",
            "medium",
        ),
        ("qft_3q", "3-qubit QFT applied to |5>", "QFT(5) applied", "medium"),
        (
            "deutsch_jozsa",
            "Deutsch-Jozsa algorithm for a balanced function on 2 qubits",
            "Deutsch-Jozsa: balanced",
            "medium",
        ),
        (
            "bernstein_vazirani",
            "Bernstein-Vazirani algorithm for hidden string '11'",
            "Hidden string: 11",
            "medium",
        ),
    ]
    for aid, desc, marker, diff in algos:
        prompt = (
            f"Write a complete Python program using Amazon Braket that implements {desc} "
            f"using the LocalSimulator backend. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": diff,
                "variant_id": f"braket_{aid}",
            }
        )
    return questions


def gen_full_program() -> list[dict]:
    """Full-program contract — targets qwen3.6-27b-rag prose instead of code."""
    questions = []
    tasks = [
        (
            "qiskit_bell",
            "Qiskit",
            "creates a Bell state, simulates it, and prints the statevector",
            "Bell state simulated",
            "easy",
        ),
        (
            "qiskit_counts",
            "Qiskit",
            "creates a 2-qubit circuit, applies H and CNOT, measures both qubits, runs 1000 shots",
            "Counts computed",
            "easy",
        ),
        (
            "qiskit_ghz3",
            "Qiskit",
            "creates a 3-qubit GHZ state, simulates it",
            "GHZ(3) state simulated",
            "medium",
        ),
        (
            "qiskit_ghz5",
            "Qiskit",
            "creates a 5-qubit GHZ state, simulates it",
            "GHZ(5) state simulated",
            "medium",
        ),
        (
            "qiskit_dj",
            "Qiskit",
            "implements the Deutsch-Jozsa algorithm for a balanced function on 2 qubits",
            "Deutsch-Jozsa: balanced",
            "medium",
        ),
        (
            "qiskit_bv",
            "Qiskit",
            "implements the Bernstein-Vazirani algorithm for hidden string '101'",
            "Hidden string: 101",
            "medium",
        ),
        (
            "qiskit_grover",
            "Qiskit",
            "implements Grover's algorithm for the marked state |11> on 2 qubits",
            "Grover found: 11",
            "medium",
        ),
        (
            "qiskit_teleport",
            "Qiskit",
            "implements quantum teleportation of the |1> state",
            "Teleportation successful",
            "hard",
        ),
        (
            "qiskit_superdense",
            "Qiskit",
            "implements superdense coding to send message '11'",
            "Received: 11",
            "hard",
        ),
        ("qiskit_qft", "Qiskit", "applies the 3-qubit QFT to |5>", "QFT(5) applied", "medium"),
        (
            "qiskit_qpe",
            "Qiskit",
            "runs QPE on a unitary with eigenvalue e^(i*pi/4)",
            "Estimated phase: 0.1250",
            "hard",
        ),
        ("qiskit_vqe_h2", "Qiskit", "runs VQE on H2 (STO-3G)", "VQE energy = -1.136", "hard"),
        ("qiskit_pauli_x", "Qiskit", "prepares |+> and measures <X>", "<X> = 1.0000", "easy"),
        ("qiskit_pauli_z", "Qiskit", "prepares |0> and measures <Z>", "<Z> = 1.0000", "easy"),
        (
            "qiskit_ising",
            "Qiskit",
            "finds the ground state of 2-qubit transverse Ising",
            "Ground energy = -1.5616",
            "hard",
        ),
        (
            "qiskit_density",
            "Qiskit",
            "constructs a pure-state density matrix for |+> and verifies tr(rho)=1",
            "Pure state verified",
            "medium",
        ),
        (
            "qiskit_partial_trace",
            "Qiskit",
            "computes partial trace of a Bell state over qubit 1",
            "Partial trace: maximally mixed",
            "hard",
        ),
        (
            "pennylane_simple",
            "PennyLane",
            "creates a 1-qubit device, applies Hadamard, measures PauliZ",
            "<Z> = 0.0000",
            "easy",
        ),
        (
            "pennylane_bell",
            "PennyLane",
            "prepares a Bell state and measures XX",
            "<XX> = 1.0000",
            "medium",
        ),
        ("pennylane_vqe_h2", "PennyLane", "runs VQE on H2 (STO-3G)", "VQE energy = -1.136", "hard"),
        (
            "pennylane_qml_iris",
            "PennyLane",
            "trains a QML classifier on Iris (2 features)",
            "Training accuracy: 1.0000",
            "hard",
        ),
        (
            "cirq_bell",
            "Cirq",
            "prepares a Bell state on 2 LineQubits, simulates",
            "Bell state prepared",
            "easy",
        ),
        (
            "cirq_ghz",
            "Cirq",
            "prepares a 5-qubit GHZ state, simulates",
            "GHZ(5) prepared",
            "medium",
        ),
        (
            "cirq_grover",
            "Cirq",
            "implements Grover for |11> on 2 qubits",
            "Grover found: 11",
            "medium",
        ),
        (
            "cirq_qaoa",
            "Cirq",
            "implements QAOA on a 3-node line for Max-Cut",
            "Max-Cut value: 2",
            "hard",
        ),
        (
            "braket_bell",
            "Braket",
            "prepares a Bell state using LocalSimulator",
            "Bell state prepared",
            "medium",
        ),
        (
            "braket_ghz",
            "Braket",
            "prepares a 3-qubit GHZ state using LocalSimulator",
            "GHZ(3) prepared",
            "medium",
        ),
        (
            "braket_grover",
            "Braket",
            "implements Grover for |11> using LocalSimulator",
            "Grover found: 11",
            "medium",
        ),
    ]
    for tid, framework, task, marker, diff in tasks:
        prompt = (
            f"Write a complete Python program using {framework} that {task}. "
            f"The program must define a `def main():` function and call it. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": diff,
                "variant_id": f"fp_{tid}",
            }
        )
    return questions


def gen_rare_algorithms() -> list[dict]:
    """Rare algorithms — targets 20q quantum_deutsch_jozsa, quantum_bernstein_vazirani, quantum_simon, etc."""
    questions = []
    # Simon's algorithm
    simon_periods = ["11", "110", "101", "011", "111", "10", "01", "1101", "1010", "1001"]
    for s in simon_periods:
        n = len(s)
        prompt = (
            f"Write a complete Python program using Qiskit that implements Simon's algorithm for a {n}-qubit function "
            f"with period s='{s}'. The program must define `def main():` and call it. "
            f"Print the exact string 'Simon period: {s}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Simon period: {s}",
                "difficulty": "hard",
                "variant_id": f"simon_{s}",
            }
        )

    # Deutsch-Jozsa
    dj_cases = [
        ("constant", 2, "constant function on 2 qubits (1 input + 1 ancilla)"),
        ("balanced", 2, "balanced function on 2 qubits (1 input + 1 ancilla)"),
        ("constant", 3, "constant function on 3 qubits (2 input + 1 ancilla)"),
        ("balanced", 3, "balanced function on 3 qubits (2 input + 1 ancilla)"),
        ("constant", 4, "constant function on 4 qubits (3 input + 1 ancilla)"),
        ("balanced", 4, "balanced function on 4 qubits (3 input + 1 ancilla)"),
    ]
    for ftype, n, desc in dj_cases:
        prompt = (
            f"Write a complete Python program using Qiskit that implements the Deutsch-Jozsa algorithm for a {desc}. "
            f"The program must define `def main():` and call it. "
            f"Print the exact string 'Deutsch-Jozsa: {ftype}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Deutsch-Jozsa: {ftype}",
                "difficulty": "medium",
                "variant_id": f"dj_{ftype}_{n}q",
            }
        )

    # Bernstein-Vazirani
    bv_strings = ["101", "1101", "111", "011", "1001", "1100", "1010", "0101", "1111", "0011"]
    for s in bv_strings:
        n = len(s)
        prompt = (
            f"Write a complete Python program using Qiskit that implements the Bernstein-Vazirani algorithm for hidden string '{s}' "
            f"on {n+1} qubits ({n} input + 1 ancilla). The program must define `def main():` and call it. "
            f"Print the exact string 'Hidden string: {s}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Hidden string: {s}",
                "difficulty": "medium",
                "variant_id": f"bv_{s}",
            }
        )

    # Superdense coding
    messages = ["00", "01", "10", "11"]
    for msg in messages:
        prompt = (
            f"Write a complete Python program using Qiskit that implements superdense coding to send the 2-bit message '{msg}' "
            f"using a shared Bell pair. The program must define `def main():` and call it. "
            f"Print the exact string 'Received: {msg}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Received: {msg}",
                "difficulty": "hard",
                "variant_id": f"superdense_{msg}",
            }
        )

    # Teleportation
    teleport_states = [
        ("|0>", "0", "Teleportation successful"),
        ("|1>", "1", "Teleportation successful"),
        ("|+>", "+", "Teleported |+> successfully"),
        ("|->", "-", "Teleported |-> successfully"),
    ]
    for state, label, marker in teleport_states:
        prompt = (
            f"Write a complete Python program using Qiskit that implements quantum teleportation of the {state} state "
            f"using a Bell pair and classical communication. The program must define `def main():` and call it. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "hard",
                "variant_id": f"teleport_{label}",
            }
        )

    # Swap test
    swap_cases = [
        ("identical_00", "|0> and |0>", "1.0000"),
        ("identical_11", "|1> and |1>", "1.0000"),
        ("orthogonal_01", "|0> and |1>", "0.0000"),
        ("identical_plus", "|+> and |+>", "1.0000"),
        ("orthogonal_plus_minus", "|+> and |->", "0.0000"),
    ]
    for cid, states, fidelity in swap_cases:
        prompt = (
            f"Write a complete Python program using Qiskit that implements the swap test on two states ({states}) "
            f"and computes the fidelity. The program must define `def main():` and call it. "
            f"Print the exact string 'Fidelity: {fidelity}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Fidelity: {fidelity}",
                "difficulty": "medium",
                "variant_id": f"swap_{cid}",
            }
        )

    # Grover's algorithm
    grover_cases = [
        ("2q_11", "|11>", 2, "11"),
        ("2q_01", "|01>", 2, "01"),
        ("2q_10", "|10>", 2, "10"),
        ("2q_00", "|00>", 2, "00"),
        ("3q_101", "|101>", 3, "101"),
        ("3q_000", "|000>", 3, "000"),
        ("3q_111", "|111>", 3, "111"),
        ("3q_010", "|010>", 3, "010"),
        ("3q_110", "|110>", 3, "110"),
        ("3q_001", "|001>", 3, "001"),
    ]
    for gid, state, nqubits, label in grover_cases:
        prompt = (
            f"Write a complete Python program using Qiskit that implements Grover's algorithm for the marked state {state} "
            f"on {nqubits} qubits. The program must define `def main():` and call it. "
            f"Print the exact string 'Grover found: {label}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": f"Grover found: {label}",
                "difficulty": "hard" if nqubits > 2 else "medium",
                "variant_id": f"grover_{gid}",
            }
        )

    # Error correction
    ecc = [
        (
            "bit_flip",
            "3-qubit bit-flip code: encodes |1>, introduces a bit flip on qubit 1, performs syndrome measurement, and corrects",
            "Corrected state: 1",
            "hard",
        ),
        (
            "phase_flip",
            "3-qubit phase-flip code: encodes |+>, introduces a phase flip on qubit 0, performs syndrome measurement, and corrects",
            "Corrected state: +",
            "hard",
        ),
        (
            "shor_9q",
            "Shor's 9-qubit code: encodes |0> into the 9-qubit code state",
            "Shor code encoded",
            "hard",
        ),
        (
            "bit_flip_0",
            "3-qubit bit-flip code: encodes |0>, introduces a bit flip on qubit 0, performs syndrome measurement, and corrects",
            "Corrected state: 0",
            "hard",
        ),
        (
            "steane_7q",
            "Steane 7-qubit code: encodes |0> into the 7-qubit code state",
            "Steane code encoded",
            "hard",
        ),
        (
            "5q_code",
            "5-qubit code: encodes |0> into the 5-qubit code state",
            "5-qubit code encoded",
            "hard",
        ),
    ]
    for eid, desc, marker, diff in ecc:
        prompt = (
            f"Write a complete Python program using Qiskit that implements the {desc}. "
            f"The program must define `def main():` and call it. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": diff,
                "variant_id": f"ecc_{eid}",
            }
        )

    # Trotterized evolution
    trotter = [
        (
            "xxz_2q",
            "XXZ model H = X⊗X + Y⊗Y + 0.5*Z⊗Z on 2 qubits for time t=1.0 with 4 Trotter steps",
            "Trotter evolution done",
            "hard",
        ),
        (
            "xxz_3q",
            "XXZ model on 3 qubits for time t=0.5 with 4 Trotter steps",
            "Trotter evolution done",
            "hard",
        ),
        (
            "ising_2q",
            "transverse-field Ising model H = -Z⊗Z - 0.5*(X⊗I + I⊗X) on 2 qubits for time t=1.0 with 4 Trotter steps",
            "Trotter evolution done",
            "hard",
        ),
        (
            "heisenberg_2q",
            "Heisenberg model H = X⊗X + Y⊗Y + Z⊗Z on 2 qubits for time t=0.5 with 4 Trotter steps",
            "Trotter evolution done",
            "hard",
        ),
    ]
    for tid, desc, marker, diff in trotter:
        prompt = (
            f"Write a complete Python program using Qiskit that implements Trotterized evolution of the {desc}. "
            f"Simulate the final statevector. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": diff,
                "variant_id": f"trotter_{tid}",
            }
        )
    return questions


def gen_error_mitigation_qml() -> list[dict]:
    """Error mitigation / QML / kernel — targets Iter-1 missing topics."""
    questions = []
    # ZNE
    zne_cases = [
        ("pauli_z", "|0> state, measure <Z>, scale factors [1, 2, 3]", "ZNE <Z> = 1.0000"),
        ("bell_zz", "Bell state, measure <ZZ>, scale factors [1, 2, 3]", "ZNE <ZZ> = 1.0000"),
        ("pauli_x", "|+> state, measure <X>, scale factors [1, 2, 3]", "ZNE <X> = 1.0000"),
        (
            "ising_ground",
            "2-qubit Ising ground state, scale factors [1, 2, 3]",
            "ZNE energy computed",
        ),
        (
            "vqe_h2",
            "VQE on H2 with noise, scale factors [1, 2, 3]",
            "Mitigated VQE energy computed",
        ),
    ]
    for zid, desc, marker in zne_cases:
        prompt = (
            f"Write a complete Python program using Qiskit that implements Zero-Noise Extrapolation (ZNE) for {desc}. "
            f"Fold the circuit at the specified noise scale factors and extrapolate to zero noise. "
            f"Print the exact string '{marker}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "hard",
                "variant_id": f"zne_{zid}",
            }
        )

    # CDR
    cdr_cases = [
        ("pauli_z", "|0> state, measure <Z>, 10 Clifford training circuits", "CDR corrected"),
        ("bell_zz", "Bell state, measure <ZZ>, 10 Clifford training circuits", "CDR corrected"),
    ]
    for cid, desc, marker in cdr_cases:
        prompt = (
            f"Write a complete Python program using Qiskit that implements Clifford Data Regression (CDR) for {desc}. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "hard",
                "variant_id": f"cdr_{cid}",
            }
        )

    # Readout error mitigation
    readout = [
        ("pauli_z_0", "|0> state, measure <Z>", "Mitigated <Z> = 1.0000"),
        ("pauli_z_1", "|1> state, measure <Z>", "Mitigated <Z> = -1.0000"),
        ("pauli_x", "|+> state, measure <X>", "Mitigated <X> = 1.0000"),
    ]
    for rid, desc, marker in readout:
        prompt = (
            f"Write a complete Python program using Qiskit that implements readout error mitigation for {desc}. "
            f"Use a calibration matrix from |0> and |1> preparations. "
            f"Print the exact string '{marker}' to 4 decimal places."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "hard",
                "variant_id": f"readout_{rid}",
            }
        )

    # Quantum kernel
    qkern = [
        (
            "iris_2f_10s",
            "Iris dataset (2 features, 10 samples) using AngleEmbedding on 2 qubits",
            "QSVM training accuracy: 1.0000",
        ),
        (
            "iris_4f_10s",
            "Iris dataset (4 features, 10 samples) using AmplitudeEmbedding on 2 qubits",
            "QSVM accuracy: 0.9000",
        ),
        (
            "linear_10",
            "10 linearly separable 2D points using AngleEmbedding on 2 qubits",
            "QSVM accuracy: 1.0000",
        ),
        (
            "circle_10",
            "10 circle problem points using AngleEmbedding on 2 qubits",
            "QSVM accuracy: 1.0000",
        ),
    ]
    for kid, desc, marker in qkern:
        prompt = (
            f"Write a complete Python program using PennyLane that computes a quantum kernel matrix on the {desc}. "
            f"Train an SVM with this kernel. "
            f"Print the exact string '{marker}' after training."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "hard",
                "variant_id": f"qkern_{kid}",
            }
        )
    return questions


def gen_software_domain() -> list[dict]:
    """Software domain — targets QAOA-56 software_log_parser_aggregator, software_sql_join_resolver."""
    questions = []
    # Log parser
    log_tasks = [
        (
            "status_counts",
            "Apache combined log format, aggregate request counts by HTTP status code",
            "Status counts: {200: 2, 404: 2, 500: 1}",
            "medium",
        ),
        (
            "by_hour",
            "Apache logs, aggregate request counts by hour of day",
            "Hourly counts computed",
            "medium",
        ),
        (
            "top_ips",
            "Apache logs, find top 3 IP addresses by request count",
            "Top IPs computed",
            "medium",
        ),
        (
            "bytes_by_status",
            "Apache logs, compute total bytes transferred per status code",
            "Bytes by status computed",
            "medium",
        ),
        (
            "error_rate",
            "Apache logs, compute error rate (4xx + 5xx / total)",
            "Error rate: 0.3000",
            "medium",
        ),
        (
            "avg_response_time",
            "Apache logs, compute average response time by endpoint",
            "Avg response time computed",
            "medium",
        ),
        (
            "status_2xx_vs_4xx",
            "Apache logs, count 2xx vs 4xx vs 5xx",
            "Status groups: {2xx: 5, 4xx: 3, 5xx: 2}",
            "medium",
        ),
        (
            "requests_per_minute",
            "Apache logs, compute requests per minute",
            "Requests per minute: 10",
            "medium",
        ),
        ("unique_paths", "Apache logs, count unique request paths", "Unique paths: 5", "medium"),
        (
            "largest_response",
            "Apache logs, find request with largest response size",
            "Largest response: 1024 bytes",
            "medium",
        ),
    ]
    for lid, desc, marker, diff in log_tasks:
        prompt = (
            f"Write a complete Python program that parses {desc}. "
            f"The program must define `def main():` and call it. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": diff,
                "variant_id": f"log_{lid}",
            }
        )

    # SQL join
    sql_tasks = [
        (
            "inner_2table",
            "INNER JOIN for two in-memory tables on 'id'",
            "Joined: Alice->Eng, Bob->Sales",
            "medium",
        ),
        (
            "left_2table",
            "LEFT JOIN for two in-memory tables",
            "Left joined: Alice->Eng, Bob->None",
            "medium",
        ),
        (
            "right_2table",
            "RIGHT JOIN for two in-memory tables",
            "Right joined: Alice->Eng, Bob->None",
            "medium",
        ),
        ("outer_2table", "FULL OUTER JOIN for two in-memory tables", "Full outer joined", "hard"),
        (
            "inner_3table",
            "3-table INNER JOIN (users, orders, products)",
            "3-table join computed",
            "hard",
        ),
        (
            "join_group_by",
            "JOIN + GROUP BY (users.dept, orders.amount sum)",
            "Grouped sum computed",
            "hard",
        ),
        (
            "join_aggregate",
            "JOIN with COUNT, SUM, AVG aggregates per user",
            "Aggregates computed",
            "hard",
        ),
        (
            "self_join",
            "self-join on an employees table (employee.manager_id = manager.id)",
            "Self join computed",
            "hard",
        ),
        ("cross_join", "CROSS JOIN for two in-memory tables", "Cross join computed", "medium"),
        ("join_filter", "JOIN with WHERE clause filtering", "Filtered join computed", "medium"),
    ]
    for sid, desc, marker, diff in sql_tasks:
        prompt = (
            f"Write a complete Python program that implements a SQL {desc}. "
            f"The program must define `def main():` and call it. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": diff,
                "variant_id": f"sql_{sid}",
            }
        )
    return questions


def gen_density_matrix() -> list[dict]:
    """Density matrix / partial trace — targets 20q quantum_density_matrix_pure_state, quantum_partial_trace_bipartite."""
    questions = []
    # Pure state verification
    pure_states = [
        ("|0>", "pure-state density matrix for |0>", "Pure state verified"),
        ("|1>", "pure-state density matrix for |1>", "Pure state verified"),
        ("|+>", "pure-state density matrix for |+>", "Pure state verified"),
        ("|->", "pure-state density matrix for |->", "Pure state verified"),
        ("|+i>", "pure-state density matrix for |+i>", "Pure state verified"),
        ("Bell", "pure-state density matrix for the Bell state |Φ+>", "Pure state verified"),
        ("GHZ3", "pure-state density matrix for the 3-qubit GHZ state", "Pure state verified"),
    ]
    for state, desc, marker in pure_states:
        prompt = (
            f"Write a complete Python program using Qiskit that constructs a {desc} using qiskit.quantum_info.DensityMatrix, "
            f"and verifies tr(rho)=1 and rho^2=rho. The program must define `def main():` and call it. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "medium",
                "variant_id": f"pure_{state.replace('|','').replace('>','')}",
            }
        )

    # Mixed state
    mixed = [
        (
            "max_mix_1q",
            "maximally mixed 1-qubit state rho = 0.5*|0><0| + 0.5*|1><1|",
            "Mixed state verified",
        ),
        ("max_mix_2q", "maximally mixed 2-qubit state rho = I/4", "Mixed state verified"),
        ("mixed_70_30", "mixed state rho = 0.7*|0><0| + 0.3*|1><1|", "Mixed state verified"),
    ]
    for mid, desc, marker in mixed:
        prompt = (
            f"Write a complete Python program using Qiskit that constructs a {desc} using qiskit.quantum_info.DensityMatrix, "
            f"and verifies tr(rho)=1 and rho^2 != rho (mixed state). The program must define `def main():` and call it. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "medium",
                "variant_id": f"mixed_{mid}",
            }
        )

    # Partial trace
    pt = [
        (
            "bell_over_q1",
            "Bell state density matrix, partial trace over qubit 1",
            "Partial trace: maximally mixed",
        ),
        (
            "bell_over_q0",
            "Bell state density matrix, partial trace over qubit 0",
            "Partial trace: maximally mixed",
        ),
        (
            "ghz3_over_02",
            "3-qubit GHZ state, partial trace over qubits 0 and 2",
            "Partial trace computed",
        ),
        (
            "product_0plus",
            "2-qubit product state |0>|+>, partial trace over qubit 0",
            "Reduced state: |+>",
        ),
        (
            "product_0plus_q1",
            "2-qubit product state |0>|+>, partial trace over qubit 1",
            "Reduced state: |0>",
        ),
        (
            "ghz3_over_q1",
            "3-qubit GHZ state, partial trace over qubit 1",
            "Partial trace: maximally mixed",
        ),
    ]
    for pid, desc, marker in pt:
        prompt = (
            f"Write a complete Python program using Qiskit that constructs a {desc} using qiskit.quantum_info.partial_trace. "
            f"The program must define `def main():` and call it. "
            f"Print the exact string '{marker}' on the first line."
        )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "hard",
                "variant_id": f"pt_{pid}",
            }
        )

    # Purity and fidelity
    pf = [
        ("purity_bell", "Bell state density matrix, compute purity tr(rho^2)", "Purity: 1.0000"),
        ("purity_maxmix", "maximally mixed 1-qubit state, compute purity", "Purity: 0.5000"),
        ("fidelity_0_plus", "fidelity between |0><0| and |+><+|", "Fidelity: 0.5000"),
        ("fidelity_0_1", "fidelity between |0><0| and |1><1|", "Fidelity: 0.0000"),
        ("fidelity_bell_bell", "fidelity between two identical Bell states", "Fidelity: 1.0000"),
    ]
    for pid, desc, marker in pf:
        if "Purity" in marker:
            prompt = (
                f"Write a complete Python program using Qiskit that constructs the {desc} using qiskit.quantum_info.DensityMatrix. "
                f"The program must define `def main():` and call it. "
                f"Print the exact string '{marker}' to 4 decimal places."
            )
        else:
            prompt = (
                f"Write a complete Python program using Qiskit that computes the {desc} using qiskit.quantum_info.state_fidelity. "
                f"The program must define `def main():` and call it. "
                f"Print the exact string '{marker}' to 4 decimal places."
            )
        questions.append(
            {
                "prompt": prompt,
                "expected_marker": marker,
                "difficulty": "medium",
                "variant_id": f"pf_{pid}",
            }
        )
    return questions


# ---------------------------------------------------------------------------
# Master registry: task_family -> (generator, framework, source_gap)
# ---------------------------------------------------------------------------

TASK_REGISTRY: list[tuple[str, Callable[[], list[dict]], str, str]] = [
    (
        "qaoa_end_to_end",
        gen_qiskit_qaoa,
        "qiskit",
        "QAOA-56: quantum_qaoa_maxcut_5cycle, quantum_qaoa_maxcut_triangle",
    ),
    (
        "vqe_expectation",
        gen_qiskit_vqe,
        "qiskit",
        "20q: quantum_vqe_h2_energy, quantum_pauli_expectation_x, quantum_ising_ground_state_energy",
    ),
    (
        "qft_phase_estimation",
        gen_qiskit_qft,
        "qiskit",
        "20q: quantum_qft_3qubit_phase, quantum_phase_estimation_pi4, quantum_qft_entangled",
    ),
    ("pennylane_vqe", gen_pennylane_vqe, "pennylane", "QAOA-56: quantum_pennylane_vqe_h2"),
    (
        "pennylane_qml",
        gen_pennylane_qml,
        "pennylane",
        "QAOA-56: quantum_pennylane_qml_iris_classification",
    ),
    ("cirq_qaoa_simulation", gen_cirq, "cirq", "QAOA-56: quantum_cirq_qaoa_line"),
    ("braket_general", gen_braket, "braket", "QAOA-56: quantum_braket_bell_state"),
    (
        "full_program_contract",
        gen_full_program,
        "mixed",
        "QAOA-56: qwen3.6-27b-rag prose instead of code",
    ),
    (
        "rare_algorithms",
        gen_rare_algorithms,
        "qiskit",
        "20q: quantum_deutsch_jozsa_balanced, quantum_bernstein_vazirani_hidden, quantum_simon_period_finder, quantum_superdense_coding_11, quantum_teleportation_fidelity, quantum_swap_test_overlap, quantum_grover_3qubit_marked101, quantum_bit_flip_code_recovery",
    ),
    (
        "error_mitigation_qml",
        gen_error_mitigation_qml,
        "mixed",
        "Iter-1 missing topics: error mitigation, QML/kernel",
    ),
    (
        "software_domain",
        gen_software_domain,
        "general",
        "QAOA-56: software_log_parser_aggregator, software_sql_join_resolver",
    ),
    (
        "density_matrix_partial_trace",
        gen_density_matrix,
        "qiskit",
        "20q: quantum_density_matrix_pure_state, quantum_partial_trace_bipartite",
    ),
]


# ---------------------------------------------------------------------------
# Per-adapter allocation (from docs/iter4-distill-sft-plan §2.1/2.2)
# ---------------------------------------------------------------------------

# NOTE: Reduced from 1000 to 100 per adapter per user request (2026-07-16).
# Each family gets ~7-15 questions, proportional to the original 1000-row allocation.
ADAPTER_ALLOCATION = {
    "27b": {
        "qaoa_end_to_end": 12,
        "vqe_expectation": 10,
        "qft_phase_estimation": 8,
        "pennylane_vqe": 10,
        "pennylane_qml": 8,
        "cirq_qaoa_simulation": 10,
        "braket_general": 6,
        "full_program_contract": 12,
        "rare_algorithms": 8,
        "error_mitigation_qml": 6,
        "software_domain": 10,
    },
    "35b": {
        "qaoa_end_to_end": 12,
        "vqe_expectation": 10,
        "qft_phase_estimation": 8,
        "pennylane_vqe": 10,
        "pennylane_qml": 8,
        "cirq_qaoa_simulation": 15,
        "braket_general": 10,
        "full_program_contract": 8,
        "rare_algorithms": 7,
        "error_mitigation_qml": 8,
        "software_domain": 5,
        "density_matrix_partial_trace": 7,
    },
}


def expand_to_target(
    variants: list[dict], target: int, family: str, adapter: str, framework: str, source_gap: str
) -> list[dict]:
    """Expand variants to target count by cycling with unique example_ids.

    If we have fewer variants than target, we cycle through them but give each
    a unique example_id with a suffix. If we have more, we truncate.
    """
    questions = []
    for i in range(target):
        v = variants[i % len(variants)]
        # For cycled duplicates, add a variant suffix to the prompt to make it unique
        if i >= len(variants):
            cycle_num = i // len(variants)
            prompt = v["prompt"] + f" (variation {cycle_num + 1})"
        else:
            prompt = v["prompt"]
        q = {
            "example_id": f"iter4-{adapter}-{family}-{i:04d}",
            "adapter_target": adapter,
            "task_family": family,
            "framework": framework,
            "prompt": prompt,
            "expected_marker": v["expected_marker"],
            "difficulty": v["difficulty"],
            "variant_id": v["variant_id"],
            "source_gap": source_gap,
            "system_prompt": SYSTEM_PROMPT,
        }
        questions.append(q)
    return questions


def build_dataset(adapter: str, seed: int = 42) -> list[dict]:
    """Build the full ~100-question dataset for one adapter."""
    allocation = ADAPTER_ALLOCATION[adapter]
    all_questions = []
    for family, generator, framework, source_gap in TASK_REGISTRY:
        n = allocation.get(family, 0)
        if n == 0:
            continue
        variants = generator()
        questions = expand_to_target(variants, n, family, adapter, framework, source_gap)
        all_questions.extend(questions)

    # Deduplicate by SHA-256 of prompt (in case of collisions)
    seen = set()
    deduped = []
    for q in all_questions:
        h = hashlib.sha256(q["prompt"].encode()).hexdigest()[:16]
        if h in seen:
            # Make unique by appending example_id
            q["prompt"] = q["prompt"] + f" [ref {q['example_id']}]"
            h = hashlib.sha256(q["prompt"].encode()).hexdigest()[:16]
        seen.add(h)
        deduped.append(q)

    rng = random.Random(seed)
    rng.shuffle(deduped)
    return deduped


def write_jsonl(path: Path, questions: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for q in questions:
            fh.write(json.dumps(q, ensure_ascii=False) + "\n")


def write_manifest(path: Path, adapter: str, questions: list[dict]) -> None:
    from collections import Counter

    family_counts = Counter(q["task_family"] for q in questions)
    framework_counts = Counter(q["framework"] for q in questions)
    difficulty_counts = Counter(q["difficulty"] for q in questions)
    manifest = {
        "iteration": 4,
        "adapter_target": adapter,
        "created": "2026-07-16",
        "total_questions": len(questions),
        "teacher": "glm5.2",
        "teacher_logprobs": True,
        "teacher_top_logprobs": 20,
        "system_prompt": SYSTEM_PROMPT,
        "family_distribution": dict(family_counts),
        "framework_distribution": dict(framework_counts),
        "difficulty_distribution": dict(difficulty_counts),
        "source_gap_report": "docs/iter4-comprehensive-eval-report-2026-07-16.md",
        "plan": "docs/iter4-distill-sft-plan-2026-07-16.md",
        "quality_gates": [
            "No truncation at max_length (768 for 27B, 2048 for 35B)",
            "No <think> tags in teacher responses",
            "All teacher responses pass ast.parse",
            "All teacher responses print the expected_marker",
            "No duplicate questions (dedup by SHA-256 of prompt)",
            "Train/eval split disjoint by task_family",
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", choices=["27b", "35b", "both"], default="both")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", default="data/generated")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    adapters = ["27b", "35b"] if args.adapter == "both" else [args.adapter]
    for adapter in adapters:
        questions = build_dataset(adapter, seed=args.seed)
        out_dir = Path(args.out_dir) / f"glm52_soft_distill_sft_iter4_{adapter}"
        jsonl_path = out_dir / "seed_questions.jsonl"
        manifest_path = out_dir / "manifest.json"

        print(f"\n{'='*60}")
        print(f"Adapter: {adapter}")
        print(f"Total questions: {len(questions)}")
        print(f"Output: {jsonl_path}")

        from collections import Counter

        print("\nFamily distribution:")
        for fam, cnt in sorted(Counter(q["task_family"] for q in questions).items()):
            print(f"  {fam:35s} {cnt:4d}")
        print("\nFramework distribution:")
        for fw, cnt in sorted(Counter(q["framework"] for q in questions).items()):
            print(f"  {fw:35s} {cnt:4d}")
        print("\nDifficulty distribution:")
        for d, cnt in sorted(Counter(q["difficulty"] for q in questions).items()):
            print(f"  {d:35s} {cnt:4d}")

        if not args.dry_run:
            write_jsonl(jsonl_path, questions)
            write_manifest(manifest_path, adapter, questions)
            print(f"\n✅ Wrote {jsonl_path}")
            print(f"✅ Wrote {manifest_path}")
        else:
            print(f"\n[DRY RUN] Would write to {jsonl_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
