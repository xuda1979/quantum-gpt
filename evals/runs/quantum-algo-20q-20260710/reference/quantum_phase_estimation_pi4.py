import math

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    n_count = 3
    tgt = n_count
    qc = QuantumCircuit(n_count + 1, n_count)
    qc.x(tgt)
    qc.h(range(n_count))
    qc.cp(math.pi/2, 0, tgt)  # CS
    qc.cp(math.pi, 1, tgt)    # CZ = S^2
    # 2^2 = S^4 = I: no gate
    # Inverse QFT on counting register
    qc.swap(0, 2)
    qc.h(0)
    qc.cp(-math.pi/2, 0, 1)
    qc.h(1)
    qc.cp(-math.pi/4, 0, 2)
    qc.cp(-math.pi/2, 1, 2)
    qc.h(2)
    qc.measure(range(n_count), range(n_count))
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=2000).result()[0].data.c.get_counts()
    top = max(counts.items(), key=lambda kv: kv[1])[0]
    val = int(top, 2)
    phase = val / (2 ** n_count)
    print(f"Measurement: {top}")
    print(f"Estimated phase: {phase:.4f}")

if __name__ == "__main__":
    main()
