import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    target = math.cos(1.1)
    c = math.cos(1.1 / 2.0)
    s = math.sin(1.1 / 2.0)

    # --- state preparation: RY(1.1) then RZ(0.8) ---
    sv = None
    try:
        sv = module.statevector()
    except Exception as e:  # noqa: BLE001
        failures.append(f"statevector raised: {e}")
    if sv is not None:
        sv = list(sv)
        if len(sv) != 2:
            failures.append(f"statevector_length={len(sv)}, expected 2")
        else:
            norm = sum(abs(complex(a)) ** 2 for a in sv)
            if abs(norm - 1.0) > 1e-9:
                failures.append(f"statevector_norm={norm:.9f}, expected 1.000000000")
            if abs(abs(complex(sv[0])) - c) > 1e-9:
                failures.append(f"amp_0={abs(complex(sv[0])):.9f}, expected {c:.9f}")
            if abs(abs(complex(sv[1])) - s) > 1e-9:
                failures.append(f"amp_1={abs(complex(sv[1])):.9f}, expected {s:.9f}")
            # relative phase must be e^{i*0.8} (RZ applied second)
            phase = math.atan2(complex(sv[1]).imag, complex(sv[1]).real) - math.atan2(
                complex(sv[0]).imag, complex(sv[0]).real
            )
            if abs(abs(phase) - 0.8) > 1e-9:
                failures.append(f"relative_phase={abs(phase):.9f}, expected 0.800000000")

    # --- teleportation circuit structure: 3 qubits, 2 registers, if_test ---
    circuit = None
    try:
        circuit = module.teleport_circuit()
        nq = len(circuit.qubits)
        if nq != 3:
            failures.append(f"circuit_qubits={nq}, expected 3")
        from qiskit.circuit import IfElseOp

        if_ops = sum(1 for op in circuit.data if isinstance(op.operation, IfElseOp))
        if if_ops != 2:
            failures.append(f"if_test_blocks={if_ops}, expected 2")
    except Exception as e:  # noqa: BLE001
        failures.append(f"teleport_circuit raised: {e}")

    # --- end-to-end run: receiver <Z> within a statistically justified window ---
    result = None
    try:
        result = module.run_teleport()
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_teleport raised: {e}")
    if result is None:
        failures.append(f"receiver_z=0.000000, expected {target:.9f} within 0.040")
    else:
        z = result.get("receiver_z")
        if z is None:
            failures.append(f"receiver_z=0.000000, expected {target:.9f} within 0.040")
        else:
            if abs(float(z) - target) > 0.04:
                failures.append(f"receiver_z={float(z):.9f}, expected {target:.9f} within 0.040")
            if abs(float(z) - target) > 0.023:
                failures.append(
                    f"receiver_z_3sigma={float(z):.9f}, expected {target:.9f} within 0.023"
                )
        shots = result.get("shots")
        if shots != 12000:
            failures.append(f"shots={shots}, expected 12000")
        if result.get("passed") is not True:
            failures.append("run_teleport passed flag must be True for the reference")

    return {
        "passed": not failures,
        "details": failures
        or [
            "teleportation of RZ(0.8)RY(1.1)|0> : receiver <Z> "
            f"{target:.9f} within the seeded 12000-shot statistical window",
        ],
    }
