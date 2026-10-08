import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mat(value):
    return value if isinstance(value, (list, tuple)) and value else None


def _max_abs_diff(a, b):
    n = len(a)
    best = 0.0
    for i in range(n):
        for j in range(n):
            best = max(best, abs(a[i][j] - b[i][j]))
    return best


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- Bell density matrix ---
    try:
        bell = module.bell_density_matrix()
    except Exception as e:  # noqa: BLE001
        bell = None
        failures.append(f"bell_density_matrix raised: {e}")
    if _mat(bell) is None:
        failures.append("bell_density_matrix returned non-matrix, expected 4x4")
        failures.append("bell_entries_correct=0, expected 16")
    else:
        if abs(bell[0][0] - 0.5) > 1e-9:
            failures.append(f"bell_rho00={float(bell[0][0]):.6f}, expected 0.500000")
        if abs(bell[0][3] - 0.5) > 1e-9:
            failures.append(f"bell_rho03={float(bell[0][3]):.6f}, expected 0.500000")
        if abs(bell[3][3] - 0.5) > 1e-9:
            failures.append(f"bell_rho33={float(bell[3][3]):.6f}, expected 0.500000")
        if abs(bell[1][1]) > 1e-9 or abs(bell[2][2]) > 1e-9:
            failures.append(f"bell_offdiag_block={float(bell[1][1]):.6f}, expected 0.000000")

    # --- channel limits: p=0 identity, p=1 maximally mixed ---
    try:
        ch0 = module.two_qubit_depolarizing(bell, 0.0)
        ch1 = module.two_qubit_depolarizing(bell, 1.0)
        ch_half = module.two_qubit_depolarizing(bell, 0.25)
    except Exception as e:  # noqa: BLE001
        ch0 = ch1 = ch_half = None
        failures.append(f"two_qubit_depolarizing raised: {e}")
    if _mat(ch0) is None or _mat(ch1) is None:
        failures.append("two_qubit_depolarizing returned non-matrix, expected 4x4")
        failures.append("channel_entries_correct=0, expected 16")
    else:
        if _max_abs_diff(ch0, bell) > 1e-9:
            failures.append("depolarizing p=0 did not preserve the input (expected 0.000000 diff)")
        if abs(ch1[0][0] - 0.25) > 1e-9:
            failures.append(f"ch1_diag={float(ch1[0][0]):.6f}, expected 0.250000")
        if abs(ch1[0][3]) > 1e-9:
            failures.append(f"ch1_coherence={float(ch1[0][3]):.6f}, expected 0.000000")

    # --- coherence decay and fidelity at p=0.25: F = 1 - 3p/4 = 0.8125 ---
    if _mat(ch_half) is not None:
        expected_fid = 1.0 - 3.0 * 0.25 / 4.0  # 0.8125
        if abs(ch_half[0][3] - 0.375) > 1e-9:
            failures.append(f"coherence={float(ch_half[0][3]):.6f}, expected 0.375000")
        trace = sum(ch_half[i][i] for i in range(4))
        if abs(trace - 1.0) > 1e-9:
            failures.append(f"channel_trace={trace:.6f}, expected 1.000000")
        try:
            fid = module.fidelity_to_bell(ch_half)
        except Exception as e:  # noqa: BLE001
            fid = None
            failures.append(f"fidelity_to_bell raised: {e}")
        if fid is None:
            failures.append(f"fidelity=0.000000, expected {expected_fid:.6f}")
        elif abs(fid - expected_fid) > 1e-9:
            failures.append(f"fidelity={float(fid):.6f}, expected {expected_fid:.6f}")

    # --- Werner state equals the channel applied to the Bell state ---
    try:
        werner = module.werner_state(0.25)
    except Exception as e:  # noqa: BLE001
        werner = None
        failures.append(f"werner_state raised: {e}")
    if _mat(ch_half) is not None and _mat(werner) is None:
        failures.append("werner_state returned non-matrix, expected 4x4")
    elif _mat(ch_half) is not None and _mat(werner) is not None:
        diff = _max_abs_diff(werner, ch_half)
        if diff > 1e-9:
            failures.append(f"werner_max_abs_diff={diff:.6f} need<=0.000001")
        # pure Bell fidelity is 1
        try:
            fid_bell = module.fidelity_to_bell(bell)
        except Exception as e:  # noqa: BLE001
            fid_bell = None
            failures.append(f"fidelity_to_bell(bell) raised: {e}")
        if fid_bell is None:
            failures.append("fidelity_to_bell=0.000000, expected 1.000000")
        elif abs(fid_bell - 1.0) > 1e-9:
            failures.append(f"fidelity_to_bell={float(fid_bell):.6f}, expected 1.000000")

    return {
        "passed": not failures,
        "details": failures
        or ["Two-qubit depolarizing channel and Bell fidelity decay all correct"],
    }
