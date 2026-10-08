from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def grover_3qubit():
    qc = QuantumCircuit(3)
    # Initialize superposition
    qc.h([0, 1, 2])

    # Oracle for |101>
    qc.x(1)  # flip q1 because it's 0 in |101>
    qc.h(2)
    qc.mcx([0, 1], 2)  # multi-controlled X with controls q0,q1 target q2
    qc.h(2)
    qc.x(1)  # uncompute

    # Diffusion operator
    qc.h([0, 1, 2])
    qc.x([0, 1, 2])
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)
    qc.x([0, 1, 2])
    qc.h([0, 1, 2])

    # Second iteration
    # Oracle
    qc.x(1)
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)
    qc.x(1)

    # Diffusion
    qc.h([0, 1, 2])
    qc.x([0, 1, 2])
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)
    qc.x([0, 1, 2])
    qc.h([0, 1, 2])

    qc.measure_all()
    return qc

def main():
    qc = grover_3qubit()
    simulator = AerSimulator(method='statevector')
    result = simulator.run(qc, shots=1000).result()
    counts = result.get_counts()
    most_likely = max(counts, key=counts.get)
    prob = counts[most_likely] / 1000
    print(f"Most likely: {most_likely}")
    print(f"Probability: {prob:.3f}")

if __name__ == "__main__":
    main()
