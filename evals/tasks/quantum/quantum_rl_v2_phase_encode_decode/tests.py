import importlib.util

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _vec(value):
    if isinstance(value, np.ndarray):
        return value
    if isinstance(value, (list, tuple)):
        return np.asarray(value, dtype=complex)
    return None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    phi = 0.9
    n = 10
    n_states = 1 << n

    # --- encode_phase: analytic amplitudes, normalization ---
    state = _vec(module.encode_phase(phi, n))
    if state is None:
        failures.append(f"encode_phase missing, expected {n_states} amplitudes")
        return {"passed": not failures, "details": failures or ["phase encode ok"]}
    if len(state) != n_states:
        failures.append(f"encode_length={len(state)}, expected {n_states}")
    else:
        norm = float(np.sum(np.abs(state) ** 2))
        if abs(norm - 1.0) > 1e-9:
            failures.append(f"encode_norm={norm:.12f}, expected 1.000000000000")
        # amplitude ratio between adjacent k matches e^{2 pi i phi}
        ok_ratio = 0
        for k in range(1, 8):
            ratio = state[k] / state[k - 1] if abs(state[k - 1]) > 1e-12 else 0.0
            if abs(ratio - np.exp(2j * np.pi * phi)) < 1e-6:
                ok_ratio += 1
        if ok_ratio != 7:
            failures.append(f"phase_ratio_correct={ok_ratio}, expected 7")

    # --- inverse QFT: unitary and truly inverts the forward QFT ---
    iqft = None
    try:
        decoded = _vec(module.inverse_qft(state))
    except Exception as e:  # noqa: BLE001
        failures.append(f"inverse_qft raised: {e}")
        decoded = None
    if decoded is not None and len(decoded) == n_states:
        dnorm = float(np.sum(np.abs(decoded) ** 2))
        if abs(dnorm - 1.0) > 1e-9:
            failures.append(f"decoded_norm={dnorm:.12f}, expected 1.000000000000")
        # compose inverse QFT with the analytic forward QFT -> identity
        fwd = np.zeros((n_states, n_states), dtype=complex)
        for j in range(n_states):
            for k in range(n_states):
                fwd[j, k] = np.exp(2j * np.pi * j * k / n_states) / np.sqrt(n_states)
        ident_err = float(np.linalg.norm(fwd @ np.asarray(decoded) - state))
        if ident_err > 1e-9:
            failures.append(f"qft_roundtrip_error={ident_err:.12f}, expected 0.000000000000")

    # --- decode_phase: maximum-likelihood grid phase with circular error ---
    if decoded is not None:
        probs = None
        try:
            probs = module.probabilities(decoded)
        except Exception as e:  # noqa: BLE001
            failures.append(f"probabilities raised: {e}")
        if probs is None or len(probs) != n_states:
            failures.append(f"prob_count={0 if probs is None else len(probs)}, expected {n_states}")
        else:
            psum = sum(probs)
            if abs(psum - 1.0) > 1e-9:
                failures.append(f"prob_sum={psum:.12f}, expected 1.000000000000")
            est = None
            try:
                est = float(module.decode_phase(probs, n))
            except Exception as e:  # noqa: BLE001
                failures.append(f"decode_phase raised: {e}")
            if est is not None:
                err = None
                try:
                    err = float(module.circular_error(est, phi))
                except Exception as e:  # noqa: BLE001
                    failures.append(f"circular_error raised: {e}")
                if err is not None:
                    if err > 1.0 / n_states + 1e-12:
                        failures.append(
                            f"circular_error={err:.12f}, expected <= {1.0 / n_states:.12f}"
                        )
                    nearest = None
                    try:
                        nearest = float(module.nearest_grid_point(phi, n))
                    except Exception as e:  # noqa: BLE001
                        failures.append(f"nearest_grid_point raised: {e}")
                    if nearest is not None:
                        if not np.isclose(nearest, 922.0 / 1024.0, atol=1e-9):
                            failures.append(
                                f"nearest_grid={nearest:.12f}, expected {922.0 / 1024.0:.12f}"
                            )
                        # the max-likelihood estimate must sit on the nearest
                        # grid point, so its circular error equals the
                        # nearest-point circular error
                        try:
                            nearest_err = float(module.circular_error(nearest, phi))
                        except Exception as exc:  # noqa: BLE001
                            failures.append(f"circular_error(nearest) raised: {exc}")
                            nearest_err = None
                        if nearest_err is not None and abs(err - nearest_err) > 1e-9:
                            failures.append(
                                f"nearest_gap_consistency={err:.12f}, "
                                f"expected {nearest_err:.12f}"
                            )

    # --- exactly representable phi = 0.25 decodes exactly ---
    try:
        s25 = _vec(module.encode_phase(0.25, n))
        d25 = _vec(module.inverse_qft(s25))
        p25 = module.probabilities(d25)
        est25 = float(module.decode_phase(p25, n))
        err25 = float(module.circular_error(est25, 0.25))
    except Exception as e:  # noqa: BLE001
        failures.append(f"representable_phi_case raised: {e}")
        est25 = err25 = None
    if est25 is not None:
        if abs(est25 - 0.25) > 1e-9:
            failures.append(f"representable_decode={est25:.12f}, expected 0.250000000000")
        if err25 is not None and err25 > 1e-9:
            failures.append(f"representable_error={err25:.12f}, expected 0.000000000000")
        # all probability must sit on the exact grid point k = 256
        if p25 is not None:
            p256 = p25[256] if len(p25) > 256 else 0.0
            if abs(p256 - 1.0) > 1e-9:
                failures.append(f"prob_at_256={p256:.12f}, expected 1.000000000000")

    return {
        "passed": not failures,
        "details": failures
        or [
            "encode_phase(0.9, 10) normalized with exact phase ratios; "
            "explicit inverse QFT unitary with round-trip identity; "
            "max-likelihood decode at grid 922/1024 with circular error "
            "<= 1/1024; phi=0.25 decodes exactly with p(256)=1",
        ],
    }
