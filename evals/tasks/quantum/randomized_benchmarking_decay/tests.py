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

    # Perfect gate: alpha = 1 -> F_avg = 1
    if not math.isclose(module.rb_average_gate_fidelity(1.0, 2), 1.0, abs_tol=1e-12):
        failures.append("alpha=1 should give F_avg=1")

    # Completely depolarizing: alpha = 0 -> F_avg = 1/d
    if not math.isclose(module.rb_average_gate_fidelity(0.0, 2), 0.5, abs_tol=1e-12):
        failures.append("alpha=0, d=2 should give F_avg=0.5")
    if not math.isclose(module.rb_average_gate_fidelity(0.0, 4), 0.25, abs_tol=1e-12):
        failures.append("alpha=0, d=4 should give F_avg=0.25")

    # Mid-range alpha
    if not math.isclose(module.rb_average_gate_fidelity(0.9, 2), 0.95, abs_tol=1e-12):
        failures.append("alpha=0.9, d=2 should give F_avg=0.95")

    # Round-trip
    for f in [0.5, 0.7, 0.95, 1.0]:
        a = module.rb_decay_parameter(f, 2)
        if not math.isclose(module.rb_average_gate_fidelity(a, 2), f, abs_tol=1e-12):
            failures.append(f"round-trip failed for F_avg={f}")
            break

    # Survival probability
    if not math.isclose(module.rb_survival_probability(0.99, 10), 0.99**10, abs_tol=1e-12):
        failures.append("survival probability mismatch for default A,B")
    if not math.isclose(module.rb_survival_probability(0.5, 0), 1.0, abs_tol=1e-12):
        failures.append("F(0) with A=1 should be 1.0")
    if not math.isclose(
        module.rb_survival_probability(0.5, 5, A=0.5, B=0.5), 0.5 * (0.5**5) + 0.5, abs_tol=1e-12
    ):
        failures.append("survival probability mismatch with A,B")

    # Invalid alpha
    try:
        module.rb_average_gate_fidelity(1.5, 2)
        failures.append("should raise on alpha > 1")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Randomized benchmarking decay correct"],
    }
