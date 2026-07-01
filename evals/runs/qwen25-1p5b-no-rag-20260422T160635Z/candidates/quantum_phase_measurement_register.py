from typing import List, Tuple

def phase_estimation(phase: float, n_bits: int) -> int:
    if n_bits <= 0:
        raise ValueError("n_bits must be positive")
    if not (0.0 <= phase < 1.0):
        raise ValueError("phase must be in [0, 1)")
    scale = 1 << n_bits
    return int(round(phase * scale)) % scale

def phase_from_measurement(measurement: int, n_bits: int) -> float:
    if n_bits <= 0:
        raise ValueError("n_bits must be positive")
    scale = 1 << n_bits
    if not (0 <= measurement < scale):
        raise ValueError("measurement out of range")
    return measurement / scale

def test_phase_estimation():
    cases = [
        (0.0, 3, 0),
        (0.25, 3, 2),
        (0.5, 3, 4),
        (0.75, 4, 12),
        (0.125, 3, 1),
        (1.0 / 3.0, 3, 3),
    ]
    for phase, n_bits, expected in cases:
        actual = phase_estimation(phase, n_bits)
