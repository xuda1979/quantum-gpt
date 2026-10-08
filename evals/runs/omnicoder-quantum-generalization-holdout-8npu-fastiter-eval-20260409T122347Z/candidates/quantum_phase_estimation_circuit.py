# Reference implementation
def phase_estimation(phase: float, n_bits: int) -> int:
    """Encode a unitary eigenphase into an n-bit integer measurement."""
    if n_bits <= 0:
        raise ValueError("n_bits must be positive")
    scale = 2 ** n_bits
    return round(phase * scale) % scale


def phase_from_measurement(measurement: int, n_bits: int) -> float:
    """Decode an n-bit measurement back to a phase in [0, 1)."""
    if n_bits <= 0:
        raise ValueError("n_bits must be positive")
    scale = 2 ** n_bits
    return measurement / scale
