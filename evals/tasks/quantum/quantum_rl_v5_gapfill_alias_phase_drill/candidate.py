"""Combined drill: gate alias normalization + phase-register roundtrip.

Graded entry points: normalize_gate_sequence, phase_to_register_bits,
register_bits_to_phase - all three under exact holdout names."""

from __future__ import annotations

_ALIASES = dict(h="H", hadamard="H", x="X", pauli_x="X", cx="CX", cnot="CX")


def normalize_gate_sequence(gates):
    normalized = []
    for gate in gates:
        key = gate.strip().lower()
        canonical = _ALIASES.get(key)
        if canonical is None:
            raise ValueError("unknown gate: %s" % gate)
        normalized.append(canonical)
    return normalized


def phase_to_register_bits(phase, n_qubits):
    if n_qubits <= 0:
        raise ValueError("n_qubits must be positive")
    if not (0.0 <= phase < 1.0):
        raise ValueError("phase must be in [0, 1)")
    scale = 1 << n_qubits
    integer_rep = int(phase * scale)
    return [(integer_rep >> shift) & 1 for shift in range(n_qubits - 1, -1, -1)]


def register_bits_to_phase(bits):
    if not bits:
        raise ValueError("bits list cannot be empty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError("bits must be 0 or 1")
    integer_rep = 0
    for bit in bits:
        integer_rep = (integer_rep << 1) | bit
    return integer_rep / (1 << len(bits))
