from typing import Dict, List, Optional


_RAW_ALIAS_ENTRIES: Dict[str, str] = {
    "h": "H",
    "hadamard": "H",
    "h_gate": "H",
    "cnot": "CX",
    "cx": "CX",
    "controlled-x": "CX",
    "x": "X",
    "pauli_x": "X",
    "paulix": "X",
    "y": "Y",
    "pauli_y": "Y",
    "z": "Z",
    "pauli_z": "Z",
    "swap": "SWAP",
    "swap_gate": "SWAP",
}


def _normalize_alias(alias: str) -> str:
    return alias.strip().lower().replace(" ", "").replace("-", "").replace("_", "")


_BASE_REGISTRY: Dict[str, str] = {
    _normalize_alias(alias): canonical for alias, canonical in _RAW_ALIAS_ENTRIES.items()
}


def _lookup_canonical(alias: str, registry: dict[str, str]) -> str:
    normalized = _normalize_alias(alias)
    canonical = registry.get(normalized)
    if canonical is None:
        raise ValueError(f"unknown gate alias: {alias!r}")
    return canonical


def normalize_gate_sequence(
    gates: List[str], *, alias_registry: Optional[Dict[str, str]] = None
) -> List[str]:
    """
    Return the canonical gate names for a sequence of aliases.

    Raises ValueError when an alias cannot be resolved.
    """
    registry = alias_registry or _BASE_REGISTRY
    return [_lookup_canonical(gate, registry) for gate in gates]


def canonical_registry() -> dict[str, str]:
    """Expose a copy of the default alias registry for inspection."""
    return dict(_BASE_REGISTRY)
