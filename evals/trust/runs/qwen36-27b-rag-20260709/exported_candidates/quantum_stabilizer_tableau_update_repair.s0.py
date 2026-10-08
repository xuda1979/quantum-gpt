def _normalize_pauli(label: str) -> str:
    normalized = label.strip().upper()
    if normalized not in {"I", "X", "Y", "Z"}:
        raise ValueError(f"unsupported Pauli operator: {label!r}")
    return normalized


_CONJUGATION_RULES = {
    "H": {
        "I": (1, "I"),
        "X": (1, "Z"),
        "Y": (-1, "Y"),
        "Z": (1, "X"),
    },
    "S": {
        "I": (1, "I"),
        "X": (1, "Y"),
        "Y": (-1, "X"),
        "Z": (1, "Z"),
    },
    "SDG": {
        "I": (1, "I"),
        "X": (-1, "Y"),
        "Y": (1, "X"),
        "Z": (1, "Z"),
    },
}


def apply_gate_sequence(pauli: str, gates: list[str]) -> tuple[int, str]:
    """Update a signed single-qubit Pauli under Clifford conjugation."""
    raw = pauli.strip()
    sign = -1 if raw.startswith("-") else 1
    label = raw[1:] if raw.startswith("-") else raw
    label = _normalize_pauli(label)

    for gate in gates:
        gate_name = gate.strip().upper()
        if gate_name not in _CONJUGATION_RULES:
            raise ValueError(f"unsupported gate: {gate!r}")
        gate_sign, next_label = _CONJUGATION_RULES[gate_name][label]
        sign *= gate_sign
        label = next_label

    return sign, label
