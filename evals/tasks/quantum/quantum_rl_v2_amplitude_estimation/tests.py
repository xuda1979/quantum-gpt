import importlib.util
import math

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    true = math.sin(0.35)
    bound = math.pi / 16.0

    # --- A = RY(0.7): |0> -> cos(0.35)|0> + sin(0.35)|1> ---
    try:
        from qiskit.quantum_info import Statevector

        sv = np.asarray(Statevector(module.amplitude_operator()))
        if abs(abs(complex(sv[0])) - math.cos(0.35)) > 1e-9:
            failures.append(f"a_amp_0={abs(complex(sv[0])):.9f}, expected {math.cos(0.35):.9f}")
        if abs(abs(complex(sv[1])) - math.sin(0.35)) > 1e-9:
            failures.append(f"a_amp_1={abs(complex(sv[1])):.9f}, expected {math.sin(0.35):.9f}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"amplitude_operator raised: {e}")

    # --- Q must be a unitary on one qubit ---
    try:
        from qiskit.quantum_info import Operator

        q_op = Operator(module.q_operator())
        if not q_op.is_unitary():
            failures.append("q_unitary=0, expected 1")
        if q_op.dim[0] != 2:
            failures.append(f"q_dim={q_op.dim[0]}, expected 2")
    except Exception as e:  # noqa: BLE001
        failures.append(f"q_operator raised: {e}")

    # --- QPE circuit: 4 evaluation + 1 state qubit, 4 clbits ---
    try:
        circuit = module.qpe_circuit()
        if len(circuit.qubits) != 5:
            failures.append(f"circuit_qubits={len(circuit.qubits)}, expected 5")
        if len(circuit.clbits) != 4:
            failures.append(f"circuit_clbits={len(circuit.clbits)}, expected 4")
    except Exception as e:  # noqa: BLE001
        failures.append(f"qpe_circuit raised: {e}")

    # --- phase peaks are symmetric ---
    peaks = None
    try:
        peaks = module.phase_peaks()
    except Exception as e:  # noqa: BLE001
        failures.append(f"phase_peaks raised: {e}")
    if peaks is None:
        failures.append("phase_peaks=None, expected two symmetric peaks")
    else:
        k = peaks.get("peak_k")
        sym = peaks.get("symmetric_k")
        if k is None or sym is None:
            failures.append("phase_peaks missing peak_k/symmetric_k")
        else:
            if (int(k) + int(sym)) != 16 and abs(int(k) - int(sym)) != 16:
                failures.append(
                    f"symmetric_k={sym}, expected 16 - peak_k={16 - int(k) if k else 0}"
                )
            # both peaks must map to the same amplitude: sin(pi k/16)
            a_k = math.sin(math.pi * int(k) / 16.0)
            a_sym = math.sin(math.pi * int(sym) / 16.0)
            if abs(a_k - a_sym) > 1e-12:
                failures.append(f"peak_amplitude_mismatch={abs(a_k - a_sym):.3e}, expected 0.0")
        pk = peaks.get("peak_probability")
        ps = peaks.get("symmetric_probability")
        if pk is not None and ps is not None and abs(float(pk) - float(ps)) > 1e-6:
            failures.append(
                f"peak_probability_diff={abs(float(pk) - float(ps)):.3e}, " "expected <= 1.0e-6"
            )

    # --- amplitude error bounded by pi/2**4 ---
    result = None
    try:
        result = module.run_amplitude_estimation()
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_amplitude_estimation raised: {e}")
    if result is None:
        failures.append(f"amplitude_error=1.000000, expected <= {bound:.6f}")
    else:
        estimate = result.get("estimate")
        if estimate is None:
            failures.append(f"amplitude_estimate=0.000000, expected {true:.6f}")
        else:
            err = abs(float(estimate) - true)
            if err > bound:
                failures.append(f"amplitude_error={err:.6f}, expected <= {bound:.6f}")
            if err > 0.05:
                failures.append(f"amplitude_error={err:.6f}, expected <= 0.050000")
        est_true = result.get("true")
        if est_true is None or abs(float(est_true) - true) > 1e-9:
            failures.append(f"true_amplitude={est_true}, expected {true:.9f}")
        b = result.get("bound")
        if b is None or abs(float(b) - bound) > 1e-9:
            failures.append(f"bound={b}, expected {bound:.9f}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "canonical amplitude estimation (qiskit, 4 evaluation qubits) on "
            "A=RY(0.7): Q unitary, symmetric phase peaks, amplitude error "
            f"{abs((result or {}).get('estimate', 0) - true):.4f} <= pi/16",
        ],
    }
