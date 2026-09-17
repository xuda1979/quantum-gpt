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

    # --- Hamiltonian: 3x1 spinful, t=0.9, U=1.5, periodic=False ---
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
            if max(coeffs) < 1.4 or max(coeffs) > 1.6:
                failures.append(f"max_coefficient={max(coeffs):.6f}, expected 1.500000 (onsite U)")
            if not any(0.85 <= c <= 0.95 for c in coeffs):
                failures.append("tunneling_term_missing=1, expected 0.9 hopping coefficient")

    # --- sparse matrix: explicit qubit count 6, dim 64, Hermitian ---
    hmat = None
    try:
        hmat = module.sparse_matrix()
    except Exception as e:  # noqa: BLE001
        failures.append(f"sparse_matrix raised: {e}")
    if hmat is not None:
        if hmat.shape[0] != 64 or hmat.shape[1] != 64:
            failures.append(f"matrix_dim={hmat.shape[0]}, expected 64")
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
        e0, psi = float(gs[0]), gs[1]
        if abs(float(np.linalg.norm(psi)) - 1.0) > 1e-8:
            failures.append(f"ground_norm={float(np.linalg.norm(psi)):.9f}, expected 1.000000000")
        e_dir = None
        try:
            e_dir = float(module.energy_expectation(psi))
        except Exception as e:  # noqa: BLE001
            failures.append(f"energy_expectation raised: {e}")
        if e_dir is not None and abs(e0 - e_dir) > 1e-9:
            failures.append(f"energy_mismatch={abs(e0 - e_dir):.9f}, expected 0.000000000")
        # exact E0 for t=0.9, U=1.5 on the 3x1 chain (verified by dense eigh)
        expected_e0 = -2.1123228866777564
        if abs(e0 - expected_e0) > 1e-6:
            failures.append(f"ground_energy={e0:.9f}, expected {expected_e0:.9f}")
        resid = None
        try:
            resid = float(module.eigenpair_residual(psi, e0))
        except Exception as e:  # noqa: BLE001
            failures.append(f"eigenpair_residual raised: {e}")
        if resid is not None and resid > 1e-8:
            failures.append(f"eigenpair_residual={resid:.3e}, expected <= 1e-8")
        try:
            hd = module.sparse_matrix().toarray()
            evals = np.linalg.eigvalsh(hd)
            gap = float(evals[1] - evals[0])
            if gap <= 0.0:
                failures.append(f"energy_gap={gap:.9f}, expected > 0.000000000")
        except Exception as e:  # noqa: BLE001
            failures.append(f"gap check raised: {e}")

    # --- particle number: ground state in the N=2 sector ---
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
            "3x1 spinful Hubbard JW spectrum: E0 = -2.112322887 with "
            "direct-expectation agreement, Hermiticity, near-zero eigenpair "
            "residual, and the ground state in the N=2 sector (<N> = 2, "
            "zero variance)"
        ],
    }
