def rb_average_gate_fidelity(alpha: float, dim: int = 2) -> float:
    """Compute the average gate fidelity from the RB decay parameter alpha.

    For a d-dimensional system, the average gate fidelity of the noise
    channel is
        F_avg = alpha + (1 - alpha) / d

    where alpha is the depolarizing parameter (per Clifford) extracted
    from the RB decay curve F(m) = A * alpha^m + B.
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be in [0, 1]")
    if dim < 2:
        raise ValueError("dim must be >= 2")
    return alpha + (1.0 - alpha) / dim


def rb_decay_parameter(f_avg: float, dim: int = 2) -> float:
    """Inverse of rb_average_gate_fidelity: given F_avg and d, return alpha."""
    if not (1.0 / dim) <= f_avg <= 1.0:
        raise ValueError(f"f_avg must be in [1/d, 1] = [1/{dim}, 1]")
    if dim < 2:
        raise ValueError("dim must be >= 2")
    return (f_avg - 1.0 / dim) / (1.0 - 1.0 / dim)


def rb_survival_probability(alpha: float, m: int, A: float = 1.0, B: float = 0.0) -> float:
    """Return the RB survival probability after m Cliffords:
    F(m) = A * alpha^m + B
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be in [0, 1]")
    if m < 0:
        raise ValueError("m must be non-negative")
    return A * (alpha**m) + B
