"""Grover's algorithm on 4 qubits with marked state |1101>.

With N=16 and 1 marked item, the optimal number of Grover iterations is
floor(pi/4 * sqrt(N)) = floor(pi/4 * 4) = 3. We use 3 iterations.
The marked state is binary 1101 (MSB-first), so qubit 3=1, qubit 2=1,
qubit 1=0, qubit 0=1. Oracle: flip phase of |1101>. Diffuser: H^{⊗n},
X^{⊗n}, multi-Z, X^{⊗n}, H^{⊗n}.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def grover_oracle(n: int, marked: str) -> QuantumCircuit:
    """Mark the state `marked` (MSB-first string of length n) with a phase flip."""
    qc = QuantumCircuit(n)
    # Apply X to qubits where marked bit is 0
    for i, b in enumerate(reversed(marked)):
        if b == '0':
            qc.x(i)
    # Multi-controlled Z
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    # Undo X
    for i, b in enumerate(reversed(marked)):
        if b == '0':
            qc.x(i)
    return qc


def grover_diffuser(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    for i in range(n):
        qc.h(i)
        qc.x(i)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    for i in range(n):
        qc.x(i)
        qc.h(i)
    return qc


def main():
    n = 4
    marked = "1101"
    N = 2 ** n
    iterations = int(np.floor(np.pi / 4 * np.sqrt(N)))
    qc = QuantumCircuit(n, n)
    for i in range(n):
        qc.h(i)
    oracle = grover_oracle(n, marked)
    diffuser = grover_diffuser(n)
    for _ in range(iterations):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)
    qc.measure(range(n), range(n))
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    top = max(counts, key=counts.get)
    p_marked = counts.get(marked, 0) / sum(counts.values())
    print(f"Top measurement: {top}")
    print(f"P(marked={marked}) = {p_marked:.3f}")
    print(f"Iterations: {iterations}")


if __name__ == "__main__":
    main()
