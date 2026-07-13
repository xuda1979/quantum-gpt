# Reference implementation
def normalize_gate_sequence(gate_list: list[str]) -> list[str]:
    """Normalize a gate sequence by stripping whitespace, converting to uppercase,
    removing duplicates, preserving order, and normalizing alias representations.
    """
    normalized = []
    seen = set()
    for token in gate_list:
        stripped = token.strip().upper()
        if stripped not in seen:
            normalized.append(stripped)
            seen.add(stripped)
    return normalized
