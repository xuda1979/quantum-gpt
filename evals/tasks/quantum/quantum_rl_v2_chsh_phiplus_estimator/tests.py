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
    s2 = 1.0 / math.sqrt(2.0)
    target = 2.0 * math.sqrt(2.0)
    expected_correlators = [s2, s2, s2, -s2]

    # --- Bell circuit must be Phi+ ---
    sv = None
    try:
        sv = module.statevector_amplitudes()
    except Exception as e:  # noqa: BLE001
        failures.append(f"statevector_amplitudes raised: {e}")
    if sv is not None:
        sv = list(sv)
        if len(sv) != 4:
            failures.append(f"statevector_length={len(sv)}, expected 4")
        else:
            if abs(abs(complex(sv[0])) - s2) > 1e-9:
                failures.append(f"amp_00={abs(complex(sv[0])):.9f}, expected {s2:.9f}")
            if abs(abs(complex(sv[3])) - s2) > 1e-9:
                failures.append(f"amp_11={abs(complex(sv[3])):.9f}, expected {s2:.9f}")
            stray = sum(abs(complex(a)) ** 2 for a in sv[1:3])
            if stray > 1e-9:
                failures.append(f"non_phiplus_mass={stray:.9f}, expected 0.000000000")

    # --- CHSH observables: 4 operators, each Hermitian ---
    try:
        obs = module.chsh_observables()
        if len(obs) != 4:
            failures.append(f"observable_count={len(obs)}, expected 4")
        else:
            for i, op in enumerate(obs):
                mat = op.to_matrix()
                if not np.allclose(mat, mat.conj().T, atol=1e-12):
                    failures.append(f"observable_{i}_hermitian=0, expected 1")
    except Exception as e:  # noqa: BLE001
        failures.append(f"chsh_observables raised: {e}")

    # --- correlators and S via StatevectorEstimator ---
    result = None
    try:
        result = module.run_chsh()
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_chsh raised: {e}")
    if result is None:
        failures.append(f"correlator_0=0.000000, expected {s2:.9f}")
        failures.append(f"chsh_value=0.000000, expected {target:.9f} within 1e-12")
        failures.append("chsh_value=0.000000, expected > 2.000000")
    else:
        correlators = result.get("correlators")
        if not correlators or len(correlators) != 4:
            failures.append(
                f"correlator_count={len(correlators) if correlators else 0}, " "expected 4"
            )
        else:
            for i, (got, exp) in enumerate(zip(correlators, expected_correlators, strict=False)):
                if abs(float(got) - exp) > 1e-12:
                    failures.append(f"correlator_{i}={float(got):.12f}, expected {exp:.12f}")
        s = result.get("s")
        if s is None:
            failures.append(f"chsh_value=0.000000, expected {target:.9f} within 1e-12")
        else:
            if abs(float(s) - target) > 1e-12:
                failures.append(f"chsh_value={float(s):.12f}, expected {target:.12f} within 1e-12")
            if float(s) <= 2.0:
                failures.append(f"chsh_value={float(s):.6f}, expected > 2.000000")
        target_val = result.get("target")
        if target_val is None or abs(float(target_val) - target) > 1e-9:
            failures.append(f"target={target_val}, expected {target:.9f}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Phi+ CHSH with StatevectorEstimator: correlators "
            "[1/2,1/2,1/2,-1/2]*sqrt(2), S = 2*sqrt(2) exact and above the "
            "classical bound 2",
        ],
    }
