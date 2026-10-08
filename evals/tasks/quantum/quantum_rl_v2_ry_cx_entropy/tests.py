import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _vec(value):
    if isinstance(value, (list, tuple)):
        return list(value)
    if hasattr(value, "data") and hasattr(value, "dim"):
        return list(value.data)  # qiskit Statevector / DensityMatrix
    try:
        import numpy as np

        if isinstance(value, np.ndarray):
            return value.tolist()
    except Exception:  # noqa: BLE001
        pass
    return None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    theta = 1.1
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)

    # --- statevector amplitudes must match RY(theta) then CX(0,1) ---
    sv = None
    try:
        sv = module.ry_cx_statevector(theta)
    except Exception as e:  # noqa: BLE001
        failures.append(f"ry_cx_statevector raised: {e}")
    sv = _vec(sv)
    if sv is None:
        failures.append("statevector_length=0, expected 4")
    else:
        if len(sv) != 4:
            failures.append(f"statevector_length={len(sv)}, expected 4")
        else:
            norm = sum(abs(float(a)) ** 2 for a in sv)
            if abs(norm - 1.0) > 1e-9:
                failures.append(f"statevector_norm={norm:.9f}, expected 1.000000000")
            if abs(abs(complex(sv[0])) - abs(c)) > 1e-9:
                failures.append(f"amp_00={abs(complex(sv[0])):.9f}, expected {abs(c):.9f}")
            if abs(abs(complex(sv[3])) - abs(s)) > 1e-9:
                failures.append(f"amp_11={abs(complex(sv[3])):.9f}, expected {abs(s):.9f}")
            stray = sum(abs(float(a)) ** 2 for a in [sv[1], sv[2]])
            if stray > 1e-9:
                failures.append(f"off_diag_amp_prob={stray:.9f}, expected 0.000000000")

    # --- entropy of qubit 0 must equal h2(sin^2(theta/2)) ---
    ent = None
    try:
        ent = module.reduced_entropy(_vec(sv) or [1.0, 0.0, 0.0, 0.0])
    except Exception as e:  # noqa: BLE001
        failures.append(f"reduced_entropy raised: {e}")
    analytic = None
    try:
        analytic = module.binary_entropy(s * s)
    except Exception as e:  # noqa: BLE001
        failures.append(f"binary_entropy raised: {e}")
    if analytic is None:
        failures.append(f"analytic_h2=0.000000, expected {s * s:.6f}")
    if ent is not None and analytic is not None:
        if abs(ent - analytic) > 1e-12:
            failures.append(f"entropy_mismatch={ent:.12f}, expected {analytic:.12f}")

    # --- binary_entropy must handle zero logarithms safely ---
    try:
        b0 = float(module.binary_entropy(0.0))
        b1 = float(module.binary_entropy(1.0))
        bhalf = float(module.binary_entropy(0.5))
    except Exception as e:  # noqa: BLE001
        b0 = None
        failures.append(f"binary_entropy edge case raised: {e}")
    if b0 is not None:
        if abs(b0) > 1e-12:
            failures.append(f"h2_0={b0:.9f}, expected 0.000000000")
        if abs(b1) > 1e-12:
            failures.append(f"h2_1={b1:.9f}, expected 0.000000000")
        if abs(bhalf - 1.0) > 1e-12:
            failures.append(f"h2_half={bhalf:.12f}, expected 1.000000000000")

    return {
        "passed": not failures,
        "details": failures
        or [
            "RY-CX reduced entropy matches h2(sin^2(1.1/2)) within 1e-12, "
            "statevector amplitudes exact, zero-log handling safe"
        ],
    }
