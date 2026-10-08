"""Phase-register roundtrip pair - exact holdout API contract.

Graded entry points: phase_to_register_bits, register_bits_to_phase.
Quantization grid spacing 2**-n; roundtrip exact on the grid."""

from __future__ import annotations


def phase_to_register_bits(phase, n_qubits):
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    if not (0.0 <= phase < 1.0):
        raise ValueError("phase must be in [0, 1)")
    scale = 1 << n_qubits
    integer_rep = int(phase * scale)
    bits = []
    for shift in range(n_qubits - 1, -1, -1):
        bits.append((integer_rep >> shift) & 1)
    return bits


def register_bits_to_phase(bits):
    if not bits:
        raise ValueError("bits list cannot be empty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("bits must be 0 or 1")
    integer_rep = 0
    for bit in bits:
        integer_rep = (integer_rep << 1) | bit
    scale = 1 << len(bits)
    return integer_rep / scale
