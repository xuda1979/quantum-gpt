from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(3, 2)
    qc.x(2)
    qc.h([0, 1, 2])
    qc.cx(0, 2)
    qc.h([0, 1])
    qc.measure([0, 1], [0, 1])
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.c.get_counts()
    top = max(counts.items(), key=lambda kv: kv[1])[0]
    classification = "constant" if top == "00" else "balanced"
    print(f"Measurement: {top}")
    print(f"Function is: {classification}")

if __name__ == "__main__":
    main()
