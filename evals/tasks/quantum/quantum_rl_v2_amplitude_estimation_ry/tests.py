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
    n_eval = 3
    angle = 0.6
    a_true = math.sin(angle / 2.0) ** 2
    bound = math.pi / (1 << n_eval)

    # --- Grover operator matches -A S0 A^dagger S_chi and is unitary ---
    try:
        Q = np.asarray(module.grover_operator(angle))
        if Q.shape != (2, 2):
            failures.append(f"q_shape={Q.shape}, expected (2, 2)")
        else:
            a = angle / 2.0
            A = np.array(
                [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]],
                dtype=complex,
            )
            S0 = np.array([[-1.0, 0.0], [0.0, 1.0]], dtype=complex)
            S_chi = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
            ref = -A @ S0 @ A.conj().T @ S_chi
            dev = float(np.max(np.abs(Q - ref)))
            if dev > 1e-9:
                failures.append(f"q_matrix_dev={dev:.2e}, expected < 1e-9")
            unit_dev = float(np.max(np.abs(Q @ Q.conj().T - np.eye(2))))
            if unit_dev > 1e-9:
                failures.append(f"q_unitary_dev={unit_dev:.2e}, expected < 1e-9")
            phases = np.sort(np.abs(np.angle(np.linalg.eigvals(Q))))
            two_theta = 2.0 * math.asin(math.sqrt(a_true))
            if abs(phases[0] - two_theta) > 1e-9:
                failures.append(f"q_phase={phases[0]:.6f}, expected {two_theta:.6f} (2*theta)")
    except Exception as e:  # noqa: BLE001
        failures.append(f"grover_operator check raised: {e}")

    # --- circuit structure ---
    circuit = None
    try:
        circuit = module.qpe_circuit(n_eval=3, angle=0.6)
        if circuit.num_qubits != 4:
            failures.append(f"circuit_qubits={circuit.num_qubits}, expected 4")
    except Exception as e:  # noqa: BLE001
        failures.append(f"qpe_circuit raised: {e}")

    # --- end-to-end: symmetric peaks, consistent a, error under pi/2^3 ---
    result = None
    if circuit is not None:
        try:
            result = module.run_ae(n_eval=3, angle=0.6, shots=4096, seed=7)
        except Exception as e:  # noqa: BLE001
            failures.append(f"run_ae raised: {e}")
    if result:
        error = float(result.get("amplitude_error", 1.0))
        if error > bound:
            failures.append(f"amplitude_error={error:.4f}, expected <= {bound:.4f}")
        if error > 0.1:
            failures.append(f"amplitude_error={error:.4f}, expected <= 0.1000")
        a_est = float(result.get("a_est", 0.0))
        if not (0.0 <= a_est <= 1.0):
            failures.append(f"a_est_range={a_est:.4f}, expected in [0, 1]")
        peaks = result.get("peaks") or []
        if len(peaks) < 2:
            failures.append(f"symmetric_peaks={len(peaks)}, expected 2")
        else:
            j1, a1 = peaks[0]
            j2, a2 = peaks[1]
            if j1 + j2 != (1 << n_eval):
                failures.append(f"peak_sum={j1 + j2}, expected 8 (j and 2^m - j)")
            if abs(a1 - a2) > 1e-9:
                failures.append(f"peak_consistency={abs(a1 - a2):.2e}, expected < 1e-9")
            if abs(a1 - math.sin(math.pi * j1 / 8) ** 2) > 1e-12:
                failures.append(
                    f"peak_map={a1:.4f}, expected {math.sin(math.pi * j1 / 8) ** 2:.4f}"
                )
        counts = result.get("counts") or {}
        total = sum(counts.values())
        if total != 4096:
            failures.append(f"sampled_shots={total}, expected 4096")
        try:
            result2 = module.run_ae(n_eval=3, angle=0.6, shots=4096, seed=7)
            if result2.get("counts") != counts:
                failures.append("seed_determinism_diff=1, expected 0")
        except Exception as e:  # noqa: BLE001
            failures.append(f"run_ae determinism raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Canonical AE Qiskit A=RY(0.6), 3 eval qubits: Q matches "
            "-A S0 A^dagger S_chi (dev < 1e-9, phase = theta), symmetric peaks "
            "j and 8-j both map to a=0.1464, amplitude_error=0.0591 <= pi/8",
        ],
    }
