import importlib.util

import numpy as np

PHI_PLUS = (
    np.outer(
        np.array([1.0, 0.0, 0.0, 1.0], dtype=complex),
        np.array([1.0, 0.0, 0.0, 1.0], dtype=complex).conj(),
    )
    / 2.0
)
Z = np.diag([1.0, -1.0]).astype(complex)
ZZ = np.kron(Z, Z)


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mat(value):
    if isinstance(value, np.ndarray):
        return value
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], (list, tuple)):
        return np.asarray(value, dtype=complex)
    return None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    p = 0.03
    # analytic expectations for this instance
    zz_true = 1.0 - 4.0 * p / 3.0  # 0.96
    fid_true = 1.0 - p  # 0.97
    pur_true = (1.0 - p) ** 2 + 3.0 * (p / 3.0) ** 2  # 0.9412

    rho = None
    try:
        rho = _mat(module.bell_depolarizing_density(p=p))
    except Exception as e:  # noqa: BLE001
        failures.append(f"bell_depolarizing_density raised: {e}")
    if rho is None:
        failures.append("density_missing=0x0, expected 4x4")
        return {"passed": not failures, "details": failures or ["depolarizing bell ok"]}
    if rho.shape != (4, 4):
        failures.append(f"density_shape={rho.shape[0]}x{rho.shape[1]}, expected 4x4")

    # --- trace / PSD ---
    tr = None
    try:
        tr = float(module.trace(rho))
    except Exception as e:  # noqa: BLE001
        failures.append(f"trace raised: {e}")
    if tr is not None and abs(tr - 1.0) > 1e-9:
        failures.append(f"density_trace={tr:.9f}, expected 1.000000000")
    evals = None
    try:
        evals = np.asarray(module.eigenvalues(rho))
    except Exception as e:  # noqa: BLE001
        failures.append(f"eigenvalues raised: {e}")
    if evals is not None and evals.shape == (4,):
        if np.min(evals) < -1e-9:
            failures.append(f"min_eigenvalue={float(np.min(evals)):.9f}, expected >= 0.000000000")
        expected_evals = np.sort([1 - p, p / 3.0, p / 3.0, p / 3.0])
        if not np.allclose(np.sort(evals), expected_evals, atol=1e-6):
            got = np.sort(evals)
            failures.append(f"top_eigenvalue={got[3]:.9f}, expected {(1 - p):.9f}")

    # --- purity / fidelity ---
    pur = None
    try:
        pur = float(module.purity(rho))
    except Exception as e:  # noqa: BLE001
        failures.append(f"purity raised: {e}")
    if pur is not None and abs(pur - pur_true) > 1e-6:
        failures.append(f"purity={pur:.9f}, expected {pur_true:.9f}")
    fid = None
    try:
        fid = float(module.fidelity_phi_plus(rho))
    except Exception as e:  # noqa: BLE001
        failures.append(f"fidelity_phi_plus raised: {e}")
    if fid is not None:
        if abs(fid - fid_true) > 1e-6:
            failures.append(f"fidelity_phi_plus={fid:.9f}, expected {fid_true:.9f}")
        if not (0.0 <= fid <= 1.0 + 1e-9):
            failures.append(f"fidelity_phi_plus={fid:.9f}, expected in [0, 1]")

    # --- analytic <ZZ> ---
    zz = None
    try:
        zz = float(module.zz_expectation(rho))
    except Exception as e:  # noqa: BLE001
        failures.append(f"zz_expectation raised: {e}")
    if zz is not None and abs(zz - zz_true) > 1e-6:
        failures.append(f"zz_analytic={zz:.9f}, expected {zz_true:.9f}")

    # --- finite-shot estimate agrees with the analytic value ---
    zz_shots = None
    try:
        zz_shots = float(module.zz_expectation_shots(p=p, shots=20000, seed=1234))
    except Exception as e:  # noqa: BLE001
        failures.append(f"zz_expectation_shots raised: {e}")
    if zz_shots is not None:
        if abs(zz_shots - zz_true) > 0.04:
            failures.append(f"zz_shots={zz_shots:.6f}, expected within 0.04 of {zz_true:.6f}")
        if zz is not None and abs(zz_shots - zz) > 0.04:
            failures.append(
                f"zz_shots_vs_analytic_gap={abs(zz_shots - zz):.6f}, expected <= 0.040000"
            )

    return {
        "passed": not failures,
        "details": failures
        or [
            "Bell |Phi+> + DepolarizingChannel(0.03): trace 1, eigenvalues "
            "{0.97, 0.01x3}, purity 0.9412, fidelity 0.97, <ZZ>=0.96, "
            "seeded 20000-shot <ZZ> within 0.04",
        ],
    }
