
def encode_message(bits: str) -> str:
    """
    Encodes a 2-bit classical message into a quantum operation string.
    Mapping:
    00 -> I (Identity)
    01 -> X (Bit flip)
    10 -> Z (Phase flip)
    11 -> XZ (Bit flip then Phase flip)
    """
    if bits == "00":
        return "I"
    elif bits == "01":
        return "X"
    elif bits == "10":
        return "Z"
    elif bits == "11":
        return "XZ"
    else:
        raise ValueError(f"Invalid bits: {bits}")

def decode_message(op: str) -> str:
    """
    Decodes a quantum operation string back to the 2-bit classical message.
    Mapping:
    I -> 00
    X -> 01
    Z -> 10
    XZ -> 11
    """
    if op == "I":
        return "00"
    elif op == "X":
        return "01"
    elif op == "Z":
        return "10"
    elif op == "XZ":
        return "11"
    else:
        raise ValueError(f"Invalid operation: {op}")
