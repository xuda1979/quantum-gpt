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

    # --- Hamiltonian parameters: 2x1 spinful, t=1, U=2, periodic=False ---
    h = None
    try:
        h = module.hamiltonian()
    except Exception as e:  # noqa: BLE001
        failures.append(f"hamiltonian raised: {e}")
    if h is not None:
        try:
            terms = list(h.terms.items())
        except Exception:  # noqa: BLE001
            terms = None
        if terms is None or len(terms) == 0:
            failures.append("hamiltonian_terms=0, expected > 0 Jordan-Wigner terms")
        else:
            coeffs = [abs(complex(c)) for _, c in terms]
            if max(coeffs) < 1.9 or max(coeffs) > 2.1:
                failures.append(f"max_coefficient={max(coeffs):.6f}, expected 2.000000 (onsite U)")
            if 0.9 <= min(coeffs) <= 1.1 or any(0.9 <= c <= 1.1 for c in coeffs):
                pass  # tunneling t=1.0 present
            else:
                failures.append("tunneling_term_missing=1, expected 1.0 hopping coefficient")

    # --- sparse matrix: explicit qubit count 4, dim 16, Hermitian ---
    hmat = None
    try:
        hmat = module.sparse_matrix()
    except Exception as e:  # noqa: BLE001
        failures.append(f"sparse_matrix raised: {e}")
    if hmat is not None:
        dim = hmat.shape[0]
        if dim != 16:
            failures.append(f"matrix_dim={dim}, expected 16")
        if hmat.shape[1] != 16:
            failures.append(f"matrix_dim2={hmat.shape[1]}, expected 16")
        try:
            hermit = float(module.hermiticity_deviation())
            if hermit > 1e-12:
                failures.append(f"hermiticity_deviation={hermit:.3e}, expected 0.0")
        except Exception as e:  # noqa: BLE001
            failures.append(f"hermiticity_deviation raised: {e}")

    # --- ground state: normalized, energy by direct expectation ---
    gs = None
    try:
        gs = module.ground_state()
    except Exception as e:  # noqa: BLE001
        failures.append(f"ground_state raised: {e}")
    if gs is not None:
        e0, psi = gs
        e0 = float(e0)
        if abs(float(np.linalg.norm(psi)) - 1.0) > 1e-8:
            failures.append(f"ground_norm={float(np.linalg.norm(psi)):.9f}, expected 1.000000000")
        e_dir = None
        try:
            e_dir = float(module.energy_expectation(psi))
        except Exception as e:  # noqa: BLE001
            failures.append(f"energy_expectation raised: {e}")
        if e_dir is not None and abs(e0 - e_dir) > 1e-9:
            failures.append(f"energy_mismatch={abs(e0 - e_dir):.9f}, expected 0.000000000")
        # exact value for the 2-site half-filled chain at U=2, t=1:
        # E0 = U/2 - sqrt((U/2)^2 + 4 t^2) = 1 - sqrt(5)
        expected_e0 = 1.0 - np.sqrt(5.0)
        if abs(e0 - expected_e0) > 1e-6:
            failures.append(f"ground_energy={e0:.9f}, expected {expected_e0:.9f}")
        resid = None
        try:
            resid = float(module.eigenpair_residual(psi, e0))
        except Exception as e:  # noqa: BLE001
            failures.append(f"eigenpair_residual raised: {e}")
        if resid is not None and resid > 1e-8:
            failures.append(f"eigenpair_residual={resid:.3e}, expected <= 1e-8")
        # energy gap: second eigenvalue above the ground state
        try:
            hd = module.sparse_matrix().toarray()
            evals = np.linalg.eigvalsh(hd)
            gap = float(evals[1] - evals[0])
            if gap <= 0.0:
                failures.append(f"energy_gap={gap:.9f}, expected > 0.000000000")
        except Exception as e:  # noqa: BLE001
            failures.append(f"gap check raised: {e}")

    # --- particle number: <N> = 2, variance 0 ---
    if gs is not None:
        try:
            n_mean, n_var = module.particle_number_stats(psi)
            n_mean, n_var = float(n_mean), float(n_var)
            if abs(n_mean - 2.0) > 1e-6:
                failures.append(f"particle_number_mean={n_mean:.9f}, expected 2.000000000")
            if n_var > 1e-6:
                failures.append(f"particle_number_variance={n_var:.9f}, expected 0.000000000")
        except Exception as e:  # noqa: BLE001
            failures.append(f"particle_number_stats raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "2x1 spinful Hubbard JW spectrum: E0 = U/2 - sqrt((U/2)^2+4t^2) "
            "= 1 - sqrt(5) with direct-expectation agreement, Hermiticity, "
            "near-zero eigenpair residual, and <N> = 2 with zero variance"
        ],
    }
