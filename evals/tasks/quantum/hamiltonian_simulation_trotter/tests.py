import cmath
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

    # Trotter step count
    if module.trotter_step_count(1.0, 0.1) != 10:
        failures.append("trotter_step_count(1.0, 0.1) should be 10")
    if module.trotter_step_count(2.0, 0.25) != 8:
        failures.append("trotter_step_count(2.0, 0.25) should be 8")
    if module.trotter_step_count(0.0, 0.1) != 1:
        failures.append("trotter_step_count(0.0, 0.1) should clamp to 1")
    # order=2 should still work
    if module.trotter_step_count(1.0, 0.1, order=2) != 10:
        failures.append("trotter_step_count order=2 should also give 10")

    # Invalid inputs
    try:
        module.trotter_step_count(1.0, 0.0)
        failures.append("should raise on dt=0")
    except ValueError:
        pass
    try:
        module.trotter_step_count(1.0, 0.1, order=3)
        failures.append("should raise on order=3")
    except ValueError:
        pass

    # Rz evolution
    s = [1.0 + 0j, 0.0 + 0j]
    out = module.pauli_z_evolution(s, math.pi)
    if not math.isclose(abs(out[0] - cmath.exp(-1j * math.pi / 2)), 0.0, abs_tol=1e-12):
        failures.append("Rz(pi)|0> phase incorrect")
    s2 = [0.0 + 0j, 1.0 + 0j]
    out2 = module.pauli_z_evolution(s2, math.pi)
    if not math.isclose(abs(out2[1] - cmath.exp(1j * math.pi / 2)), 0.0, abs_tol=1e-12):
        failures.append("Rz(pi)|1> phase incorrect")
    # Norm preservation
    norm = sum(abs(a) ** 2 for a in out)
    if not math.isclose(norm, 1.0, abs_tol=1e-12):
        failures.append("Rz evolution should preserve norm")

    # Error bound scales correctly
    e1 = module.trotter_error_bound(10, 1.0, 0.1, order=1)
    e2 = module.trotter_error_bound(10, 1.0, 0.1, order=2)
    if not (e1 > 0 and e2 > 0 and e2 < e1):
        failures.append("2nd-order error bound should be smaller than 1st-order")
    # e1 = 10 * (0.1)^2 = 0.1
    if not math.isclose(e1, 0.1, abs_tol=1e-12):
        failures.append(f"first-order bound should be 0.1, got {e1}")

    return {
        "passed": not failures,
        "details": failures or ["Trotterized Hamiltonian evolution correct"],
    }
