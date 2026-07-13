"""CHSH Bell inequality test with optimal measurement angles.

Prepare a Bell state |Phi+> = (|00>+|11>)/sqrt(2). Alice picks between
a=0 and a'=pi/4. Bob picks between b=pi/8 and b'=-pi/8. The CHSH value
S = E(a,b) + E(a,b') + E(a',b) - E(a',b') = 2*sqrt(2) ≈ 2.828,
violating the classical bound of 2.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def measure_correlation(angle_a: float, angle_b: float, shots: int = 4000) -> float:
    """Returns E(a,b) = P(00)+P(11)-P(01)-P(10) for the Bell state."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(2 * angle_a, 0)
    qc.ry(2 * angle_b, 1)
    qc.measure([0, 1], [0, 1])
    counts = StatevectorSampler().run([qc], shots=shots).result()[0].data.c.get_counts()
    total = sum(counts.values())
    p00 = counts.get("00", 0) / total
    p11 = counts.get("11", 0) / total
    p01 = counts.get("01", 0) / total
    p10 = counts.get("10", 0) / total
    return p00 + p11 - p01 - p10


def main():
    a = 0.0
    a2 = np.pi / 4
    b = np.pi / 8
    b2 = -np.pi / 8
    e_ab = measure_correlation(a, b)
    e_ab2 = measure_correlation(a, b2)
    e_a2b = measure_correlation(a2, b)
    e_a2b2 = measure_correlation(a2, b2)
    S = e_ab + e_ab2 + e_a2b - e_a2b2
    print(f"S = {S:.3f}")
    print(f"violation: {S > 2.0}")


if __name__ == "__main__":
    main()
