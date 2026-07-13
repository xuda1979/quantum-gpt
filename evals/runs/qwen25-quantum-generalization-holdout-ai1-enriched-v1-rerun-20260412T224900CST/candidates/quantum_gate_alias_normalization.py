# Reference implementation
def normalize_gate_sequence(gate_list: list[str]) -> list[str]:
    """Normalize gate names to lowercase and strip whitespace."""
    normalized = []
    for gate in gate_list:
        normalized_gate = gate.strip().lower()
        if normalized_gate not in {"h", "cx", "x"}:
            raise ValueError(f"unsupported gate: {gate!r}")
        normalized.append(normalized_gate)
    return normalized
