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
        ([0], 0, 0.0),
        ([1], 1, 0.5),
        ([1, 0], 2, 0.5),
        ([0, 1, 1], 3, 0.375),
        ([1, 1, 0, 0], 12, 0.75),
    ]
    for bits, expected_int, expected_phase in cases:
        actual_int = module.bit_register_to_int(bits)
        if actual_int != expected_int:
            failures.append(f"bit_register_to_int({bits!r}) -> {actual_int}, expected {expected_int}")
        actual_phase = module.measurement_register_to_phase(bits)
        if not math.isclose(actual_phase, expected_phase, abs_tol=1e-9):
            failures.append(
                f"measurement_register_to_phase({bits!r}) -> {actual_phase}, expected {expected_phase}"
            )

    for bad_bits in ([], [0, 2], [1, -1], [1, 3, 0]):
        try:
            module.bit_register_to_int(bad_bits)
        except ValueError:
            continue
        except Exception as exc:
            failures.append(f"bit_register_to_int({bad_bits!r}) raised {type(exc).__name__}, expected ValueError")
        else:
            failures.append(f"bit_register_to_int({bad_bits!r}) did not raise ValueError")

    return {
        "passed": not failures,
        "details": failures or ["binary measurement decoder enforces {0,1} registers and correct phase conversion"],
    }
