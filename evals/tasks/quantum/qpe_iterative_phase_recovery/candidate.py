def iterative_qpe_phase(measurements: list[int], n_counting_bits: int) -> float:
    """Recover the phase from iterative QPE bit measurements.

    In iterative QPE, each measurement yields one bit of the phase
    register (most-significant bit first). Given the list of `n_counting_bits`
    measured bits (each 0 or 1), reconstruct the phase estimate

        phase = sum_{k=0}^{n-1} bit_k / 2^(k+1)

    where bit_0 is the most-significant bit. Return a float in [0, 1).
    """
    if len(measurements) != n_counting_bits:
        raise ValueError("measurements length must equal n_counting_bits")
    phase = 0.0
    for k, bit in enumerate(measurements):
        if bit not in (0, 1):
            raise ValueError("each measurement must be 0 or 1")
        phase += bit / (1 << (k + 1))
    return phase


def phase_to_bitstring(phase: float, n_counting_bits: int) -> str:
    """Convert a phase in [0,1) to its n-bit QPE bitstring (MSB first).

    Phases that would round up to 1.0 (i.e. 2^n) wrap to the largest
    representable code (2^n - 1, all ones) rather than to 0, matching the
    convention that a phase just below 1.0 is reported as all-ones.
    """
    n_states = 1 << n_counting_bits
    scaled = round(phase * n_states)
    if scaled >= n_states:
        scaled = n_states - 1
    if scaled < 0:
        scaled = 0
    return format(scaled, f"0{n_counting_bits}b")
