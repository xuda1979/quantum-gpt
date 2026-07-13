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

    # Identical states -> overlap 1
    if not math.isclose(module.swap_test_overlap(1.0), 1.0, abs_tol=1e-12):
        failures.append("P(0)=1 should give overlap 1")
    # Orthogonal states -> overlap 0, P(0)=0.5
    if not math.isclose(module.swap_test_overlap(0.5), 0.0, abs_tol=1e-12):
        failures.append("P(0)=0.5 should give overlap 0")
    # Anti-parallel states -> overlap 1 (squared)
    if not math.isclose(module.swap_test_overlap(1.0), 1.0, abs_tol=1e-12):
        failures.append("P(0)=1 again")

    # Round trip: psi, phi -> P(0) -> overlap == fidelity
    psi = [1.0, 0.0]
    phi = [0.6, 0.8]
    p0 = module.swap_test_prob_zero(psi, phi)
    expected_fid = 0.36
    if not math.isclose(module.fidelity(psi, phi), expected_fid, abs_tol=1e-12):
        failures.append(
            f"fidelity(psi,phi) should be {expected_fid}, got {module.fidelity(psi, phi)}"
        )
    if not math.isclose(module.swap_test_overlap(p0), expected_fid, abs_tol=1e-12):
        failures.append("swap_test_overlap(swap_test_prob_zero) should round-trip")

    # Different dimensions should raise
    try:
        module.swap_test_prob_zero([1.0, 0.0], [1.0, 0.0, 0.0])
        failures.append("should raise on dimension mismatch")
    except ValueError:
        pass

    # Invalid probability
    try:
        module.swap_test_overlap(1.5)
        failures.append("should raise on prob > 1")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["SWAP test overlap correct for all test cases"],
    }
