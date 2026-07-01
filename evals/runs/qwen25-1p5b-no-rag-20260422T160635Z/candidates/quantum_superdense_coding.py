from typing import Dict, Tuple

def encode_message(bits: str) -> str:
    operations = {
        "00": "I",
        "01": "X",
        "10": "Z",
        "11": "XZ",
    }
    if bits not in operations:
        raise ValueError("bits must be one of 00, 01, 10, 11")
    return operations[bits]

def decode_message(operation: str) -> str:
    inverse = {
        "I": "00",
        "X": "01",
        "Z": "10",
        "XZ": "11",
    }
    if operation not in inverse:
        raise ValueError("unknown operation")
    return inverse[operation]
