import importlib.util

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _exact_ground_reference():
    """Harness-side independent eigensolution of the same Hamiltonian."""
    Z = np.diag([1.0, -1.0]).astype(complex)
    X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    I = np.eye(2, dtype=complex)
    H = 0.5 * np.kron(Z, Z) + 0.8 * np.kron(X, I) + 0.8 * np.kron(I, X) + 0.2 * np.kron(Z, I)
    return float(np.linalg.eigvalsh(H)[0])


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    exact = _exact_ground_reference()

    # --- candidate's exact eigensolution agrees with the harness reference ---
    cand_exact = None
    try:
        cand_exact = float(module.exact_ground_energy())
    except Exception as e:  # noqa: BLE001
        failures.append(f"exact_ground_energy raised: {e}")
    if cand_exact is not None and abs(cand_exact - exact) > 1e-6:
        failures.append(f"exact_energy={cand_exact:.9f}, expected {exact:.9f}")

    # --- variational energy: bound respected and error below 1e-4 ---
    vqe = None
    try:
        vqe = float(module.vqe_energy())
    except Exception as e:  # noqa: BLE001
        failures.append(f"vqe_energy raised: {e}")
    if vqe is None:
        failures.append(f"vqe_energy=0.000000, expected <= {exact + 1e-4:.6f}")
        return {"passed": not failures, "details": failures or ["vqe ok"]}
    if vqe < exact - 1e-8:
        failures.append(f"variational_bound={vqe - exact:.9f}, expected >= -0.000000010")
    err = vqe - exact
    if err > 1e-4:
        failures.append(f"energy_error={err:.9f}, expected <= 0.000100000")
    if vqe > 0.0:
        failures.append(f"vqe_energy={vqe:.6f}, expected < 0.000000")

    # --- ansatz shape: three layers -> 12 parameters, deterministic starts ---
    try:
        starts = module.restart_starts(seed_base=0)
        n_starts = len(starts) if starts is not None else 0
    except Exception as e:  # noqa: BLE001
        n_starts = 0
        failures.append(f"restart_starts raised: {e}")
    if n_starts < 6:
        failures.append(f"restarts={n_starts}, expected >= 6")
    if starts:
        p0 = np.asarray(starts[0])
        if p0.size != 12:
            failures.append(f"ansatz_params={p0.size}, expected 12")
        else:
            p1 = np.asarray(starts[1])
            if np.allclose(p0, p1):
                failures.append("restart_determinism=0, expected distinct starts")

    return {
        "passed": not failures,
        "details": failures
        or [
            "VQE H=0.5 Z0Z1+0.8X0+0.8X1+0.2Z0: best energy "
            f"{vqe:.6f} vs exact {exact:.6f}, variational bound held, "
            "error < 1e-4, 6 deterministic restarts of the 3-layer ansatz",
        ],
    }
