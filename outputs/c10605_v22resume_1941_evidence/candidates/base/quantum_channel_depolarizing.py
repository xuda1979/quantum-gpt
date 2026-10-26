import numpy as np


def depolarizing_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """
    Apply a depolarizing channel to a single-qubit density matrix.

    The depolarizing channel is defined as:
    E(rho) = (1 - p) * rho + (p/3) * (X rho X + Y rho Y + Z rho Z)

    where X, Y, Z are the Pauli matrices.

    Parameters:
    -----------
    rho : np.ndarray
        Input density matrix (2x2 for single qubit)
    p : float
        Depolarizing probability (0 <= p <= 1)

    Returns:
    --------
    np.ndarray
        Output density matrix after applying the depolarizing channel
    """
    if p < 0 or p > 1:
        raise ValueError("Depolarizing probability p must be in [0, 1]")

    if rho.shape != (2, 2):
        raise ValueError("Input density matrix must be 2x2")

    # Pauli matrices
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    # Apply the depolarizing channel
    result = (1 - p) * rho + (p / 3) * (X @ rho @ X + Y @ rho @ Y + Z @ rho @ Z)

    # Ensure the result is Hermitian (numerical stability)
    result = (result + result.conj().T) / 2

    return result


def depolarizing_channel_nqubit(rho: np.ndarray, p: float) -> np.ndarray:
    """
    Apply a depolarizing channel to an n-qubit density matrix.

    For an n-qubit system, the depolarizing channel applies a random Pauli
    error to each qubit independently with probability p.

    Parameters:
    -----------
    rho : np.ndarray
        Input density matrix (2^n x 2^n)
    p : float
        Depolarizing probability per qubit (0 <= p <= 1)

    Returns:
    --------
    np.ndarray
        Output density matrix after applying the depolarizing channel
    """
    if p < 0 or p > 1:
        raise ValueError("Depolarizing probability p must be in [0, 1]")

    dim = rho.shape[0]
    if dim != dim or dim % 2 != 0:
        raise ValueError("Input density matrix must be square with even dimension")

    # Determine number of qubits
    n = int(np.log2(dim))
    if 2**n != dim:
        raise ValueError("Dimension must be a power of 2")

    # Pauli matrices
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    paulis = [I, X, Y, Z]

    # For each qubit, apply the depolarizing channel
    # E(rho) = sum over all Pauli strings P of (p/3)^k * (1-p)^(n-k) * P rho P^dagger
    # where k is the number of non-identity Paulis

    result = np.zeros_like(rho, dtype=complex)

    for mask in range(4**n):
        # Determine which Pauli to apply to each qubit
        pauli_string = []
        weight = 0
        for q in range(n):
            idx = (mask >> (2 * q)) & 3
            pauli_string.append(paulis[idx])
            if idx != 0:
                weight += 1

        # Probability of this Pauli string
        prob = (p / 3) ** weight * (1 - p) ** (n - weight)

        # Build the full Pauli operator
        P = pauli_string[0]
        for q in range(1, n):
            P = np.kron(P, pauli_string[q])

        result += prob * (P @ rho @ P.conj().T)

    # Ensure the result is Hermitian (numerical stability)
    result = (result + result.conj().T) / 2

    return result


def simulate_depolarizing_channel(rho: np.ndarray, p: float, n_qubits: int = None) -> np.ndarray:
    """
    Simulate a depolarizing channel on a density matrix.

    Parameters:
    -----------
    rho : np.ndarray
        Input density matrix
    p : float
        Depolarizing probability
    n_qubits : int, optional
        Number of qubits. If None, inferred from the dimension of rho.

    Returns:
    --------
    np.ndarray
        Output density matrix after applying the depolarizing channel
    """
    dim = rho.shape[0]

    if n_qubits is None:
        n_qubits = int(np.log2(dim))
        if 2**n_qubits != dim:
            raise ValueError("Dimension must be a power of 2")

    if n_qubits == 1:
        return depolarizing_channel(rho, p)
    else:
        return depolarizing_channel_nqubit(rho, p)


def depolarizing_channel_kraus(rho: np.ndarray, p: float) -> np.ndarray:
    """
    Apply a depolarizing channel using Kraus operators.

    The Kraus operators for the single-qubit depolarizing channel are:
    K0 = sqrt(1 - p) * I
    K1 = sqrt(p/3) * X
    K2 = sqrt(p/3) * Y
    K3 = sqrt(p/3) * Z

    Parameters:
    -----------
    rho : np.ndarray
        Input density matrix (2x2)
    p : float
        Depolarizing probability (0 <= p <= 1)

    Returns:
    --------
    np.ndarray
        Output density matrix
    """
    if p < 0 or p > 1:
        raise ValueError("Depolarizing probability p must be in [0, 1]")

    if rho.shape != (2, 2):
        raise ValueError("Input density matrix must be 2x2")

    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    K0 = np.sqrt(1 - p) * I
    K1 = np.sqrt(p / 3) * X
    K2 = np.sqrt(p / 3) * Y
    K3 = np.sqrt(p / 3) * Z

    result = np.zeros_like(rho, dtype=complex)
    for K in [K0, K1, K2, K3]:
        result += K @ rho @ K.conj().T

    # Ensure the result is Hermitian (numerical stability)
    result = (result + result.conj().T) / 2

    return result
