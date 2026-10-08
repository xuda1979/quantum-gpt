# Reference implementation
def normalize_gate_sequence(gate_sequence: list[str]) -> list[str]:
    """Normalize gate sequence by stripping whitespace, lowercasing, and removing duplicates."""
    normalized = []
    seen = set()
    for token in gate_sequence:
        stripped = token.strip().lower()
        if stripped not in seen:
            normalized.append(stripped)
            seen.add(stripped)
    return normalized
