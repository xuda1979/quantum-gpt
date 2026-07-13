from qiskit import QuantumCircuit
from qiskit_aer.primitives import StatevectorSampler


def main():
    # 1. Create Bell pair |Phi+> = (|00> + |11>)/sqrt(2)
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)

    # 2. Alice encodes "11": Z then X on q0
    qc.z(0)  # Z gate
    qc.x(0)  # X gate

    # 3. Bob's operations: CX q0->q1, then H on q0, then measure
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])

    # 4. Simulate with StatevectorSampler, 1000 shots
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=1000)
    result = job.result()

    # Get counts from the first (and only) circuit
    counts = result[0].data.c.get_counts()

    # Find most likely bitstring
    most_likely = max(counts, key=counts.get)
    prob = counts[most_likely] / 1000.0

    print(f"Decoded bits: {most_likely}")
    print(f"Probability: {prob:.3f}")

if __name__ == "__main__":
    main()
