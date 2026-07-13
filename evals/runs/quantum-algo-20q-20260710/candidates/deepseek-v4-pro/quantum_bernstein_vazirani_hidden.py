from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def bernstein_vazirani_oracle(s: str) -> QuantumCircuit:
    n = len(s)
    oracle = QuantumCircuit(n + 1)
    for i, bit in enumerate(s):
        if bit == '1':
            oracle.cx(i, n)
    return oracle

def main():
    s = "101"
    n = len(s)

    # Create circuit with n+1 qubits and n classical bits
    qc = QuantumCircuit(n + 1, n)

    # Initialize last qubit to |1>
    qc.x(n)

    # Apply Hadamard to all qubits
    qc.h(range(n + 1))

    # Apply oracle
    oracle = bernstein_vazirani_oracle(s)
    qc.compose(oracle, inplace=True)

    # Apply Hadamard to first n qubits
    qc.h(range(n))

    # Measure first n qubits
    qc.measure(range(n), range(n))

    # Run with StatevectorSampler
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=1000)
    result = job.result()

    # Get the most frequent result
    counts = result[0].data.c.get_counts()
    max_count = max(counts.values())
    measured = next(k for k, v in counts.items() if v == max_count)

    # The measured string is in little-endian order (q0 is rightmost), reverse to get natural order
    recovered = measured[::-1]

    print(f"Hidden string: {recovered}")

if __name__ == "__main__":
    main()
