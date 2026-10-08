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
    target = math.cos(2.0)

    # --- exact assignment matrix under the declared convention ---
    a = None
    try:
        a = np.asarray(module.assignment_matrix(), dtype=float)
    except Exception as e:  # noqa: BLE001
        failures.append(f"assignment_matrix raised: {e}")
    if a is not None:
        if a.shape != (2, 2):
            failures.append(f"assignment_shape={a.shape}, expected 2x2")
        else:
            expected = np.array([[0.9, 0.04], [0.1, 0.96]])
            diff = float(np.max(np.abs(a - expected)))
            if diff > 1e-12:
                failures.append(f"assignment_matrix_diff={diff:.3e}, expected 0.0")
            # explicit convention: rows = measured, cols = prepared
            if abs(a[1, 0] - 0.1) > 1e-12 or abs(a[0, 1] - 0.04) > 1e-12:
                failures.append("assignment_convention=0, expected rows=measured cols=prepared")

    # --- ill-conditioned matrices rejected ---
    try:
        cond = float(module.condition_number())
        if not (1.0 <= cond < 20.0):
            failures.append(f"condition_number={cond:.4f}, expected < 20.0")
    except Exception as e:  # noqa: BLE001
        failures.append(f"condition_number raised: {e}")

    # --- exact probability algebra recovers cos(2.0) ---
    proof = None
    try:
        proof = module.exact_algebra_proof()
    except Exception as e:  # noqa: BLE001
        failures.append(f"exact_algebra_proof raised: {e}")
    if proof is None:
        failures.append(f"algebra_z=0.000000, expected {target:.9f}")
    else:
        z = proof.get("recovered_z")
        if z is None:
            failures.append(f"algebra_z=0.000000, expected {target:.9f}")
        elif abs(float(z) - target) > 1e-12:
            failures.append(f"algebra_z={float(z):.12f}, expected {target:.12f}")

    # --- mitigation run: corrected Z within the statistical tolerance ---
    result = None
    try:
        result = module.run_mitigation()
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_mitigation raised: {e}")
    if result is None:
        failures.append(f"corrected_z=0.000000, expected {target:.9f} within 0.030")
    else:
        z = result.get("z_corrected")
        if z is None:
            failures.append(f"corrected_z=0.000000, expected {target:.9f} within 0.030")
        else:
            if abs(float(z) - target) > 0.03:
                failures.append(f"corrected_z={float(z):.9f}, expected {target:.9f} within 0.030")
        z_true = result.get("z_true")
        if z_true is None or abs(float(z_true) - target) > 1e-9:
            failures.append(f"z_true={z_true}, expected {target:.9f}")
        if result.get("passed") is not True:
            failures.append("run_mitigation passed flag must be True")
        diag = result.get("diagnostics")
        if not isinstance(diag, dict):
            failures.append("diagnostics must be a dict with clipping/norm data")

    return {
        "passed": not failures,
        "details": failures
        or [
            "readout-error mitigation: assignment matrix and algebra exact, "
            "shot-based corrected <Z> = cos(2.0) within the 0.03 statistical "
            "window at 30000 seeded shots",
        ],
    }
