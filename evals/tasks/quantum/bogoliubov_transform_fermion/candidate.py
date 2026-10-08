import math


def bogoliubov_basis_energy(theta: float, epsilon: float, delta: float) -> float:
    """Compute the single-mode Bogoliubov quasiparticle energy.

    For a fermionic quadratic Hamiltonian with on-site energy epsilon and
    pairing amplitude delta, the Bogoliubov rotation angle theta diagonalizes
    the Hamiltonian. The quasiparticle energy is

        E = sqrt(epsilon^2 + delta^2)

    independent of theta, but theta sets the rotation:
        tan(2*theta) = delta / epsilon
    """
    return math.sqrt(epsilon * epsilon + delta * delta)


def bogoliubov_angle(epsilon: float, delta: float) -> float:
    """Return the Bogoliubov rotation angle theta such that

        tan(2*theta) = delta / epsilon

    Returns theta in (-pi/4, pi/4].
    """
    if epsilon == 0.0 and delta == 0.0:
        return 0.0
    return 0.5 * math.atan2(delta, epsilon)


def bogoliubov_ground_state_energy(epsilon: float, delta: float) -> float:
    """Return the ground-state energy of the single-mode Bogoliubov Hamiltonian.

    The BdG Hamiltonian has eigenvalues +/- E with E = sqrt(eps^2 + delta^2);
    the ground-state (vacuum) energy is -E.
    """
    return -math.sqrt(epsilon * epsilon + delta * delta)


def bogoliubov_transform_coefficients(theta: float) -> tuple[float, float]:
    """Return the (u, v) coefficients of the Bogoliubov transform

        gamma = u * c + v * c^dagger

    where u = cos(theta), v = sin(theta).
    """
    return (math.cos(theta), math.sin(theta))
