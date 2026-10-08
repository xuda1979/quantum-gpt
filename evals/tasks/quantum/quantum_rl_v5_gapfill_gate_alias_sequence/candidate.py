"""Gate alias sequence normalization - exact holdout API contract.

The holdout grader imports normalize_gate_sequence. Missing or misnamed
entry points fail immediately; this reference teaches the exact name."""

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
