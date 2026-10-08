import numpy as np


def heisenberg_chain_matrix(J: float, h: float) -> np.ndarray:
    """
    2-qubit transverse-field Ising chain Hamiltonian:

        H = J (Z Z) + h (X I + I X)

    The Ising coupling J Z Z and the transverse field h (X I + I X) do NOT
    commute, so a product-form (Trotter) evolution is only approximately
    correct and converges with the number of steps. Returns the 4x4
    Hermitian matrix (complex dtype).
    """
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    I = np.eye(2, dtype=complex)
    return J * np.kron(Z, Z) + h * (np.kron(X, I) + np.kron(I, X))


def _expm(h: np.ndarray, theta: float) -> np.ndarray:
    """exp(-i theta H) for a Hermitian matrix H via eigendecomposition."""
    w, v = np.linalg.eigh(h)
    return (v * np.exp(-1j * w * theta)) @ v.conj().T


def exact_evolution_matrix(J: float, h: float, t: float) -> np.ndarray:
    """The exact time-evolution unitary exp(-i t H) for the chain."""
    return _expm(heisenberg_chain_matrix(J, h), t)


def trotter_evolution_matrix(J: float, h: float, t: float, steps: int) -> np.ndarray:
    """
    First-order Trotterized evolution with the split

        U(t) ~ [ exp(-i dt J Z Z) exp(-i dt h (X I + I X)) ] ** steps,
        dt = t / steps.

    Returns the 4x4 unitary matrix.
    """
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    I = np.eye(2, dtype=complex)
    dt = t / steps
    u_zz = _expm(J * np.kron(Z, Z), dt)
    u_field = _expm(h * (np.kron(X, I) + np.kron(I, X)), dt)
    u_step = u_zz @ u_field
    u = np.eye(4, dtype=complex)
    for _ in range(steps):
        u = u_step @ u
    return u


def trotter_max_abs_error(J: float, h: float, t: float, steps: int) -> float:
    """Max entrywise absolute difference between Trotter and exact unitaries."""
    diff = trotter_evolution_matrix(J, h, t, steps) - exact_evolution_matrix(J, h, t)
    return float(np.max(np.abs(diff)))
