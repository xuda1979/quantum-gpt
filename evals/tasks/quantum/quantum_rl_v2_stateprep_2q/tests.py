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
    raw_expected = np.array([1.0, 1.0j, -1.0, -1.0j], dtype=complex)

    # --- raw amplitudes must be the declared vector ---
    raw = None
    try:
        raw = np.asarray(module.raw_amplitudes(), dtype=complex)
    except Exception as e:  # noqa: BLE001
        failures.append(f"raw_amplitudes raised: {e}")
    if raw is not None:
        if raw.shape != (4,):
            failures.append(f"raw_amplitude_count={raw.shape[0] if raw.ndim else 0}, expected 4")
        elif float(np.max(np.abs(raw - raw_expected))) > 1e-12:
            failures.append(
                f"raw_amplitudes_deviation={float(np.max(np.abs(raw - raw_expected))):.3e}, expected 0.0"
            )

    # --- explicit normalization: norm 2 -> 0.5 scale ---
    target = None
    try:
        target = np.asarray(module.normalized_target(), dtype=complex)
    except Exception as e:  # noqa: BLE001
        failures.append(f"normalized_target raised: {e}")
    if target is not None:
        if target.shape != (4,):
            failures.append(
                f"target_amplitude_count={target.shape[0] if target.ndim else 0}, expected 4"
            )
        else:
            t_norm = float(np.linalg.norm(target))
            if abs(t_norm - 1.0) > 1e-9:
                failures.append(f"target_norm={t_norm:.9f}, expected 1.000000000")
            expected_norm = np.array([0.5, 0.5j, -0.5, -0.5j], dtype=complex)
            if float(np.max(np.abs(target - expected_norm))) > 1e-9:
                failures.append(
                    f"normalized_vector_deviation={float(np.max(np.abs(target - expected_norm))):.3e}, expected 0.0"
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
            if sv_data.shape != (4,):
                failures.append(f"prepared_length={sv_data.shape[0]}, expected 4")
            elif abs(float(np.linalg.norm(sv_data)) - 1.0) > 1e-9:
                failures.append(
                    f"prepared_norm={float(np.linalg.norm(sv_data)):.9f}, expected 1.000000000"
                )

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

    # --- probabilities in the declared q1 q0 bit order ---
    probs = None
    try:
        probs = module.probabilities()
    except Exception as e:  # noqa: BLE001
        failures.append(f"probabilities raised: {e}")
    if probs is not None:
        if not isinstance(probs, dict) or len(probs) != 4:
            failures.append(
                f"prob_entry_count={0 if not isinstance(probs, dict) else len(probs)}, expected 4"
            )
        else:
            total = sum(float(v) for v in probs.values())
            if abs(total - 1.0) > 1e-9:
                failures.append(f"prob_sum={total:.9f}, expected 1.000000000")
            if sv_data is not None:
                for i in range(4):
                    key = format(i, "02b")
                    if key not in probs:
                        failures.append(f"prob_key_missing={key}, expected q1q0 bitstring")
                        break
                    p = float(probs[key])
                    p_exact = float(abs(sv_data[i]) ** 2)
                    if abs(p - p_exact) > 1e-9:
                        failures.append(
                            f"prob_deviation_{key}={abs(p - p_exact):.3e}, expected 0.0"
                        )
            # every basis amplitude has probability 1/4
            for key in ("00", "01", "10", "11"):
                p = float(probs.get(key, 0.0))
                if abs(p - 0.25) > 1e-9:
                    failures.append(f"prob_{key}={p:.9f}, expected 0.250000000")

    return {
        "passed": not failures,
        "details": failures
        or [
            "StatePreparation of [1, 1j, -1, -1j]/2 on 2 qubits: fidelity "
            "1.0, phase-aligned max amplitude error < 1e-9, and uniform "
            "q1q0 bit-order probabilities 1/4"
        ],
    }
