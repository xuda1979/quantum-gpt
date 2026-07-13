"""Prepare a 4-qubit GHZ state and verify via measurement statistics.

GHZ_4 = (|0000> + |1111>)/sqrt(2). Apply H to qubit 0, then CNOT(0,1),
CNOT(1,2), CNOT(2,3). Measure with StatevectorSampler. The probability
of 0000 should be ~0.5 and 1111 should be ~0.5; total GHZ probability
P_GHZ = P(0000) + P(1111) should be >= 0.99.
"""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    n = 4
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure(range(n), range(n))
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    p0000 = counts.get("0000", 0) / total
    p1111 = counts.get("1111", 0) / total
    p_ghz = p0000 + p1111
    print(f"P(0000) = {p0000:.3f}")
    print(f"P(1111) = {p1111:.3f}")
    print(f"P(GHZ) = {p_ghz:.3f}")


if __name__ == "__main__":
    main()
