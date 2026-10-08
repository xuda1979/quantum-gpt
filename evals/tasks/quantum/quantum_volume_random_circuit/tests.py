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

    # Heavy output threshold
    if not math.isclose(module.heavy_output_threshold(1), 0.5, abs_tol=1e-12):
        failures.append("threshold(1) should be 0.5")
    if not math.isclose(module.heavy_output_threshold(2), 0.25, abs_tol=1e-12):
        failures.append("threshold(2) should be 0.25")
    if not math.isclose(module.heavy_output_threshold(5), 1.0 / 32, abs_tol=1e-12):
        failures.append("threshold(5) should be 1/32")

    # is_heavy_output
    if not module.is_heavy_output(0.6, 0.5):
        failures.append("0.6 > 0.5 should be heavy")
    if module.is_heavy_output(0.5, 0.5):
        failures.append("0.5 is not strictly > 0.5; should be light")
    if module.is_heavy_output(0.4, 0.5):
        failures.append("0.4 < 0.5 should be light")

    # Heavy output probability: 4 outcomes [0.1, 0.2, 0.3, 0.4], median = 0.25, 2 above
    probs = [0.1, 0.2, 0.3, 0.4]
    hop = module.heavy_output_probability(probs)
    if not math.isclose(hop, 0.5, abs_tol=1e-12):
        failures.append(f"HOP([0.1,0.2,0.3,0.4]) should be 0.5, got {hop}")

    # All-equal probabilities -> no value strictly above median -> HOP = 0
    equal = [0.25, 0.25, 0.25, 0.25]
    if module.heavy_output_probability(equal) != 0.0:
        failures.append("all-equal probabilities should give HOP=0")

    # Quantum volume achievement
    if not module.quantum_volume_is_achieved(4, 0.7):
        failures.append("HOP=0.7 should achieve QV (threshold 0.625)")
    if module.quantum_volume_is_achieved(4, 0.5):
        failures.append("HOP=0.5 should NOT achieve QV")
    if module.quantum_volume_is_achieved(4, 0.625):
        failures.append("HOP=0.625 (boundary, strict >) should NOT achieve QV")

    # Invalid inputs
    try:
        module.heavy_output_threshold(0)
        failures.append("should raise on n_qubits=0")
    except ValueError:
        pass
    try:
        module.is_heavy_output(1.5, 0.5)
        failures.append("should raise on prob > 1")
    except ValueError:
        pass
    try:
        module.heavy_output_probability([])
        failures.append("should raise on empty probabilities")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Quantum volume heavy-output computation correct"],
    }
