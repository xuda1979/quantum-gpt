def measurement_mapping(bitstring: str) -> dict[str, int]:
    """Map q0/q1 to integer measurement results from a two-bit string.

    The input bitstring is ordered as q1q0, so the rightmost bit corresponds
    to q0 and the leftmost bit corresponds to q1.
    """
    if len(bitstring) != 2 or any(ch not in "01" for ch in bitstring):
        raise ValueError("expected a two-bit measurement string")
    return {"q0": int(bitstring[1]), "q1": int(bitstring[0])}
