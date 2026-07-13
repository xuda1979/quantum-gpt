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

    # No error: syndrome 0, no flip
    if module.bit_flip_syndrome([0, 0, 0]) != 0:
        failures.append("syndrome of |000> should be 0")
    if module.bit_flip_syndrome([1, 1, 1]) != 0:
        failures.append("syndrome of |111> should be 0")
    if module.bit_flip_error_index(0) != -1:
        failures.append("syndrome 0 -> no error (-1)")

    # Flip on qubit 0: |100> -> syndrome = (1^0, 0^0) = (1,0) = 2
    if module.bit_flip_syndrome([1, 0, 0]) != 2:
        failures.append("syndrome of |100> should be 2")
    if module.bit_flip_error_index(2) != 0:
        failures.append("syndrome 2 -> error on qubit 0")

    # Flip on qubit 1: |010> -> syndrome = (0^1, 1^0) = (1,1) = 3
    if module.bit_flip_syndrome([0, 1, 0]) != 3:
        failures.append("syndrome of |010> should be 3")
    if module.bit_flip_error_index(3) != 1:
        failures.append("syndrome 3 -> error on qubit 1")

    # Flip on qubit 2: |001> -> syndrome = (0^0, 0^1) = (0,1) = 1
    if module.bit_flip_syndrome([0, 0, 1]) != 1:
        failures.append("syndrome of |001> should be 1")
    if module.bit_flip_error_index(1) != 2:
        failures.append("syndrome 1 -> error on qubit 2")

    # Correction: majority vote
    if module.bit_flip_correct([1, 0, 0]) != [0, 0, 0]:
        failures.append("correct([1,0,0]) should give [0,0,0]")
    if module.bit_flip_correct([1, 1, 0]) != [1, 1, 1]:
        failures.append("correct([1,1,0]) should give [1,1,1]")
    if module.bit_flip_correct([0, 0, 0]) != [0, 0, 0]:
        failures.append("correct([0,0,0]) should give [0,0,0]")

    # Bad input
    try:
        module.bit_flip_syndrome([0, 1])
        failures.append("should raise on wrong length")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Bit-flip code syndrome decoding correct"],
    }
