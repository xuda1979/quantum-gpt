def teleportation_corrections(m0: int, m1: int) -> list[str]:
    """Return the Pauli corrections to apply for teleportation measurement bits (m0, m1).

    m0 controls the X correction and m1 controls the Z correction.
    The returned list is ordered as operations to apply.
    """
    if m0 not in (0, 1) or m1 not in (0, 1):
        raise ValueError("measurement bits must be 0 or 1")

    ops: list[str] = []
    if m1 == 1:
        ops.append("Z")
    if m0 == 1:
        ops.append("X")
    return ops
