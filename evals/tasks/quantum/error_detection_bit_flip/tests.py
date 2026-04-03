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

    # No error — syndrome should be [0, 0], state recovered correctly
    for init in (0, 1):
        for err_q in (0, 1, 2):
            result = module.bit_flip_code(init, err_q)

            if not isinstance(result, dict):
                failures.append(f"bit_flip_code({init},{err_q}) must return dict, got {type(result)}")
                continue

            syndrome = result.get("syndrome")
            corrected = result.get("corrected_state")

            if not isinstance(syndrome, list) or len(syndrome) != 2:
                failures.append(f"bit_flip_code({init},{err_q}): syndrome must be list of length 2, got {syndrome}")
                continue

            # Syndrome correctness: only one qubit flipped
            # Error on qubit 0: s0=1, s1=0
            # Error on qubit 1: s0=1, s1=1
            # Error on qubit 2: s0=0, s1=1
            expected_syndromes = {0: [1, 0], 1: [1, 1], 2: [0, 1]}
            expected_syndrome = expected_syndromes[err_q]
            if syndrome != expected_syndrome:
                failures.append(
                    f"bit_flip_code({init},{err_q}): syndrome={syndrome}, expected {expected_syndrome}"
                )

            if corrected != init:
                failures.append(
                    f"bit_flip_code({init},{err_q}): corrected_state={corrected}, expected {init}"
                )

    return {
        "passed": not failures,
        "details": failures or ["Bit-flip code correct for all initial states and error positions"],
    }
