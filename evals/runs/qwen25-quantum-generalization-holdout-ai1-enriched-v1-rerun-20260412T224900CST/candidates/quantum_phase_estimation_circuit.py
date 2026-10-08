# Reference implementation
import cmath


def phase_estimation(phase: float, n_bits: int) -> int:
    """Return the integer representation of exp(i * phase) modulo 2**n_bits."""
    return int(round(cmath.exp(phase * 1j).modulus * 2 ** -n_bits))


def phase_from_measurement(measurement: int, n_bits: int) -> float:
    """Return the phase corresponding to the least significant bit measurement.

    Assumes measurement is already normalized to be between 0 and 2**n_bits - 1.
    """
    return measurement * 2 ** -1.0 * n_bits
