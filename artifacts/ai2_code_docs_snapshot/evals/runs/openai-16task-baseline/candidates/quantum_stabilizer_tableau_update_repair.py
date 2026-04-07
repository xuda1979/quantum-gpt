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
    raw = pauli.strip()
    if not raw:
        raise ValueError(f"unsupported Pauli operator: {pauli!r}")

    sign = 1
    if raw.startswith("-"):
        sign = -1
        raw = raw[1:].strip()

    label = _normalize_pauli(raw)

    for gate in gates:
        gate_name = gate.strip().upper()
        if gate_name not in _CONJUGATION_RULES:
            raise ValueError(f"unsupported gate: {gate!r}")
        gate_sign, next_label = _CONJUGATION_RULES[gate_name][label]
        sign *= gate_sign
        label = next_label

    return sign, label
