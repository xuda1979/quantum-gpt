def phase_to_register_bits(phase: float, n_qubits: int) -> list[int]:
    """
    Map a fractional phase [0, 1) into a fixed-length register bit vector.
    """
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    if not (0.0 <= phase < 1.0):
        raise ValueError("phase must be in [0, 1)")

    scale = 1 << n_qubits
    integer_rep = int(phase * scale)
    bits: list[int] = []
    for shift in range(n_qubits - 1, -1, -1):
        bits.append((integer_rep >> shift) & 1)
    return bits


def register_bits_to_phase(bits: list[int]) -> float:
    """
    Recover the phase represented by a register bit vector.
    """
    if not bits:
        raise ValueError("bits list cannot be empty")
    if any(bit not in {0, 1} for bit in bits):
        raise ValueError("bits must be 0 or 1")

    integer_rep = 0
    for bit in bits:
        integer_rep = (integer_rep << 1) | bit
    scale = 1 << len(bits)
    return integer_rep / scale
