import math

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def correlation(theta_a: float, theta_b: float) -> float:
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)
    # Rotate each qubit by -2*theta around Y to measure in the sigma_X(theta) basis
    qc.ry(-2 * theta_a, 0)
    qc.ry(-2 * theta_b, 1)
    qc.measure([0, 1], [0, 1])
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    e = (counts.get("00", 0) + counts.get("11", 0) - counts.get("01", 0) - counts.get("10", 0)) / total
    return e

def main():
    a = 0.0
    a2 = math.pi / 2
    b = math.pi / 4
    b2 = -math.pi / 4
    E_ab = correlation(a, b)
    E_ab2 = correlation(a, b2)
    E_a2b = correlation(a2, b)
    E_a2b2 = correlation(a2, b2)
    S = abs(E_ab - E_ab2 + E_a2b + E_a2b2)
    print(f"S = {S:.3f}")
    print(f"violation: {'True' if S > 2.0 else 'False'}")

if __name__ == "__main__":
    main()
