def phase_to_register_bits(phase: float, n_qubits: int) -> list[int]:
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    if not (0.0 <= phase < 1.0):
        raise ValueError("phase must be in [0, 1)")
    scale = 1 << n_qubits
    integer_rep = int(phase * scale)
    if integer_rep >= scale:
        integer_rep = scale - 1
    return [(integer_rep >> (n_qubits - 1 - bit)) & 1 for bit in range(n_qubits)]


def register_bits_to_phase(bits: list[int]) -> float:
    if not bits:
        raise ValueError("bits must be non-empty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("bits must be 0 or 1")
    integer_rep = 0
    for bit in bits:
        integer_rep = (integer_rep << 1) | int(bit)
    scale = 1 << len(bits)
    return integer_rep / scale
