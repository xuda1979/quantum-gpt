def measurement_mapping(bitstring: str) -> dict[str, int]:
    """Return a mapping of qubit labels to measured bits.

    Measurement strings are ordered as q1q0, so the rightmost bit maps to q0
    and the leftmost bit maps to q1.
    """
    if len(bitstring) != 2 or any(ch not in "01" for ch in bitstring):
        raise ValueError("expected a two-bit measurement string containing only 0 or 1")
    return {"q0": int(bitstring[1]), "q1": int(bitstring[0])}
