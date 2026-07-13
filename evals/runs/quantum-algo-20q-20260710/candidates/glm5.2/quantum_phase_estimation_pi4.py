from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def qft_inverse(qc, qubits):
    """Apply inverse QFT on the given qubits."""
    n = len(qubits)
    # Swap qubits
    for i in range(n // 2):
        qc.swap(qubits[i], qubits[n - 1 - i])
    # Inverse QFT
    for j in range(n):
        for k in range(j):
            qc.cp(-np.pi / (2 ** (j - k)), qubits[j], qubits[k])
        qc.h(qubits[j])

def main():
    # Create circuit with 4 qubits: 3 counting + 1 target
    qc = QuantumCircuit(4, 3)

    # Prepare eigenstate |1> on target qubit (qubit 3)
    qc.x(3)

    # Apply H to counting qubits
    qc.h(0)
    qc.h(1)
    qc.h(2)

    # Apply controlled-U^(2^k)
    # q0: controlled-S (S^1), phase = pi/2
    qc.cp(np.pi / 2, 0, 3)
    # q1: controlled-S^2 = controlled-Z, phase = pi
    qc.cp(np.pi, 1, 3)
    # q2: controlled-S^4 = controlled-I, no gate needed

    # Inverse QFT on counting qubits
    qft_inverse(qc, [0, 1, 2])

    # Measure counting qubits
    qc.measure([0, 1, 2], [0, 1, 2])

    # Run with StatevectorSampler
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=2000).result()

    # Get counts
    counts = result[0].data.c.get_counts()

    # Find most likely measurement
    most_likely = max(counts, key=counts.get)

    # Calculate estimated phase
    # In Qiskit, the bitstring is little-endian: leftmost char is q2
    # The integer value is int(most_likely, 2) if we interpret it as q2 q1 q0
    measured_int = int(most_likely, 2)
    estimated_phase = measured_int / (2 ** 3)

    print(f"Measurement: {most_likely}")
    print(f"Estimated phase: {round(estimated_phase, 4)}")

if __name__ == "__main__":
    import numpy as np
    main()
