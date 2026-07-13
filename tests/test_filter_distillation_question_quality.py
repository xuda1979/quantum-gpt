from __future__ import annotations

from scripts import filter_distillation_question_quality as quality


def row(source_path: str, instruction: str, task_type: str = "implementation") -> dict:
    return {
        "example_id": "ex",
        "task_type": task_type,
        "instruction": instruction,
        "response": "Rationale: implement a quantum circuit function with tests for qubit statevector behavior.",
        "metadata": {"source_path": source_path, "source_title": source_path},
    }


def test_accepts_quantum_coding_instruction() -> None:
    reasons = quality.rejection_reasons(
        row(
            "docs/quantum_libraries/qaoa_maxcut.md",
            "Implement a Qiskit QAOA MaxCut circuit builder function with unit tests for a three-edge graph, "
            "including a simulator-backed assertion for the cost Hamiltonian expectation.",
        )
    )
    assert reasons == []


def test_rejects_accessibility_source_even_if_quantum_named() -> None:
    reasons = quality.rejection_reasons(
        row(
            "docs/external/quantum-sdk-docs-latest/qiskit/accessibility.md",
            "Implement a Qiskit dashboard accessibility checker with keyboard navigation notes.",
        )
    )
    assert "low_value_source_doc" in reasons


def test_repair_requires_failure_signal() -> None:
    reasons = quality.rejection_reasons(
        row(
            "docs/quantum_libraries/cirq_basics.md",
            "Implement a Cirq circuit construction helper for a quantum Bell pair.",
            task_type="repair",
        )
    )
    assert "repair_without_failure_signal" in reasons


def test_agentic_requires_agent_or_failure_signal() -> None:
    reasons = quality.rejection_reasons(
        row(
            "docs/quantum_libraries/braket_basics.md",
            "Implement a Braket quantum circuit helper with a small simulator test.",
            task_type="agentic_trajectory",
        )
    )
    assert "agentic_without_agent_failure_signal" in reasons


def test_optimization_requires_optimization_signal() -> None:
    reasons = quality.rejection_reasons(
        row(
            "docs/quantum_libraries/pytket_basics.md",
            "This is a long instruction containing more than twenty words to bypass the length constraint. It asks to build a simple Hamiltonian and run some expectations but is completely missing any optimization concepts or keywords.",
            task_type="optimization",
        )
    )
    assert "optimization_without_optimization_signal" in reasons
