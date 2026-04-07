import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    ok = True
    details = []

    if module.measurement_mapping("10") != {"q0": 0, "q1": 1}:
        ok = False
        details.append("mapping for '10' was incorrect")

    if module.measurement_mapping("01") != {"q0": 1, "q1": 0}:
        ok = False
        details.append("mapping for '01' was incorrect")

    try:
        module.measurement_mapping("2")
        ok = False
        details.append("invalid input should raise ValueError")
    except ValueError:
        details.append("invalid input rejected correctly")

    return {"passed": ok, "details": details or ["measurement mapping passed"]}
