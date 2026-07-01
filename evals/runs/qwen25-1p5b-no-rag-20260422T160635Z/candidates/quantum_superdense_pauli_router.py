_ENCODE = {
    "00": "I",
    "01": "X",
    "10": "Z",
    "11": "XZ",
}

_DECODE = {opcode: bits for bits, opcode in _ENCODE.items()}


def _canonical_opcode(opcode: str) -> str:
    normalized = "".join(str(opcode).strip().upper().split())
    if normalized == "ZX":
        normalized = "XZ"
    if normalized not in _DECODE:
        raise ValueError("opcode must be one of I, X, Z, XZ")
    return normalized


def encode_message(bits: str) -> str:
    if bits not in _ENCODE:
        raise ValueError("bits must be one of 00, 01, 10, 11")
    return _ENCODE[bits]


def decode_message(opcode: str) -> str:
    return _DECODE[_canonical_opcode(opcode)]
