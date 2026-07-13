from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.z(0)
    qc.x(0)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.c.get_counts()
    top_bs, top_n = max(counts.items(), key=lambda kv: kv[1])
    total = sum(counts.values())
    decoded = top_bs[::-1]
    print(f"Decoded bits: {decoded}")
    print(f"Probability: {top_n/total:.3f}")

if __name__ == "__main__":
    main()
