from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def build_oracle(n, s):
    oracle = QuantumCircuit(n + 1)
    for i in range(n):
        if s[i] == '1':
            oracle.cx(i, n)
    return oracle

def main():
    n = 3
    s = "101"

    qc = QuantumCircuit(n + 1, n)

    # Initialize ancilla to |-> state
    qc.x(n)
    qc.h(n)

    # Apply Hadamard to input qubits
    qc.h(range(n))

    # Apply oracle
    oracle = build_oracle(n, s)
    qc.compose(oracle, inplace=True)

    # Apply Hadamard to input qubits
    qc.h(range(n))

    # Measure
    qc.measure(range(n), range(n))

    # Run with StatevectorSampler
    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=1000)
    result = job.result()

    # Get counts
    counts = result[0].data.c.get_counts()

    # Find most common result
    most_common = max(counts, key=counts.get)

    # Reverse to get natural order (s[0] s[1] s[2])
    recovered = most_common[::-1]

    print(f"Hidden string: {recovered}")

if __name__ == "__main__":
    main()
