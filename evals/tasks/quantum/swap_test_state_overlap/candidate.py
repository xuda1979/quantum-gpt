def swap_test_overlap(prob_zero: float) -> float:
    """Given the measured probability of outcome 0 on the SWAP-test ancilla,
    return the squared overlap |<psi|phi>|^2 of the two tested states.

    Relation: P(0) = (1 + |<psi|phi>|^2) / 2  =>  |<psi|phi>|^2 = 2*P(0) - 1.
    """
    if not 0.0 <= prob_zero <= 1.0:
        raise ValueError("prob_zero must be in [0, 1]")
    return 2.0 * prob_zero - 1.0


def swap_test_prob_zero(psi: list[complex], phi: list[complex]) -> float:
    """Compute the SWAP-test ancilla P(0) for two pure states.

    P(0) = (1 + |<psi|phi>|^2) / 2.
    """
    if len(psi) != len(phi):
        raise ValueError("states must have the same dimension")
    if not psi:
        raise ValueError("states must be non-empty")
    overlap = sum(p.conjugate() * q for p, q in zip(psi, phi, strict=False))
    return (1.0 + abs(overlap) ** 2) / 2.0


def fidelity(psi: list[complex], phi: list[complex]) -> float:
    """Return the squared overlap |<psi|phi>|^2 of two pure states."""
    if len(psi) != len(phi):
        raise ValueError("states must have the same dimension")
    overlap = sum(p.conjugate() * q for p, q in zip(psi, phi, strict=False))
    return abs(overlap) ** 2
