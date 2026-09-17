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
    raw_expected = np.array([0.5, 0.5j, -0.25, 0.25j, 0.1, -0.2j, 0.3, -0.4], dtype=complex)
    norm_sq = float(np.sum(np.abs(raw_expected) ** 2))  # 0.925

    # --- raw amplitudes must be the declared vector ---
    raw = None
    try:
        raw = np.asarray(module.raw_amplitudes(), dtype=complex)
    except Exception as e:  # noqa: BLE001
        failures.append(f"raw_amplitudes raised: {e}")
    if raw is not None:
        if raw.shape != (8,):
            failures.append(f"raw_amplitude_count={raw.shape[0] if raw.ndim else 0}, expected 8")
        elif float(np.max(np.abs(raw - raw_expected))) > 1e-12:
            failures.append(
                f"raw_amplitudes_deviation={float(np.max(np.abs(raw - raw_expected))):.3e}, expected 0.0"
            )

    # --- explicit normalization ---
    target = None
    try:
        target = np.asarray(module.normalized_target(), dtype=complex)
    except Exception as e:  # noqa: BLE001
        failures.append(f"normalized_target raised: {e}")
    if target is not None:
        if target.shape != (8,):
            failures.append(
                f"target_amplitude_count={target.shape[0] if target.ndim else 0}, expected 8"
            )
        else:
            t_norm = float(np.linalg.norm(target))
            if abs(t_norm - 1.0) > 1e-9:
                failures.append(f"target_norm={t_norm:.9f}, expected 1.000000000")
            if raw is not None:
                ratio = np.zeros_like(target)
                for i in range(8):
                    if abs(raw[i]) > 0.0:
                        ratio[i] = target[i] / raw[i]
                if float(np.max(np.abs(ratio - ratio[0]))) > 1e-9:
                    failures.append(
                        "target_not_proportional=1, expected 0 (all amplitudes scaled by one factor)"
                    )

    # --- exact Statevector from StatePreparation ---
    sv = None
    try:
        sv = module.prepared_statevector()
    except Exception as e:  # noqa: BLE001
        failures.append(f"prepared_statevector raised: {e}")
    sv_data = None
    if sv is not None:
        from qiskit.quantum_info import Statevector

        if not isinstance(sv, Statevector):
            failures.append("prepared_statevector_type=?, expected qiskit Statevector")
        else:
            sv_data = np.asarray(sv.data, dtype=complex)
            if sv_data.shape != (8,):
                failures.append(f"prepared_length={sv_data.shape[0]}, expected 8")
            else:
                sv_norm = float(np.linalg.norm(sv_data))
                if abs(sv_norm - 1.0) > 1e-9:
                    failures.append(f"prepared_norm={sv_norm:.9f}, expected 1.000000000")

    # --- fidelity > 1 - 1e-12 ---
    f = None
    try:
        f = float(module.fidelity())
    except Exception as e:  # noqa: BLE001
        failures.append(f"fidelity raised: {e}")
    if f is not None:
        if not (f > 1.0 - 1e-12):
            failures.append(f"fidelity={f:.9f}, expected > 0.999999999999")
        if abs(f - 1.0) > 1e-9:
            failures.append(f"fidelity={f:.9f}, expected 1.000000000")

    # --- maximum amplitude error after phase alignment ---
    err = None
    try:
        err = float(module.max_amplitude_error())
    except Exception as e:  # noqa: BLE001
        failures.append(f"max_amplitude_error raised: {e}")
    if err is not None and err > 1e-9:
        failures.append(f"max_amplitude_error={err:.3e}, expected <= 1e-9")

    # --- probabilities in the declared q2 q1 q0 bit order ---
    probs = None
    try:
        probs = module.probabilities()
    except Exception as e:  # noqa: BLE001
        failures.append(f"probabilities raised: {e}")
    if probs is not None:
        if not isinstance(probs, dict) or len(probs) != 8:
            failures.append(
                f"prob_entry_count={0 if not isinstance(probs, dict) else len(probs)}, expected 8"
            )
        else:
            total = sum(float(v) for v in probs.values())
            if abs(total - 1.0) > 1e-9:
                failures.append(f"prob_sum={total:.9f}, expected 1.000000000")
            if sv_data is not None:
                for i in range(8):
                    key = format(i, "03b")
                    if key not in probs:
                        failures.append(f"prob_key_missing={key}, expected q2q1q0 bitstring")
                        break
                    p = float(probs[key])
                    p_exact = float(abs(sv_data[i]) ** 2)
                    if abs(p - p_exact) > 1e-9:
                        failures.append(
                            f"prob_deviation_{key}={abs(p - p_exact):.3e}, expected 0.0"
                        )
            if target is not None:
                p000 = float(probs.get("000", 0.0))
                expected_000 = float(abs(target[0]) ** 2)
                if abs(p000 - expected_000) > 1e-9:
                    failures.append(f"prob_000={p000:.9f}, expected {expected_000:.9f}")
                p111 = float(probs.get("111", 0.0))
                expected_111 = float(abs(target[7]) ** 2)
                if abs(p111 - expected_111) > 1e-9:
                    failures.append(f"prob_111={p111:.9f}, expected {expected_111:.9f}")
                # hard numeric check: p('000') = 0.25 / 0.925
                if abs(p000 - 0.25 / norm_sq) > 1e-9:
                    failures.append(f"prob_000={p000:.9f}, expected {0.25 / norm_sq:.9f}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "StatePreparation of the 8-amplitude target: explicit "
            "normalization, fidelity 1.0, phase-aligned max amplitude error "
            "< 1e-9, and q2q1q0 bit-order probabilities matching exact "
            "squared amplitudes"
        ],
    }
