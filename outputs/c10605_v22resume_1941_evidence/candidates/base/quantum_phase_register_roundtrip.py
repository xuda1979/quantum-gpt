def phase_to_register_bits(phase: float, n_qubits: int) -> list:
    """
    Convert a phase value in [0, 1) to a fixed-point phase register representation.

    Args:
        phase: A float in [0, 1)
        n_qubits: Number of qubits (positive integer)

    Returns:
        A list of n_qubits binary digits (0 or 1), MSB first.

    Raises:
        ValueError: If n_qubits <= 0 or phase is not in [0, 1).
    """
    if not isinstance(n_qubits, int) or n_qubits <= 0:
        raise ValueError("n_qubits must be a positive integer")
    if not isinstance(phase, (int, float)):
        raise ValueError("phase must be a number")
    if phase < 0 or phase >= 1:
        raise ValueError("phase must be in [0, 1)")

    # Compute floor(phase * 2**n_qubits)
    value = int(phase * (2**n_qubits))
    # Clamp to valid range due to floating point issues
    if value < 0:
        value = 0
    if value >= (2**n_qubits):
        value = (2**n_qubits) - 1

    # Convert to binary string with exactly n_qubits digits
    binary_str = format(value, f"0{n_qubits}b")
    return [int(b) for b in binary_str]


def register_bits_to_phase(bits: list) -> float:
    """
    Convert a fixed-point phase register representation back to a phase value.

    Args:
        bits: A non-empty list of 0/1 integers, MSB first.

    Returns:
        A float in [0, 1) representing the phase.

    Raises:
        ValueError: If bits is empty or contains values other than 0 or 1.
    """
    if not isinstance(bits, list):
        raise ValueError("bits must be a list")
    if len(bits) == 0:
        raise ValueError("bits must be non-empty")

    for b in bits:
        if not isinstance(b, int) or b not in (0, 1):
            raise ValueError("bits must contain only 0 or 1")

    # Interpret as unsigned MSB-first integer
    value = 0
    for b in bits:
        value = (value << 1) | b

    return value / (2 ** len(bits))
