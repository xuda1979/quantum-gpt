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
    failures = []

    # N=4, M=1 (index 3 marked), one iteration should put all amplitude on marked
    state = module.uniform_initial_state(4)
    out = module.grover_state_after_iterations(state, [3], 1)
    if not math.isclose(out[3], 1.0, abs_tol=1e-9):
        failures.append(f"after 1 iter on N=4 M=1, |a_3| should be 1.0, got {out[3]}")
    if not all(math.isclose(out[i], 0.0, abs_tol=1e-9) for i in [0, 1, 2]):
        failures.append("other amplitudes should be 0 after 1 iter on N=4 M=1")

    # Zero iterations returns unchanged
    s = module.uniform_initial_state(8)
    out0 = module.grover_state_after_iterations(s, [0], 0)
    if not all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(s, out0, strict=False)):
        failures.append("0 iterations should return unchanged state")

    # Norm is preserved
    state = module.uniform_initial_state(8)
    out = module.grover_state_after_iterations(state, [2, 5], 3)
    norm = sum(a * a for a in out)
    if not math.isclose(norm, 1.0, abs_tol=1e-9):
        failures.append(f"norm should be 1.0, got {norm}")

    # Out-of-range marked index should raise
    try:
        module.grover_state_after_iterations([1.0, 0.0], [5], 1)
        failures.append("should raise on out-of-range marked index")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Amplitude amplification iteration correct"],
    }
