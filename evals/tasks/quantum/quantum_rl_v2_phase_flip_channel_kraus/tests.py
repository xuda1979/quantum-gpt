import importlib.util
import math

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
    p = 0.18

    # --- Kraus completeness: sum K^dagger K = I ---
    try:
        ks = module.kraus_operators(p)
        if len(ks) != 2:
            failures.append(f"kraus_count={len(ks)}, expected 2")
        else:
            dev = float(module.completeness_deviation(ks))
            if dev > 1e-12:
                failures.append(f"completeness_dev={dev:.2e}, expected < 1e-12")
            # Kraus coefficients sqrt(1-p), sqrt(p)
            n0 = float(np.max(np.abs(ks[0] - math.sqrt(1.0 - p) * np.eye(2))))
            n1 = float(np.max(np.abs(ks[1] - math.sqrt(p) * np.diag([1.0, -1.0]))))
            if n0 > 1e-12 or n1 > 1e-12:
                failures.append(f"kraus_norm_dev={max(n0, n1):.2e}, expected < 1e-12")
    except Exception as e:  # noqa: BLE001
        failures.append(f"kraus_operators raised: {e}")

    # --- channel on |+><+|: off-diagonal (1-2p)/2 = 0.32, purity 0.7048 ---
    try:
        rho_plus = module.plus_state()
        out = np.asarray(module.apply_channel(rho_plus, module.kraus_operators(p)))
        off = float(np.real(out[0, 1]))
        if abs(off - (1.0 - 2.0 * p) / 2.0) > 1e-12:
            failures.append(f"rho_plus_01={off:.4f}, expected {(1.0 - 2.0 * p) / 2.0:.4f}")
        tr = float(np.trace(out).real)
        if abs(tr - 1.0) > 1e-12:
            failures.append(f"rho_plus_trace={tr:.6f}, expected 1.000000")
        if np.max(np.abs(out - out.conj().T)) > 1e-12:
            failures.append("rho_plus_hermitian=1, expected 0")
        if float(np.min(np.linalg.eigvalsh((out + out.conj().T) / 2.0))) < -1e-12:
            failures.append("rho_plus_psd=0, expected 1")
    except Exception as e:  # noqa: BLE001
        failures.append(f"channel on plus state raised: {e}")

    # --- purity and fidelity numerics ---
    try:
        rho_plus = module.plus_state()
        out = np.asarray(module.apply_channel(rho_plus, module.kraus_operators(p)))
        pur = float(module.purity(out))
        if abs(pur - 0.7048) > 1e-4:
            failures.append(f"purity_plus={pur:.4f}, expected 0.7048")
        fid = float(module.fidelity_sq(rho_plus, out))
        if abs(fid - (1.0 - p)) > 1e-9:
            failures.append(f"fidelity_plus={fid:.4f}, expected {1.0 - p:.4f}")
        if not (0.0 <= fid <= 1.0):
            failures.append(f"fidelity_range={fid:.4f}, expected in [0, 1]")
        if abs(float(module.trace_distance(out, out))) > 1e-12:
            failures.append("trace_distance_self=0.0, expected 0.000000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"purity/fidelity checks raised: {e}")

    # --- seeded random mixed state: channel drops purity, trace preserved ---
    try:
        rho_rand = np.asarray(module.random_mixed_state(seed=1))
        if np.max(np.abs(rho_rand - rho_rand.conj().T)) > 1e-12:
            failures.append("rho_rand_hermitian=1, expected 0")
        tr_before = float(np.trace(rho_rand).real)
        if abs(tr_before - 1.0) > 1e-12:
            failures.append(f"rho_rand_trace={tr_before:.6f}, expected 1.000000")
        pur_before = float(module.purity(rho_rand))
        out = np.asarray(module.apply_channel(rho_rand, module.kraus_operators(p)))
        pur_after = float(module.purity(out))
        if pur_after >= pur_before - 1e-12:
            failures.append(f"purity_drop={pur_before - pur_after:.4f}, expected > 0")
        if abs(float(np.trace(out).real) - 1.0) > 1e-12:
            failures.append("rho_rand_out_trace=0.0, expected 1.000000")
        if not (0.5 <= pur_before <= 1.0):
            failures.append(f"purity_rand_before={pur_before:.4f}, expected in [0.5, 1]")
        fid = float(module.fidelity_sq(rho_rand, out))
        if not (0.0 <= fid <= 1.0):
            failures.append(f"fidelity_rand={fid:.4f}, expected in [0, 1]")
        d = float(module.trace_distance(rho_rand, out))
        if not (0.0 <= d <= 1.0):
            failures.append(f"trace_distance_range={d:.4f}, expected in [0, 1]")
    except Exception as e:  # noqa: BLE001
        failures.append(f"random mixed-state checks raised: {e}")

    # --- end-to-end run ---
    try:
        result = module.run_checks(p=0.18, seed=1)
        if result.get("completeness_dev", 1.0) > 1e-12:
            failures.append(
                f"run_completeness_dev={result.get('completeness_dev')}, expected < 1e-12"
            )
        if abs(float(result.get("rho_plus_01", 0.0)) - (1.0 - 2.0 * p) / 2.0) > 1e-9:
            failures.append(
                f"run_rho_plus_01={result.get('rho_plus_01')}, expected {(1.0 - 2.0 * p) / 2.0:.4f}"
            )
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_checks raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Phase-flip channel p=0.18 (NumPy/SciPy): Kraus complete (dev 0), "
            "E(|+><+|) off-diag 0.32, purity 0.7048, fidelity^2 0.82, seeded "
            "mixed state purity drops with unit trace preserved",
        ],
    }
