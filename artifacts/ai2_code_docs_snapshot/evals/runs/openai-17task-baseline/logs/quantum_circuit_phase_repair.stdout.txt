def repair_phase_sequence(ops: list[str]) -> list[str]:
    """Normalize a one-qubit gate stream and remove redundant cancellations.

    Rules:
    - Normalize tokens by stripping whitespace and uppercasing.
    - Accept only H, X, Z, S, SDG.
    - Cancel adjacent inverse phase pairs: S+SDG and SDG+S.
    - Cancel adjacent self-inverse pairs: H+H, X+X, Z+Z.
    - Preserve all other operations in order.
    - Raise ValueError on unsupported operations.
    """
    allowed = {"H", "X", "Z", "S", "SDG"}
    result: list[str] = []

    for raw in ops:
        token = raw.strip().upper()
        if token not in allowed:
            raise ValueError(f"unsupported gate: {raw}")

        if result:
            prev = result[-1]
            if (prev, token) in {("S", "SDG"), ("SDG", "S")}:
                result.pop()
                continue
            if prev == token and token in {"H", "X", "Z"}:
                result.pop()
                continue

        result.append(token)

    return result
