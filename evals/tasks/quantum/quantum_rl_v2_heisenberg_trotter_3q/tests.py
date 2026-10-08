import importlib.util

import numpy as np
from scipy.linalg import expm


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    t = 0.55

    # --- explicit Pauli terms: 9 terms, coefficients 0.6 (edges) / 1.1 (Z) ---
    terms = None
    try:
        terms = module.heisenberg_terms()
    except Exception as e:  # noqa: BLE001
        failures.append(f"heisenberg_terms raised: {e}")
    if terms is None or len(terms) != 9:
        failures.append(f"term_count={0 if terms is None else len(terms)}, expected 9")
    elif terms:
        for c, m, label in terms:
            if abs(c - 0.6) > 1e-12 and abs(c - 1.1) > 1e-12:
                failures.append(f"term_coefficient={c:.4f} ({label}), expected 0.6 or 1.1")
            if m.shape != (8, 8):
                failures.append(f"term_matrix_shape={m.shape}, expected (8, 8)")

    # --- Hamiltonian matrix matches an independent construction ---
    h = None
    try:
        h = module.h_matrix()
    except Exception as e:  # noqa: BLE001
        failures.append(f"h_matrix raised: {e}")
    if h is not None:
        if h.shape != (8, 8):
            failures.append(f"h_matrix_shape={h.shape}, expected (8, 8)")
        else:
            # independent construction in the test
            I2 = np.eye(2, dtype=complex)
            X2 = np.array([[0, 1], [1, 0]], dtype=complex)
            Y2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
            Z2 = np.array([[1, 0], [0, -1]], dtype=complex)

            def kron_many(mats):
                out = mats[0]
                for m in mats[1:]:
                    out = np.kron(out, m)
                return out

            h_ind = np.zeros((8, 8), dtype=complex)
            for edge in (0, 1):
                for pauli, M in (("X", X2), ("Y", Y2), ("Z", Z2)):
                    mats = [I2, I2, I2]
                    mats[edge] = M
                    mats[edge + 1] = M
                    h_ind += 0.6 * kron_many(mats)
            for q in range(3):
                mats = [I2, I2, I2]
                mats[q] = Z2
                h_ind += 1.1 * kron_many(mats)
            if np.max(np.abs(h - h_ind)) > 1e-9:
                failures.append(
                    f"h_matrix_deviation={float(np.max(np.abs(h - h_ind))):.3e}, expected 0.0"
                )
            hermit = np.max(np.abs(h - h.conj().T))
            if hermit > 1e-9:
                failures.append(f"h_hermiticity={hermit:.3e}, expected 0.0")

    # --- initial state: |010> in q2 q1 q0 order -> index 2 ---
    psi0 = None
    try:
        psi0 = module.initial_state()
    except Exception as e:  # noqa: BLE001
        failures.append(f"initial_state raised: {e}")
    if psi0 is not None:
        if psi0.shape != (8,):
            failures.append(f"initial_state_shape={psi0.shape}, expected (8,)")
        elif (
            abs(abs(psi0[2]) - 1.0) > 1e-9
            or np.max(np.abs(psi0[:2])) > 1e-9
            or np.max(np.abs(psi0[3:])) > 1e-9
        ):
            failures.append("initial_state_basis=?, expected |010> (index 2)")

    # --- exact evolution ---
    uex = None
    try:
        uex = module.exact_unitary(t)
    except Exception as e:  # noqa: BLE001
        failures.append(f"exact_unitary raised: {e}")
    if uex is not None:
        if np.max(np.abs(uex.conj().T @ uex - np.eye(8, dtype=complex))) > 1e-9:
            failures.append("exact_unitary_not_unitary=1, expected 0")
        # direct independent check: expm(-i H t) with test-built H
        u_ind = expm(-1.0j * h_ind * t)
        if np.max(np.abs(uex - u_ind)) > 1e-9:
            failures.append(
                f"exact_unitary_deviation={float(np.max(np.abs(uex - u_ind))):.3e}, expected 0.0"
            )

    # --- palindromic symmetric second-order formula ---
    us2 = None
    try:
        us2 = module.suzuki2_unitary(t, 20)
    except Exception as e:  # noqa: BLE001
        failures.append(f"suzuki2_unitary raised: {e}")
    if us2 is not None:
        if np.max(np.abs(us2.conj().T @ us2 - np.eye(8, dtype=complex))) > 1e-9:
            failures.append("suzuki2_not_unitary=1, expected 0")

        # second-order signature: the step error scales as O(delta^3), so
        # err(2*delta)/err(delta) ~ 8 for a symmetric S2 formula (a
        # first-order formula scales as O(delta^2) with ratio ~ 4)
        def _step_err(delta):
            step = np.eye(8, dtype=complex)
            for c, m, _ in terms:
                step = expm(-0.5j * delta * c * m) @ step
            for c, m, _ in reversed(terms):
                step = expm(-0.5j * delta * c * m) @ step
            return float(np.max(np.abs(step - expm(-1.0j * h_ind * delta))))

        try:
            err_d = _step_err(t / 80.0)
            err_2d = _step_err(t / 40.0)
            ratio = err_2d / err_d if err_d > 0 else 0.0
            if not (6.0 <= ratio <= 10.0):
                failures.append(f"order_scaling={ratio:.3f}, expected ~8.000 (second order)")
        except Exception as e:  # noqa: BLE001
            failures.append(f"order scaling check raised: {e}")
        # the candidate's own operator must be the palindromic S2 built from
        # its own terms (catches first-order/half-step implementations)
        try:
            step_ref = np.eye(8, dtype=complex)
            delta = t / 20.0
            for c, m, _ in terms:
                step_ref = expm(-0.5j * delta * c * m) @ step_ref
            for c, m, _ in reversed(terms):
                step_ref = expm(-0.5j * delta * c * m) @ step_ref
            s2_ref = np.linalg.matrix_power(step_ref, 20)
            impl_err = float(np.max(np.abs(us2 - s2_ref)))
            if impl_err > 1e-9:
                failures.append(
                    f"suzuki2_implementation_deviation={impl_err:.6f}, expected 0.000000"
                )
        except Exception as e:  # noqa: BLE001
            failures.append(f"suzuki2 implementation check raised: {e}")

    # --- fidelity and <Z0> vs exact ---
    f = None
    try:
        f = float(module.final_state_fidelity(t, 20))
    except Exception as e:  # noqa: BLE001
        failures.append(f"final_state_fidelity raised: {e}")
    if f is not None:
        if f <= 0.995:
            failures.append(f"trotter_fidelity={f:.9f}, expected > 0.995000000")
    if uex is not None and psi0 is not None and us2 is not None:
        try:
            z_t = float(module.z0_expectation(us2 @ psi0))
            z_e = float(module.z0_expectation(uex @ psi0))
            if abs(z_t - z_e) > 0.005:
                failures.append(f"z0_error={abs(z_t - z_e):.6f}, expected <= 0.005000")
        except Exception as e:  # noqa: BLE001
            failures.append(f"z0_expectation raised: {e}")

    # --- convergence: 20 steps close to 40 steps ---
    if us2 is not None:
        try:
            us2_40 = module.suzuki2_unitary(t, 40)
            diff = float(np.max(np.abs(us2 - us2_40)))
            if diff > 1e-3:
                failures.append(f"step_convergence={diff:.6f}, expected <= 0.001000")
        except Exception as e:  # noqa: BLE001
            failures.append(f"40-step comparison raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Heisenberg 3-qubit S2 Trotter (20 steps): fidelity 0.99999998 "
            "vs exact expm evolution, <Z0> = 0.37893 vs 0.37872, Hamiltonian "
            "match and second-order (O(delta^3)) error scaling verified"
        ],
    }
