import math

def phase_estimation(eigenvalue_phase: float, n_counting_bits: int) -> int:
    """Simulate quantum phase estimation for a unitary with eigenvalue e^(2*pi*i*phase).

    Given the true phase (0 <= phase < 1) and the number of counting qubits,
    return the integer measurement outcome that QPE would produce (ideal, no noise).

    The QPE algorithm maps phase -> round(phase * 2^n) mod 2^n.
    """
    n_states = 1 << n_counting_bits
    return round(eigenvalue_phase * n_states) % n_states

def phase_from_measurement(measurement: int, n_counting_bits: int) -> float:
    """Recover the estimated phase from a QPE measurement outcome.

    Returns a float in [0, 1).
    """
    n_states = 1 << n_counting_bits
    return measurement / n_states
