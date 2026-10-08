import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, SparsePauliOp

def build_bell_state():
    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1)
    return qc

def measure_all_paulis(n):
    """Return the 4^n Pauli basis operators as SparsePauliOp for n qubits."""
    paulis = ["I", "X", "Y", "Z"]
    ops = []
    from itertools import product
    for combo in product(paulis, repeat=n):
        label = "".join(combo)
        ops.append(label)
    return ops

def reconstruct_density_matrix(pauli_expectations, n):
    """Given a dict {pauli_string: expectation_value}, reconstruct the density
    matrix via rho = (1/2^n) * sum_{P} <P> * P."""
    from qiskit.quantum_info import Pauli
    N = 2 ** n
    rho = np.zeros((N, N), dtype=complex)
    for pauli_str, exp_val in pauli_expectations.items():
        # Build the matrix for this Pauli string
        P = Pauli(pauli_str).to_matrix()
        rho += exp_val * P
    rho /= N
    return rho

def main():
    n = 2
    qc = build_bell_state()
    sv = Statevector.from_instruction(qc)
    # Measure all 16 Pauli operators (I, X, Y, Z)^2
    paulis = measure_all_paulis(n)
    expectations = {}
    for p in paulis:
        op = SparsePauliOp.from_list([(p, 1.0)])
        expectations[p] = float(sv.expectation_value(op).real)
    # Reconstruct density matrix
    rho_reconstructed = reconstruct_density_matrix(expectations, n)
    # True density matrix
    rho_true = DensityMatrix(sv).data
    # Fidelity between reconstructed and true: F = Tr(sqrt(sqrt(rho_true) rho_rec sqrt(rho_true)))^2
    # For pure states this is |<psi|rho_rec|psi>|^2
    fidelity = float(np.real(np.vdot(sv.data, rho_reconstructed @ sv.data)))
    # Check entanglement: concurrence for 2 qubits
    # Concurrence C = max(0, lambda1 - lambda2 - lambda3 - lambda4)
    # where lambdas are sqrt of eigenvalues of rho * (Y (x) Y) * rho* * (Y (x) Y)
    Y = np.array([[0, -1j], [1j, 0]])
    YY = np.kron(Y, Y)
    rho_tilde = YY @ rho_reconstructed.conj() @ YY
    product = rho_reconstructed @ rho_tilde
    eigs = np.linalg.eigvalsh(product)
    lambdas = np.sqrt(np.maximum(eigs, 0))
    lambdas = np.sort(lambdas)[::-1]
    concurrence = float(max(0.0, lambdas[0] - lambdas[1] - lambdas[2] - lambdas[3]))
    print(f"Bell state: 2 qubits")
    print(f"Tomography Paulis = {len(paulis)}")
    print(f"Reconstruction fidelity = {fidelity:.6f}")
    print(f"Concurrence = {concurrence:.6f}")
    print(f"Entangled: {abs(concurrence - 1.0) < 1e-6}")
    print(f"Correct: {fidelity > 0.9999 and abs(concurrence - 1.0) < 1e-6}")

if __name__ == "__main__":
    main()
