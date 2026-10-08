_ALIASES = {
    "h": "H",
    "hadamard": "H",
    "x": "X",
    "pauli_x": "X",
    "cx": "CX",
    "cnot": "CX",
}


def normalize_gate_sequence(gates):
    normalized = []
    for gate in gates:
        key = gate.strip().lower()
        canonical = _ALIASES.get(key)
        if canonical is None:
            raise ValueError(f"unknown gate: {gate}")
        normalized.append(canonical)
    return normalized
