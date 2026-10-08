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

    required = ["normalize_gate_sequence", "phase_to_register_bits", "register_bits_to_phase"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)

    try:
        if m.normalize_gate_sequence(["hadamard", "cnot"]) != ["H", "CX"]:
            failures.append("[hadamard, cnot] must normalize to [H, CX]")
        try:
            m.normalize_gate_sequence(["swap"])
            failures.append("unknown gate must raise ValueError")
        except ValueError:
            pass
        if m.phase_to_register_bits(0.625, 3) != [1, 0, 1]:
            failures.append("phase 0.625 at 3 qubits must be [1, 0, 1]")
        if abs(m.register_bits_to_phase([1, 0, 1]) - 0.625) > 1e-12:
            failures.append("bits [1, 0, 1] must decode to 0.625")
        if abs(m.register_bits_to_phase([1]) - 0.5) > 1e-12:
            failures.append("bits [1] must decode to 0.5")
        try:
            m.register_bits_to_phase([1, 2])
            failures.append("non-binary bits must raise ValueError")
        except ValueError:
            pass
    except Exception as e:  # noqa: BLE001
        failures.append("combined drill raised: %s" % e)

    return dict(passed=not failures, details=failures)
