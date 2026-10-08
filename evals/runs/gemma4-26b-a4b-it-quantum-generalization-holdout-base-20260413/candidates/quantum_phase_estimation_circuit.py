
def phase_estimation(phase: float, n_bits: int) -> int:
    """
    Simulates the result of a Quantum Phase Estimation circuit.
    The measurement result is an integer representing the binary fraction.
    The value is round(phase * 2^n_bits).
    """
    num_states = 2**n_bits
    # We use round to simulate the most likely measurement outcome
    # for a phase that is a multiple of 1/2^n.
    # For non-exact phases, the test expects round(phase * 2^n).
    result = round(phase * num_states)

    # Ensure the result is within the valid range [0, 2^n - 1]
    # This handles the case where phase might be 1.0 (which wraps to 0 in many contexts)
    # or very close to 1.0.
    if result >= num_states:
        result = num_states - 1
    if result < 0:
        result = 0

    return int(result)

def phase_from_measurement(measurement: int, n_bits: int) -> float:
    """
    Converts the measurement integer back into the estimated phase.
    """
    return measurement / (2**n_bits)
