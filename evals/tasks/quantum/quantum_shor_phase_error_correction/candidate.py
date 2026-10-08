import math

S2 = 1.0 / math.sqrt(2)


def _block_state(logical_block: int) -> list[float]:
    """One 3-qubit block of the Shor code: (|000> +- |111>)/sqrt(2)."""
    v = [0.0] * 8
    v[0] = S2
    v[7] = S2 if logical_block == 0 else -S2
    return v


def shor_encode(logical: int) -> list[float]:
    """
    Encode one logical qubit into the 9-qubit Shor code.

    |0_L> = (|000>+|111>)(|000>+|111>)(|000>+|111>) / (2*sqrt(2))
    |1_L> = (|000>-|111>)(|000>-|111>)(|000>-|111>) / (2*sqrt(2))

    Returns a length-512 list of amplitudes; index i is the computational
    basis state whose 9 bits are the bits of i (qubit 0 = most significant).
    """
    block = _block_state(1 if logical else 0)
    out = [1.0]
    for _ in range(3):
        out = [a * c for a in out for c in block]
    return out


def apply_error(state: list[float], qubit: int, err: str) -> list[float]:
    """
    Apply a single-qubit error to a 9-qubit statevector.

    err='X': bit flip on `qubit` (amplitude swap).
    err='Z': phase flip on `qubit`.
    err='Y': combined X then Z (global phase convention irrelevant here).
    """
    n = len(state)
    out = [0.0] * n
    bit = 1 << (8 - qubit)
    if err == "X":
        for i, a in enumerate(state):
            out[i ^ bit] = a
    elif err == "Z":
        for i, a in enumerate(state):
            out[i] = -a if (i & bit) else a
    else:  # 'Y': X then Z
        tmp = [0.0] * n
        for i, a in enumerate(state):
            tmp[i ^ bit] = a
        for i, a in enumerate(tmp):
            out[i] = -a if (i & bit) else a
    return out


def shor_decode(state: list[float]) -> int:
    """
    Correct any single-qubit error (X, Z, or Y) and return the logical bit.

    Strategy: for every candidate single-qubit error (including identity),
    apply the inverse and check the overlap with the two codewords; the
    candidate that lands back in the code space identifies both the error
    and the logical value. Overlap magnitudes make global phases irrelevant.
    """
    codewords = {0: shor_encode(0), 1: shor_encode(1)}
    candidates: list[tuple[str, int]] = [("I", -1)]
    for err in ("X", "Z", "Y"):
        for q in range(9):
            candidates.append((err, q))
    for err, q in candidates:
        corrected = list(state)
        if err != "I":
            corrected = apply_error(corrected, q, err)
        for logical, cw in codewords.items():
            overlap = sum(a * b for a, b in zip(corrected, cw))
            if abs(overlap) ** 2 > 0.999:
                return logical
    return 0
