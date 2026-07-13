def hadamard_test_expectation(prob_zero: float) -> float:
    """Recover Re(<psi|U|psi>) from a Hadamard test.

    In the standard Hadamard test, the probability of measuring 0 on the
    control qubit is  P(0) = (1 + Re(<psi|U|psi>)) / 2.

    Therefore Re(<psi|U|psi>) = 2*P(0) - 1.
    """
    if not 0.0 <= prob_zero <= 1.0:
        raise ValueError("prob_zero must be in [0, 1]")
    return 2.0 * prob_zero - 1.0


def hadamard_test_prob_zero(real_expectation: float) -> float:
    """Inverse of the Hadamard test: given Re(<psi|U|psi>), return P(0)."""
    if not -1.0 <= real_expectation <= 1.0:
        raise ValueError("real expectation must be in [-1, 1]")
    return (1.0 + real_expectation) / 2.0


def hadamard_test_imaginary(prob_zero_swap: float) -> float:
    """Recover Im(<psi|U|psi>) using the variant Hadamard test where the
    control qubit is initialized with an S^dagger (phase) gate.

    P(0) for this variant equals (1 - Im(<psi|U|psi>)) / 2.
    """
    if not 0.0 <= prob_zero_swap <= 1.0:
        raise ValueError("prob_zero must be in [0, 1]")
    return 1.0 - 2.0 * prob_zero_swap
