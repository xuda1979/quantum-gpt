import importlib.util


CASES = [
    ("  Hello World  ", "hello_world"),
    ("Already__Snake", "already_snake"),
    ("quantum-phase-estimation", "quantum_phase_estimation"),
    ("Noisy Label!!! 42", "noisy_label_42"),
]

REQUIRED_DOCSTRING_SNIPPETS = [
    "lowercase snake_case identifier",
    "Collapse repeated underscores",
]


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    for raw, expected in CASES:
        actual = module.normalize_identifier(raw)
        if actual != expected:
            failures.append(f"normalize_identifier({raw!r}) -> {actual!r}, expected {expected!r}")

    docstring = module.normalize_identifier.__doc__ or ""
    for snippet in REQUIRED_DOCSTRING_SNIPPETS:
        if snippet not in docstring:
            failures.append(f"docstring missing required phrase: {snippet!r}")

    return {
        "passed": not failures,
        "details": failures or ["Behavior and documented contract both preserved"],
    }
