from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def QFT3():
    qc = QuantumCircuit(3, name="qft3")
    qc.h(2)
    qc.cp(3.141592653589793/2, 1, 2)
    qc.cp(3.141592653589793/4, 0, 2)
    qc.h(1)
    qc.cp(3.141592653589793/2, 0, 1)
    qc.h(0)
    qc.swap(0, 2)
    return qc

def main():
    qc = QuantumCircuit(3)
    qc.x(0)
    qc.x(2)
    qc.compose(QFT3(), inplace=True)
    qc.measure_all()
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=2000).result()[0].data.meas.get_counts()
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:2]
    print(f"Top: {top[0][0]} count={top[0][1]}")
    print(f"2nd: {top[1][0]} count={top[1][1]}")

if __name__ == "__main__":
    main()
