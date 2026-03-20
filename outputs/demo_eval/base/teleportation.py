def teleportation_corrections(m0, m1):
    if (m0, m1) == (0, 0):
        return []
    if (m0, m1) == (0, 1):
        return ["X"]
    if (m0, m1) == (1, 0):
        return ["Z"]
    if (m0, m1) == (1, 1):
        return ["X", "Z"]
    raise ValueError("measurement bits must be 0 or 1")
