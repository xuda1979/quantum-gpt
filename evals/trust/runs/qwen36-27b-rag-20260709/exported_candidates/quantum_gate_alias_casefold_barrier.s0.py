from collections.abc import Iterable

_ALIASES = {
    "h": "H",
    "hadamard": "H",
    "cx": "CX",
    "cnot": "CX",
    "controlledx": "CX",
    "x": "X",
    "paulix": "X",
    "z": "Z",
    "pauliz": "Z",
}


def _normalize_alias(raw_gate: str) -> str:
    return "".join(str(raw_gate).strip().lower().replace("-", "").replace("_", "").split())


def normalize_gate_sequence(gates: Iterable[str]) -> list[str]:
    canonical: list[str] = []
    for gate in gates:
        alias = _normalize_alias(gate)
        if alias == "measure":
            raise ValueError("measurement is not a gate alias")
        resolved = _ALIASES.get(alias)
        if resolved is None:
            raise ValueError(f"unknown gate alias: {gate!r}")
        canonical.append(resolved)
    return canonical
