def teleportation_corrections(m0, m1):
    if m0 not in (0, 1) or m1 not in (0, 1):
        raise ValueError("measurement bits must be 0 or 1")
    ops = []
    if m1 == 1:
        ops.append("Z")
    if m0 == 1:
        ops.append("X")
    return ops
