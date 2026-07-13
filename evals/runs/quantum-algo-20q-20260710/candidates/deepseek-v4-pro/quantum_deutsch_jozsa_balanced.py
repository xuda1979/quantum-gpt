from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def deutsch_jozsa_balanced():
    # 2 query qubits + 1 ancilla
    qc = QuantumCircuit(3, 2)

    # Initialize ancilla to |1> (X gate) then H on all
    qc.x(2)
    qc.h([0, 1, 2])

    # Oracle for f(x0,x1) = x0: CX from q0 to ancilla
    qc.cx(0, 2)

    # H on query qubits
    qc.h([0, 1])

    # Measure query qubits
    qc.measure([0, 1], [0, 1])

    return qc

def main():
    qc = deutsch_jozsa_balanced()

    # Use StatevectorSampler (AerSimulator with statevector method)
    simulator = AerSimulator(method='statevector')
    job = simulator.run(qc, shots=1000)
    result = job.result()
    counts = result.get_counts()

    # Get the most frequent measurement result
    measured = max(counts, key=counts.get)

    # Classification
    classification = "constant" if measured == "00" else "balanced"

    print(f"Measurement: {measured}")
    print(f"Function is: {classification}")

if __name__ == "__main__":
    main()
