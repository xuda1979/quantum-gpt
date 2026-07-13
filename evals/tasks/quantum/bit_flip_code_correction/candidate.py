def bit_flip_syndrome(qubit_states: list[int]) -> int:
    """Compute the syndrome for the 3-qubit bit-flip code.

    The 3-qubit bit-flip code encodes |0> -> |000>, |1> -> |111>.
    Syndrome = (q0 XOR q1, q1 XOR q2) returned as an integer in {0,1,2,3}:
        syndrome bits: s_high = q0 ^ q1, s_low = q1 ^ q2
        syndrome_int = s_high * 2 + s_low

    qubit_states is a list of three 0/1 measurement outcomes.
    """
    if len(qubit_states) != 3:
        raise ValueError("expected 3 qubit states")
    q0, q1, q2 = qubit_states
    for v in (q0, q1, q2):
        if v not in (0, 1):
            raise ValueError("qubit states must be 0 or 1")
    s_high = q0 ^ q1
    s_low = q1 ^ q2
    return s_high * 2 + s_low


def bit_flip_correct(qubit_states: list[int]) -> list[int]:
    """Apply the 3-qubit bit-flip correction based on the syndrome.

    Returns the corrected 3-tuple of qubit states (majority vote).
    """
    if len(qubit_states) != 3:
        raise ValueError("expected 3 qubit states")
    majority = 1 if sum(qubit_states) >= 2 else 0
    return [majority, majority, majority]


def bit_flip_error_index(syndrome: int) -> int:
    """Map a syndrome integer to the index of the flipped qubit, or -1 if no error.

    Syndrome mapping (s_high s_low):
        00 -> no error (-1)
        10 -> qubit 0 flipped
        01 -> qubit 2 flipped
        11 -> qubit 1 flipped
    """
    if syndrome not in (0, 1, 2, 3):
        raise ValueError("syndrome must be in 0..3")
    if syndrome == 0:
        return -1
    if syndrome == 2:  # s_high=1, s_low=0
        return 0
    if syndrome == 1:  # s_high=0, s_low=1
        return 2
    return 1  # syndrome == 3
