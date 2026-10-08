# Reference implementation
def encode_message(bits: str) -> str:
    """Encode two-bit qubits into a three-bit string."""
    return f"{bits[:2]}1"


def decode_message(msg: str) -> str:
    """Decode a three-bit string into two bits."""
    return msg[3:]
