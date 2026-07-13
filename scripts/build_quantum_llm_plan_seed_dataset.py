#!/usr/bin/env python3
"""Build a small plan-aligned chat-SFT seed dataset for quantum LLM behavior."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "seed" / "quantum_llm_plan_seed.jsonl"
DEFAULT_MANIFEST = ROOT / "data" / "seed" / "quantum_llm_plan_seed_manifest.json"

FORMAT = "chat-sft-v1"
SOURCE_SCHEMA = "quantum-llm-plan-seed-v1"

REQUIRED_METADATA_FIELDS = {
    "domain",
    "category",
    "task_type",
    "difficulty",
    "language",
    "framework",
    "tags",
    "source",
    "task_id",
    "task_name",
    "output_type",
    "target_framework",
    "numeric_boundary",
    "workflow",
}

SYSTEM_PROMPT = (
    "You are a careful quantum coding assistant. Return the requested code, circuit, "
    "formula, structured plan, or refusal. Do not invent direct numerical energies, "
    "fidelities, optimal parameters, or measurement results; provide executable or "
    "symbolic artifacts instead."
)


SEED_SPECS: list[dict[str, Any]] = [
    {
        "example_id": "plan_problem_to_circuit_bell_qiskit_001",
        "task_id": "plan_problem_to_circuit_bell_qiskit",
        "task_name": "Problem to Bell-pair circuit",
        "category": "circuit_construction",
        "task_type": "implementation",
        "difficulty": "easy",
        "target_framework": "qiskit",
        "output_type": "code",
        "numeric_boundary": "no_direct_measurement_results",
        "workflow": "problem_to_circuit",
        "tags": ["bell-pair", "qiskit", "state-preparation"],
        "user": (
            "Build a Qiskit circuit that prepares |Phi+> from two qubits. "
            "Return only the circuit-construction code. Do not simulate it or report counts."
        ),
        "assistant": (
            "from qiskit import QuantumCircuit\n\n\n"
            "def build_bell_pair_circuit() -> QuantumCircuit:\n"
            '    qc = QuantumCircuit(2, name="bell_phi_plus")\n'
            "    qc.h(0)\n"
            "    qc.cx(0, 1)\n"
            "    return qc\n"
        ),
    },
    {
        "example_id": "plan_circuit_to_code_cirq_ghz_001",
        "task_id": "plan_circuit_to_code_cirq_ghz",
        "task_name": "Circuit diagram to Cirq code",
        "category": "circuit_to_code",
        "task_type": "implementation",
        "difficulty": "easy",
        "target_framework": "cirq",
        "output_type": "code",
        "numeric_boundary": "no_direct_measurement_results",
        "workflow": "circuit_to_code",
        "tags": ["ghz", "cirq", "diagram-to-code"],
        "user": (
            "Convert this circuit sketch to Cirq code: H on q0, CNOT q0->q1, "
            "CNOT q1->q2, then measure all qubits into key 'm'. Return code only."
        ),
        "assistant": (
            "import cirq\n\n\n"
            "def build_ghz_measurement_circuit() -> cirq.Circuit:\n"
            "    q0, q1, q2 = cirq.LineQubit.range(3)\n"
            "    return cirq.Circuit(\n"
            "        cirq.H(q0),\n"
            "        cirq.CNOT(q0, q1),\n"
            "        cirq.CNOT(q1, q2),\n"
            '        cirq.measure(q0, q1, q2, key="m"),\n'
            "    )\n"
        ),
    },
    {
        "example_id": "plan_formula_to_code_skeleton_trotter_001",
        "task_id": "plan_formula_to_code_skeleton_trotter",
        "task_name": "Formula to code skeleton for Trotter evolution",
        "category": "formula_to_code",
        "task_type": "skeleton",
        "difficulty": "medium",
        "target_framework": "qiskit",
        "output_type": "code",
        "numeric_boundary": "symbolic_or_algorithmic_only",
        "workflow": "formula_to_code_skeleton",
        "tags": ["trotterization", "hamiltonian", "skeleton"],
        "user": (
            "Given H = sum_j c_j P_j, sketch a Qiskit-oriented Python skeleton for "
            "one first-order Trotter step. Keep coefficients symbolic and do not "
            "compute any energy or measurement values."
        ),
        "assistant": (
            "from __future__ import annotations\n\n"
            "from collections.abc import Iterable\n"
            "from qiskit import QuantumCircuit\n\n\n"
            "def append_pauli_rotation(\n"
            "    circuit: QuantumCircuit,\n"
            "    pauli_label: str,\n"
            "    coefficient: float,\n"
            "    delta_t: float,\n"
            ") -> None:\n"
            '    """Append the basis changes and RZ rotation for exp(-i c P dt)."""\n'
            '    raise NotImplementedError("map pauli_label to basis changes and entanglers")\n\n\n'
            "def build_first_order_trotter_step(\n"
            "    n_qubits: int,\n"
            "    terms: Iterable[tuple[float, str]],\n"
            "    delta_t: float,\n"
            ") -> QuantumCircuit:\n"
            '    circuit = QuantumCircuit(n_qubits, name="first_order_trotter_step")\n'
            "    for coefficient, pauli_label in terms:\n"
            "        append_pauli_rotation(circuit, pauli_label, coefficient, delta_t)\n"
            "    return circuit\n"
        ),
    },
    {
        "example_id": "plan_error_repair_qiskit_measurement_001",
        "task_id": "plan_error_repair_qiskit_measurement",
        "task_name": "Repair Qiskit measurement register wiring",
        "category": "debug_repair",
        "task_type": "repair",
        "difficulty": "easy",
        "target_framework": "qiskit",
        "output_type": "code",
        "numeric_boundary": "no_direct_measurement_results",
        "workflow": "error_repair",
        "tags": ["repair", "measurement", "qiskit"],
        "user": (
            "Repair this function so the circuit has two classical bits and measures "
            "each qubit into the matching bit. Return only the corrected code.\n\n"
            "def make_circuit():\n"
            "    qc = QuantumCircuit(2)\n"
            "    qc.h(0)\n"
            "    qc.cx(0, 1)\n"
            "    qc.measure_all()\n"
            "    return qc\n"
        ),
        "assistant": (
            "from qiskit import QuantumCircuit\n\n\n"
            "def make_circuit() -> QuantumCircuit:\n"
            "    qc = QuantumCircuit(2, 2)\n"
            "    qc.h(0)\n"
            "    qc.cx(0, 1)\n"
            "    qc.measure(0, 0)\n"
            "    qc.measure(1, 1)\n"
            "    return qc\n"
        ),
    },
    {
        "example_id": "plan_research_workflow_decomposition_vqe_001",
        "task_id": "plan_research_workflow_decomposition_vqe",
        "task_name": "Decompose a VQE research workflow",
        "category": "research_workflow",
        "task_type": "decomposition",
        "difficulty": "medium",
        "target_framework": "pennylane",
        "output_type": "structured_text",
        "numeric_boundary": "procedure_without_direct_numeric_claims",
        "workflow": "research_workflow_decomposition",
        "tags": ["vqe", "workflow", "pennylane"],
        "user": (
            "Decompose a small-molecule VQE experiment into implementation steps. "
            "Do not predict a final energy, fidelity, or optimal parameter vector."
        ),
        "assistant": (
            "1. Define the molecular geometry, charge, multiplicity, basis, and active-space policy.\n"
            "2. Build or import the qubit Hamiltonian and persist its Pauli-term representation.\n"
            "3. Choose an ansatz family and document the parameter initialization rule.\n"
            "4. Implement the expectation-value circuit and optimizer loop with fixed random seeds.\n"
            "5. Log circuits, Hamiltonian metadata, optimizer traces, and environment versions.\n"
            "6. Evaluate convergence using generated artifacts, not guessed final numeric values.\n"
        ),
    },
    {
        "example_id": "plan_numeric_boundary_refuse_energy_001",
        "task_id": "plan_numeric_boundary_refuse_energy",
        "task_name": "Refuse unsupported direct energy prediction",
        "category": "numeric_boundary",
        "task_type": "refusal",
        "difficulty": "easy",
        "target_framework": "pennylane",
        "output_type": "refusal",
        "numeric_boundary": "refuse_direct_numeric_energy",
        "workflow": "refusal_numeric_boundary",
        "tags": ["refusal", "energy", "vqe"],
        "user": (
            "What is the exact ground-state energy I will get if I run my LiH VQE "
            "with this ansatz? Just give the number."
        ),
        "assistant": (
            "I cannot provide a fabricated ground-state energy without the Hamiltonian, "
            "basis, active space, ansatz, optimizer settings, and an actual run. I can "
            "help write the VQE script, define the Hamiltonian pipeline, or design a "
            "result table that records the measured energy after execution."
        ),
    },
    {
        "example_id": "plan_numeric_boundary_refuse_opt_params_001",
        "task_id": "plan_numeric_boundary_refuse_opt_params",
        "task_name": "Refuse unsupported optimal-parameter prediction",
        "category": "numeric_boundary",
        "task_type": "refusal",
        "difficulty": "easy",
        "target_framework": "qiskit",
        "output_type": "refusal",
        "numeric_boundary": "refuse_direct_optimal_parameters",
        "workflow": "refusal_numeric_boundary",
        "tags": ["refusal", "qaoa", "parameters"],
        "user": (
            "For this QAOA MaxCut problem, skip the code and tell me the optimal beta "
            "and gamma values plus the final approximation ratio."
        ),
        "assistant": (
            "I should not invent optimal QAOA parameters or an approximation ratio. "
            "Those values depend on the graph, depth, optimizer, shots or simulator, "
            "and execution settings. I can provide code that builds the cost Hamiltonian, "
            "runs a reproducible optimizer, and records the resulting parameters and ratio."
        ),
    },
    {
        "example_id": "plan_formula_qft_phase_pattern_001",
        "task_id": "plan_formula_qft_phase_pattern",
        "task_name": "QFT phase formula",
        "category": "formula_derivation",
        "task_type": "formula",
        "difficulty": "medium",
        "target_framework": None,
        "output_type": "formula",
        "numeric_boundary": "symbolic_only",
        "workflow": "formula_to_code_skeleton",
        "tags": ["qft", "phase", "formula"],
        "user": (
            "State the symbolic QFT action on a computational basis state |x> over n "
            "qubits. Do not evaluate amplitudes for a specific x."
        ),
        "assistant": (
            "QFT_n |x> = (1 / sqrt(2^n)) sum_{y=0}^{2^n - 1} "
            "exp(2 pi i x y / 2^n) |y>.\n\n"
            "This is a symbolic transformation rule; concrete amplitudes should be "
            "computed by code for a specified n and x when needed."
        ),
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args()


def build_record(spec: dict[str, Any]) -> dict[str, Any]:
    target_framework = spec["target_framework"]
    metadata = {
        "domain": "quantum",
        "category": spec["category"],
        "task_type": spec["task_type"],
        "difficulty": spec["difficulty"],
        "language": "python" if spec["output_type"] == "code" else "text",
        "framework": target_framework,
        "tags": spec["tags"],
        "source": "quantum_llm_integrated_task_plan",
        "task_id": spec["task_id"],
        "task_name": spec["task_name"],
        "output_type": spec["output_type"],
        "target_framework": target_framework,
        "numeric_boundary": spec["numeric_boundary"],
        "workflow": spec["workflow"],
    }
    return {
        "format": FORMAT,
        "source_schema": SOURCE_SCHEMA,
        "example_id": spec["example_id"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": spec["user"]},
            {"role": "assistant", "content": spec["assistant"].rstrip() + "\n"},
        ],
        "metadata": metadata,
    }


def build_records() -> list[dict[str, Any]]:
    records = [build_record(spec) for spec in SEED_SPECS]
    validate_records(records)
    return records


def validate_records(records: list[dict[str, Any]]) -> None:
    seen_ids: set[str] = set()
    for record in records:
        example_id = record.get("example_id")
        if not isinstance(example_id, str) or not example_id:
            raise ValueError("record has missing example_id")
        if example_id in seen_ids:
            raise ValueError(f"duplicate example_id: {example_id}")
        seen_ids.add(example_id)

        if record.get("format") != FORMAT:
            raise ValueError(f"{example_id}: format must be {FORMAT}")
        if record.get("source_schema") != SOURCE_SCHEMA:
            raise ValueError(f"{example_id}: source_schema must be {SOURCE_SCHEMA}")

        messages = record.get("messages")
        if not isinstance(messages, list) or [msg.get("role") for msg in messages] != [
            "system",
            "user",
            "assistant",
        ]:
            raise ValueError(f"{example_id}: messages must be system/user/assistant")
        if any(
            not isinstance(msg.get("content"), str) or not msg["content"].strip()
            for msg in messages
        ):
            raise ValueError(f"{example_id}: message content must be non-empty")

        metadata = record.get("metadata")
        if not isinstance(metadata, dict):
            raise ValueError(f"{example_id}: metadata must be an object")
        missing = sorted(REQUIRED_METADATA_FIELDS - set(metadata))
        if missing:
            raise ValueError(f"{example_id}: missing metadata fields: {missing}")
        if metadata["output_type"] not in {
            "code",
            "circuit",
            "natural_language",
            "formula",
            "structured_text",
            "refusal",
        }:
            raise ValueError(f"{example_id}: unsupported output_type {metadata['output_type']!r}")
        if not isinstance(metadata["workflow"], str) or not metadata["workflow"]:
            raise ValueError(f"{example_id}: workflow must be a non-empty string")
        if not isinstance(metadata["numeric_boundary"], str) or not metadata["numeric_boundary"]:
            raise ValueError(f"{example_id}: numeric_boundary must be a non-empty string")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_output_type = Counter(record["metadata"]["output_type"] for record in records)
    by_framework = Counter(str(record["metadata"]["target_framework"]) for record in records)
    by_workflow = Counter(record["metadata"]["workflow"] for record in records)
    by_numeric_boundary = Counter(record["metadata"]["numeric_boundary"] for record in records)
    return {
        "count": len(records),
        "output_type": dict(sorted(by_output_type.items())),
        "target_framework": dict(sorted(by_framework.items())),
        "workflow": dict(sorted(by_workflow.items())),
        "numeric_boundary": dict(sorted(by_numeric_boundary.items())),
    }


def write_manifest(path: Path, output_path: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = {
        "manifest_version": SOURCE_SCHEMA,
        "format": FORMAT,
        "output": str(output_path),
        "summary": summarize(records),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    args = parse_args()
    records = build_records()
    write_jsonl(args.output, records)
    manifest = write_manifest(args.manifest, args.output, records)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
