import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.primitives import StatevectorSampler


def main():
    # Register A: 3 qubits (q0,q1,q2), hold 3 = |011> (q0=1, q1=1, q2=0)
    # Register B: 2 qubits (q3,q4), hold 2 = |10> (q3=0, q4=1)
    nA = 3
    nB = 2
    total = nA + nB
    qc = QuantumCircuit(total, nA)
    # Init A = 3
    qc.x(0); qc.x(1)
    # Init B = 2
    qc.x(4)
    # QFT on A
    qc.append(QFT(nA, do_swaps=False), range(nA))
    # Draper rotations: for each bit b_j of B (j=0..nB-1), and for each a_k
    # in A (k=0..nA-1) with k >= j, apply controlled-P(2*pi/2^(k-j+1)) from
    # b_j to a_k.
    for j in range(nB):
        b_qubit = nA + j
        for k in range(j, nA):
            angle = 2 * np.pi / (2 ** (k - j + 1))
            qc.cp(angle, b_qubit, k)
    # Inverse QFT on A
    qc.append(QFT(nA, inverse=True, do_swaps=False), range(nA))
    # Measure A
    qc.measure(range(nA), range(nA))
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    top = max(counts, key=counts.get)
    # top is c2 c1 c0 (big-endian Qiskit). Integer = int(top, 2).
    val = int(top, 2)
    print(f"sum = {val}")

if __name__ == "__main__":
    main()
