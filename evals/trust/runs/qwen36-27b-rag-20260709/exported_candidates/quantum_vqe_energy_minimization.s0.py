import math


def ry_state(theta: float) -> tuple[float, float]:
    """Return the statevector after applying RY(theta) to |0>.

    Returns (alpha, beta) where state = alpha|0> + beta|1>.
    """
    return (math.cos(theta / 2), math.sin(theta / 2))


def energy_expectation(theta: float, h_coeffs: tuple[float, float, float]) -> float:
    """Compute <psi(theta)| H |psi(theta)> for a single-qubit Hamiltonian.

    H = c_I * I + c_Z * Z + c_X * X

    h_coeffs = (c_I, c_Z, c_X)

    The ansatz is RY(theta)|0>.
    """
    c_i, c_z, c_x = h_coeffs
    alpha, beta = ry_state(theta)
    # <Z> = |alpha|^2 - |beta|^2
    exp_z = alpha**2 - beta**2
    # <X> = 2 * Re(alpha * conj(beta)) — both real here
    exp_x = 2 * alpha * beta
    return c_i + c_z * exp_z + c_x * exp_x


def find_min_energy(
    h_coeffs: tuple[float, float, float], n_samples: int = 200
) -> tuple[float, float]:
    """Brute-force search for the theta that minimizes energy_expectation.

    Returns (best_theta, best_energy). Search over [0, 2*pi).
    """
    best_theta = 0.0
    best_energy = float("inf")
    for i in range(n_samples):
        theta = 2 * math.pi * i / n_samples
        e = energy_expectation(theta, h_coeffs)
        if e < best_energy:
            best_energy = e
            best_theta = theta
    return (best_theta, best_energy)
