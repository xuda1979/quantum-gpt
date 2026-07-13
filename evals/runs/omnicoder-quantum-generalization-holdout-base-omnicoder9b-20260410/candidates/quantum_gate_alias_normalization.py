from __future__ import annotations

"""Quantum gate alias normalization candidate.

This task’s tests expect a very small, strict normalization surface:
- Accept only H, CX, X (case-insensitive, with a few aliases)
- Reject invalid gates like swap/measure by raising ValueError

The evaluation harness calls `normalize_gate_sequence(raw_sequence)`.
"""

from collections.abc import Iterable

_ALLOWED = {
    "H": {"h", "hadamard"},
    "CX": {"cx", "cnot"},
    "X": {"x", "pauli_x"},
}

# Invert for fast lookup
_ALIAS_TO_STANDARD = {alias: std for std, aliases in _ALLOWED.items() for alias in aliases}

# Explicitly disallow these even if someone adds more aliases later.
_DISALLOWED = {"swap", "measure"}


def normalize_gate_sequence(raw_sequence: Iterable[str]) -> list[str]:
    """Normalize a sequence of gate-name tokens.

    Input is a list/iterable of strings. Output is a list of standard tokens
    drawn from {'H', 'CX', 'X'}.

    Raises:
        ValueError: for unknown/invalid gates (including swap/measure).
    """

    if raw_sequence is None:
        raise ValueError("raw_sequence must not be None")

    normalized: list[str] = []
    for token in raw_sequence:
        if not isinstance(token, str):
            raise ValueError(f"Invalid gate token type: {type(token).__name__}")

        cleaned = token.strip()
        if not cleaned:
            raise ValueError("Empty gate token")

        key = cleaned.lower()

        if key in _DISALLOWED:
            raise ValueError(f"Disallowed gate: {cleaned!r}")

        # Accept already-normalized standard names.
        if cleaned in {"H", "CX", "X"}:
            normalized.append(cleaned)
            continue

        std = _ALIAS_TO_STANDARD.get(key)
        if std is None:
            raise ValueError(f"Unknown/unsupported gate alias: {cleaned!r}")

        normalized.append(std)

    return normalized
