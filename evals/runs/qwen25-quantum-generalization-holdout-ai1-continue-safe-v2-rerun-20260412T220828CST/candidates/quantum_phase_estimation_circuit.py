# Reference implementation


def phase_estimation(phase: float, n_bits: int) -> int:
    """Return the integer representation of exp(i*phase) modulo 2**n_bits."""
    exponent = phase / (2.0 ** n_bits)
    return int(round(exponent)) & ((1 << n_bits) - 1)


def phase_from_measurement(value: int, n_bits: int) -> float:
    """Return the phase corresponding to measurement bitstring value."""
    raw_exponent = value >> n_bits
    coefficient = raw_exponent / (1 << n_bits)
    return coefficient * 2.0 ** n_bits
