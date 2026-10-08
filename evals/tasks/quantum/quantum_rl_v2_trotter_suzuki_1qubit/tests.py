import importlib.util

import numpy as np
from scipy.linalg import expm

X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
I2 = np.eye(2, dtype=complex)


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mat(value):
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], (list, tuple)):
        return np.asarray(value, dtype=complex)
    if isinstance(value, np.ndarray):
        return value
    return None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    a, b, t, n = 0.9, 0.9, 1.1, 8
    ue_ref = expm(-1j * (a * X + b * Z) * t)

    # --- exact evolution matches scipy/numpy expm directly ---
    ue = _mat(module.exact_unitary(a, b, t))
    if ue is None:
        failures.append("exact_unitary missing, expected 2x2")
    elif ue.shape != (2, 2):
        failures.append(f"exact_shape={ue.shape[0]}x{ue.shape[1]}, expected 2x2")
    else:
        err = float(np.linalg.norm(ue - ue_ref) / 2.0)
        if err > 1e-9:
            failures.append(f"exact_error={err:.12f}, expected 0.000000000000")

    # --- first-order and second-order unitaries ---
    u1 = _mat(module.first_order_trotter(a, b, t, n))
    u2 = _mat(module.second_order_suzuki(a, b, t, n))
    if u1 is None:
        failures.append("first_order_trotter missing, expected 2x2")
    elif u1.shape != (2, 2):
        failures.append(f"first_shape={u1.shape[0]}x{u1.shape[1]}, expected 2x2")
    if u2 is None:
        failures.append("second_order_suzuki missing, expected 2x2")
    elif u2.shape != (2, 2):
        failures.append(f"second_shape={u2.shape[0]}x{u2.shape[1]}, expected 2x2")

    unitary_ok = 0
    for name, u in (("first", u1), ("second", u2)):
        if _mat(u) is not None and u.shape == (2, 2):
            if np.allclose(u.conj().T @ u, I2, atol=1e-9):
                unitary_ok += 1
    if unitary_ok != 2:
        failures.append(f"unitary_approximations={unitary_ok}, expected 2")

    # --- errors and ordering: e2 must be clearly < e1 for this instance ---
    # Independent reference: symmetric second-order Suzuki with the SAME
    # instance parameters, recomputed in the harness (not from the candidate).
    u2_ref = np.eye(2, dtype=complex)
    dt = t / n
    ux_ref = expm(-1j * a * X * dt)
    uz2_ref = expm(-1j * b * Z * dt / 2.0)
    step_ref = uz2_ref @ ux_ref @ uz2_ref
    for _ in range(n):
        u2_ref = u2_ref @ step_ref
    e2_true = float(np.linalg.norm(u2_ref - ue_ref) / 2.0)
    if u1 is not None and u2 is not None and ue is not None:
        try:
            e1 = float(module.frobenius_error(u1, ue))
            e2 = float(module.frobenius_error(u2, ue))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"frobenius_error raised: {exc}")
            e1 = e2 = None
        if e1 is not None:
            if e1 <= 0.0 or e1 > 1.0:
                failures.append(f"first_error={e1:.6f}, expected in (0, 1]")
            if e2 is not None:
                if not e2 < e1 / 4.0:  # 4x margin; true ratio is ~20x
                    failures.append(
                        f"second_error={e2:.6f} >= first_error/4={e1 / 4.0:.6f}, "
                        "expected symmetric-splitting improvement"
                    )
                if abs(e2 - e2_true) > 0.5 * e2_true:
                    failures.append(f"second_error={e2:.6f}, expected {e2_true:.6f}")
        if e2 is not None and e2 > 0.5:
            failures.append(f"second_error={e2:.6f}, expected <= 0.500000")

    # --- state fidelities from |0> ---
    if u1 is not None and u2 is not None:
        try:
            f1 = float(module.fidelity_from_zero(u1))
            f2 = float(module.fidelity_from_zero(u2))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"fidelity_from_zero raised: {exc}")
            f1 = f2 = None
        if f1 is not None:
            if not (0.0 <= f1 <= 1.0):
                failures.append(f"fidelity_1st={f1:.6f}, expected in [0, 1]")
            if f2 is not None and f2 <= f1:
                failures.append(f"fidelity_2nd={f2:.6f} <= fidelity_1st={f1:.6f}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "H=0.9X+0.9Z, t=1.1, n=8: exact expm matched, both approximations "
            "unitary, second-order Frobenius error < first-order error",
        ],
    }
