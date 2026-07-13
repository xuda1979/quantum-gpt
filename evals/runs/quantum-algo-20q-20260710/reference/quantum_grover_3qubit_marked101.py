from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def ccz(qc: QuantumCircuit):
    qc.h(2)
    qc.mcx([0, 1], 2)
    qc.h(2)

def main():
    n = 3
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(2):
        # Oracle for |101>: q0=1, q1=0, q2=1
        qc.x(1)
        ccz(qc)
        qc.x(1)
        # Diffusion
        qc.h(range(n))
        qc.x(range(n))
        ccz(qc)
        qc.x(range(n))
        qc.h(range(n))
    qc.measure_all()
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.meas.get_counts()
    top_bs, top_n = max(counts.items(), key=lambda kv: kv[1])
    total = sum(counts.values())
    print(f"Most likely: {top_bs}")
    print(f"Probability: {top_n/total:.3f}")

if __name__ == "__main__":
    main()
