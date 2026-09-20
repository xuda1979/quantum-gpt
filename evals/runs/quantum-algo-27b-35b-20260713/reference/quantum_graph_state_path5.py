import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp

def build_path_graph_state(n, edges):
    """Build a graph state on n qubits with the given edges.
    Apply H to all qubits, then CZ to each edge."""
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for i, j in edges:
        qc.cz(i, j)
    return qc

def graph_state_stabilizers(n, edges):
    """The stabilizers of a graph state are K_i = X_i * prod_{j in N(i)} Z_j,
    one per qubit."""
    stabilizers = []
    adj = {i: [] for i in range(n)}
    for i, j in edges:
        adj[i].append(j); adj[j].append(i)
    for i in range(n):
        # Build the Pauli string (qubit 0 first)
        paulis = ['I'] * n
        paulis[i] = 'X'
        for j in adj[i]:
            paulis[j] = 'Z'
        stabilizers.append("".join(paulis))
    return stabilizers

def main():
    n = 5
    edges = [(0, 1), (1, 2), (2, 3), (3, 4)]  # path graph P_5
    qc = build_path_graph_state(n, edges)
    sv = Statevector.from_instruction(qc)
    stabilizers = graph_state_stabilizers(n, edges)
    results = []
    for pauli in stabilizers:
        op = SparsePauliOp.from_list([(pauli, 1.0)])
        val = float(sv.expectation_value(op).real)
        results.append((pauli, val))
    all_plus = all(abs(v - 1.0) < 1e-9 for _, v in results)
    # Entanglement: trace out 4 qubits, check the remaining is mixed
    from qiskit.quantum_info import DensityMatrix, partial_trace
    dm = DensityMatrix(sv)
    rho0 = partial_trace(dm, list(range(1, n)))
    purity0 = float(np.real(np.trace(rho0.data @ rho0.data)))
    # Graph state is a stabilizer state, so it's pure (single-qubit reduced
    # state is maximally mixed for connected graphs)
    print(f"Graph state: {n} qubits, path graph")
    for pauli, v in results:
        print(f"  <{pauli}> = {v:+.4f}")
    print(f"All stabilizers +1: {all_plus}")
    print(f"Single-qubit purity = {purity0:.4f}")
    print(f"Entangled: {abs(purity0 - 0.5) < 1e-6}")
    print(f"Valid graph state: {all_plus and abs(purity0 - 0.5) < 1e-6}")

if __name__ == "__main__":
    main()
