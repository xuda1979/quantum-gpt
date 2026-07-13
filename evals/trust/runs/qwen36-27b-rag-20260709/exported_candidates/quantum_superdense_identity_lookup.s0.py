_BITS_TO_OPCODE = {
    "00": "I",
    "01": "X",
    "10": "Z",
    "11": "XZ",
}

_OPCODE_TO_BITS = {opcode: bits for bits, opcode in _BITS_TO_OPCODE.items()}


def encode_bits(bits: str) -> str:
    if bits not in _BITS_TO_OPCODE:
        raise ValueError("bits must be one of 00, 01, 10, 11")
    return _BITS_TO_OPCODE[bits]


def decode_opcode(opcode: str) -> str:
    normalized = "".join(str(opcode).strip().upper().split())
    if normalized == "ZX":
        normalized = "XZ"
    bits = _OPCODE_TO_BITS.get(normalized)
    if bits is None:
        raise ValueError("opcode must be one of I, X, Z, XZ")
    return bits
