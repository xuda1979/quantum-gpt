import numpy as np


def quantum_phase_estimation(
    unitary: np.ndarray, eigenstate: np.ndarray, num_qubits: int = 4, num_measurements: int = 1000
) -> float:
    """
    Estimate the phase (eigenvalue phase) of a unitary operator acting on a given eigenstate.

    Parameters:
    -----------
    unitary : np.ndarray
        The unitary matrix U (2^n x 2^n)
    eigenstate : np.ndarray
        The eigenstate vector |psi> such that U|psi> = e^(2*pi*i*phi)|psi>
    num_qubits : int
        Number of qubits in the phase estimation register
    num_measurements : int
        Number of measurement shots for statistical estimation

    Returns:
    --------
    float
        Estimated phase phi in [0, 1)
    """
    dim = len(eigenstate)
    n = int(np.log2(dim))

    # Total number of qubits: num_qubits for phase register + n for eigenstate
    total_qubits = num_qubits + n
    total_dim = 2**total_qubits

    # Build the full state: |0...0> (phase register) ⊗ |psi> (eigenstate)
    phase_register = np.zeros(2**num_qubits)
    phase_register[0] = 1.0
    initial_state = np.kron(phase_register, eigenstate)

    # Apply Hadamard gates to phase register
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

    # Apply H to each qubit in the phase register
    for i in range(num_qubits):
        # Qubit i in phase register corresponds to qubit (num_qubits - 1 - i) in the full system
        # We need to apply H to the i-th qubit of the phase register
        # In the full system, phase register qubits are the most significant
        # Qubit index in full system: (num_qubits - 1 - i) + n
        qubit_idx = (num_qubits - 1 - i) + n
        H_full = _embed_single_qubit_gate(H, qubit_idx, total_qubits)
        initial_state = H_full @ initial_state

    # Apply controlled-U^(2^k) for k = 0 to num_qubits-1
    # The control is the k-th qubit of the phase register
    # The target is the eigenstate register
    for k in range(num_qubits):
        # Compute U^(2^k)
        U_power = _matrix_power(unitary, 2**k)

        # Build controlled-U^(2^k)
        # Control qubit is at position (num_qubits - 1 - k) in the full system
        # Target is the n-qubit eigenstate register (least significant n qubits)
        control_idx = (num_qubits - 1 - k) + n
        target_start = 0  # eigenstate register is the least significant n qubits
        target_end = n

        controlled_gate = _build_controlled_gate(
            U_power, control_idx, target_start, target_end, total_qubits
        )
        initial_state = controlled_gate @ initial_state

    # Apply inverse Hadamard gates to phase register
    for i in range(num_qubits - 1, -1, -1):
        qubit_idx = (num_qubits - 1 - i) + n
        H_full = _embed_single_qubit_gate(H, qubit_idx, total_qubits)
        initial_state = H_full @ initial_state

    # Measure the phase register
    # The phase register is the most significant num_qubits qubits
    # We need to extract the probability distribution over the phase register

    # Reshape the state to separate phase register and eigenstate
    phase_dim = 2**num_qubits
    eigen_dim = 2**n
    state_matrix = initial_state.reshape(phase_dim, eigen_dim)

    # Probability of each phase register state
    probs = np.sum(np.abs(state_matrix) ** 2, axis=1)

    # Sample from the distribution
    samples = np.random.choice(phase_dim, size=num_measurements, p=probs)

    # Convert samples to phase estimates
    # The phase register value m corresponds to phase m / 2^num_qubits
    phase_estimates = samples / phase_dim

    # Return the most common estimate (mode) or the mean
    # Use the mode for better accuracy
    values, counts = np.unique(phase_estimates, return_counts=True)
    most_common = values[np.argmax(counts)]

    return float(most_common)


def _embed_single_qubit_gate(gate: np.ndarray, qubit_idx: int, total_qubits: int) -> np.ndarray:
    """
    Embed a single-qubit gate into the full Hilbert space.
    qubit_idx is the index of the qubit (0 = least significant).
    """
    dim = 2**total_qubits
    result = np.zeros((dim, dim), dtype=complex)

    for i in range(dim):
        for j in range(2):
            # Check if qubit_idx is 0 in i
            if (i >> qubit_idx) & 1 == 0:
                # j=0: target qubit is 0
                target = i
                result[target, i] += gate[j, 0]
                # j=1: target qubit is 1
                target = i | (1 << qubit_idx)
                result[target, i] += gate[j, 1]
            else:
                # qubit_idx is 1 in i
                # j=0: target qubit is 0
                target = i & ~(1 << qubit_idx)
                result[target, i] += gate[j, 0]
                # j=1: target qubit is 1
                target = i
                result[target, i] += gate[j, 1]

    return result


def _matrix_power(matrix: np.ndarray, power: int) -> np.ndarray:
    """Compute matrix power using repeated squaring."""
    if power == 0:
        return np.eye(len(matrix), dtype=complex)

    result = np.eye(len(matrix), dtype=complex)
    base = matrix.copy()
    exp = power

    while exp > 0:
        if exp % 2 == 1:
            result = base @ result
        base = base @ base
        exp //= 2

    return result


def _build_controlled_gate(
    target_gate: np.ndarray, control_idx: int, target_start: int, target_end: int, total_qubits: int
) -> np.ndarray:
    """
    Build a controlled gate where:
    - control_idx is the control qubit
    - target_start to target_end-1 are the target qubits
    - The target gate acts on the target qubits
    """
    dim = 2**total_qubits
    target_dim = 2 ** (target_end - target_start)
    result = np.zeros((dim, dim), dtype=complex)

    for i in range(dim):
        # Check if control qubit is 1
        if (i >> control_idx) & 1 == 1:
            # Extract target qubits
            target_mask = (1 << (target_end - target_start)) - 1
            target_val = (i >> target_start) & target_mask

            # Apply target gate
            for j in range(target_dim):
                coeff = target_gate[j, target_val]
                if abs(coeff) > 1e-15:
                    # Set target qubits to j
                    new_target = (i & ~(target_mask << target_start)) | (j << target_start)
                    result[new_target, i] += coeff
        else:
            # Control is 0, identity on target
            result[i, i] += 1.0

    return result


def estimate_eigenvalue_phase(
    unitary: np.ndarray, eigenstate: np.ndarray, num_qubits: int = 4, num_measurements: int = 1000
) -> float:
    """
    Convenience function to estimate the phase of an eigenvalue.

    Parameters:
    -----------
    unitary : np.ndarray
        The unitary matrix U
    eigenstate : np.ndarray
        The eigenstate vector
    num_qubits : int
        Number of qubits in the phase estimation register
    num_measurements : int
        Number of measurement shots

    Returns:
    --------
    float
        Estimated phase phi in [0, 1)
    """
    return quantum_phase_estimation(unitary, eigenstate, num_qubits, num_measurements)
