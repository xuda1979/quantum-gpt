def encode_message(bits: str) -> str:
    mapping = {
        "00": "I",
        "01": "X",
        "10": "Z",
        "11": "XZ",
    }
    if bits not in mapping:
        raise ValueError("bits must be one of: 00, 01, 10, 11")
    return mapping[bits]


def decode_message(operation: str) -> str:
    mapping = {
        "I": "00",
        "X": "01",
        "Z": "10",
        "XZ": "11",
    }
    if operation not in mapping:
        raise ValueError("operation must be one of: I, X, Z, XZ")
    return mapping[operation]
