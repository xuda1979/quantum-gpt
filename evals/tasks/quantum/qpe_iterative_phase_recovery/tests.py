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

    # 3-bit phase = 0.375 (binary .011)
    if not math.isclose(module.iterative_qpe_phase([0, 1, 1], 3), 0.375, abs_tol=1e-12):
        failures.append("iterative_qpe_phase([0,1,1],3) should be 0.375")

    # 4-bit phase = 0.0625 (binary .0001)
    if not math.isclose(module.iterative_qpe_phase([0, 0, 0, 1], 4), 0.0625, abs_tol=1e-12):
        failures.append("iterative_qpe_phase([0,0,0,1],4) should be 0.0625")

    # All zeros -> phase 0.0
    if not math.isclose(module.iterative_qpe_phase([0, 0, 0], 3), 0.0, abs_tol=1e-12):
        failures.append("all-zero measurements should give phase 0.0")

    # All ones -> phase 1 - 2^-n
    if not math.isclose(module.iterative_qpe_phase([1, 1, 1], 3), 0.875, abs_tol=1e-12):
        failures.append("iterative_qpe_phase([1,1,1],3) should be 0.875")

    # phase_to_bitstring round trip
    if module.phase_to_bitstring(0.375, 3) != "011":
        failures.append("phase_to_bitstring(0.375,3) should be '011'")
    if module.phase_to_bitstring(0.5, 4) != "1000":
        failures.append("phase_to_bitstring(0.5,4) should be '1000'")
    if module.phase_to_bitstring(0.999, 3) != "111":
        failures.append("phase_to_bitstring(0.999,3) should wrap to '111'")

    # Length mismatch must raise
    try:
        module.iterative_qpe_phase([0, 1], 3)
        failures.append("iterative_qpe_phase should raise on length mismatch")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Iterative QPE phase recovery correct for all test cases"],
    }
