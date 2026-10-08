"""Bare-file gate alias normalization - no-fence exemplar.

Teaches: emit the complete file directly; keep it short enough to finish."""


def normalize_gate_sequence(gates):
    aliases = dict(h="H", hadamard="H", x="X", pauli_x="X", cx="CX", cnot="CX")
    normalized = []
    for gate in gates:
        key = str(gate).strip().lower()
        if key not in aliases:
            raise ValueError("unknown gate: %r" % (gate,))
        normalized.append(aliases[key])
    return normalized


def _self_test():
    assert normalize_gate_sequence(["h", "CX", "pauli_x", "hadamard"]) == [
        "H",
        "CX",
        "X",
        "H",
    ]
    assert normalize_gate_sequence([]) == []
    try:
        normalize_gate_sequence(["toffoli"])
    except ValueError:
        pass
    else:
        raise AssertionError("unknown gate must raise ValueError")


_self_test()
