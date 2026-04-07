import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    state = module.bell_pair_state()
    expected = [2 ** -0.5, 0.0, 0.0, 2 ** -0.5]
    ok = len(state) == 4 and all(math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9) for a, b in zip(state, expected))
    return {
        "passed": ok,
        "details": [f"state={state}"] if ok else ["Bell pair amplitudes did not match expected |Phi+> state"],
    }
