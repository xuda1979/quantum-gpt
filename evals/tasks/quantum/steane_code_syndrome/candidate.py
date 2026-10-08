def steane_parity_check_matrix() -> list[list[int]]:
    """Return the 3x7 binary parity-check matrix H of the Steane [[7,1,3]] code.

    Each row is a parity check over GF(2); rows are the three independent
    checks of the Hamming [7,4,3] code (Steane uses its dual for the X/Z checks).
    Convention (one valid choice):
        row 0: 1 1 1 0 1 0 0
        row 1: 1 1 0 1 0 1 0
        row 2: 1 0 1 1 0 0 1
    """
    return [
        [1, 1, 1, 0, 1, 0, 0],
        [1, 1, 0, 1, 0, 1, 0],
        [1, 0, 1, 1, 0, 0, 1],
    ]


def steane_syndrome(error_pattern: list[int]) -> list[int]:
    """Compute the 3-bit syndrome of a 7-bit error pattern over GF(2).

    syndrome[i] = (sum_j H[i][j] * error_pattern[j]) mod 2.
    """
    if len(error_pattern) != 7:
        raise ValueError("error_pattern must have 7 bits")
    if any(b not in (0, 1) for b in error_pattern):
        raise ValueError("error_pattern must be binary")
    H = steane_parity_check_matrix()
    return [sum(H[i][j] * error_pattern[j] for j in range(7)) % 2 for i in range(3)]


def steane_correctable(error_pattern: list[int]) -> bool:
    """Return True if a single-bit error pattern is correctable by the Steane code."""
    if len(error_pattern) != 7:
        raise ValueError("error_pattern must have 7 bits")
    weight = sum(error_pattern)
    return weight == 0 or weight == 1
