# Reference implementation
def encode_message(bits: str) -> str:
    """Return the one-qubit gate to apply to |0> for the two-bit message."""
    if bits not in {"00", "01", "10", "11"}:
        raise ValueError("expected a two-bit message")
    return {
        "00": "I",
        "01": "X",
        "10": "Z",
        "11": "XZ",
    }[bits]


def decode_message(operation: str) -> str:
    """Return the two-bit message for the given gate sequence."""
    mapping = {
        "I": "00",
        "X": "01",
        "Z": "10",
        "XZ": "11",
    }
    if operation not in mapping:
        raise ValueError(f"unsupported operation {operation!r}")
    return mapping[operation]
