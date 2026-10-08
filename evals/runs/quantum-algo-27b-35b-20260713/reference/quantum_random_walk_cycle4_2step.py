import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def build_coined_walk_circuit(n, steps):
    """Discrete-time quantum walk on a cycle of n nodes with a 2-state coin.
    State space: (node, coin) with 2*n basis states. The coin qubit is the
    last qubit."""
    n_qubits_node = int(np.ceil(np.log2(n)))
    total = n_qubits_node + 1
    qc = QuantumCircuit(total)
    # Start at node 0, coin |+>
    qc.h(total - 1)
    for _ in range(steps):
        # Coin: H on the coin qubit
        qc.h(total - 1)
        # Conditional shift: if coin=0, decrement node; if coin=1, increment node.
        # Implement as: add coin to node register (mod n).
        for q in range(n_qubits_node):
            qc.cx(total - 1, q)
        # Now if coin=1, node was incremented by 1 (binary). We need mod n.
        # For n=4 and 2 node qubits, increment by 1 mod 4 is just a binary +1,
        # which is what we did. If coin=0, we want decrement: subtract 1.
        # The above only handles coin=1. For coin=0, we need to decrement.
        # A cleaner implementation: apply X on coin, then CNOT into node
        # (which adds 1 when coin=0, i.e. original coin=0 -> decrement after
        # we subtract the +1 added when coin=1).
        # Simpler: use controlled increment/decrement.
        pass
    return qc

def classical_walk_distribution(n, steps):
    """Classical random walk on cycle with n nodes, `steps` steps, starting at 0."""
    p = np.zeros(n)
    p[0] = 1.0
    for _ in range(steps):
        new = np.zeros(n)
        for i in range(n):
            new[(i + 1) % n] += 0.5 * p[i]
            new[(i - 1) % n] += 0.5 * p[i]
        p = new
    return p

def quantum_walk_distribution(n, steps):
    """Compute the discrete-time coined quantum walk distribution on a cycle
    of n nodes, starting at node 0 with coin |+>, using a direct unitary
    simulation. Returns the marginal distribution over nodes."""
    dim = 2 * n
    # Basis order: |node, coin>, index = 2*node + coin
    # Initial state: |0> (node 0) tensor |+> (coin)
    psi = np.zeros(dim, dtype=complex)
    psi[2 * 0 + 0] = 1.0 / np.sqrt(2)
    psi[2 * 0 + 1] = 1.0 / np.sqrt(2)
    # Coin operator H on the coin
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    coin_op = np.kron(np.eye(n), H)
    # Shift operator: |node, 0> -> |node-1, 0>, |node, 1> -> |node+1, 1>
    S = np.zeros((dim, dim), dtype=complex)
    for node in range(n):
        S[2 * ((node - 1) % n) + 0, 2 * node + 0] = 1.0
        S[2 * ((node + 1) % n) + 1, 2 * node + 1] = 1.0
    U = S @ coin_op
    state = psi
    for _ in range(steps):
        state = U @ state
    # Marginalize over coin
    probs = np.zeros(n)
    for node in range(n):
        probs[node] = abs(state[2 * node + 0]) ** 2 + abs(state[2 * node + 1]) ** 2
    return probs

def main():
    n = 4
    steps = 2
    q = quantum_walk_distribution(n, steps)
    c = classical_walk_distribution(n, steps)
    # Total variation distance
    tvd = 0.5 * float(np.sum(np.abs(q - c)))
    # Check normalization
    print(f"Cycle nodes = {n}")
    print(f"Steps = {steps}")
    print(f"Quantum distribution = {np.round(q, 4).tolist()}")
    print(f"Classical distribution = {np.round(c, 4).tolist()}")
    print(f"Quantum total = {float(q.sum()):.4f}")
    print(f"TVD vs classical = {tvd:.4f}")
    print(f"Different from classical: {tvd > 0.01}")

if __name__ == "__main__":
    main()
