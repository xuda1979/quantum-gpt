import numpy as np


def prepare_bell_state() -> np.ndarray:
    """
    Prepare a Bell state |Phi+> = (|00> + |11>) / sqrt(2).

    Returns:
        A 4x4 density matrix representing the Bell state.
    """
    # Bell state |Phi+> = (|00> + |11>) / sqrt(2)
    psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    # Density matrix
    rho = np.outer(psi, psi.conj())
    return rho


def apply_hadamard(state: np.ndarray) -> np.ndarray:
    """
    Apply Hadamard gate to the first qubit of a two-qubit state.

    Args:
        state: A 4-element state vector or 4x4 density matrix.

    Returns:
        The transformed state.
    """
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

    if state.shape == (4, 4):
        # Density matrix: apply H on first qubit
        # H ⊗ I
        H_tensor_I = np.kron(H, np.eye(2, dtype=complex))
        return H_tensor_I @ state @ H_tensor_I.conj().T
    else:
        # State vector
        H_tensor_I = np.kron(H, np.eye(2, dtype=complex))
        return H_tensor_I @ state


def apply_cnot(state: np.ndarray) -> np.ndarray:
    """
    Apply CNOT gate with first qubit as control and second as target.

    Args:
        state: A 4-element state vector or 4x4 density matrix.

    Returns:
        The transformed state.
    """
    CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)

    if state.shape == (4, 4):
        return CNOT @ state @ CNOT.conj().T
    else:
        return CNOT @ state


def prepare_bell_state_via_gates() -> np.ndarray:
    """
    Prepare a Bell state using Hadamard and CNOT gates.

    Returns:
        A 4x4 density matrix representing the Bell state.
    """
    # Start with |00>
    psi = np.array([1, 0, 0, 0], dtype=complex)
    # Apply H to first qubit
    psi = apply_hadamard(psi)
    # Apply CNOT
    psi = apply_cnot(psi)
    # Convert to density matrix
    rho = np.outer(psi, psi.conj())
    return rho


def parity_check(state: np.ndarray) -> float:
    """
    Perform a parity check on a two-qubit state.

    The parity check measures whether the two qubits have the same value (even parity)
    or different values (odd parity). For a Bell state |Phi+> = (|00> + |11>)/sqrt(2),
    the parity is always even (both qubits are the same).

    Args:
        state: A 4x4 density matrix or 4-element state vector.

    Returns:
        The probability of even parity (00 or 11).
    """
    if state.shape == (4, 4):
        rho = state
    else:
        rho = np.outer(state, state.conj())

    # Even parity: |00> and |11>
    # Probability of |00> is rho[0,0], probability of |11> is rho[3,3]
    p_even = np.real(rho[0, 0] + rho[3, 3])
    return float(p_even)


def parity_check_via_measurement(state: np.ndarray) -> tuple[float, float]:
    """
    Perform a parity check by measuring in the computational basis.

    Args:
        state: A 4x4 density matrix or 4-element state vector.

    Returns:
        A tuple (p_even, p_odd) where p_even is the probability of even parity
        (00 or 11) and p_odd is the probability of odd parity (01 or 10).
    """
    if state.shape == (4, 4):
        rho = state
    else:
        rho = np.outer(state, state.conj())

    p_00 = np.real(rho[0, 0])
    p_01 = np.real(rho[1, 1])
    p_10 = np.real(rho[2, 2])
    p_11 = np.real(rho[3, 3])

    p_even = p_00 + p_11
    p_odd = p_01 + p_10

    return float(p_even), float(p_odd)


def verify_bell_state(rho: np.ndarray, tolerance: float = 1e-10) -> bool:
    """
    Verify that a density matrix represents the Bell state |Phi+>.

    Args:
        rho: A 4x4 density matrix.
        tolerance: Numerical tolerance for comparison.

    Returns:
        True if the state is the Bell state |Phi+>, False otherwise.
    """
    expected = prepare_bell_state()
    return np.allclose(rho, expected, atol=tolerance)


def bell_state_parity_check() -> dict:
    """
    Complete Bell state preparation and parity check.

    Returns:
        A dictionary containing:
        - 'density_matrix': The 4x4 density matrix of the Bell state
        - 'p_even': Probability of even parity
        - 'p_odd': Probability of odd parity
        - 'is_bell_state': Whether the state is verified as Bell state
    """
    # Prepare Bell state
    rho = prepare_bell_state_via_gates()

    # Verify it's a Bell state
    is_bell = verify_bell_state(rho)

    # Perform parity check
    p_even, p_odd = parity_check_via_measurement(rho)

    return {"density_matrix": rho, "p_even": p_even, "p_odd": p_odd, "is_bell_state": is_bell}


if __name__ == "__main__":
    result = bell_state_parity_check()
    print("Bell State Density Matrix:")
    print(result["density_matrix"])
    print(f"\nProbability of even parity (00 or 11): {result['p_even']:.6f}")
    print(f"Probability of odd parity (01 or 10): {result['p_odd']:.6f}")
    print(f"Is Bell state: {result['is_bell_state']}")
