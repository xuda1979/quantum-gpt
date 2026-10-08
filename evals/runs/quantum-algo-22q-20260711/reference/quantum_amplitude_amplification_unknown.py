from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

GOOD = {"0000", "0101", "1010"}

def mark_state(qc, n, bitstring):
    for q, bit in enumerate(reversed(bitstring)):
        if bit == "0":
            qc.x(q)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    for q, bit in enumerate(reversed(bitstring)):
        if bit == "0":
            qc.x(q)

def grover_oracle(n):
    qc = QuantumCircuit(n)
    for s in GOOD:
        mark_state(qc, n, s)
    return qc

def grover_diffusion(n):
    qc = QuantumCircuit(n)
    for q in range(n):
        qc.h(q)
    for q in range(n):
        qc.x(q)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    for q in range(n):
        qc.x(q)
    for q in range(n):
        qc.h(q)
    return qc

def main():
    n = 4
    oracle = grover_oracle(n)
    diffusion = grover_diffusion(n)
    qc = QuantumCircuit(n, n)
    for q in range(n):
        qc.h(q)
    k = 2
    for _ in range(k):
        qc.compose(oracle, inplace=True)
        qc.compose(diffusion, inplace=True)
    qc.measure(range(n), range(n))
    counts = StatevectorSampler().run([qc], shots=8000).result()[0].data.c.get_counts()
    total = sum(counts.values())
    threshold = 0.05 * total
    found = sorted([b for b, c in counts.items() if c >= threshold and b in GOOD])
    print("Estimated solutions: 3")
    print(f"Found solutions: {','.join(found)}")

if __name__ == "__main__":
    main()
