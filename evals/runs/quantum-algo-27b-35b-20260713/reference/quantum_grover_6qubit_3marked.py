import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def grover_oracle(marked_ints, n):
    qc = QuantumCircuit(n)
    for m in marked_ints:
        # Flip phase on |m>
        bits = format(m, f"0{n}b")
        for q, b in enumerate(bits):
            if b == '0':
                qc.x(q)
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        for q, b in enumerate(bits):
            if b == '0':
                qc.x(q)
    return qc

def grover_diffuser(n):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    return qc

def build_grover(marked_ints, n, iterations):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(iterations):
        qc.compose(grover_oracle(marked_ints, n), inplace=True)
        qc.compose(grover_diffuser(n), inplace=True)
    return qc

def main():
    n = 6
    marked = [3, 17, 42]
    N = 2 ** n
    M = len(marked)
    # Optimal iterations = (pi/4) * sqrt(N/M)
    opt_iter = int(round(np.pi / 4 * np.sqrt(N / M)))
    qc = build_grover(marked, n, opt_iter)
    sv = Statevector.from_instruction(qc)
    probs = sv.probabilities()
    # Success probability = sum of probabilities of marked states
    succ = float(sum(probs[m] for m in marked))
    top_idx = int(np.argmax(probs))
    print(f"N = {N}")
    print(f"M = {M} (marked: {sorted(marked)})")
    print(f"Iterations = {opt_iter}")
    print(f"Success prob = {succ:.4f}")
    print(f"Top state = {top_idx}")
    print(f"In marked set: {top_idx in marked}")

if __name__ == "__main__":
    main()
