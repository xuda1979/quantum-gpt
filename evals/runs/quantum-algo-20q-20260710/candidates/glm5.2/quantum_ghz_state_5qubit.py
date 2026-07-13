from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def main():
    qc = QuantumCircuit(5)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 3)
    qc.cx(3, 4)
    qc.measure_all()

    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=4000)
    result = job.result()
    counts = result[0].data.meas.get_counts()

    total = sum(counts.values())
    favorable = counts.get("00000", 0) + counts.get("11111", 0)
    probability = favorable / total

    print(f"P(all-0 or all-1) = {probability:.3f}")


if __name__ == "__main__":
    main()
