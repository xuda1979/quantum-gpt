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

    cases = [
        (0.0, 3, 0),
        (0.25, 3, 2),
        (0.5, 3, 4),
        (0.75, 4, 12),
        (0.125, 3, 1),
        (1.0 / 3.0, 3, 3),
    ]
    for phase, n_bits, expected in cases:
        actual = module.phase_estimation(phase, n_bits)
        if actual != expected:
            failures.append(f"phase_estimation({phase}, {n_bits}) -> {actual}, expected {expected}")

    for phase in [0.0, 0.25, 0.5, 0.75, 0.125]:
        measured = module.phase_estimation(phase, 4)
        recovered = module.phase_from_measurement(measured, 4)
        if not math.isclose(recovered, phase, abs_tol=1e-9):
            failures.append(f"phase round-trip failed for {phase}: {measured} -> {recovered}")

    try:
        module.phase_estimation(1.0, 3)
        failures.append("phase_estimation did not reject phase == 1.0")
    except ValueError:
        pass

    try:
        module.phase_from_measurement(8, 3)
        failures.append("phase_from_measurement did not reject out-of-range measurement")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["phase measurement register converts phases without tuple/pow mistakes"],
    }
