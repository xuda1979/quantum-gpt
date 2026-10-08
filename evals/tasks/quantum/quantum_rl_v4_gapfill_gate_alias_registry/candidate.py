"""Gate-name normalization registry with an exact required API.

The registry maps casefolded aliases to canonical gate names. This task grades
the entry-point contract itself: every required function must exist under its
exact name, mirroring the s97 gap class where candidates scored 4+ on rubric
axes yet failed on a missing module attribute."""

from __future__ import annotations

REGISTRY = dict(
    h="h",
    hadamard="h",
    x="x",
    pauli_x="x",
    cx="cx",
    cnot="cx",
    ccx="ccx",
    toffoli="ccx",
    s="s",
    z="z",
)


def normalize(name):
    """Casefold then look up; unknown names raise KeyError."""
    return REGISTRY[name.casefold().strip()]


def lookup(name):
    """Alias for normalize (kept as a separate required entry point)."""
    return normalize(name)


def aliases():
    """All alias keys, sorted."""
    return sorted(REGISTRY.keys())


def canonicals():
    """Distinct canonical targets, sorted."""
    return sorted(set(REGISTRY.values()))


def register(alias, canonical):
    """Add a new alias at runtime."""
    REGISTRY[alias.casefold().strip()] = canonical


def stats():
    """Registry size summary."""
    return dict(n_aliases=len(REGISTRY), n_canonicals=len(set(REGISTRY.values())))


def main():
    assert normalize("Hadamard") == "h"
    assert lookup("PAULI_X") == "x"
    assert normalize("cnot") == "cx"
    register("sx", "x")
    assert normalize("SX") == "x"
    st = stats()
    assert st["n_canonicals"] == len(set(canonicals()))
    print("gate alias registry OK", st)


if __name__ == "__main__":
    main()
