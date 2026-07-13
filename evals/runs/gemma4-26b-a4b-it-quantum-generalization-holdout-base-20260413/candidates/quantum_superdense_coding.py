def encode_message(bits: str) -> str:
    """
    In superdense coding, the sender applies a specific gate to their qubit 
    to encode two classical bits.
    Mapping based on the test requirements:
    '00' -> 'I' (Identity)
    '01' -> 'X' (Pauli-X)
    '10' -> 'Z' (Pauli-Z)
    '11' -> 'XZ' (Both X and Z)
    """
    mapping = {
        "00": "I",
        "01": "X",
        "10": "Z",
        "11": "XZ"
    }
    return mapping.get(bits)

def decode_message(op: str) -> str:
    """
    The receiver performs a Bell measurement to retrieve the two classical bits.
    """
    mapping = {
        "I": "00",
        "X": "01",
        "Z": "10",
        "XZ": "11"
    }
    return mapping.get(op)
