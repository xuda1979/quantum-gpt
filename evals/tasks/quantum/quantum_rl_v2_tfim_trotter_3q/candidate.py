"""3-qubit open-boundary transverse-field Ising (TFIM) time evolution by
a palindromic symmetric second-order (Strang) product formula.

Hamiltonian: H = -0.7*sum_i Z_i Z_{i+1} - 0.5*sum_i X_i (open boundary)
Time t = 0.8, initial state |010> in q2 q1 q0 display order (index 2),
10 steps of S2(delta) = prod_j exp(-i delta H_j / 2)
                        prod_j exp(-i delta H_j / 2)  (palindromic),
with the five Pauli terms listed explicitly. The Hamiltonian matrix is
rebuilt independently with NumPy/SciPy and the final state is compared
with exact expm(-i H t) evolution by fidelity and <Z0>.
"""

import numpy as np
from scipy.linalg import expm

N_QUBITS = 3
T = 0.8
STEPS = 10

I2 = np.eye(2, dtype=complex)
X2 = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
Y2 = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
Z2 = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
_PAULI = {"X": X2, "Y": Y2, "Z": Z2}


def _kron_many(mats):
    out = mats[0]
    for m in mats[1:]:
        out = np.kron(out, m)
    return out


def pauli_term_matrix(qubit, pauli):
    """Full 2^n x 2^n matrix of a single-qubit Pauli on `qubit`."""
    mats = [I2] * N_QUBITS
    mats[qubit] = _PAULI[pauli]
    return _kron_many(mats)


def tfim_terms():
    """Explicitly listed Pauli terms as (coefficient, matrix, label):
    edges (0,1), (1,2) with -0.7*ZZ, then -0.5*X per qubit."""
    terms = []
    for edge in (0, 1):
        m = pauli_term_matrix(edge, "Z")
        m = m @ pauli_term_matrix(edge + 1, "Z")
        terms.append((-0.7, m, f"Z{edge}Z{edge + 1}"))
    for q in range(N_QUBITS):
        terms.append((-0.5, pauli_term_matrix(q, "X"), f"X{q}"))
    return terms


def h_matrix():
    """H as an 8x8 matrix: sum of the explicitly listed terms."""
    return sum(c * m for c, m, _ in tfim_terms())


def initial_state():
    """|010> in q2 q1 q0 display order -> computational-basis index 2."""
    psi = np.zeros(1 << N_QUBITS, dtype=complex)
    psi[2] = 1.0
    return psi


def exact_unitary(t=T):
    """expm(-i H t)."""
    return expm(-1.0j * h_matrix() * t)


def suzuki2_unitary(t=T, steps=STEPS):
    """Palindromic symmetric second-order product formula, S2(delta)^steps
    with delta = t/steps; each step applies the half-steps of every term
    in listed order and then again in reverse (palindromic)."""
    delta = t / steps
    step = np.eye(1 << N_QUBITS, dtype=complex)
    for c, m, _ in tfim_terms():
        step = expm(-0.5j * delta * c * m) @ step
    for c, m, _ in reversed(tfim_terms()):
        step = expm(-0.5j * delta * c * m) @ step
    return np.linalg.matrix_power(step, steps)


def z0_expectation(psi):
    """<Z0> = Tr(|psi><psi| (Z otimes I otimes I)), qubit 0 = index bit 0."""
    z0 = _kron_many([Z2, I2, I2])
    return float(np.real(np.vdot(psi, z0 @ psi)))


def final_state_fidelity(t=T, steps=STEPS):
    """|langle psi_trotter | psi_exact rangle|^2."""
    psi_exact = exact_unitary(t) @ initial_state()
    psi_trotter = suzuki2_unitary(t, steps) @ initial_state()
    return float(abs(np.vdot(psi_exact, psi_trotter)) ** 2)


def main():
    psi_exact = exact_unitary() @ initial_state()
    psi_trotter = suzuki2_unitary() @ initial_state()
    f = final_state_fidelity()
    z_t = z0_expectation(psi_trotter)
    z_e = z0_expectation(psi_exact)
    print("fidelity =", f)
    print("<Z0> trotter =", z_t, " exact =", z_e)
    assert f > 0.995, f"fidelity {f} not above 0.995"
    assert abs(z_t - z_e) < 0.005
    u = suzuki2_unitary()
    assert np.max(np.abs(u.conj().T @ u - np.eye(8, dtype=complex))) < 1e-9


if __name__ == "__main__":
    main()
