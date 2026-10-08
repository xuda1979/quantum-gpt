def phase_flip_syndrome(phase_parity: list[int]) -> int:
    """Compute the syndrome for the 3-qubit phase-flip code.

    The phase-flip code encodes |+> -> |+++>, |-> -> |--->. After measuring
    in the X basis, the syndrome compares consecutive phase parities:
        s_high = p0 XOR p1
        s_low  = p1 XOR p2
    Returned as integer s_high*2 + s_low in {0,1,2,3}.

    `phase_parity` is a list of three +1/-1 outcomes (X-basis measurements
    represented as +/-1; pass 0/1 by converting -1->1, +1->0 first).
    """
    if len(phase_parity) != 3:
        raise ValueError("expected 3 phase parities")
    bits = []
    for v in phase_parity:
        if v not in (0, 1):
            raise ValueError("phase parities must be 0 or 1")
        bits.append(v)
    p0, p1, p2 = bits
    s_high = p0 ^ p1
    s_low = p1 ^ p2
    return s_high * 2 + s_low


def phase_flip_error_index(syndrome: int) -> int:
    """Map a syndrome to the flipped-qubit index, or -1 for no error.

    Same mapping as the bit-flip code but interpreted on phase parities.
    """
    if syndrome not in (0, 1, 2, 3):
        raise ValueError("syndrome must be in 0..3")
    if syndrome == 0:
        return -1
    if syndrome == 2:
        return 0
    if syndrome == 1:
        return 2
    return 1


def phase_flip_correct_amplitudes(amplitudes: list[complex], error_index: int) -> list[complex]:
    """Apply a Z gate to the qubit at `error_index` to correct a phase flip.
    error_index = -1 means no correction.
    """
    if len(amplitudes) != 3:
        raise ValueError("expected 3 amplitudes")
    if error_index < -1 or error_index > 2:
        raise ValueError("error_index must be in -1..2")
    out = list(amplitudes)
    if error_index >= 0:
        out[error_index] = -out[error_index]
    return out
