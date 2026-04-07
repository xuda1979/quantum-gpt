import cmath


def qft_basis_state(n_qubits: int, basis_index: int) -> list[complex]:
    """Return the exact QFT statevector for computational basis |basis_index>."""
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")

    dimension = 1 << n_qubits
    if basis_index < 0 or basis_index >= dimension:
        raise ValueError("basis_index out of range")

    scale = dimension ** -0.5
    return [
        scale * cmath.exp(2j * cmath.pi * basis_index * output_index / dimension)
        for output_index in range(dimension)
    ]
