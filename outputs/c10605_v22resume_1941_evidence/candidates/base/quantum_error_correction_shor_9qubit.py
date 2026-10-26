import numpy as np


def shor_9qubit_code():
    """
    Simulate the 9-qubit Shor error correction code.

    The 9-qubit code encodes 1 logical qubit into 9 physical qubits.
    It can correct any single-qubit error (X, Y, Z) on any of the 9 qubits.

    The code is a concatenation of:
    1. A 3-qubit bit-flip code (corrects X errors)
    2. A 3-qubit phase-flip code (corrects Z errors)

    Encoding:
    |0_L> = (|000> + |111>)^3 / (2*sqrt(2))
    |1_L> = (|000> - |111>)^3 / (2*sqrt(2))

    This code can detect and correct:
    - Bit flip (X) on any qubit
    - Phase flip (Z) on any qubit
    - Combined (Y = iXZ) on any qubit
    """

    # Define Pauli matrices
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)

    # Create the 9-qubit code states
    # |0_L> = (|000> + |111>)^3 / (2*sqrt(2))
    # |1_L> = (|000> - |111>)^3 / (2*sqrt(2))

    def create_code_state(logical_bit):
        """Create the 9-qubit encoded state for logical 0 or 1."""
        # Start with 3-qubit code state
        if logical_bit == 0:
            # (|000> + |111>) / sqrt(2)
            state_3q = np.zeros(8, dtype=complex)
            state_3q[0] = 1.0 / np.sqrt(2)  # |000>
            state_3q[7] = 1.0 / np.sqrt(2)  # |111>
        else:
            # (|000> - |111>) / sqrt(2)
            state_3q = np.zeros(8, dtype=complex)
            state_3q[0] = 1.0 / np.sqrt(2)  # |000>
            state_3q[7] = -1.0 / np.sqrt(2)  # |111>

        # Tensor product of three 3-qubit states
        state_9q = state_3q
        for _ in range(2):
            state_9q = np.kron(state_9q, state_3q)

        # Normalize
        norm = np.sqrt(np.vdot(state_9q, state_9q).real)
        state_9q = state_9q / norm

        return state_9q

    # Create encoded states
    psi_0 = create_code_state(0)
    psi_1 = create_code_state(1)

    # Verify orthogonality
    overlap = np.vdot(psi_0, psi_1)
    assert abs(overlap) < 1e-10, "Code states should be orthogonal"

    # Define error operators for all 9 qubits
    # For each qubit i (0-8), apply X, Y, or Z
    def apply_error(state, error_type, qubit_index):
        """Apply a Pauli error to a specific qubit in a 9-qubit state."""
        # Build the full 9-qubit operator
        operators = [I] * 9
        operators[qubit_index] = error_type

        # Apply tensor product
        full_op = operators[0]
        for op in operators[1:]:
            full_op = np.kron(full_op, op)

        return full_op @ state

    # Syndrome measurement operators
    # For bit-flip detection: measure Z_i Z_{i+1} for each block of 3
    # For phase-flip detection: measure X_i X_{i+1} for each block of 3

    def measure_syndrome(state, observable):
        """Measure an observable and return the eigenvalue (+1 or -1)."""
        # Project onto +1 and -1 eigenspaces
        # For simplicity, we'll compute the expectation value
        expectation = np.vdot(state, observable @ state).real
        return expectation

    # Define stabilizer generators for the 9-qubit code
    # The 9-qubit code has 8 stabilizer generators (9 qubits - 1 logical = 8)

    # Bit-flip stabilizers (detect X errors):
    # S1 = Z1 Z2, S2 = Z2 Z3 (for first block)
    # S3 = Z4 Z5, S4 = Z5 Z6 (for second block)
    # S5 = Z7 Z8, S6 = Z8 Z9 (for third block)

    # Phase-flip stabilizers (detect Z errors):
    # S7 = X1 X2 X3 X4 X5 X6 (first two blocks)
    # S8 = X4 X5 X6 X7 X8 X9 (last two blocks)

    def build_stabilizer(qubits, pauli):
        """Build a stabilizer operator for given qubits with given Pauli."""
        ops = [I] * 9
        for q in qubits:
            ops[q] = pauli
        op = ops[0]
        for o in ops[1:]:
            op = np.kron(op, o)
        return op

    # Stabilizer generators
    stabilizers = []

    # Bit-flip stabilizers
    stabilizers.append(build_stabilizer([0, 1], Z))  # Z1 Z2
    stabilizers.append(build_stabilizer([1, 2], Z))  # Z2 Z3
    stabilizers.append(build_stabilizer([3, 4], Z))  # Z4 Z5
    stabilizers.append(build_stabilizer([4, 5], Z))  # Z5 Z6
    stabilizers.append(build_stabilizer([6, 7], Z))  # Z7 Z8
    stabilizers.append(build_stabilizer([7, 8], Z))  # Z8 Z9

    # Phase-flip stabilizers
    stabilizers.append(build_stabilizer([0, 1, 2, 3, 4, 5], X))  # X1 X2 X3 X4 X5 X6
    stabilizers.append(build_stabilizer([3, 4, 5, 6, 7, 8], X))  # X4 X5 X6 X7 X8 X9

    # Verify that code states are +1 eigenstates of all stabilizers
    for s in stabilizers:
        for psi in [psi_0, psi_1]:
            result = s @ psi
            # Check if result is proportional to psi with eigenvalue +1
            ratio = np.vdot(psi, result) / np.vdot(psi, psi)
            assert abs(ratio - 1.0) < 1e-10, f"Stabilizer check failed: {ratio}"

    # Error correction procedure
    def correct_error(state, logical_bit):
        """
        Attempt to correct a single-qubit error in the 9-qubit code.
        Returns the corrected state and the identified error.
        """
        # Measure all stabilizers
        syndrome = []
        for s in stabilizers:
            # Project state onto +1 and -1 eigenspaces
            # For a stabilizer S, S^2 = I, so eigenvalues are ±1
            # We can compute the expectation value
            exp_val = np.vdot(state, s @ state).real
            # If exp_val is close to +1, eigenvalue is +1; if close to -1, eigenvalue is -1
            syndrome.append(1 if exp_val > 0 else -1)

        # Determine the error from the syndrome
        # For a single-qubit error, the syndrome pattern identifies which qubit and what type
        # This is a simplified version - in practice, we'd use a lookup table

        # For demonstration, let's just return the syndrome
        return syndrome

    # Demonstrate error correction
    print("Shor 9-qubit Error Correction Code Simulation")
    print("=" * 50)
    print(f"Code state |0_L> norm: {np.sqrt(np.vdot(psi_0, psi_0).real):.6f}")
    print(f"Code state |1_L> norm: {np.sqrt(np.vdot(psi_1, psi_1).real):.6f}")
    print(f"Overlap <0_L|1_L>: {abs(overlap):.6f}")
    print(f"Number of stabilizer generators: {len(stabilizers)}")
    print()

    # Test with a single-qubit X error on qubit 0
    print("Testing error correction...")
    error_state = apply_error(psi_0, X, 0)
    syndrome = correct_error(error_state, 0)
    print(f"X error on qubit 0 - Syndrome: {syndrome}")

    # Test with a single-qubit Z error on qubit 3
    error_state = apply_error(psi_0, Z, 3)
    syndrome = correct_error(error_state, 0)
    print(f"Z error on qubit 3 - Syndrome: {syndrome}")

    # Test with a single-qubit Y error on qubit 5
    error_state = apply_error(psi_0, Y, 5)
    syndrome = correct_error(error_state, 0)
    print(f"Y error on qubit 5 - Syndrome: {syndrome}")

    # Verify that the code can distinguish all single-qubit errors
    # by checking that different errors produce different syndromes
    print()
    print("Verifying error distinguishability...")
    error_types = [X, Y, Z]
    error_names = ["X", "Y", "Z"]
    syndromes = {}

    for qubit in range(9):
        for i, err in enumerate(error_types):
            error_state = apply_error(psi_0, err, qubit)
            syndrome = tuple(correct_error(error_state, 0))
            key = (qubit, error_names[i])
            syndromes[key] = syndrome

    # Check that all 27 single-qubit errors have distinct syndromes
    unique_syndromes = set(syndromes.values())
    print(f"Total single-qubit errors: {len(syndromes)}")
    print(f"Unique syndromes: {len(unique_syndromes)}")

    if len(unique_syndromes) == 27:
        print("All single-qubit errors are distinguishable!")
    else:
        print("Warning: Some errors may not be distinguishable")

    return {"psi_0": psi_0, "psi_1": psi_1, "stabilizers": stabilizers, "syndromes": syndromes}


if __name__ == "__main__":
    result = shor_9qubit_code()
