def teleportation_corrections(m0: int, m1: int) -> list[str]:
    """Return the Pauli corrections for teleportation measurement bits.

    In the standard teleportation rule:
    - m1 controls a Z correction
    - m0 controls an X correction

    Corrections are returned in application order.
    """
    if m0 not in (0, 1) or m1 not in (0, 1):
        raise ValueError("measurement bits must be 0 or 1")

    ops: list[str] = []
    if m1 == 1:
        ops.append("Z")
    if m0 == 1:
        ops.append("X")
    return ops
