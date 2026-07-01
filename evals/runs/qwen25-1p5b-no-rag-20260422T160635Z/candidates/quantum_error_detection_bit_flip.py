from typing import List, Dict

def bit_flip_code(initial_state: int, error_qubit: int) -> Dict[str, int]:
    """3-qubit bit-flip repetition code.

    Encodes logical qubit |initial_state> into 3 physical qubits,
    applies a bit-flip error on error_qubit, measures the syndrome,
    and corrects to recover the original logical state.

    Args:
        initial_state: 0 or 1 — the logical qubit value to encode.
        error_qubit: 0, 1, or 2 — which physical qubit receives the error.

    Returns:
        dict with:
            'syndrome': list[int] of length 2 — parity check results.
            'corrected_state': int — recovered logical value (0 or 1).
    """

    # Encode: all 3 physical qubits = initial_state
    qubits = [initial_state, initial_state, initial_state]

    # Apply error
    qubits[error_qubit] ^= 1

    # Syndrome measurement (parity checks)
    # s0 = q0 XOR q1 (do q0 and q1 agree?)
    # s1 = q1 XOR q2 (do q1 and q2 agree?)
    s0 = qubits[0] ^ qubits[1]
    s1 = qubits[1] ^ qubits[2]
    syndrome = [s0, s1]

    # Correct: majority vote
    corrected_state = 1 if (qubits[0] + qubits[1] + qubits[2]) >= 2 else 0

    return {"syndrome": syndrome, "corrected_state": corrected_state}
