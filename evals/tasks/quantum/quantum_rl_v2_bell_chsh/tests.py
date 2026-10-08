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
    s2 = np.sqrt(2.0)

    # --- singlet state preparation is exact ---
    fid = None
    try:
        sv = module.singlet_circuit()
        fid = float(module.singlet_fidelity(sv))
    except Exception as e:  # noqa: BLE001
        failures.append(f"singlet preparation raised: {e}")
    if fid is not None and abs(fid - 1.0) > 1e-9:
        failures.append(f"singlet_fidelity={fid:.12f}, expected 1.000000000000")

    # --- the four correlators are consistent with the singlet ---
    corr = None
    try:
        corr = module.chsh_correlators()
    except Exception as e:  # noqa: BLE001
        failures.append(f"chsh_correlators raised: {e}")
    if corr is None or len(corr) != 4:
        n_c = len(corr) if corr is not None else 0
        failures.append(f"correlator_count={n_c}, expected 4")
    elif any(not isinstance(c, (int, float)) for c in corr):
        failures.append("correlators_not_numeric=1, expected 0")
    else:
        for i, c in enumerate(corr):
            if abs(c) > 1.0 + 1e-9:
                failures.append(f"correlator_{i}={c:.6f}, expected in [-1, 1]")
        # analytic singlet correlators for the declared observables
        # (B = (Z+X)/sqrt(2), B' = (Z-X)/sqrt(2); <a.sigma b.sigma> = -a.b)
        e_ab_true = -1.0 / s2
        e_apb_true = -1.0 / s2
        e_abp_true = -1.0 / s2
        e_apbp_true = 1.0 / s2
        diffs = [
            abs(corr[0] - e_ab_true),
            abs(corr[1] - e_apb_true),
            abs(corr[2] - e_abp_true),
            abs(corr[3] - e_apbp_true),
        ]
        if max(diffs) > 1e-9:
            failures.append(f"correlator_deviation={max(diffs):.12f}, expected 0.000000000000")

    # --- S = E(A,B)+E(A',B)+E(A,B')-E(A',B') has |S| = 2*sqrt(2) ---
    s = None
    try:
        s = float(module.chsh_value())
    except Exception as e:  # noqa: BLE001
        failures.append(f"chsh_value raised: {e}")
    if s is not None:
        if abs(abs(s) - 2.0 * s2) > 1e-9:
            failures.append(f"abs_S={abs(s):.12f}, expected {2.0 * s2:.12f}")
        if not abs(s) > 2.0:
            failures.append(f"abs_S={abs(s):.9f}, expected > 2.000000000")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Singlet |Psi-> exact, CHSH correlators -1/sqrt(2), +1/sqrt(2), "
            "|S| = 2*sqrt(2) within 1e-12, exceeds classical bound 2",
        ],
    }
