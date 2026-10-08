from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(2)
    qc.h([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.z([0, 1])
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.measure_all()
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.meas.get_counts()
    top_bs, top_n = max(counts.items(), key=lambda kv: kv[1])
    total = sum(counts.values())
    print(f"Most likely: {top_bs}")
    print(f"Probability: {top_n/total:.3f}")

if __name__ == "__main__":
    main()
