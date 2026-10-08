from typing import Dict, Tuple

_BITS_TO_LABEL: Dict[str, str] = {
    "00": "I",
    "01": "X",
    "10": "Z",
    "11": "XZ",
}

_LABEL_TO_BITS: Dict[str, str] = {value: key for key, value in _BITS_TO_LABEL.items()}

def canonicalize_pauli_label(label: str) -> str:
    normalized = "".join(str(label).strip().upper().split())
    if normalized == "ZX":
        normalized = "XZ"
    if normalized not in _LABEL_TO_BITS:
        raise ValueError("unknown Pauli label")
    return normalized
