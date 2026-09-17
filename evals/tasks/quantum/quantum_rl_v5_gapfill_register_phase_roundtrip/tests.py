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

    required = ["phase_to_register_bits", "register_bits_to_phase"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s %s" % (", ".join(missing), ""))
        return dict(passed=False, details=failures)

    try:
        if m.phase_to_register_bits(0.375, 3) != [0, 1, 1]:
            failures.append("phase 0.375 at 3 qubits must be [0, 1, 1]")
        if abs(m.register_bits_to_phase([0, 1, 1]) - 0.375) > 0.0:
            failures.append("roundtrip of 0.375 must be exactly 0.375")
        if abs(m.register_bits_to_phase([1, 1, 0]) - 0.75) > 1e-12:
            failures.append("bits [1, 1, 0] must decode to 0.75")
        if abs(m.register_bits_to_phase([1]) - 0.5) > 1e-12:
            failures.append("bits [1] must decode to 0.5")
        for k in range(8):
            bits = m.phase_to_register_bits(k / 8.0, 3)
            if abs(m.register_bits_to_phase(bits) - k / 8.0) > 1e-12:
                failures.append("grid roundtrip failed at %s/8" % k)
        try:
            m.register_bits_to_phase([1, 2])
            failures.append("non-binary bits must raise ValueError")
        except ValueError:
            pass
        try:
            m.register_bits_to_phase([])
            failures.append("empty bits must raise ValueError")
        except ValueError:
            pass
        try:
            m.phase_to_register_bits(1.0, 3)
            failures.append("phase 1.0 must raise ValueError")
        except ValueError:
            pass
        try:
            m.phase_to_register_bits(0.5, 0)
            failures.append("n_qubits 0 must raise ValueError")
        except ValueError:
            pass
    except Exception as e:  # noqa: BLE001
        failures.append("roundtrip pair raised: %s" % e)

    return dict(passed=not failures, details=failures)
