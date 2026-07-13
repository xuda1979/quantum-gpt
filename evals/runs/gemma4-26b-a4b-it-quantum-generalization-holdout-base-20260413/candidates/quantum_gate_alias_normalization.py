def normalize_gate_sequence(sequence):
    """
    Normalizes a sequence of quantum gate aliases.
    Supported gates: H (Hadamard), CX (CNOT), X (Pauli-X).
    """
    mapping = {
        "H": "H",
        "HADAMARD": "H",
        "CX": "CX",
        "CNOT": "CX",
        "X": "X",
        "PAULI_X": "X"
    }

    normalized = []
    for gate in sequence:
        clean_gate = gate.strip().upper()
        if clean_gate in mapping:
            normalized.append(mapping[clean_gate])
        else:
            raise ValueError(f"Unknown gate alias: {gate}")

    return normalized
