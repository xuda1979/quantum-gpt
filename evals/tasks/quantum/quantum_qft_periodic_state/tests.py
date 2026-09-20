import importlib.util

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _vec(value):
    return value if isinstance(value, (list, tuple)) else None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- circuit construction ---
    try:
        qc = module.qft_circuit(3)
    except Exception as e:  # noqa: BLE001
        qc = None
        failures.append(f"qft_circuit raised: {e}")
    if qc is None or not hasattr(qc, "num_qubits"):
        failures.append("qft_circuit() did not return a QuantumCircuit-like object")
    else:
        if qc.num_qubits != 3:
            failures.append(f"qft_circuit num_qubits={qc.num_qubits}, expected 3")

    # --- periodic state ---
    try:
        ps = module.periodic_state(3)
    except Exception as e:  # noqa: BLE001
        ps = None
        failures.append(f"periodic_state raised: {e}")
    if _vec(ps) is None:
        failures.append("periodic_state returned None, expected 8 amplitudes")
        failures.append("norm=0.000000, expected 1.000000")
    else:
        if len(ps) != 8:
            failures.append(f"periodic_state length={len(ps)}, expected 8")
        else:
            norm = sum(abs(a) ** 2 for a in ps)
            if abs(norm - 1.0) > 1e-6:
                failures.append(f"norm={norm:.6f}, expected 1.000000")
            if abs(complex(ps[0]) - 1 / np.sqrt(2)) > 1e-6:
                failures.append(f"periodic_amp0={abs(complex(ps[0])):.6f}, expected 0.707107")
            if abs(complex(ps[4]) - 1 / np.sqrt(2)) > 1e-6:
                failures.append(f"periodic_amp4={abs(complex(ps[4])):.6f}, expected 0.707107")

    # --- QFT of the periodic state: even indices only, amplitude 1/2 ---
    try:
        out = module.apply_qft(ps) if _vec(ps) is not None else None
    except Exception as e:  # noqa: BLE001
        out = None
        failures.append(f"apply_qft raised: {e}")
    if _vec(out) is None:
        failures.append("apply_qft returned None, expected 8 amplitudes")
        failures.append("qft_amp0=0.000000, expected 0.500000")
    else:
        if len(out) != 8:
            failures.append(f"apply_qft length={len(out)}, expected 8")
        else:
            norm = sum(abs(a) ** 2 for a in out)
            if abs(norm - 1.0) > 1e-6:
                failures.append(f"qft_norm={norm:.6f}, expected 1.000000")
            amp_correct = 0
            for k in range(8):
                want = 0.5 if k % 2 == 0 else 0.0
                if abs(abs(complex(out[k])) - want) <= 1e-6:
                    amp_correct += 1
            if amp_correct != 8:
                failures.append(f"qft_amps_correct={amp_correct}, expected 8")
            if abs(abs(complex(out[0])) - 0.5) > 1e-6:
                failures.append(f"qft_amp0={abs(complex(out[0])):.6f}, expected 0.500000")
            if abs(abs(complex(out[1])) - 0.0) > 1e-6:
                failures.append(f"qft_amp1={abs(complex(out[1])):.6f}, expected 0.000000")
            if abs(abs(complex(out[4])) - 0.5) > 1e-6:
                failures.append(f"qft_amp4={abs(complex(out[4])):.6f}, expected 0.500000")

    # --- QFT of |1>: all amplitudes have magnitude 1/sqrt(8) ---
    e1 = [0.0j, 1.0 + 0.0j] + [0.0j] * 6  # index 1 = |001>
    try:
        out1 = module.apply_qft(e1)
    except Exception as e:  # noqa: BLE001
        out1 = None
        failures.append(f"apply_qft(|1>) raised: {e}")
    if _vec(out1) is not None and len(out1) == 8:
        mag = abs(complex(out1[1]))
        if abs(mag - 1 / np.sqrt(8)) > 1e-6:
            failures.append(f"qft_e1_amp1={mag:.6f}, expected 0.353553")
        # phase of omega/ sqrt(8) with omega = exp(2 pi i / 8)
        phase = np.angle(complex(out1[1]))
        want_phase = 2 * np.pi / 8
        if abs(phase - want_phase) > 1e-6 and abs(abs(phase - want_phase) - 2 * np.pi) > 1e-6:
            failures.append(f"qft_e1_phase={phase:.6f}, expected {want_phase:.6f}")

    return {
        "passed": not failures,
        "details": failures
        or ["QFT of periodic and single-basis states matches the analytic Fourier pattern"],
    }
