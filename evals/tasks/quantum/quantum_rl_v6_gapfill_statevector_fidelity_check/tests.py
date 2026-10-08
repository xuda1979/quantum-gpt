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
    except Exception as e:
        return dict(passed=False, details=["candidate import failed: %s" % e])
    required = ["statevector_fidelity", "fidelity_table"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)
    try:
        one = [1.0, 0.0]
        zero = [0.0, 1.0]
        plus = [1.0, 1.0]
        minus = [1.0, -1.0]
        if abs(m.statevector_fidelity(one, one) - 1.0) > 1e-12:
            failures.append("identical states must have fidelity 1.0")
        if abs(m.statevector_fidelity(one, zero)) > 1e-12:
            failures.append("orthogonal states must have fidelity 0.0")
        if abs(m.statevector_fidelity(plus, minus)) > 1e-12:
            failures.append("plus/minus must have fidelity 0.0 after inner normalization")
        table = m.fidelity_table([(one, one), (plus, minus)])
        if abs(table[0] - 1.0) > 1e-12 or abs(table[1]) > 1e-12:
            failures.append("fidelity_table values wrong")
        try:
            m.statevector_fidelity(one, [1.0, 0.0, 0.0])
            failures.append("length mismatch must raise ValueError")
        except ValueError:
            pass
    except Exception as e:
        failures.append("fidelity suite raised: %s" % e)
    return dict(passed=not failures, details=failures)
