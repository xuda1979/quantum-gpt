import importlib.util

import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
Y = np.array([[0.0, -1j], [1j, 0.0]], dtype=complex)
Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
PLUS = 0.5 * np.ones((2, 2), dtype=complex)


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
    p = 0.25

    # --- Kraus operators: exact expected coefficients ---
    kraus = None
    try:
        kraus = module.depolarizing_kraus(p)
    except Exception as e:  # noqa: BLE001
        failures.append(f"depolarizing_kraus raised: {e}")
    if kraus is None or not isinstance(kraus, (list, tuple)) or len(kraus) != 4:
        n_k = len(kraus) if isinstance(kraus, (list, tuple)) else 0
        failures.append(f"kraus_count={n_k}, expected 4")
    else:
        expected = [np.sqrt(1 - p), np.sqrt(p / 3.0), np.sqrt(p / 3.0), np.sqrt(p / 3.0)]
        ok = 0
        for k, want in zip(kraus, expected, strict=False):
            k = _mat(k)
            if k is not None and k.shape == (2, 2):
                # a Pauli-scalar a*P has Frobenius norm |a|*sqrt(2)
                nrm = float(np.linalg.norm(k) / np.sqrt(2.0))
                if abs(nrm - want) < 1e-9:
                    ok += 1
        if ok != 4:
            failures.append(f"kraus_norms_correct={ok}, expected 4")

    # --- completeness: sum K^dag K = I ---
    if kraus:
        try:
            comp = _mat(module.kraus_completeness(kraus))
        except Exception as e:  # noqa: BLE001
            comp = None
            failures.append(f"kraus_completeness raised: {e}")
        if comp is not None:
            dev = float(np.linalg.norm(comp - I2))
            if dev > 1e-9:
                failures.append(f"completeness_deviation={dev:.12f}, expected 0.000000000000")

    # --- apply to |+><+|: E(rho) = (1-p)|+><+| + (p/3)(I - |+><+| + ... )
    # Exact result: [[0.5, 1/3], [1/3, 0.5]] for p = 0.25.
    rho_out = None
    if kraus:
        try:
            rho_out = _mat(module.apply_channel(kraus, PLUS))
        except Exception as e:  # noqa: BLE001
            failures.append(f"apply_channel raised: {e}")
    if rho_out is not None:
        expected_out = np.array([[0.5, 1.0 / 3.0], [1.0 / 3.0, 0.5]], dtype=complex)
        dev = float(np.linalg.norm(rho_out - expected_out))
        if dev > 1e-9:
            failures.append(f"channel_plus_deviation={dev:.12f}, expected 0.000000000000")
        evals = np.linalg.eigvalsh(rho_out)
        if np.min(evals) < -1e-9:
            failures.append(f"psd_min_eval={float(np.min(evals)):.9f}, expected >= 0.000000000")
        if abs(float(np.trace(rho_out)) - 1.0) > 1e-9:
            failures.append(f"channel_trace={float(np.trace(rho_out)):.9f}, expected 1.000000000")
        pur = None
        try:
            pur = float(module.purity(rho_out))
        except Exception as e:  # noqa: BLE001
            failures.append(f"purity raised: {e}")
        if pur is not None:
            if abs(pur - 13.0 / 18.0) > 1e-6:
                failures.append(f"plus_purity={pur:.9f}, expected {(13.0/18.0):.9f}")
        if pur is not None and not (1.0 / 2.0 <= pur <= 1.0):
            failures.append(f"plus_purity={pur:.6f}, expected in [0.5, 1]")

    # --- seeded random mixed state: valid density matrix, channel preserves validity ---
    rho_rand = None
    try:
        rho_rand = _mat(module.random_mixed_state(seed=7))
    except Exception as e:  # noqa: BLE001
        failures.append(f"random_mixed_state raised: {e}")
    if rho_rand is not None:
        if abs(float(np.trace(rho_rand)) - 1.0) > 1e-9:
            failures.append(f"rand_trace={float(np.trace(rho_rand)):.9f}, expected 1.000000000")
        if np.min(np.linalg.eigvalsh(rho_rand)) < -1e-9:
            failures.append("rand_psd=0, expected 1")
        if kraus:
            try:
                rho_rand_out = _mat(module.apply_channel(kraus, rho_rand))
            except Exception as e:  # noqa: BLE001
                rho_rand_out = None
                failures.append(f"apply_channel(rand) raised: {e}")
            if rho_rand_out is not None:
                if abs(float(np.trace(rho_rand_out)) - 1.0) > 1e-9:
                    failures.append(
                        f"rand_out_trace={float(np.trace(rho_rand_out)):.9f}, expected 1.000000000"
                    )
                if np.min(np.linalg.eigvalsh(rho_rand_out)) < -1e-9:
                    failures.append("rand_out_psd=0, expected 1")

    # --- trace distance of E(|+><+|) vs |0><0|: sqrt(1/4 + 1/9) = sqrt(13)/6 ---
    # (eigenvalues of the difference are +/-sqrt(1/4+1/9), so 0.5*2*s = s)
    if rho_out is not None:
        td_expect = float(np.sqrt(13.0) / 6.0)
        try:
            td = float(module.trace_distance(rho_out, np.diag([1.0, 0.0])))
        except Exception as e:  # noqa: BLE001
            failures.append(f"trace_distance raised: {e}")
            td = None
        if td is not None:
            if abs(td - td_expect) > 1e-9:
                failures.append(f"trace_distance={td:.9f}, expected {td_expect:.9f}")

    # --- squared Uhlmann fidelity: F^2(rho,rho)=1, and in [0,1] for distinct states ---
    if rho_out is not None:
        try:
            f_self = float(module.uhlmann_fidelity_sq(rho_out, rho_out))
        except Exception as e:  # noqa: BLE001
            failures.append(f"uhlmann_fidelity_sq raised: {e}")
            f_self = None
        if f_self is not None:
            if abs(f_self - 1.0) > 1e-9:
                failures.append(f"fidelity_self={f_self:.9f}, expected 1.000000000")
        if rho_rand is not None:
            try:
                f_pair = float(module.uhlmann_fidelity_sq(rho_out, rho_rand))
            except Exception as e:  # noqa: BLE001
                failures.append(f"uhlmann_fidelity_sq(pair) raised: {e}")
                f_pair = None
            if f_pair is not None and not (0.0 <= f_pair <= 1.0 + 1e-9):
                failures.append(f"fidelity_pair={f_pair:.9f}, expected in [0, 1]")

    return {
        "passed": not failures,
        "details": failures
        or [
            "p=0.25 depolarizing Kraus: exact coefficients, completeness "
            "I, E(|+><+|) = [[0.5, 1/3],[1/3, 0.5]], purity 13/18, PSD/unit "
            "trace, trace distance 0.5, fidelity in [0, 1]",
        ],
    }
