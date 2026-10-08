"""2x1 spinful Fermi-Hubbard model in OpenFermion: Jordan-Wigner
transform, sparse matrix with explicit qubit count, ground-state
eigenpair, direct-energy verification, and total particle number.

Instance: tunneling=1.0, onsite coulomb=2.0, chemical potential=0,
open boundary (periodic=False). Two sites x two spins -> 4 qubits.
The Hamiltonian commutes with the total particle number, so the
ground state (half-filled, 2 electrons) has <N> = 2 with zero variance.
"""

import numpy as np
from openfermion import (
    fermi_hubbard,
    get_sparse_operator,
    jordan_wigner,
    number_operator,
)
from scipy.linalg import eigh


def hamiltonian():
    """Fermi-Hubbard FermionOperator for the 2x1 spinful chain."""
    return fermi_hubbard(
        2,
        1,
        tunneling=1.0,
        coulomb=2.0,
        chemical_potential=0.0,
        periodic=False,
        spinless=False,
    )


def jw_hamiltonian(n_qubits=4):
    """Jordan-Wigner transform of the Hubbard Hamiltonian."""
    return jordan_wigner(hamiltonian())


def sparse_matrix(n_qubits=4):
    """Explicit sparse matrix of the JW Hamiltonian on n_qubits."""
    return get_sparse_operator(jw_hamiltonian(), n_qubits=n_qubits)


def ground_state(n_qubits=4):
    """(E0, normalized ground statevector) via dense exact diagonalization."""
    h = sparse_matrix(n_qubits).toarray()
    evals, evecs = eigh(h)
    return float(np.real(evals[0])), evecs[:, 0].astype(complex)


def energy_expectation(psi, n_qubits=4):
    """<psi|H|psi> via the sparse matrix."""
    h = sparse_matrix(n_qubits)
    return float(np.real(np.vdot(psi, h @ psi)))


def hermiticity_deviation(n_qubits=4):
    """||H - H^dag||_max of the sparse matrix."""
    h = sparse_matrix(n_qubits).toarray()
    return float(np.max(np.abs(h - h.conj().T)))


def eigenpair_residual(psi, e0, n_qubits=4):
    """||H|psi> - E|psi>||_2."""
    h = sparse_matrix(n_qubits)
    return float(np.linalg.norm(h @ psi - e0 * psi))


def number_operator_jw(n_qubits=4):
    """JW total particle number N = sum_i n_i as a sparse matrix."""
    total = 0
    for i in range(n_qubits):
        total += number_operator(n_qubits, i)
    return get_sparse_operator(jordan_wigner(total), n_qubits=n_qubits)


def particle_number_stats(psi, n_qubits=4):
    """<N> and Var(N) = <N^2> - <N>^2 for the given state."""
    n_op = number_operator_jw(n_qubits)
    mean = float(np.real(np.vdot(psi, n_op @ psi)))
    n2 = n_op @ (n_op @ psi)
    second = float(np.real(np.vdot(psi, n2)))
    return mean, second - mean * mean


def main():
    e0, psi = ground_state()
    e_direct = energy_expectation(psi)
    resid = eigenpair_residual(psi, e0)
    hermit = hermiticity_deviation()
    n_mean, n_var = particle_number_stats(psi)
    print("E0 =", e0)
    print("<psi|H|psi> =", e_direct)
    print("residual =", resid)
    print("hermiticity =", hermit)
    print("<N> =", n_mean, " Var(N) =", n_var)
    assert abs(e0 - e_direct) < 1e-10
    assert resid < 1e-8
    assert hermit < 1e-12
    assert abs(n_mean - 2.0) < 1e-9
    assert n_var < 1e-9
    assert abs(np.linalg.norm(psi) - 1.0) < 1e-9
    print("Hubbard spectrum OK")


if __name__ == "__main__":
    main()
