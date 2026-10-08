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

    # Identity expectation: Re = 1 -> P(0) = 1 -> recovered = 1
    if not math.isclose(module.hadamard_test_expectation(1.0), 1.0, abs_tol=1e-12):
        failures.append("P(0)=1 should give Re(expect) = 1")
    # Re = 0 -> P(0) = 0.5
    if not math.isclose(module.hadamard_test_expectation(0.5), 0.0, abs_tol=1e-12):
        failures.append("P(0)=0.5 should give Re(expect) = 0")
    # Re = -1 -> P(0) = 0
    if not math.isclose(module.hadamard_test_expectation(0.0), -1.0, abs_tol=1e-12):
        failures.append("P(0)=0 should give Re(expect) = -1")

    # Inverse round-trip
    for v in [-1.0, -0.5, 0.0, 0.3, 0.7, 1.0]:
        p0 = module.hadamard_test_prob_zero(v)
        if not math.isclose(module.hadamard_test_expectation(p0), v, abs_tol=1e-12):
            failures.append(f"round-trip failed for Re(expect)={v}")
            break

    # Imaginary variant: P(0)=0.5 -> Im = 0; P(0)=0 -> Im = 1; P(0)=1 -> Im = -1
    if not math.isclose(module.hadamard_test_imaginary(0.5), 0.0, abs_tol=1e-12):
        failures.append("Im variant: P(0)=0.5 should give Im=0")
    if not math.isclose(module.hadamard_test_imaginary(0.0), 1.0, abs_tol=1e-12):
        failures.append("Im variant: P(0)=0 should give Im=1")
    if not math.isclose(module.hadamard_test_imaginary(1.0), -1.0, abs_tol=1e-12):
        failures.append("Im variant: P(0)=1 should give Im=-1")

    # Invalid inputs should raise
    try:
        module.hadamard_test_expectation(2.0)
        failures.append("should raise on prob > 1")
    except ValueError:
        pass
    try:
        module.hadamard_test_prob_zero(2.0)
        failures.append("should raise on Re(expect) > 1")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Hadamard test expectation recovery correct"],
    }
