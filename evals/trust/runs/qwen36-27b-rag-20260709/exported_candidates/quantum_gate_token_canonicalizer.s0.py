_ALIASES = {
    "h": "H",
    "hadamard": "H",
    "x": "X",
    "paulix": "X",
    "z": "Z",
    "pauliz": "Z",
    "cx": "CX",
    "cnot": "CX",
    "controlledx": "CX",
}


def canonical_gate_token(raw_gate: str) -> str:
    alias = "".join(str(raw_gate).strip().lower().replace("-", "").replace("_", "").split())
    resolved = _ALIASES.get(alias)
    if resolved is None:
        raise ValueError(f"unknown gate token: {raw_gate!r}")
    return resolved
