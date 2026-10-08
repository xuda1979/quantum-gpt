from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=2000).result()
    counts = result[0].data.meas.get_counts()
    total = sum(counts.values())
    p00 = counts.get("00", 0) / total
    p11 = counts.get("11", 0) / total
    print(f"P(00) = {p00:.3f}")
    print(f"P(11) = {p11:.3f}")

if __name__ == "__main__":
    main()
