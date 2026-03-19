import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    cases = module.regression_cases()
    failures = []

    if len(cases) < 3:
        failures.append("expected at least three regression cases")

    for case in cases:
        if "raises" in case:
            try:
                module.parse_assignment(case["input"])
                failures.append(f"case '{case['name']}' should raise {case['raises'].__name__}")
            except Exception as exc:
                if not isinstance(exc, case["raises"]):
                    failures.append(f"case '{case['name']}' raised {type(exc).__name__}, expected {case['raises'].__name__}")
        else:
            actual = module.parse_assignment(case["input"])
            if actual != case["expected"]:
                failures.append(f"case '{case['name']}' -> {actual}, expected {case['expected']}")

    return {"passed": not failures, "details": failures or ["regression cases cover parser edge cases"]}
