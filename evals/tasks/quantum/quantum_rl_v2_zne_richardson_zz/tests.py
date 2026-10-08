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
    p = 0.04

    # --- folded circuits: 1, 3, 5 consecutive CX after H ---
    for scale, ncx in [(1, 1), (2, 3), (3, 5)]:
        qc = None
        try:
            qc = module.bell_zz_circuit(scale)
        except Exception as e:  # noqa: BLE001
            failures.append(f"bell_zz_circuit({scale}) raised: {e}")
            continue
        if qc.num_qubits != 2:
            failures.append(f"scale{scale}_qubits={qc.num_qubits}, expected 2")
            continue
        ops = qc.count_ops()
        if ops.get("cx", 0) != ncx:
            failures.append(f"scale{scale}_cx_count={ops.get('cx', 0)}, expected {ncx}")
        if ops.get("h", 0) != 1:
            failures.append(f"scale{scale}_h_count={ops.get('h', 0)}, expected 1")
        if ops.get("measure", 0) != 0:
            failures.append(f"scale{scale}_measurements={ops.get('measure', 0)}, expected 0")

    # --- exact density-matrix expectations: e1 = 1-p, monotone decay ---
    try:
        e1 = float(module.exact_zz(1))
        e3 = float(module.exact_zz(2))
        e5 = float(module.exact_zz(3))
    except Exception as e:  # noqa: BLE001
        failures.append(f"exact_zz raised: {e}")
        e1 = e3 = e5 = None
    if e1 is not None:
        if abs(e1 - (1.0 - p)) > 1e-9:
            failures.append(f"exact_e1={e1:.9f}, expected {1.0 - p:.9f}")
        if not (e1 > e3 > e5):
            failures.append(f"monotone_decay=({e1:.4f},{e3:.4f},{e5:.4f}), expected e1 > e3 > e5")
        if not (0.0 < e5 < 1.0):
            failures.append(f"exact_e5={e5:.9f}, expected within (0.0, 1.0)")

    # --- quadratic Richardson: weights 15/8, -5/4, 3/8, closer to 1 ---
    quad = None
    if e1 is not None:
        try:
            quad = float(module.quadratic_richardson(e1, e3, e5))
        except Exception as e:  # noqa: BLE001
            failures.append(f"quadratic_richardson raised: {e}")
    if quad is not None:
        expected = (15.0 / 8.0) * e1 - (5.0 / 4.0) * e3 + (3.0 / 8.0) * e5
        if abs(quad - expected) > 1e-9:
            failures.append(
                f"richardson_weights_deviation={abs(quad - expected):.9f}, expected 0.000000000"
            )
        if abs(quad - 1.0) > 5e-4:
            failures.append(f"exact_quadratic_intercept={quad:.9f}, expected 1.000000000")
        if abs(quad - 1.0) >= abs(e1 - 1.0):
            failures.append(
                f"intercept_distance={abs(quad - 1.0):.6f}, "
                f"expected < noisy_distance={abs(e1 - 1.0):.6f}"
            )

    # --- shot-based parity estimates: 50000 seeded shots per scale ---
    res = None
    try:
        res = module.zne_shots(shots=50000, seed=1234, n_boot=50)
    except Exception as e:  # noqa: BLE001
        failures.append(f"zne_shots raised: {e}")
    if res is not None:
        s1 = float(res["e1"])
        s3 = float(res["e3"])
        s5 = float(res["e5"])
        if abs(s1 - e1) > 0.03:
            failures.append(f"shot_e1={s1:.6f}, expected within 0.03 of exact {e1:.6f}")
        if abs(s3 - e3) > 0.03:
            failures.append(f"shot_e3={s3:.6f}, expected within 0.03 of exact {e3:.6f}")
        if abs(s5 - e5) > 0.03:
            failures.append(f"shot_e5={s5:.6f}, expected within 0.03 of exact {e5:.6f}")
        sq = float(res["quadratic_intercept"])
        if abs(sq - 1.0) > 0.05:
            failures.append(f"shot_quadratic_intercept={sq:.6f}, expected within 0.05 of 1.0")
        sl = float(res["linear_intercept"])
        if abs(sl - 1.0) > 0.05:
            failures.append(f"shot_linear_intercept={sl:.6f}, expected within 0.05 of 1.0")
        bq = float(res["quadratic_bootstrap_std"])
        bl = float(res["linear_bootstrap_std"])
        if not (bq > 0.0) or not np.isfinite(bq):
            failures.append(f"quadratic_bootstrap_std={bq}, expected finite > 0")
        if not (bl > 0.0) or not np.isfinite(bl):
            failures.append(f"linear_bootstrap_std={bl}, expected finite > 0")

    # --- zne_exact bundle ---
    try:
        ex = module.zne_exact()
        q2 = float(ex["quadratic_intercept"])
        if abs(q2 - 1.0) > 5e-4:
            failures.append(f"zne_exact_quadratic={q2:.9f}, expected 1.000000000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"zne_exact raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "ZNE on <ZZ>: exact (1-p) scale-1 expectation, quadratic "
            "Richardson intercept (15/8, -5/4, 3/8) recovers 1.0 to 5e-4 and "
            "beats the scale-1 noisy value; shot intercepts within 0.05 with "
            "bootstrap uncertainty"
        ],
    }
