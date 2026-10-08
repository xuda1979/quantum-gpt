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
    theta1, theta2 = 0.4, 1.7
    analytic = float(np.cos((theta1 - theta2) / 2.0) ** 2)  # 0.633749...

    # --- circuit structure: 3 qubits, 1 measured ancilla, CSWAP present ---
    qc = None
    try:
        qc = module.swap_test_circuit(theta1, theta2)
    except Exception as e:  # noqa: BLE001
        failures.append(f"swap_test_circuit raised: {e}")
    if qc is not None:
        if qc.num_qubits != 3:
            failures.append(f"circuit_qubits={qc.num_qubits}, expected 3")
        ops = qc.count_ops()
        if ops.get("measure", 0) != 1:
            failures.append(f"measurement_count={ops.get('measure', 0)}, expected 1")
        if ops.get("cswap", 0) != 1:
            failures.append(f"cswap_count={ops.get('cswap', 0)}, expected 1")
        if ops.get("h", 0) != 2:
            failures.append(f"h_count={ops.get('h', 0)}, expected 2")

    # --- analytic value: cos^2((0.4-1.7)/2) ---
    a = None
    try:
        a = float(module.analytic_overlap_sq(theta1, theta2))
    except Exception as e:  # noqa: BLE001
        failures.append(f"analytic_overlap_sq raised: {e}")
    if a is not None:
        if abs(a - analytic) > 1e-12:
            failures.append(f"analytic_overlap={a:.12f}, expected {analytic:.12f}")

    # --- exact statevector: P(ancilla=0) = (1 + analytic)/2 ---
    p0 = None
    try:
        p0 = float(module.exact_ancilla_zero_probability(theta1, theta2))
    except Exception as e:  # noqa: BLE001
        failures.append(f"exact_ancilla_zero_probability raised: {e}")
    if p0 is not None:
        expected_p0 = (1.0 + analytic) / 2.0
        if abs(p0 - expected_p0) > 1e-9:
            failures.append(f"exact_p0={p0:.9f}, expected {expected_p0:.9f}")
        if p0 <= 0.5:
            failures.append(f"exact_p0={p0:.9f}, expected > 0.500000000")

    # --- shot estimate: 20000 shots, seed 31415, error < 0.025 ---
    est = None
    try:
        est = float(module.estimate_overlap_sq(20000, 31415, theta1, theta2))
    except Exception as e:  # noqa: BLE001
        failures.append(f"estimate_overlap_sq raised: {e}")
    if est is not None:
        if not (-1.0 <= est <= 1.0):
            failures.append(f"estimate_out_of_range={est:.6f}, expected within [-1, 1]")
        err = abs(est - analytic)
        if err >= 0.025:
            failures.append(f"swap_test_error={err:.6f}, expected < 0.025000")
    # determinism: same seed, same estimate
    try:
        est2 = float(module.estimate_overlap_sq(20000, 31415, theta1, theta2))
        if est is not None and abs(est - est2) > 1e-12:
            failures.append(f"seed_determinism_deviation={abs(est - est2):.3e}, expected 0.0")
    except Exception as e:  # noqa: BLE001
        failures.append(f"determinism re-run raised: {e}")

    # --- swap_test_error helper ---
    try:
        err2 = float(module.swap_test_error(20000, 31415))
        if err2 is not None and err2 >= 0.025:
            failures.append(f"swap_test_error={err2:.6f}, expected < 0.025000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"swap_test_error raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "SWAP test on RY(0.4)|0> and RY(1.7)|0>: exact P(0) = "
            "(1+cos^2(0.65))/2 and the 20000-shot seeded estimate agree "
            "with cos^2((0.4-1.7)/2) = 0.6337 within 0.025"
        ],
    }
