# Reference implementation
def normalize_gate_sequence(raw: list[str]) -> list[str]:
    """Normalize quantum gate names to canonical uppercase aliases."""
    canonical = {
        "h": "H",
        "hadamard": "H",
        "x": "X",
        "pauli_x": "X",
        "cx": "CX",
        "cnot": "CX",
        "measure": "MEASURE",
        "swap": "SWAP",
    }
    normalized = []
    for token in raw:
        cleaned = token.strip()
        key = cleaned.lower()
        if key not in canonical:
            raise ValueError(f"unsupported gate: {cleaned!r}")
        normalized.append(canonical[key])
    return normalized
