_BITS_TO_LABEL = {
    "00": "I",
    "01": "X",
    "10": "Z",
    "11": "XZ",
}

_LABEL_TO_BITS = {value: key for key, value in _BITS_TO_LABEL.items()}


def canonicalize_pauli_label(label: str) -> str:
    normalized = "".join(str(label).strip().upper().split())
    if normalized == "ZX":
        normalized = "XZ"
    if normalized not in _LABEL_TO_BITS:
        raise ValueError("unknown Pauli label")
    return normalized


def bits_to_pauli_label(bits: str) -> str:
    if bits not in _BITS_TO_LABEL:
        raise ValueError("bits must be one of 00, 01, 10, 11")
    return _BITS_TO_LABEL[bits]


def pauli_label_to_bits(label: str) -> str:
    return _LABEL_TO_BITS[canonicalize_pauli_label(label)]
