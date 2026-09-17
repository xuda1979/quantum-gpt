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

    required = ["phase_bits_roundtrip", "roundtrip_error_table"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)

    try:
        if abs(m.phase_bits_roundtrip(0.375, 3) - 0.375) > 0.0:
            failures.append("0.375 at 3 qubits must roundtrip exactly")
        for phase in (0.25, 0.5, 0.75):
            if abs(m.phase_bits_roundtrip(phase, 2) - phase) > 1e-12:
                failures.append("phase %s must roundtrip exactly at 2 qubits" % phase)
        table = m.roundtrip_error_table([0.0, 0.375, 0.75], 3)
        if any(err > 1e-12 for err in table.values()):
            failures.append("roundtrip errors on the 1/8 grid must be 0")
        try:
            m.phase_bits_roundtrip(1.0, 3)
            failures.append("phase 1.0 must raise ValueError")
        except ValueError:
            pass
        try:
            m.phase_bits_roundtrip(-0.1, 3)
            failures.append("negative phase must raise ValueError")
        except ValueError:
            pass
        try:
            m.phase_bits_roundtrip(0.5, 0)
            failures.append("n_qubits 0 must raise ValueError")
        except ValueError:
            pass
    except Exception as e:  # noqa: BLE001
        failures.append("phase roundtrip suite raised: %s" % e)

    return dict(passed=not failures, details=failures)
