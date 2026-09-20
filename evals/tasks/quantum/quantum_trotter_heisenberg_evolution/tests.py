import importlib.util

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mat(value):
    return value if isinstance(value, np.ndarray) else None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- Hamiltonian structure: H = J ZZ + h (XI + IX) at J=1, h=0.5 ---
    try:
        H = module.heisenberg_chain_matrix(1.0, 0.5)
    except Exception as e:  # noqa: BLE001
        H = None
        failures.append(f"heisenberg_chain_matrix raised: {e}")
    if _mat(H) is None:
        failures.append("heisenberg_chain_matrix returned non-matrix, expected 4x4")
    else:
        if H.shape != (4, 4):
            failures.append(f"heisenberg_chain_matrix shape={list(H.shape)}, expected [4, 4]")
        else:
            # J ZZ = diag(1, -1, -1, 1); h(XI + IX) has |00><01| etc. couplings.
            if abs(H[0][0] - 1.0) > 1e-9:
                failures.append(f"h_00={float(H[0][0].real):.6f}, expected 1.000000")
            if abs(H[1][1] + 1.0) > 1e-9:
                failures.append(f"h_11={float(H[1][1].real):.6f}, expected -1.000000")
            if abs(H[0][1] - 0.5) > 1e-9:
                failures.append(f"h_01={float(H[0][1].real):.6f}, expected 0.500000")
            if abs(H[2][3] - 0.5) > 1e-9:
                failures.append(f"h_23={float(H[2][3].real):.6f}, expected 0.500000")
            if abs(H[3][3] - 1.0) > 1e-9:
                failures.append(f"h_33={float(H[3][3].real):.6f}, expected 1.000000")

    # --- exact evolution is unitary ---
    try:
        u_exact = module.exact_evolution_matrix(1.0, 0.5, 1.3)
    except Exception as e:  # noqa: BLE001
        u_exact = None
        failures.append(f"exact_evolution_matrix raised: {e}")
    if _mat(u_exact) is not None:
        if u_exact.shape != (4, 4):
            failures.append(f"exact_evolution_matrix shape={list(u_exact.shape)}, expected [4, 4]")
        else:
            unitarity = float(np.max(np.abs(u_exact @ u_exact.conj().T - np.eye(4))))
            if unitarity > 1e-9:
                failures.append(f"exact_unitarity_err={unitarity:.6f}, expected 0.000000")

    # --- Trotter is unitary ---
    trotter_ok = True
    try:
        u_t2 = module.trotter_evolution_matrix(1.0, 0.5, 2.0, 2)
        u_t8 = module.trotter_evolution_matrix(1.0, 0.5, 2.0, 8)
    except Exception as e:  # noqa: BLE001
        u_t2 = u_t8 = None
        trotter_ok = False
        failures.append(f"trotter_evolution_matrix raised: {e}")
    if trotter_ok and (_mat(u_t2) is None or _mat(u_t8) is None):
        trotter_ok = False
        failures.append("trotter_evolution_matrix returned non-matrix, expected 4x4")
    if trotter_ok:
        unitarity_t = float(np.max(np.abs(u_t2 @ u_t2.conj().T - np.eye(4))))
        if unitarity_t > 1e-9:
            failures.append(f"trotter_unitarity_err={unitarity_t:.6f}, expected 0.000000")

    # --- Trotter error decreases with steps and is small at steps=8 ---
    try:
        e2 = module.trotter_max_abs_error(1.0, 0.5, 2.0, 2)
        e8 = module.trotter_max_abs_error(1.0, 0.5, 2.0, 8)
    except Exception as e:  # noqa: BLE001
        e2 = e8 = None
        failures.append(f"trotter_max_abs_error raised: {e}")
    if e2 is None or e8 is None:
        failures.append("max_abs_error=1.000000 need<=0.050000")
    else:
        if e8 > 0.05:
            failures.append(f"max_abs_error={e8:.6f} need<=0.050000")
        if e8 >= e2:
            failures.append(f"error_steps8={e8:.6f} error_steps2={e2:.6f}")

    return {
        "passed": not failures,
        "details": failures or ["Trotterized Ising evolution converges to the exact unitary"],
    }
