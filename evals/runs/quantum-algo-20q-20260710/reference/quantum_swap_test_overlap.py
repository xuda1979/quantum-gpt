from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(3, 1)
    qc.h(2)
    qc.h(0)
    qc.cswap(0, 1, 2)
    qc.h(0)
    qc.measure(0, 0)
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=4000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    p0 = counts.get("0", 0) / total
    overlap_sq = 2 * p0 - 1
    print(f"P(0) = {p0:.3f}")
    print(f"|<A|B>|^2 = {overlap_sq:.3f}")

if __name__ == "__main__":
    main()
