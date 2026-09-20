import importlib.util

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _float(v):
    try:
        return float(v)
    except Exception:  # noqa: BLE001
        return None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- circuit: 3 qubits, H + CX(0,1) + CX(0,2) ---
    qc = None
    try:
        qc = module.ghz_circuit()
    except Exception as e:  # noqa: BLE001
        failures.append(f"ghz_circuit raised: {e}")
    if qc is not None:
        if qc.num_qubits != 3:
            failures.append(f"circuit_qubits={qc.num_qubits}, expected 3")
        ops = qc.count_ops()
        if ops.get("cx", 0) != 2:
            failures.append(f"cx_count={ops.get('cx', 0)}, expected 2")
        if ops.get("h", 0) != 1:
            failures.append(f"h_count={ops.get('h', 0)}, expected 1")

    # --- GHZ state fidelity ---
    sv = None
    try:
        sv = module.ghz_circuit()
        from qiskit.quantum_info import Statevector, state_fidelity

        ideal = Statevector(np.array([1.0, 0, 0, 0, 0, 0, 0, 1.0]) / np.sqrt(2.0))
        f = float(state_fidelity(Statevector(sv), ideal))
        if abs(f - 1.0) > 1e-9:
            failures.append(f"ghz_fidelity={f:.9f}, expected 1.000000000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"state fidelity check raised: {e}")

    # --- four correlators: +1, -1, -1, -1 ---
    corr = None
    try:
        corr = [float(v) for v in module.mabk_correlators()]
    except Exception as e:  # noqa: BLE001
        failures.append(f"mabk_correlators raised: {e}")
    if corr is not None:
        if len(corr) != 4:
            failures.append(f"correlator_count={len(corr)}, expected 4")
        else:
            expected = [1.0, -1.0, -1.0, -1.0]
            names = ["XXX", "XYY", "YXY", "YYX"]
            for name, got, exp in zip(names, corr, expected):
                if abs(got - exp) > 1e-9:
                    failures.append(f"{name.lower()}_correlator={got:.9f}, expected {exp:.1f}")

    # --- MABK value: M = 4 ---
    m = None
    try:
        m = _float(module.mabk_value())
    except Exception as e:  # noqa: BLE001
        failures.append(f"mabk_value raised: {e}")
    if m is not None:
        if abs(m - 4.0) > 1e-9:
            failures.append(f"mabk_value={m:.9f}, expected 4.000000000")
        if m <= 2.0:
            failures.append(f"mabk_value={m:.9f}, expected > 2.000000000")

    # --- direct matrix cross-check ---
    m2 = None
    try:
        m2 = _float(module.mabk_value_matrix())
    except Exception as e:  # noqa: BLE001
        failures.append(f"mabk_value_matrix raised: {e}")
    if m is not None and m2 is not None:
        if abs(m - m2) > 1e-9:
            failures.append(f"matrix_mismatch={abs(m - m2):.9f}, expected 0.000000000")
    if m2 is not None and abs(m2 - 4.0) > 1e-9:
        failures.append(f"matrix_mabk={m2:.9f}, expected 4.000000000")

    # --- witness violation helper ---
    try:
        v = _float(module.witness_violation())
        if v is not None and v <= 0.0:
            failures.append(f"witness_violation={v:.9f}, expected > 0.000000000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"witness_violation raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "MABK witness M = <XXX>-<XYY>-<YXY>-<YYX> = 4 on the 3-qubit GHZ "
            "state, estimator and matrix calculations agree exactly"
        ],
    }
