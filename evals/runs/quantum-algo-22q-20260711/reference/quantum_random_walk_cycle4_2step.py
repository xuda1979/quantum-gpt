from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler


def shift_cycle4(qc, coin, q0, q1):
    # Decrement (-1 mod 4) controlled on coin=1
    qc.x(q0)
    qc.ccx(coin, q0, q1)
    qc.x(q0)
    qc.cx(coin, q0)
    # Increment (+1 mod 4) controlled on coin=0
    qc.x(coin)
    qc.ccx(coin, q0, q1)
    qc.cx(coin, q0)
    qc.x(coin)

def main():
    total_q = 3
    steps = 2
    qc = QuantumCircuit(total_q, 2)
    for _ in range(steps):
        qc.h(2)
        shift_cycle4(qc, 2, 0, 1)
    qc.measure([0, 1], [0, 1])
    counts = StatevectorSampler().run([qc], shots=8000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    p0 = counts.get("00", 0) / total
    p2 = counts.get("10", 0) / total
    print(f"P(node=0) = {p0:.3f}")
    print(f"P(node=2) = {p2:.3f}")

if __name__ == "__main__":
    main()
