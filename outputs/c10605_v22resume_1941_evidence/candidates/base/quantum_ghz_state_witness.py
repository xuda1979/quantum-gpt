import numpy as np


def prepare_ghz_state(n_qubits: int) -> np.ndarray:
    """
    Prepare an n-qubit GHZ state: (|0...0> + |1...1>) / sqrt(2)

    Args:
        n_qubits: Number of qubits

    Returns:
        A 2^n dimensional numpy array representing the state vector
    """
    dim = 2**n_qubits
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0 / np.sqrt(2)
    state[-1] = 1.0 / np.sqrt(2)
    return state


def compute_entanglement_witness(state: np.ndarray, n_qubits: int) -> float:
    """
    Compute an entanglement witness for the GHZ state.

    For an n-qubit GHZ state, we can use the witness:
    W = I - 2 * |GHZ><GHZ|

    A state is entangled if <W> < 0.
    For the GHZ state itself, <W> = 1 - 2*1 = -1.

    More generally, we can compute the expectation value of the witness
    for the given state.

    Args:
        state: State vector of dimension 2^n
        n_qubits: Number of qubits

    Returns:
        The expectation value of the entanglement witness
    """
    dim = 2**n_qubits
    ghz = prepare_ghz_state(n_qubits)

    # W = I - 2 * |GHZ><GHZ|
    # <W> = 1 - 2 * |<GHZ|state>|^2
    overlap = np.vdot(ghz, state)
    witness_value = 1.0 - 2.0 * np.abs(overlap) ** 2
    return float(np.real(witness_value))


def is_entangled(state: np.ndarray, n_qubits: int, threshold: float = 1e-10) -> bool:
    """
    Determine if a state is entangled using the GHZ entanglement witness.

    Args:
        state: State vector of dimension 2^n
        n_qubits: Number of qubits
        threshold: Numerical threshold

    Returns:
        True if the state is entangled (witness value < 0)
    """
    witness_value = compute_entanglement_witness(state, n_qubits)
    return witness_value < -threshold


def ghz_state_fidelity(state: np.ndarray, n_qubits: int) -> float:
    """
    Compute the fidelity between a given state and the ideal GHZ state.

    Args:
        state: State vector of dimension 2^n
        n_qubits: Number of qubits

    Returns:
        Fidelity value between 0 and 1
    """
    ghz = prepare_ghz_state(n_qubits)
    overlap = np.vdot(ghz, state)
    return float(np.abs(overlap) ** 2)


def verify_ghz_preparation(n_qubits: int) -> dict:
    """
    Verify GHZ state preparation by checking:
    1. The state is normalized
    2. The state has the correct structure (only |0...0> and |1...1> components)
    3. The entanglement witness confirms entanglement
    4. The fidelity with ideal GHZ is 1

    Args:
        n_qubits: Number of qubits

    Returns:
        Dictionary with verification results
    """
    state = prepare_ghz_state(n_qubits)
    dim = 2**n_qubits

    # Check normalization
    norm = np.vdot(state, state).real
    is_normalized = np.isclose(norm, 1.0, atol=1e-10)

    # Check structure: only first and last elements should be non-zero
    non_zero_indices = np.where(np.abs(state) > 1e-10)[0]
    expected_indices = [0, dim - 1]
    has_correct_structure = set(non_zero_indices.tolist()) == set(expected_indices)

    # Check amplitudes
    correct_amplitudes = np.isclose(state[0], 1.0 / np.sqrt(2), atol=1e-10) and np.isclose(
        state[-1], 1.0 / np.sqrt(2), atol=1e-10
    )

    # Entanglement witness
    witness_value = compute_entanglement_witness(state, n_qubits)
    is_entangled_state = is_entangled(state, n_qubits)

    # Fidelity
    fidelity = ghz_state_fidelity(state, n_qubits)

    return {
        "n_qubits": n_qubits,
        "is_normalized": is_normalized,
        "has_correct_structure": has_correct_structure,
        "correct_amplitudes": correct_amplitudes,
        "witness_value": witness_value,
        "is_entangled": is_entangled_state,
        "fidelity": fidelity,
        "all_checks_passed": is_normalized
        and has_correct_structure
        and correct_amplitudes
        and is_entangled_state,
    }


def main():
    """
    Main function to demonstrate GHZ state preparation and entanglement witness.
    """
    results = {}
    for n in range(2, 6):
        results[n] = verify_ghz_preparation(n)

    return results


if __name__ == "__main__":
    results = main()
    for n, res in results.items():
        print(f"n={n}: {res}")
