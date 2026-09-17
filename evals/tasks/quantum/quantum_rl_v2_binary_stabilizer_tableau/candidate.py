"""Aaronson-Gottesman style binary stabilizer tableau for 3 qubits.

The tableau holds 2n binary rows: the first n are the destabilizer rows
(initially X_i) and the last n are the stabilizer rows (initially Z_i),
each with an x-bit vector, a z-bit vector and a sign bit. H, S and CNOT
conjugation follow the standard symplectic update rules with sign
updates computed from the ORIGINAL bits before any x/z mutation. CZ is
composed as H-CNOT-H. GHZ and cluster-state test circuits are applied
and the stabilizer rows are converted to signed Pauli strings."""

from __future__ import annotations

import numpy as np


def new_tableau(n: int) -> dict:
    """Tableau with destabilizer rows X_i and stabilizer rows Z_i."""
    t = {
        "n": n,
        "x": np.zeros((2 * n, n), dtype=np.uint8),
        "z": np.zeros((2 * n, n), dtype=np.uint8),
        "phase": np.zeros(2 * n, dtype=np.uint8),
    }
    for i in range(n):
        t["x"][i, i] = 1  # destabilizer X_i
        t["z"][n + i, i] = 1  # stabilizer Z_i
    return t


def apply_h(t: dict, q: int) -> None:
    """H conjugation: swap x/z, sign flips when both bits were set."""
    n = t["n"]
    for r in range(2 * n):
        t["phase"][r] ^= t["x"][r, q] & t["z"][r, q]
        x = t["x"][r, q]
        t["x"][r, q] = t["z"][r, q]
        t["z"][r, q] = x


def apply_s(t: dict, q: int) -> None:
    """S conjugation: X -> Y (z ^= x), sign flips on Y (both bits set)."""
    n = t["n"]
    for r in range(2 * n):
        t["phase"][r] ^= t["x"][r, q] & t["z"][r, q]
        t["z"][r, q] ^= t["x"][r, q]


def apply_cnot(t: dict, control: int, target: int) -> None:
    """CNOT conjugation: X flows control->target, Z flows target->control;
    the sign flips on X_control Z_target pairs (Y_control Y_target)."""
    n = t["n"]
    for r in range(2 * n):
        t["phase"][r] ^= (
            t["x"][r, control] & t["z"][r, target] & (1 ^ (t["x"][r, target] ^ t["z"][r, control]))
        )
        t["x"][r, target] ^= t["x"][r, control]
        t["z"][r, control] ^= t["z"][r, target]


def apply_cz(t: dict, a: int, b: int) -> None:
    """CZ conjugation via H(b) CNOT(a,b) H(b)."""
    apply_h(t, b)
    apply_cnot(t, a, b)
    apply_h(t, b)


def stabilizer_paulis(t: dict) -> list[str]:
    """Signed Pauli strings of the n stabilizer rows (qubit 0 leftmost)."""
    return _row_paulis(t, start=t["n"])


def destabilizer_paulis(t: dict) -> list[str]:
    """Signed Pauli strings of the n destabilizer rows."""
    return _row_paulis(t, start=0)


def _row_paulis(t: dict, start: int) -> list[str]:
    out = []
    for r in range(start, start + t["n"]):
        s = "-" if t["phase"][r] else "+"
        for q in range(t["n"]):
            x, z = int(t["x"][r, q]), int(t["z"][r, q])
            if not x and not z:
                s += "I"
            elif x and not z:
                s += "X"
            elif not x and z:
                s += "Z"
            else:
                s += "Y"
        out.append(s)
    return out


def symplectic_product(t: dict, i: int, j: int) -> int:
    """Binary symplectic product of rows i and j: 1 = anticommute."""
    n = t["n"]
    xz = int(np.sum(t["x"][i, :] * t["z"][j, :])) % 2
    zx = int(np.sum(t["z"][i, :] * t["x"][j, :])) % 2
    return (xz + zx) % 2


def ghz_tableau() -> dict:
    """Tableau after H(0), CNOT(0,1), CNOT(0,2)."""
    t = new_tableau(3)
    apply_h(t, 0)
    apply_cnot(t, 0, 1)
    apply_cnot(t, 0, 2)
    return t


def cluster_tableau() -> dict:
    """Tableau after H on all qubits, CZ(0,1), CZ(1,2)."""
    t = new_tableau(3)
    for q in range(3):
        apply_h(t, q)
    apply_cz(t, 0, 1)
    apply_cz(t, 1, 2)
    return t


def run_checks() -> dict:
    """Expected generators and commutation relations for both states."""
    t_ghz = ghz_tableau()
    t_cluster = cluster_tableau()
    comm = {"ghz": 0, "cluster": 0}
    for name, t in (("ghz", t_ghz), ("cluster", t_cluster)):
        for i in range(3):
            for j in range(3):
                comm[name] += symplectic_product(t, t["n"] + i, t["n"] + j)
    return {
        "ghz_generators": sorted(stabilizer_paulis(t_ghz)),
        "cluster_generators": sorted(stabilizer_paulis(t_cluster)),
        "ghz_commute_violations": comm["ghz"],
        "cluster_commute_violations": comm["cluster"],
    }


def main():
    result = run_checks()
    print("ghz_generators =", result["ghz_generators"])
    print("cluster_generators =", result["cluster_generators"])
    assert result["ghz_generators"] == ["+XXX", "+ZIZ", "+ZZI"], "GHZ generators"
    assert result["cluster_generators"] == ["+IZX", "+XZI", "+ZXZ"], "cluster generators"
    assert result["ghz_commute_violations"] == 0, "GHZ stabilizers commute"
    assert result["cluster_commute_violations"] == 0, "cluster stabilizers commute"


if __name__ == "__main__":
    main()
