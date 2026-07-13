from __future__ import annotations

import json

import pytest

from quantum_ir import (
    IRValidationError,
    QuantumProgramIR,
    collect_validation_errors,
    loads_quantum_ir,
    parse_quantum_ir,
    validate_quantum_ir_dict,
)


def _bell_ir_dict() -> dict:
    return {
        "schema_version": "quantum-ir-v1",
        "program_id": "bell_pair",
        "description": "Prepare and measure a Bell pair.",
        "qubits": [{"name": "q", "size": 2}],
        "classical_bits": [{"name": "c", "size": 2}],
        "parameters": [{"name": "theta", "value": "pi/2", "unit": "radian"}],
        "operations": [
            {"op_type": "gate", "name": "h", "targets": ["q[0]"]},
            {"op_type": "gate", "name": "cx", "controls": ["q[0]"], "targets": ["q[1]"]},
            {
                "op_type": "measurement",
                "name": "measure",
                "targets": ["q[0]", "q[1]"],
                "classical_targets": ["c[0]", "c[1]"],
            },
        ],
        "measurements": [
            {"qubit": "q[0]", "classical_bit": "c[0]"},
            {"qubit": "q[1]", "classical_bit": "c[1]"},
        ],
        "subcircuits": [
            {
                "name": "entangle",
                "qubits": [{"name": "sq", "size": 2}],
                "operations": [
                    {"op_type": "gate", "name": "h", "targets": ["sq[0]"]},
                    {"op_type": "gate", "name": "cx", "controls": ["sq[0]"], "targets": ["sq[1]"]},
                ],
            }
        ],
        "constraints": [
            {"kind": "hardware", "expression": "use only single-qubit gates and cx"},
        ],
        "target": {
            "framework": "qiskit",
            "version": "1.x",
            "backend": "aer_simulator",
            "output_format": "sdk",
        },
        "test_entrypoints": [
            {"name": "pytest", "command": "python -m pytest tests/test_bell.py"},
        ],
        "verification_requirements": [
            {
                "name": "simulate_counts",
                "method": "shot_counts",
                "external_tool": "qiskit-aer",
                "acceptance_criteria": ["counts are produced by the simulator"],
            }
        ],
        "repair_records": [
            {
                "source": "external_tool",
                "tool_name": "pytest",
                "message": "Initial smoke test passed.",
                "numeric_results": {"passed": 1, "failed": 0},
            }
        ],
        "metadata": {"source": "unit-test"},
    }


def test_parse_quantum_ir_accepts_complete_task3_shape() -> None:
    ir = parse_quantum_ir(_bell_ir_dict())

    assert isinstance(ir, QuantumProgramIR)
    assert ir.program_id == "bell_pair"
    assert ir.qubits[0].name == "q"
    assert ir.operations[1].controls == ("q[0]",)
    assert ir.measurements[1].classical_bit == "c[1]"
    assert ir.subcircuits[0].name == "entangle"
    assert ir.target.framework == "qiskit"
    assert ir.verification_requirements[0].external_tool == "qiskit-aer"


def test_to_dict_round_trips_through_json() -> None:
    ir = parse_quantum_ir(_bell_ir_dict())
    rendered = json.dumps(ir.to_dict(), sort_keys=True)

    reparsed = loads_quantum_ir(rendered)

    assert reparsed == ir


def test_gate_sequence_alias_is_accepted_for_model_facing_payloads() -> None:
    payload = _bell_ir_dict()
    payload["gate_sequence"] = payload.pop("operations")

    ir = parse_quantum_ir(payload)

    assert [operation.name for operation in ir.operations] == ["h", "cx", "measure"]


def test_validation_rejects_unknown_register_references() -> None:
    payload = _bell_ir_dict()
    payload["operations"][0]["targets"] = ["missing[0]"]

    with pytest.raises(IRValidationError, match="unknown register 'missing'"):
        validate_quantum_ir_dict(payload)


def test_validation_rejects_out_of_range_bit_references() -> None:
    payload = _bell_ir_dict()
    payload["measurements"][1]["classical_bit"] = "c[2]"

    with pytest.raises(IRValidationError, match="index 2 out of range"):
        parse_quantum_ir(payload)


def test_call_operations_must_reference_declared_subcircuits() -> None:
    payload = _bell_ir_dict()
    payload["operations"].insert(
        0,
        {"op_type": "call", "name": "apply_unknown", "subcircuit": "unknown", "targets": ["q[0]"]},
    )

    with pytest.raises(IRValidationError, match="unknown subcircuit 'unknown'"):
        parse_quantum_ir(payload)


def test_measurement_operations_require_classical_targets() -> None:
    payload = _bell_ir_dict()
    del payload["operations"][2]["classical_targets"]

    with pytest.raises(IRValidationError, match="measurement operations require"):
        parse_quantum_ir(payload)


def test_verification_numeric_results_are_not_allowed_in_model_metadata() -> None:
    payload = _bell_ir_dict()
    payload["verification_requirements"][0]["metadata"] = {
        "observed_result": {"counts": {"00": 512, "11": 512}},
    }

    with pytest.raises(IRValidationError, match="observed numeric results"):
        parse_quantum_ir(payload)


def test_repair_numeric_results_require_external_or_validator_source() -> None:
    payload = _bell_ir_dict()
    payload["repair_records"] = [
        {
            "source": "model",
            "message": "I think the simulated fidelity is high.",
            "numeric_results": {"fidelity": 0.99},
        }
    ]

    with pytest.raises(IRValidationError, match="numeric results must come from"):
        parse_quantum_ir(payload)


def test_external_numeric_repair_results_require_tool_name() -> None:
    payload = _bell_ir_dict()
    payload["repair_records"] = [
        {
            "source": "external_tool",
            "message": "Tool produced counts.",
            "numeric_results": {"shots": 1024},
        }
    ]

    with pytest.raises(IRValidationError, match="tool_name"):
        parse_quantum_ir(payload)


def test_collect_validation_errors_returns_strings_for_json_callers() -> None:
    payload = _bell_ir_dict()
    payload["qubits"] = []

    errors = collect_validation_errors(payload)

    assert len(errors) == 1
    assert "$.qubits" in errors[0]
