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

    # Single marked item in N=4 -> optimal R = 1
    if module.optimal_grover_iterations(4, 1) != 1:
        failures.append("Grover(N=4, M=1) should be 1 iteration")

    # Single marked in N=8 -> optimal R = 2
    if module.optimal_grover_iterations(8, 1) != 2:
        failures.append("Grover(N=8, M=1) should be 2 iterations")

    # Single marked in N=1024 -> optimal R approx 25
    r = module.optimal_grover_iterations(1024, 1)
    if not (24 <= r <= 26):
        failures.append(f"Grover(N=1024, M=1) expected ~25, got {r}")

    # Half marked -> 0 iterations
    if module.optimal_grover_iterations(8, 4) != 0:
        failures.append("Grover(N=8, M=4) should be 0 iterations")

    # All marked -> 0 iterations
    if module.optimal_grover_iterations(8, 8) != 0:
        failures.append("Grover(N=8, M=8) should be 0 iterations")

    # Success probability for N=4, M=1, R=1 should be 1.0
    p = module.grover_success_probability(4, 1, 1)
    if not math.isclose(p, 1.0, abs_tol=1e-9):
        failures.append(f"P(N=4,M=1,R=1) should be 1.0, got {p}")

    # Success probability monotonic-ish for N=8, M=1, R=0 -> 1/8
    p0 = module.grover_success_probability(8, 1, 0)
    if not math.isclose(p0, 0.125, abs_tol=1e-9):
        failures.append(f"P(N=8,M=1,R=0) should be 0.125, got {p0}")

    # Invalid inputs should raise
    try:
        module.optimal_grover_iterations(0, 1)
        failures.append("should raise on n_items=0")
    except ValueError:
        pass
    try:
        module.optimal_grover_iterations(8, 0)
        failures.append("should raise on n_marked=0")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Grover multi-solution iteration count correct"],
    }
