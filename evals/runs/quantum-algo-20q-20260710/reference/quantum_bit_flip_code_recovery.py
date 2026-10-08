from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(5, 5)
    qc.x([0, 1, 2])
    qc.x(1)
    qc.cx(0, 3)
    qc.cx(1, 3)
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.measure(3, 0)
    qc.measure(4, 1)
    qc.measure(0, 2)
    qc.measure(1, 3)
    qc.measure(2, 4)
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    maj_one = 0
    for bs, c in counts.items():
        data_bits = [bs[4], bs[3], bs[2]]
        if sum(int(b) for b in data_bits) >= 2:
            maj_one += c
    print(f"P(majority=1) = {maj_one/total:.3f}")

if __name__ == "__main__":
    main()
