import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # No phase error: all parities equal -> syndrome 0
    if module.phase_flip_syndrome([0, 0, 0]) != 0:
        failures.append("syndrome of equal parities should be 0")
    if module.phase_flip_syndrome([1, 1, 1]) != 0:
        failures.append("syndrome of all-ones should be 0")

    # Phase flip on qubit 0: parities [1,0,0] -> s=(1^0,0^0)=(1,0)=2
    if module.phase_flip_syndrome([1, 0, 0]) != 2:
        failures.append("syndrome([1,0,0]) should be 2")
    if module.phase_flip_error_index(2) != 0:
        failures.append("phase syndrome 2 -> qubit 0")

    # Phase flip on qubit 1: [0,1,0] -> s=(0^1,1^0)=(1,1)=3
    if module.phase_flip_syndrome([0, 1, 0]) != 3:
        failures.append("syndrome([0,1,0]) should be 3")
    if module.phase_flip_error_index(3) != 1:
        failures.append("phase syndrome 3 -> qubit 1")

    # Phase flip on qubit 2: [0,0,1] -> s=(0^0,0^1)=(0,1)=1
    if module.phase_flip_syndrome([0, 0, 1]) != 1:
        failures.append("syndrome([0,0,1]) should be 1")
    if module.phase_flip_error_index(1) != 2:
        failures.append("phase syndrome 1 -> qubit 2")

    # Correction applies Z (sign flip)
    amps = [1.0 + 0j, 0.5 + 0j, -0.2 + 0j]
    corrected = module.phase_flip_correct_amplitudes(amps, 1)
    if corrected[1] != -(0.5 + 0j):
        failures.append("Z on qubit 1 should negate amplitude[1]")
    corrected_none = module.phase_flip_correct_amplitudes(amps, -1)
    if corrected_none != amps:
        failures.append("error_index=-1 should leave amplitudes unchanged")

    # Invalid input
    try:
        module.phase_flip_syndrome([0, 1])
        failures.append("should raise on wrong length")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Phase-flip code syndrome decoding correct"],
    }
