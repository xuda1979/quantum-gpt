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

    cases = [
        (0.0, 3, [0, 0, 0]),
        (0.25, 4, [0, 1, 0, 0]),
        (0.5, 4, [1, 0, 0, 0]),
        (0.875, 4, [1, 1, 1, 0]),
    ]

    for phase, n_qubits, expected in cases:
        bits = module.phase_to_register_bits(phase, n_qubits)
        if bits != expected:
            failures.append(
                f"phase_to_register_bits({phase}, {n_qubits}) -> {bits}, expected {expected}"
            )

    for phase, n_qubits, _ in cases:
        bits = module.phase_to_register_bits(phase, n_qubits)
        recovered = module.register_bits_to_phase(bits)
        scale = 1 << n_qubits
        if abs(recovered - phase) > 1.0 / scale:
            failures.append(
                f"round-trip {phase} with {n_qubits} qubits -> {recovered}, tolerance {1.0/scale}"
            )

    try:
        module.phase_to_register_bits(1.0, 2)
        failures.append("phase_to_register_bits did not reject phase == 1.0")
    except ValueError:
        pass

    try:
        module.register_bits_to_phase([])
        failures.append("register_bits_to_phase did not reject empty list")
    except ValueError:
        pass

    try:
        module.register_bits_to_phase([0, 2, 1])
        failures.append("register_bits_to_phase did not reject invalid bit value")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["phase register round trips correctly"],
    }
