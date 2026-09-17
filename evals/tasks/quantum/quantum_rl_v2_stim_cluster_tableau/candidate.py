"""4-qubit linear cluster Clifford circuit in Stim, with no measurements.

Conventions (explicit):
  * qubit order: string character i (left to right) names the Pauli on
    qubit i (e.g. "XZ__" = X on q0, Z on q1, identity on q2, q3);
  * stabilizer generators of the linear cluster (H on all, CZ on the path
    edges) are g0 = X0 Z1, g1 = Z0 X1 Z2, g2 = Z1 X2 Z3, g3 = Z2 X3,
    all with sign +.
The tableau is obtained via stim.Tableau.from_circuit, the stabilizers via
the public z_output(i) API, each generator is verified to leave the
prepared state invariant, and the inverse tableau appended as a circuit
gives the identity tableau."""

import numpy as np
import stim

I2 = np.eye(2, dtype=complex)
X2 = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
Z2 = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)


def cluster_circuit():
    """Linear cluster on 4 qubits: H on all, CZ on (0,1),(1,2),(2,3)."""
    circuit = stim.Circuit()
    circuit.append("H", [0, 1, 2, 3])
    circuit.append("CZ", [0, 1, 1, 2, 2, 3])
    return circuit


def cluster_tableau():
    return stim.Tableau.from_circuit(cluster_circuit())


def stabilizer_generators():
    """Stabilizer generators as signed stim.PauliString (public API:
    z_output(i) gives the Pauli that Z_i maps to under the circuit)."""
    tableau = cluster_tableau()
    return [tableau.z_output(i) for i in range(4)]


def _pauli_matrix(pauli_string):
    """16x16 unitary matrix of a 4-qubit signed Pauli string (numpy)."""
    single = {"_": I2, "I": I2, "X": X2, "Z": Z2, "Y": 1j * X2 @ Z2}
    mat = np.array([[1.0]])
    for ch in str(pauli_string)[1:]:  # skip the leading sign
        mat = np.kron(mat, single[ch])
    if str(pauli_string)[0] == "-":
        mat = -mat
    return mat


def generator_invariants():
    """Number of generators (out of 4) that leave the tableau state
    invariant: g |psi> = |psi> for the prepared cluster state."""
    tableau = cluster_tableau()
    # endian="big": qubit 0 is the most significant index bit, matching the
    # numpy kron(q0, q1, q2, q3) convention used by _pauli_matrix.
    state = tableau.to_unitary_matrix(endian="big")[:, 0]
    n_ok = 0
    for g in stabilizer_generators():
        if np.allclose(_pauli_matrix(g) @ state, state, atol=1e-9):
            n_ok += 1
    return n_ok


def combined_tableau_is_identity():
    """Append the inverse tableau as a circuit; the combined tableau must
    be the identity (z_output -> +Z_i, x_output -> +X_i for every qubit)."""
    circuit = cluster_circuit()
    circuit += cluster_tableau().inverse().to_circuit()
    combined = stim.Tableau.from_circuit(circuit)
    for i in range(4):
        z_expected = stim.PauliString("_" * i + "Z" + "_" * (3 - i))
        x_expected = stim.PauliString("_" * i + "X" + "_" * (3 - i))
        if combined.z_output(i) != z_expected:
            return False
        if combined.x_output(i) != x_expected:
            return False
    return True


def main():
    circuit = cluster_circuit()
    assert circuit.num_measurements == 0, "circuit must have no measurements"
    generators = stabilizer_generators()
    expected = ["XZ__", "ZXZ_", "_ZXZ", "__ZX"]
    for g, want in zip(generators, expected, strict=False):
        assert str(g) == "+" + want, f"generator {g} != +{want}"
    assert generator_invariants() == 4, "not every generator is invariant"
    assert combined_tableau_is_identity(), "combined tableau not identity"
    print("circuit =", circuit)
    print("generators =", generators)
    print("combined identity =", combined_tableau_is_identity())


if __name__ == "__main__":
    main()
