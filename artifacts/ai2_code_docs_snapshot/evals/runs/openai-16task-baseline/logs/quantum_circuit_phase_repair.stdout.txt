def repair_phase_sequence(ops: list[str]) -> list[str]:
    """Normalize a one-qubit gate stream and remove adjacent cancellations.

    Supported gates after normalization:
    H, X, Z, S, SDG

    Cancellation rules:
    - S followed by SDG, or SDG followed by S
    - H H, X X, Z Z
    """
    supported = {"H", "X", "Z", "S", "SDG"}
    out: list[str] = []

    for raw in ops:
        token = raw.strip().upper()
        if token not in supported:
            raise ValueError(f"unsupported gate: {raw}")

        if out:
            prev = out[-1]
            if (prev, token) in {("S", "SDG"), ("SDG", "S")}:
                out.pop()
                continue
            if prev == token and token in {"H", "X", "Z"}:
                out.pop()
                continue

        out.append(token)

    return out
