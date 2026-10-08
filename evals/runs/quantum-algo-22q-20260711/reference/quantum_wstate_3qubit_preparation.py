import math

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(3, 3)
    # Prepare W state (|100>+|010>+|001>)/sqrt(3)
    # Standard construction:
    theta1 = 2 * math.acos(1 / math.sqrt(3))
    qc.ry(theta1, 0)
    qc.cx(0, 1)
    theta2 = 2 * math.acos(1 / math.sqrt(2))
    qc.ry(-theta2, 0)
    qc.cx(0, 2)
    qc.cx(1, 2)
    # After this, the state should be |W> on q0 q1 q2 with
    # |100> (q0=1), |010> (q1=1), |001> (q2=1) — but the exact qubit ordering
    # depends on the construction. We'll just measure and count Hamming weight 1.
    qc.measure([0, 1, 2], [0, 1, 2])
    counts = StatevectorSampler().run([qc], shots=6000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    hw1 = [b for b in counts if b.count("1") == 1]
    p1 = sum(counts[b] for b in hw1) / total
    print(f"W-state count: {len(hw1)}")
    print(f"P(single excitation) = {p1:.3f}")

if __name__ == "__main__":
    main()
