"""Standard QPE with 2 ancilla qubits estimating theta = 1/3.

U = diag(1, exp(i*2*pi*1/3)). Eigenstate |1> has eigenvalue exp(i*2*pi/3).
With 2 ancillas, the closest 2-bit approximation to 1/3 is round(4/3)=1, so
phase_bits='01' and phase_float = 1/4 = 0.25 (the nearest 2-bit fraction).
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT, PhaseGate
from qiskit.primitives import StatevectorSampler


def main():
    m = 2
    theta = 1.0 / 3.0
    qc = QuantumCircuit(m + 1, m)
    qc.x(m)  # eigenstate |1>
    for i in range(m):
        qc.h(i)
    for i in range(m):
        cu = PhaseGate(2 * np.pi * theta * (2 ** i)).control(1)
        qc.append(cu, [i, m])
    qc.append(QFT(m, inverse=True), range(m))
    qc.measure(range(m), range(m))
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    top = max(counts, key=counts.get)
    phase_bits = top
    phase_float = int(phase_bits, 2) / (2 ** m)
    print(f"phase_bits = {phase_bits}")
    print(f"phase_float = {phase_float:.3f}")


if __name__ == "__main__":
    main()
