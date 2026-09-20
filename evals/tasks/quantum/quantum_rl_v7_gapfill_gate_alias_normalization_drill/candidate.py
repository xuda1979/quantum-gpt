"""Reference completion: gate alias normalization (exact holdout API).

Mined by C-0007 for holdout task quantum_gate_alias_normalization, whose
grader requires the entry point normalize_gate_sequence(gates) to
canonicalize case-insensitively after stripping surrounding whitespace --
h|hadamard to H, x|pauli_x to X, cx|cnot to CX, order preserved -- and to
raise ValueError on any unknown gate name.
"""

from __future__ import annotations

ALIASES = dict(
    h="H",
    hadamard="H",
    x="X",
    pauli_x="X",
    cx="CX",
    cnot="CX",
)


def normalize_gate_sequence(gates):
    """Canonicalize a gate-name sequence; raise ValueError on unknown gates."""
    normalized = []
    for raw in gates:
        token = raw.strip().lower()
        if token not in ALIASES:
            raise ValueError("unknown gate name: " + repr(raw))
        normalized.append(ALIASES[token])
    return normalized


if __name__ == "__main__":
    assert normalize_gate_sequence(["H", "cx", "x"]) == ["H", "CX", "X"]
    assert normalize_gate_sequence([" hadamard ", "CNOT", "Pauli_X"]) == ["H", "CX", "X"]
    assert normalize_gate_sequence(["h", "h", "cx"]) == ["H", "H", "CX"]
    assert normalize_gate_sequence([]) == []
    try:
        normalize_gate_sequence(["swap"])
    except ValueError:
        pass
    else:
        raise AssertionError("swap must raise ValueError")
    try:
        normalize_gate_sequence(["H", "measure"])
    except ValueError:
        pass
    else:
        raise AssertionError("measure must raise ValueError")
