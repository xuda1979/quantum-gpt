# normalize_gate_sequence.py


def normalize_gate_sequence(gates: list[str]) -> list[str]:
    """Normalize gate sequence by removing duplicates and preserving order."""
    normalized = []
    seen = set()
    for gate in gates:
        # Normalize case and remove duplicates while preserving order
        normalized_gate = "".join(
            c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(gate)
        )
        if normalized_gate not in seen:
            normalized.append(normalized_gate)
            seen.add(normalized_gate)
    return normalized
