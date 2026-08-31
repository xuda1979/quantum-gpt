from __future__ import annotations

import importlib.util
from pathlib import Path

from scripts.build_rl_tasks_stageB import build_tests, source_contract_for
from scripts.stageb_common import validate_quantum_source_contract

CIRQ_CONTRACT = {
    "framework_import_roots": ["cirq"],
    "circuit_constructors": ["Circuit"],
    "simulator_constructors": ["Simulator", "DensityMatrixSimulator"],
    "execution_methods": ["run", "simulate", "run_sweep", "simulate_sweep"],
    "require_dynamic_output": True,
}


def test_source_contract_rejects_hard_coded_semantic_stdout() -> None:
    source = "print({'000': 2000, '111': 2000})\n"

    passed, details = validate_quantum_source_contract(source, CIRQ_CONTRACT)

    assert not passed
    assert any("cirq" in detail.lower() for detail in details)


def test_source_contract_rejects_unused_quantum_scaffolding_with_constant_output() -> None:
    source = """
import cirq

qubits = cirq.LineQubit.range(3)
circuit = cirq.Circuit(cirq.H(qubits[0]))
simulator = cirq.Simulator()
simulator.run(circuit, repetitions=10)
counts = {'000': 2000, '111': 2000}
print(counts)
"""

    passed, details = validate_quantum_source_contract(source, CIRQ_CONTRACT)

    assert not passed
    assert any("execution-derived" in detail.lower() for detail in details)


def test_source_contract_rejects_constant_ifexp_guarded_by_dummy_run() -> None:
    source = """
import cirq

qubits = cirq.LineQubit.range(3)
circuit = cirq.Circuit(cirq.H(qubits[0]))
simulator = cirq.Simulator()
samples = simulator.run(circuit, repetitions=10)
print({'000': 2000, '111': 2000} if samples is not None else {})
"""

    passed, details = validate_quantum_source_contract(source, CIRQ_CONTRACT)

    assert not passed
    assert any("execution-derived" in detail.lower() for detail in details)


def test_source_contract_rejects_constant_reconstructed_by_helper_call() -> None:
    source = """
import json
import cirq

qubits = cirq.LineQubit.range(3)
circuit = cirq.Circuit(cirq.H(qubits[0]))
simulator = cirq.Simulator()
simulator.run(circuit, repetitions=10)
print(json.loads('{"000": 2000, "111": 2000}'))
"""

    passed, details = validate_quantum_source_contract(source, CIRQ_CONTRACT)

    assert not passed
    assert any("execution-derived" in detail.lower() for detail in details)


def test_source_contract_accepts_aliases_and_execution_derived_output() -> None:
    source = """
import cirq as cq

qubits = cq.LineQubit.range(3)
circuit = cq.Circuit(cq.H(qubits[0]))
simulator = cq.Simulator()
samples = simulator.run(circuit, repetitions=10)
counts = samples.histogram(key='m')
print(counts)
"""

    passed, details = validate_quantum_source_contract(source, CIRQ_CONTRACT)

    assert passed, details


def test_generated_stageb_harness_rejects_constant_print_before_execution(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate.py"
    candidate.write_text("print({'000': 2000, '111': 2000})\n", encoding="utf-8")
    harness = tmp_path / "tests.py"
    harness.write_text(
        build_tests(
            "qc-test",
            "concentration",
            {"p_lo": 0.3, "label": "counts", "total_min": 0.6},
            source_contract=CIRQ_CONTRACT,
        ),
        encoding="utf-8",
    )
    spec = importlib.util.spec_from_file_location("generated_stageb_test", harness)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    result = module.run_tests(str(candidate))

    assert result["passed"] is False
    assert any("framework import" in detail for detail in result["details"])


def test_source_contract_derivation_uses_public_framework_roles_only() -> None:
    contract = source_contract_for(
        "Using Cirq, build and simulate a Bell circuit.",
        "import cirq\nprint('reference body is not copied')\n",
    )

    assert contract == CIRQ_CONTRACT
    assert "reference" not in repr(contract).lower()


def test_active_qc0421_harness_rejects_the_observed_stdout_exploit(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate.py"
    candidate.write_text("print({'000': 2000, '111': 2000})\n", encoding="utf-8")
    harness = (
        Path(__file__).resolve().parents[1]
        / "evals/tasks/quantum_distill_sampling/qc-0421/tests.py"
    )
    spec = importlib.util.spec_from_file_location("active_qc0421_test", harness)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    result = module.run_tests(str(candidate))

    assert result["passed"] is False
    assert any("source contract" in detail for detail in result["details"])


def test_every_active_distill_harness_rejects_constant_print_shortcuts(
    tmp_path: Path,
) -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "evals/benchmarks/quantum_grpo_training_v6_runtime30_disjoint.txt"
    task_ids = [
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.startswith("qc-")
    ]
    assert len(task_ids) == 30
    candidate = tmp_path / "candidate.py"
    candidate.write_text("print({'000': 2000, '111': 2000})\n", encoding="utf-8")

    for task_id in task_ids:
        harness = root / f"evals/tasks/quantum_distill_sampling/{task_id}/tests.py"
        spec = importlib.util.spec_from_file_location(
            f"active_{task_id.replace('-', '_')}_test", harness
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.run_tests(str(candidate))
        assert result["passed"] is False, task_id
        assert any("source contract" in detail for detail in result["details"]), task_id
