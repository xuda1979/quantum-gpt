def teleportation_corrections(m0: int, m1: int) -> list[str]:
    """Return the Pauli corrections for teleportation measurement bits.

    In the standard teleportation protocol:
    - m0 controls whether an X correction is needed
    - m1 controls whether a Z correction is needed

    The returned list is ordered as corrections to apply.
    """
    if m0 not in (0, 1) or m1 not in (0, 1):
        raise ValueError("measurement bits must be 0 or 1")

    ops: list[str] = []
    if m1 == 1:
        ops.append("Z")
    if m0 == 1:
        ops.append("X")
    return ops
