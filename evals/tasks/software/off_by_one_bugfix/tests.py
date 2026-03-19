import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    cases = [
        ((1, 3), 6),
        ((4, 4), 4),
        ((5, 2), 0),
    ]
    failures = []
    for args, expected in cases:
        actual = module.inclusive_range_sum(*args)
        if actual != expected:
            failures.append(f"inclusive_range_sum{args} -> {actual}, expected {expected}")
    return {"passed": not failures, "details": failures or ["range sum behaves inclusively"]}
