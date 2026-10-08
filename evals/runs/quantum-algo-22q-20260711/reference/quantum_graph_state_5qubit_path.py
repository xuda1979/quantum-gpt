from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

# Path graph P5 edges
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4)]

def neighbors(i):
    return [j for (a, b) in EDGES for j in ([b] if a == i else ([a] if b == i else []))]

def main():
    n = 5
    # Measure each stabilizer K_i = X_i * prod_{j in N(i)} Z_j in a separate shot.
    # To measure K_i: convert X_i to Z_i by H on qubit i; the Z neighbors are
    # already Z. So total operator is Z_i * prod_{j in N(i)} Z_j = product of
    # Z on qubit i and all its neighbors. Measure by CNOT from each of those
    # qubits to an ancilla, then measure the ancilla.
    # Simpler: use 5 separate circuits, each measuring one stabilizer.
    plus1_count = 0
    sampler = StatevectorSampler()
    for i in range(n):
        qc = QuantumCircuit(n + 1, 1)
        # Prepare graph state
        for q in range(n):
            qc.h(q)
        for (a, b) in EDGES:
            qc.cz(a, b)
        # Measure stabilizer K_i: convert X_i to Z_i by H, then CNOT all
        # involved qubits (i and its neighbors) to ancilla, measure ancilla.
        qc.h(i)  # now K_i = Z_i * prod_{j in N(i)} Z_j
        targets = [i] + neighbors(i)
        anc = n
        for t in targets:
            qc.cx(t, anc)
        qc.measure(anc, 0)
        counts = sampler.run([qc], shots=2000).result()[0].data.c.get_counts()
        top = max(counts, key=counts.get)
        # Measurement outcome 0 means +1 eigenvalue, 1 means -1
        if top == "0":
            plus1_count += 1
    print(f"stab_eigenvalue = {plus1_count}")
    print(f"graph_state: {'True' if plus1_count == 5 else 'False'}")

if __name__ == "__main__":
    main()
