"""Compact phase roundtrip - bare-file exemplar.

Teaches: the shortest complete roundtrip drill within budget."""


def phase_bits_roundtrip(phase, n_qubits):
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    if not 0.0 <= phase < 1.0:
        raise ValueError("phase must lie in [0, 1)")
    grid = int(phase * 2**n_qubits)
    return grid / float(2**n_qubits)


def roundtrip_error_table(phases, n_qubits):
    table = {}
    for phase in phases:
        table[phase] = abs(phase_bits_roundtrip(phase, n_qubits) - phase)
    return table


def _self_test():
    assert phase_bits_roundtrip(0.375, 3) == 0.375
    for phase in (0.25, 0.5, 0.75):
        assert phase_bits_roundtrip(phase, 2) == phase
    assert roundtrip_error_table([0.0, 0.375], 3) == {0.0: 0.0, 0.375: 0.0}
    for bad_phase in (1.0, -0.1):
        try:
            phase_bits_roundtrip(bad_phase, 3)
        except ValueError:
            pass
        else:
            raise AssertionError("phase outside [0, 1) must raise")
    try:
        phase_bits_roundtrip(0.5, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("n_qubits 0 must raise")


_self_test()
