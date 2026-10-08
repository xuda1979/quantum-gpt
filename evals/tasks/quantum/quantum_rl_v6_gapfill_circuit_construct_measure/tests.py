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
    required = ["apply_fixed_gates_and_measure"]
    missing = [name for name in required if not hasattr(m, name)]
    if missing:
        failures.append("missing required function(s): %s" % ", ".join(missing))
        return dict(passed=False, details=failures)
    try:
        import numpy

        if not numpy.allclose(m.apply_fixed_gates_and_measure([1.0, 0.0], ["H"]), [0.5, 0.5]):
            failures.append("H on |0> must give uniform probabilities")
        if not numpy.allclose(m.apply_fixed_gates_and_measure([1.0, 0.0], ["X"]), [0.0, 1.0]):
            failures.append("X on |0> must give |1>")
        plus = [0.7071067811865476, 0.7071067811865476]
        if not numpy.allclose(m.apply_fixed_gates_and_measure(plus, ["Z"]), [0.5, 0.5]):
            failures.append("Z on |+> must keep probabilities [0.5, 0.5]")
        try:
            m.apply_fixed_gates_and_measure([1.0, 0.0], ["SWAP"])
            failures.append("unsupported gate must raise ValueError")
        except ValueError:
            pass
    except Exception as e:
        failures.append("circuit suite raised: %s" % e)
    return dict(passed=not failures, details=failures)
