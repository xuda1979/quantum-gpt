# Reference implementation
def encode_message(bits: str) -> str:
    """Quantum superdense coding encode.

    Input bits should be a binary string.
    Returns the quantum operation to apply.
    """
    h = lambda: "H"
    t = lambda: "S"
    m = {
        "0": h,
        "1": t,
    }
    raw = list(bits.strip())
    n = len(raw)
    qubits = [m.get(raw[i], None) for i in range(n)]
    return "".join(qubits)


def decode_message(op: str) -> str:
    """Quantum superdense coding decode.

    Input op should be a two-qubit quantum operation.
    Returns the decoded bits as a plain string.
    """
    s = {
        "I": "",
        "X": "1",
        "Z": "0",
        "XZ": "11",
    }
    return s[op.strip()]
