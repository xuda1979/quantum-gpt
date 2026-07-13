from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    n = 5
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure_all()
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=4000).result()[0].data.meas.get_counts()
    total = sum(counts.values())
    p = (counts.get("0" * n, 0) + counts.get("1" * n, 0)) / total
    print(f"P(all-0 or all-1) = {p:.3f}")

if __name__ == "__main__":
    main()
