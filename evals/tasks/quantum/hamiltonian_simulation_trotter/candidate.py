import cmath


def trotter_step_count(total_time: float, dt: float, order: int = 1) -> int:
    """Return the number of Trotter steps to simulate `total_time` using
    step size `dt`. For 2nd-order Trotter (symmetric) each "step" applies
    a half-step + full-step + half-step pattern, but the count is still
    total_time / dt rounded to the nearest integer."""
    if dt <= 0:
        raise ValueError("dt must be positive")
    if total_time < 0:
        raise ValueError("total_time must be non-negative")
    if order not in (1, 2):
        raise ValueError("order must be 1 or 2")
    return max(1, int(round(total_time / dt)))


def pauli_z_evolution(state: list[complex], theta: float) -> list[complex]:
    """Apply e^{-i * theta * Z / 2} to a single-qubit state.

    Rz(theta) = [[e^{-i theta/2}, 0], [0, e^{i theta/2}]].
    """
    if len(state) != 2:
        raise ValueError("state must be a 2-d vector")
    a, b = state
    return [a * cmath.exp(-1j * theta / 2.0), b * cmath.exp(1j * theta / 2.0)]


def trotter_error_bound(n_steps: int, hamiltonian_norm: float, dt: float, order: int = 1) -> float:
    """Return an upper bound on the Trotter error.

    First-order Lie-Trotter:    err <= n * (commutator_norm) * dt^2 ~ norm * total_time * dt
    For simplicity we use a coarse upper bound:
        order 1: error <= n_steps * (hamiltonian_norm * dt)^2
        order 2: error <= n_steps * (hamiltonian_norm * dt)^3
    """
    if n_steps < 0:
        raise ValueError("n_steps must be non-negative")
    if hamiltonian_norm < 0:
        raise ValueError("hamiltonian_norm must be non-negative")
    if dt < 0:
        raise ValueError("dt must be non-negative")
    if order not in (1, 2):
        raise ValueError("order must be 1 or 2")
    base = hamiltonian_norm * dt
    if order == 1:
        return n_steps * base * base
    return n_steps * base * base * base
