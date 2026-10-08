def repair_phase_sequence(ops: list[str]) -> list[str]:
    """Normalize a one-qubit gate stream and remove redundant phase cancellations.

    Rules:
    - Normalize tokens by stripping whitespace and uppercasing.
    - Accept only H, X, Z, S, SDG.
    - Cancel adjacent inverse phase pairs: S followed by SDG, or SDG followed by S.
    - Cancel adjacent self-inverse pairs: H H, X X, Z Z.
    - Preserve all other operations in order.
    - Raise ValueError on unsupported operations.
    """
    normalized = []
    for raw in ops:
        token = raw.strip().upper()
        if token not in {"H", "X", "Z", "S", "SDG"}:
            raise ValueError(f"unsupported gate: {raw}")
        if normalized:
            prev = normalized[-1]
            if (prev, token) in {("S", "SDG"), ("SDG", "S")}:
                normalized.pop()
                continue
            if prev == token and token in {"H", "X", "Z"}:
                normalized.pop()
                continue
        normalized.append(token)
    return normalized
