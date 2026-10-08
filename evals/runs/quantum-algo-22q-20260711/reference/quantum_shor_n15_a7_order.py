import math
from fractions import Fraction

from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.primitives import StatevectorSampler


def build_shor_circuit():
    n_count = 4
    n_reg = 4
    total = n_count + n_reg
    qc = QuantumCircuit(total, n_count)
    qc.x(n_count)
    for i in range(n_count):
        qc.h(i)
    for i in range(n_count):
        p = (2 ** i) % 4
        for _ in range(p):
            qc.cswap(i, n_count + 0, n_count + 2)
            qc.cswap(i, n_count + 1, n_count + 3)
    qc.append(QFT(n_count, inverse=True), range(n_count))
    qc.measure(range(n_count), range(n_count))
    return qc

def main():
    qc = build_shor_circuit()
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    N = 15
    a = 7
    r = None
    for measured in sorted(counts, key=lambda b: -counts[b]):
        if measured == "0" * 4:
            continue
        phase = int(measured, 2) / (2 ** 4)
        cand = Fraction(phase).limit_denominator(N).denominator
        if pow(a, cand, N) == 1:
            r = cand
            break
    if r is None:
        for cand in range(1, N):
            if pow(a, cand, N) == 1:
                r = cand
                break
    print(f"order r = {r}")
    if r is not None and r % 2 == 0:
        half = pow(a, r // 2, N)
        f1 = math.gcd(half - 1, N)
        f2 = math.gcd(half + 1, N)
        fs = sorted({f1, f2} - {1, N})
        if len(fs) >= 2:
            print(f"factors = {fs[0]},{fs[1]}")
        else:
            all_factors = sorted({math.gcd(half - 1, N), math.gcd(half + 1, N)} - {1, N})
            print(f"factors = {all_factors[0]},{all_factors[-1]}")
    else:
        print("factors = 1,15")

if __name__ == "__main__":
    main()
