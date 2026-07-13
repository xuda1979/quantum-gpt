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

    # Controlled-phase angles
    if not math.isclose(module.controlled_phase_angle(1, 3), math.pi, abs_tol=1e-12):
        failures.append("CP(k=1) should be pi")
    if not math.isclose(module.controlled_phase_angle(2, 3), math.pi / 2, abs_tol=1e-12):
        failures.append("CP(k=2) should be pi/2")
    if not math.isclose(module.controlled_phase_angle(3, 3), math.pi / 4, abs_tol=1e-12):
        failures.append("CP(k=3) should be pi/4")

    # Phase schedule
    sched = module.qft_adder_phase_schedule(3)
    if len(sched) != 3 or any(len(row) != 3 for row in sched):
        failures.append("schedule should be 3x3")
    if not math.isclose(sched[0][0], math.pi, abs_tol=1e-12):
        failures.append("schedule[0][0] should be pi (k=1)")
    if not math.isclose(sched[1][0], math.pi / 2, abs_tol=1e-12):
        failures.append("schedule[1][0] should be pi/2 (k=2)")
    if not math.isclose(sched[2][0], math.pi / 4, abs_tol=1e-12):
        failures.append("schedule[2][0] should be pi/4 (k=3)")
    if sched[0][1] != 0.0 or sched[0][2] != 0.0:
        failures.append("upper triangle of schedule should be zero")

    # QFT adder sum
    if module.phase_kickback_sum(2, 3, 3) != 5:
        failures.append("2 + 3 mod 8 should be 5")
    if module.phase_kickback_sum(7, 1, 3) != 0:
        failures.append("7 + 1 mod 8 should be 0 (wraps)")
    if module.phase_kickback_sum(0, 0, 3) != 0:
        failures.append("0 + 0 mod 8 should be 0")
    if module.phase_kickback_sum(5, 5, 3) != 2:
        failures.append("5 + 5 mod 8 should be 2")

    # Out of range
    try:
        module.phase_kickback_sum(8, 0, 3)
        failures.append("should raise on a >= 2^n")
    except ValueError:
        pass
    try:
        module.controlled_phase_angle(0, 3)
        failures.append("should raise on k=0")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Phase kickback adder decomposition correct"],
    }
