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

    # phase_estimation tests
    cases = [
        # (phase, n_bits, expected_measurement)
        (0.0, 3, 0),
        (0.25, 3, 2),    # 0.25 * 8 = 2
        (0.5, 3, 4),     # 0.5 * 8 = 4
        (0.75, 4, 12),   # 0.75 * 16 = 12
        (0.125, 3, 1),   # 0.125 * 8 = 1
        (1.0 / 3.0, 3, 3),  # round(8/3) = round(2.667) = 3
    ]
    for phase, n_bits, expected in cases:
        actual = module.phase_estimation(phase, n_bits)
        if actual != expected:
            failures.append(
                f"phase_estimation({phase}, {n_bits}) -> {actual}, expected {expected}"
            )

    # phase_from_measurement tests (round-trip for exact phases)
    for phase in [0.0, 0.25, 0.5, 0.75, 0.125]:
        m = module.phase_estimation(phase, 4)
        recovered = module.phase_from_measurement(m, 4)
        if not math.isclose(recovered, phase, abs_tol=1e-9):
            failures.append(
                f"Round-trip failed for phase={phase}: measurement={m}, recovered={recovered}"
            )

    # Edge: phase just below 1.0 should wrap
    m = module.phase_estimation(0.999, 3)
    if not (0 <= m < 8):
        failures.append(f"phase_estimation(0.999, 3) out of range: {m}")

    return {
        "passed": not failures,
        "details": failures or ["Phase estimation simulation correct for all test cases"],
    }
