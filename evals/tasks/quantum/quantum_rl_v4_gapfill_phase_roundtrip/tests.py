import importlib.util


def _load(candidate_path):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path):
    failures = []
    try:
        m = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return dict(passed=False, details=["candidate import failed: %s" % e])

    required = ["bits_to_phase", "phase_to_bits", "phase_grid", "roundtrip_error", "register_diag"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)

    try:
        if abs(m.bits_to_phase("101") - 0.625) > 1e-12:
            failures.append("bits_to_phase(101) must be 0.625")
        if abs(m.bits_to_phase("1") - 0.5) > 1e-12:
            failures.append("bits_to_phase(1) must be 0.5")
        if m.phase_to_bits(0.5, 1) != "1":
            failures.append("phase_to_bits(0.5, 1) must be 1")
        if m.phase_to_bits(0.625, 3) != "101":
            failures.append("phase_to_bits(0.625, 3) must be 101")
        if m.phase_to_bits(0.625, 5) != "10100":
            failures.append("phase_to_bits(0.625, 5) must zero-extend to 10100")
    except Exception as e:  # noqa: BLE001
        failures.append("bit/phase mapping raised: %s" % e)

    try:
        grid = m.phase_grid(3)
        if len(grid) != 8:
            failures.append("phase_grid(3) must hold 8 points, got %s" % len(grid))
        if grid[0] != 0.0 or abs(grid[1] - 0.125) > 1e-12:
            failures.append("phase_grid spacing must be 2^-n")
    except Exception as e:  # noqa: BLE001
        failures.append("phase_grid raised: %s" % e)

    try:
        for bits in ("0", "1", "01", "10", "101", "1101", "101110"):
            err = float(m.roundtrip_error(bits))
            if err != 0.0:
                failures.append("roundtrip %s error %.2e expected exactly 0" % (bits, err))
    except Exception as e:  # noqa: BLE001
        failures.append("roundtrip checks raised: %s" % e)

    try:
        diag = m.register_diag(4)
        for key in ("n_bits", "n_phases", "spacing", "max_roundtrip_error"):
            if key not in diag:
                failures.append("register_diag missing key %s" % key)
        if diag.get("n_phases") != 16 or abs(diag.get("spacing", 1.0) - 0.0625) > 1e-12:
            failures.append("register_diag(4) must report 16 phases with spacing 1/16")
        if float(diag.get("max_roundtrip_error", 1.0)) != 0.0:
            failures.append("register_diag max_roundtrip_error must be exactly 0")
    except Exception as e:  # noqa: BLE001
        failures.append("register_diag raised: %s" % e)

    return dict(
        passed=not failures,
        details=failures
        or [
            "Phase register roundtrip: binary-fraction encode/decode exact on all "
            "representable strings; all five entry points present"
        ],
    )
