def encode_message(message: str) -> str:
    """
    Encode a two-bit message into a Pauli label.

    Mapping:
        00 -> I
        01 -> X
        10 -> Z
        11 -> XZ

    Args:
        message: A two-character string representing the message bits.

    Returns:
        The corresponding Pauli label.

    Raises:
        ValueError: If the message is not a valid two-bit string.
    """
    if not isinstance(message, str) or len(message) != 2:
        raise ValueError(f"Unsupported two-bit message: {message!r}")

    if message not in ("00", "01", "10", "11"):
        raise ValueError(f"Unsupported two-bit message: {message!r}")

    mapping = {"00": "I", "01": "X", "10": "Z", "11": "XZ"}

    return mapping[message]


def decode_message(label: str) -> str:
    """
    Decode a Pauli label into a two-bit message.

    Mapping:
        I -> 00
        X -> 01
        Z -> 10
        XZ -> 11

    Args:
        label: A Pauli label string.

    Returns:
        The corresponding two-bit message.

    Raises:
        ValueError: If the label is not a valid Pauli label.
    """
    if not isinstance(label, str):
        raise ValueError(f"Unsupported operation label: {label!r}")

    if label not in ("I", "X", "Z", "XZ"):
        raise ValueError(f"Unsupported operation label: {label!r}")

    mapping = {"I": "00", "X": "01", "Z": "10", "XZ": "11"}

    return mapping[label]
