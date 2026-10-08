from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    s = "101"
    n = len(s)
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))
    for i, bit in enumerate(s):
        if bit == "1":
            qc.cx(i, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=1000).result()[0].data.c.get_counts()
    top = max(counts.items(), key=lambda kv: kv[1])[0]
    recovered = top[::-1]
    print(f"Hidden string: {recovered}")

if __name__ == "__main__":
    main()
