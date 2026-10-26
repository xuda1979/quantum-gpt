"""[[5,1,3]] perfect code stabilizer generators and syndrome table.

The five-qubit code is the smallest quantum error-correcting code that
corrects any single-qubit error. This module exposes the four stabilizer
generators as Pauli strings and a function that maps a single-qubit error
(X/Y/Z on qubit 0..4) to its 4-bit syndrome.
"""

import numpy as np


def stabilizer_generators() -> list[str]:
    """Return the four stabilizer generators of the [[5,1,3]] code.

    Each generator is a length-5 Pauli string over {I,X,Y,Z}, ordered
    qubit 0..4 left to right.
    """
    return ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]


def _pauli_to_vec(p: str) -> np.ndarray:
    """Map a Pauli char to a (x,z) binary pair for the symplectic representation."""
    table = {
        "I": (0, 0),
        "X": (1, 0),
        "Y": (1, 1),
        "Z": (0, 1),
    }
    return np.array(table[p], dtype=int)


def stabilizer_matrix() -> np.ndarray:
    """Return the 4x10 binary symplectic matrix S = [Sx | Sz]."""
    gens = stabilizer_generators()
    rows = []
    for g in gens:
        sx, sz = [], []
        for ch in g:
            x, z = _pauli_to_vec(ch)
            sx.append(x)
            sz.append(z)
        rows.append(sx + sz)
    return np.array(rows, dtype=int)


def syndrome_of(error: str) -> str:
    """Compute the 4-bit syndrome of a length-5 Pauli error string.

    The syndrome is the bitwise XOR of the stabilizer generators that
    anticommute with the error.
    """
    gens = stabilizer_generators()
    if len(error) != 5 or any(c not in "IXYZ" for c in error):
        raise ValueError(f"error must be a length-5 Pauli string, got {error!r}")
    ex = np.array([_pauli_to_vec(c)[0] for c in error], dtype=int)
    ez = np.array([_pauli_to_vec(c)[1] for c in error], dtype=int)
    S = stabilizer_matrix()  # (4, 10)
    Sx = S[:, :5]
    Sz = S[:, 5:]
    # Anticommutes if the symplectic inner product is 1 mod 2.
    syndrome = (Sx @ ez + Sz @ ex) % 2
    return "".join(str(b) for b in syndrome)


def single_qubit_error_table() -> dict[str, str]:
    """Map every single-qubit Pauli error on every qubit to its syndrome.

    Keys are like 'X0', 'Y2', 'Z4'. The 'I' (no error) case maps to '0000'.
    """
    table = {"I": "0000"}
    for q in range(5):
        for p in "XYZ":
            err = ["I"] * 5
            err[q] = p
            table[f"{p}{q}"] = syndrome_of("".join(err))
    return table


if __name__ == "__main__":
    table = single_qubit_error_table()
    for k, v in sorted(table.items()):
        print(f"  {k}: {v}")
    # Sanity: every single-qubit error should have a unique, non-zero syndrome
    syndromes = [v for k, v in table.items() if k != "I"]
    assert len(set(syndromes)) == 15, "five-qubit code must correct all single-qubit errors"
