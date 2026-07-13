def phase_estimation(phase, n_bits):
    """
    Simulates the measurement outcome of a Quantum Phase Estimation circuit.
    Given a phase phi (0 <= phi < 1) and n_bits of precision, returns the
    integer measurement result.
    
    The measurement result is round(phi * 2^n_bits).
    """
    if not (0 <= phase < 1):
        raise ValueError("Phase must be in the range [0, 1)")

    precision = 2 ** n_bits
    result = round(phase * precision)

    # Ensure the result is within the valid range [0, 2^n_bits - 1]
    # This handles cases where rounding might push the value to 2^n_bits
    if result >= precision:
        result = precision - 1

    return result


def phase_from_measurement(measurement, n_bits):
    """
    Recovers the estimated phase from a measurement outcome.
    
    Args:
        measurement (int): The integer result from phase_estimation.
        n_bits (int): The number of bits used in the estimation.
        
    Returns:
        float: The estimated phase value.
    """
    if not (0 <= measurement < 2 ** n_bits):
        raise ValueError("Measurement must be in the range [0, 2^n_bits)")

    precision = 2 ** n_bits
    return measurement / precision


# Expose functions for the test runner
__all__ = ['phase_estimation', 'phase_from_measurement']
