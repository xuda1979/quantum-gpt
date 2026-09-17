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

    required = ["normalize_gate_sequence"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)

    try:
        if m.normalize_gate_sequence(["h", "CX", "pauli_x", "hadamard"]) != ["H", "CX", "X", "H"]:
            failures.append("alias mapping must yield [H, CX, X, H]")
        if m.normalize_gate_sequence([]) != []:
            failures.append("empty input must normalize to empty list")
        if m.normalize_gate_sequence([" h "]) != ["H"]:
            failures.append("surrounding whitespace must be stripped before lookup")
        if m.normalize_gate_sequence(["cnot"]) != ["CX"]:
            failures.append("cnot must alias to CX")
        try:
            m.normalize_gate_sequence(["toffoli"])
            failures.append("unknown gate must raise ValueError")
        except ValueError:
            pass
    except Exception as e:  # noqa: BLE001
        failures.append("normalize_gate_sequence raised unexpectedly: %s" % e)

    return dict(passed=not failures, details=failures)
