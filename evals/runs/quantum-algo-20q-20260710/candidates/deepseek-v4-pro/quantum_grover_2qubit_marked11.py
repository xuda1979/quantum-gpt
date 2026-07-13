from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def grover_2qubit():
    qc = QuantumCircuit(2)
    # Step 1: Initialize superposition
    qc.h([0, 1])
    # Step 2: Oracle for |11>
    qc.cz(0, 1)
    # Step 3: Diffusion operator
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])
    qc.measure_all()
    return qc

def main():
    qc = grover_2qubit()
    sampler = StatevectorSampler(seed=42)
    job = sampler.run([qc], shots=1000)
    result = job.result()
    counts = result[0].data.meas.get_counts()
    most_likely = max(counts, key=counts.get)
    prob = counts[most_likely] / 1000
    print(f"Most likely: {most_likely}")
    print(f"Probability: {prob:.3f}")

if __name__ == "__main__":
    main()
