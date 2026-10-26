def bit_register_to_int(bits):
    """
    Convert a list of 0/1 values (MSB first) to an unsigned integer.
    Raises ValueError for empty register or non-binary values.
    """
    if not bits:
        raise ValueError("Empty register")
    for b in bits:
        if b not in (0, 1):
            raise ValueError(f"Non-binary value: {b}")
    result = 0
    for b in bits:
        result = (result << 1) | b
    return result


def measurement_register_to_phase(bits):
    """
    Return bit_register_to_int(bits) / 2**len(bits).
    Uses the same validation as bit_register_to_int.
    """
    if not bits:
        raise ValueError("Empty register")
    for b in bits:
        if b not in (0, 1):
            raise ValueError(f"Non-binary value: {b}")
    value = bit_register_to_int(bits)
    return value / (2 ** len(bits))
