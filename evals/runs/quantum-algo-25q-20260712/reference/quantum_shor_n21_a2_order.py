"""Shor's order-finding for N=21, a=2.

Compute the multiplicative order r of a=2 modulo N=21: 2^r mod 21 = 1.
2^1=2, 2^2=4, 2^3=8, 2^4=16, 2^5=11, 2^6=1. So r=6.
Use 8 counting qubits and 5 target qubits. After QPE, use continued
fractions to recover r from the measured phase (skipping phase=0 which
carries no information). Then gcd(a^(r/2) - 1, N) and gcd(a^(r/2) + 1, N)
give the factors 3 and 7.
"""
from fractions import Fraction
from math import gcd

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Operator


def c_amod21(a: int, power: int, n_target: int = 5) -> QuantumCircuit:
    """Controlled multiplication by a^power mod 21 on n_target qubits."""
    N = 21
    size = 2 ** n_target
    U = QuantumCircuit(n_target)
    a_pow = pow(a, power, N)
    perm = list(range(size))
    for y in range(size):
        if y < N:
            perm[y] = (a_pow * y) % N
        else:
            perm[y] = y
    mat = np.zeros((size, size))
    for y in range(size):
        mat[perm[y], y] = 1
    U.unitary(Operator(mat), range(n_target))
    return U


def recover_order(counts: dict, n_count: int, N: int, a: int) -> int:
    """Recover the order from QPE counts, skipping uninformative phase=0."""
    sorted_items = sorted(counts.items(), key=lambda x: -x[1])
    for bitstring, _ in sorted_items:
        phase = int(bitstring, 2) / (2 ** n_count)
        if phase == 0:
            continue  # uninformative
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator
        # Verify: a^r mod N should be 1
        if r > 0 and pow(a, r, N) == 1:
            return r
    return 0


def main():
    N = 21
    a = 2
    n_count = 8
    n_target = 5
    qc = QuantumCircuit(n_count + n_target, n_count)
    qc.x(n_count)
    for i in range(n_count):
        qc.h(i)
    for k in range(n_count):
        cu = c_amod21(a, 2 ** k, n_target).control(1)
        qc.append(cu, [k] + list(range(n_count, n_count + n_target)))
    qc.append(QFT(n_count, inverse=True), range(n_count))
    qc.measure(range(n_count), range(n_count))
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    r = recover_order(counts, n_count, N, a)
    if r % 2 == 0 and r > 0:
        a_r_half = pow(a, r // 2, N)
        f1 = gcd(a_r_half - 1, N)
        f2 = gcd(a_r_half + 1, N)
        factors = sorted([f for f in (f1, f2) if 1 < f < N])
    else:
        factors = []
    print(f"order r = {r}")
    print(f"factors = {','.join(str(f) for f in factors) if factors else 'none'}")


if __name__ == "__main__":
    main()
