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
        return list(value.data)
    return None


def _mat(value):
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], (list, tuple)):
        return value
    if hasattr(value, "data"):
        return _vec(value)
    return None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    inv_s3 = 1.0 / math.sqrt(3.0)
    h2_third = -(2.0 / 3.0) * math.log2(2.0 / 3.0) - (1.0 / 3.0) * math.log2(1.0 / 3.0)

    amps = _vec(module.w_state_amplitudes())
    if amps is None:
        failures.append("w_state_amplitudes returned nothing, expected 8 amplitudes")
    else:
        if len(amps) != 8:
            failures.append(f"amplitude_length={len(amps)}, expected 8")
        else:
            norm = sum(abs(complex(a)) ** 2 for a in amps)
            if abs(norm - 1.0) > 1e-9:
                failures.append(f"amplitude_norm={norm:.9f}, expected 1.000000000")
            for i in (1, 2, 4):
                if abs(abs(complex(amps[i])) - inv_s3) > 1e-9:
                    failures.append(
                        f"amp_{i:03b}={abs(complex(amps[i])):.9f}, expected {inv_s3:.9f}"
                    )
            stray = sum(abs(complex(amps[i])) ** 2 for i in (0, 3, 5, 6, 7))
            if stray > 1e-9:
                failures.append(f"non_w_basis_prob={stray:.9f}, expected 0.000000000")

    sv = None
    try:
        sv = module.w_statevector()
    except Exception as e:  # noqa: BLE001
        failures.append(f"w_statevector raised: {e}")
    sv = _vec(sv)
    if sv is None:
        failures.append("prepared_state=0 amplitudes, expected 8")
    elif len(sv) != 8:
        failures.append(f"prepared_length={len(sv)}, expected 8")
    else:
        norm = sum(abs(complex(a)) ** 2 for a in sv)
        if abs(norm - 1.0) > 1e-9:
            failures.append(f"prepared_norm={norm:.9f}, expected 1.000000000")
        # basis states whose Hamming weight is not 1 must have zero probability
        stray = sum(abs(complex(sv[i])) ** 2 for i in (0, 3, 5, 6, 7))
        if stray > 1e-9:
            failures.append(f"prepared_non_w_prob={stray:.9f}, expected 0.000000000")
        for i in (1, 2, 4):
            if abs(abs(complex(sv[i])) - inv_s3) > 1e-6:
                failures.append(
                    f"prepared_amp_{i:03b}={abs(complex(sv[i])):.9f}, expected {inv_s3:.9f}"
                )

    fid = None
    try:
        fid = float(module.target_fidelity(_vec(sv) or [1.0] + [0.0] * 7))
    except Exception as e:  # noqa: BLE001
        failures.append(f"target_fidelity raised: {e}")
    if fid is not None and abs(fid - 1.0) > 1e-9:
        failures.append(f"w_fidelity={fid:.9f}, expected 1.000000000")

    ent = None
    try:
        ent = float(module.qubit0_entropy(_vec(sv) or [1.0] + [0.0] * 7))
    except Exception as e:  # noqa: BLE001
        failures.append(f"qubit0_entropy raised: {e}")
    if ent is not None and abs(ent - h2_third) > 1e-6:
        failures.append(f"w_entropy_qubit0={ent:.9f}, expected {h2_third:.9f}")

    rho0 = None
    try:
        rho0 = module.reduced_qubit0_density(_vec(sv) or [1.0] + [0.0] * 7)
    except Exception as e:  # noqa: BLE001
        failures.append(f"reduced_qubit0_density raised: {e}")
    rho0 = _mat(rho0)
    if rho0 is None:
        failures.append("rho0_missing=0x0, expected 2x2")
    elif len(rho0) != 2 or len(rho0[0]) != 2:
        failures.append(f"rho0_shape={len(rho0)}x{len(rho0[0]) if rho0 else 0}, expected 2x2")
    else:
        r00 = complex(rho0[0][0]).real
        r11 = complex(rho0[1][1]).real
        if abs(r00 - 2.0 / 3.0) > 1e-6:
            failures.append(f"rho0_00={r00:.9f}, expected {(2.0/3.0):.9f}")
        if abs(r11 - 1.0 / 3.0) > 1e-6:
            failures.append(f"rho0_11={r11:.9f}, expected {(1.0/3.0):.9f}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "W state exact: normalization 1, only Hamming-weight-1 basis "
            "states populated, fidelity 1, entropy(qubit0) = h2(1/3)",
        ],
    }
