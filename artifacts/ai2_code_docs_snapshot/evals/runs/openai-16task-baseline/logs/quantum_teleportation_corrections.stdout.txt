def teleportation_corrections(m0: int, m1: int) -> list[str]:
    """Return the teleportation correction operations for measurement bits (m0, m1).

    In the standard protocol:
    - m1 == 1 implies a Z correction
    - m0 == 1 implies an X correction

    The returned list is ordered in the sequence to apply.
    """
    if m0 not in (0, 1) or m1 not in (0, 1):
        raise ValueError("measurement bits must be 0 or 1")

    ops: list[str] = []
    if m1 == 1:
        ops.append("Z")
    if m0 == 1:
        ops.append("X")
    return ops
