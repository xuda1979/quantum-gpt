import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    # Create circuit with 3 counting qubits + 1 target qubit
    n_count = 3
    qc = QuantumCircuit(n_count + 1)

    # Prepare target qubit in eigenstate |1>
    qc.x(n_count)

    # Apply Hadamard to counting qubits
    for i in range(n_count):
        qc.h(i)

    # Apply controlled-U^(2^k) operations
    # U = S gate, eigenvalue e^{i*pi/2}, phase = 1/4
    # k=0: U^(2^0) = S, controlled-S = cp(pi/2)
    qc.cp(np.pi/2, 0, n_count)
    # k=1: U^(2^1) = S^2 = Z, controlled-Z = cp(pi)
    qc.cp(np.pi, 1, n_count)
    # k=2: U^(2^2) = S^4 = I, no gate needed

    # Inverse QFT on counting qubits
    # Swap qubits for standard QFT ordering
    qc.swap(0, 2)
    # Apply inverse QFT
    for j in range(n_count):
        qc.h(j)
        for k in range(j + 1, n_count):
            qc.cp(-np.pi / (2 ** (k - j)), k, j)

    # Measure counting qubits
    qc.measure_all()

    # Run with StatevectorSampler
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=2000)
    result = job.result()[0]

    # Get counts
    counts = result.data.meas.get_counts()

    # Find most likely measurement
    most_likely = max(counts, key=counts.get)

    # Qiskit little-endian: leftmost char is q2
    # Convert to integer (binary string is q2 q1 q0)
    int_val = int(most_likely, 2)
    estimated_phase = int_val / (2 ** n_count)

    print(f"Measurement: {most_likely}")
    print(f"Estimated phase: {estimated_phase:.4f}")

if __name__ == "__main__":
    main()
