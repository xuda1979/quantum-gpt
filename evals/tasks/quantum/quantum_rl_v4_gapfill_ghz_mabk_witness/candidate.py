"""GHZ state builder and Mermin (MABK) witness with an exact required API.

M = XXX - XYY - YXY - YYX; local hidden variable theories satisfy
|<M>| <= 2 while the GHZ state reaches 4. This task grades the
entry-point contract itself: every required function must exist under
its exact name.
"""

from __future__ import annotations

import numpy as np


def _pauli(name):
    if name == "X":
        return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    if name == "Y":
        return np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
    return np.eye(2, dtype=complex)


def _kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


def ghz_state():
    """(|000> + |111>) / sqrt(2) as a length-8 state vector."""
    psi = np.zeros(8, dtype=complex)
    psi[0] = 1.0 / np.sqrt(2.0)
    psi[7] = 1.0 / np.sqrt(2.0)
    return psi


def mermin_operator():
    """M = XXX - XYY - YXY - YYX as an 8x8 matrix."""
    M = np.zeros((8, 8), dtype=complex)
    M += _kron3(_pauli("X"), _pauli("X"), _pauli("X"))
    for term in ("XYY", "YXY", "YYX"):
        M -= _kron3(_pauli(term[0]), _pauli(term[1]), _pauli(term[2]))
    return M


def expectation(psi, M):
    """Real part of psi^dagger M psi."""
    return float(np.real(np.conj(psi) @ M @ psi))


def witness_value(psi):
    """|<M>| minus the LHV bound of 2."""
    M = mermin_operator()
    return abs(expectation(psi, M)) - 2.0


def density_matrix(psi):
    """|psi><psi|."""
    return np.outer(psi, np.conj(psi))


def run_checks():
    """All witness quantities for the harness."""
    psi = ghz_state()
    M = mermin_operator()
    rho = density_matrix(psi)
    pur = float(np.sum(np.linalg.eigvalsh((rho + rho.conj().T) / 2.0) ** 2))
    return dict(
        m_exp=expectation(psi, M),
        witness=witness_value(psi),
        is_pure=pur,
    )


def main():
    res = run_checks()
    for key, value in res.items():
        print(key, "=", value)
    assert abs(abs(res["m_exp"]) - 4.0) < 1e-9, "GHZ must saturate |<M>| = 4"
    assert abs(res["witness"] - 2.0) < 1e-9, "witness must exceed the LHV bound by 2"
    assert abs(res["is_pure"] - 1.0) < 1e-12, "GHZ density matrix must be pure"
    print("GHZ Mermin witness OK")


if __name__ == "__main__":
    main()
