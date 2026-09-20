import importlib.util

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

    # --- sign convention: 8 correlators, XXXX +, YYYY -, six 2-Y terms + ---
    conv = None
    try:
        conv = module.mabk_sign_convention()
    except Exception as e:  # noqa: BLE001
        failures.append(f"mabk_sign_convention raised: {e}")
    if conv is None or not isinstance(conv, dict):
        failures.append("convention_entries=0, expected 8")
    else:
        if len(conv) != 8:
            failures.append(f"convention_entries={len(conv)}, expected 8")
        if "XXXX" not in conv or conv.get("XXXX") != 1.0:
            failures.append(f"convention_XXXX={conv.get('XXXX')}, expected 1.0")
        if "YYYY" not in conv or conv.get("YYYY") != -1.0:
            failures.append(f"convention_YYYY={conv.get('YYYY')}, expected -1.0")
        two_y = [k for k in conv if k not in ("XXXX", "YYYY")]
        if len(two_y) != 6:
            failures.append(f"two_y_term_count={len(two_y)}, expected 6")
        if two_y and any(conv[k] != 1.0 for k in two_y):
            bad = [k for k in two_y if conv[k] != 1.0]
            failures.append(f"two_y_sign_wrong={bad}, expected all +1.0")

    # --- circuit: 4 qubits, 1 H + 3 CX ---
    qc = None
    try:
        qc = module.ghz4_circuit()
    except Exception as e:  # noqa: BLE001
        failures.append(f"ghz4_circuit raised: {e}")
    if qc is not None:
        if qc.num_qubits != 4:
            failures.append(f"circuit_qubits={qc.num_qubits}, expected 4")
        ops = qc.count_ops()
        if ops.get("cx", 0) != 3:
            failures.append(f"cx_count={ops.get('cx', 0)}, expected 3")

    # --- GHZ4 fidelity ---
    try:
        from qiskit.quantum_info import Statevector, state_fidelity

        ideal = Statevector(
            np.array([1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0]) / np.sqrt(2.0)
        )
        f = float(state_fidelity(Statevector(qc), ideal))
        if abs(f - 1.0) > 1e-9:
            failures.append(f"ghz4_fidelity={f:.9f}, expected 1.000000000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"fidelity check raised: {e}")

    # --- eight correlators: XXXX/YYYY = +1, two-Y terms = -1 ---
    corr = None
    try:
        corr = [float(v) for v in module.mabk_correlators()]
    except Exception as e:  # noqa: BLE001
        failures.append(f"mabk_correlators raised: {e}")
    if corr is not None:
        if len(corr) != 8:
            failures.append(f"correlator_count={len(corr)}, expected 8")
        else:
            labels = (
                list(module.mabk_sign_convention())
                if isinstance(module.mabk_sign_convention(), dict)
                else []
            )
            for label, v in zip(labels, corr):
                expected = 1.0 if label in ("XXXX", "YYYY") else -1.0
                if abs(v - expected) > 1e-9:
                    failures.append(f"{label.lower()}_correlator={v:.9f}, expected {expected:.1f}")

    # --- quantum value: |M4| = 3 ---
    m = None
    try:
        m = float(module.mabk_value())
    except Exception as e:  # noqa: BLE001
        failures.append(f"mabk_value raised: {e}")
    if m is not None:
        if abs(abs(m) - 3.0) > 1e-9:
            failures.append(f"mabk_value={m:.9f}, expected -3.000000000")

    # --- direct matrix cross-check ---
    m2 = None
    try:
        m2 = float(module.mabk_value_matrix())
    except Exception as e:  # noqa: BLE001
        failures.append(f"mabk_value_matrix raised: {e}")
    if m is not None and m2 is not None and abs(m - m2) > 1e-9:
        failures.append(f"matrix_mismatch={abs(m - m2):.9f}, expected 0.000000000")

    # --- violation over the LHV bound 2*sqrt(2) ---
    v = None
    try:
        v = float(module.mabk_violation())
    except Exception as e:  # noqa: BLE001
        failures.append(f"mabk_violation raised: {e}")
    if v is not None:
        expected_v = 3.0 - 2.0 * np.sqrt(2.0)
        if abs(v - expected_v) > 1e-9:
            failures.append(f"violation={v:.9f}, expected {expected_v:.9f}")
        if v <= 0.0:
            failures.append(f"violation={v:.9f}, expected > 0.000000000")

    return {
        "passed": not failures,
        "details": failures
        or [
            "4-party MABK witness M4 = -3 on |GHZ4> (|M4| = 3 > 2*sqrt(2)), "
            "eight correlators and matrix cross-check exact"
        ],
    }
