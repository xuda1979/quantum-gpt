"""Order-finding core of Shor's algorithm for N=15, base a=8, with 6
counting qubits and a 4-qubit work register initialized to |1>.

Each controlled multiplication by a^(2^k) mod 15 is a reversible
permutation UnitaryGate mapping x<15 -> a^(2^k)*x mod 15 and leaving |15>
fixed. An inverse QFT on the counting register is followed by seeded
sampling; candidate periods are recovered with Fraction.limit_denominator
(15), validated by a^r mod 15 == 1, and nontrivial factors come from
gcd(a^(r/2)+-1, 15)."""

from fractions import Fraction
from math import gcd

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.circuit.library import QFT, UnitaryGate
from qiskit_aer import AerSimulator


def mul_mod_matrix(multiplier, n_work=4):
    """16x16 permutation matrix for x -> (x * multiplier) mod 15 (x<15),
    with |15> fixed (the residue-15 class is not in Z_15)."""
    size = 1 << n_work
    mat = np.zeros((size, size), dtype=complex)
    for x in range(size):
        if x == size - 1:
            y = x  # |15> fixed
        else:
            y = (x * multiplier) % 15
        mat[y, x] = 1.0
    return mat


def order_finding_circuit(a, n_count=6, n_work=4):
    """Build the QPE circuit for U = multiply-by-a (mod 15) on n_work
    qubits, with n_count counting qubits and the work register at |1>."""
    qc = QuantumCircuit(n_count + n_work)
    work = list(range(n_count, n_count + n_work))
    qc.x(n_count)  # work register |1>
    qc.h(range(n_count))
    for k in range(n_count):
        mult = pow(a, 1 << k, 15)
        gate = UnitaryGate(mul_mod_matrix(mult, n_work), label="mul_%d" % mult)
        cgate = gate.control(1)
        qc.append(cgate, [qc.qubits[k]] + [qc.qubits[i] for i in work])
    qft_inv = QFT(n_count, inverse=True)
    qc.append(qft_inv, range(n_count))
    creg = ClassicalRegister(n_count, "c")
    qc.add_register(creg)
    qc.measure(range(n_count), creg)
    return qc


def sample_counts(circuit, shots=2048, seed=42):
    """Seeded AerSimulator sampling; returns {bitstring: count}."""
    sim = AerSimulator(seed_simulator=seed)
    # The controlled permutation gates are custom unitaries; transpile to
    # the simulator's native basis so they can be executed.
    from qiskit import transpile

    tqc = transpile(circuit, backend=sim)
    counts = sim.run(tqc, shots=shots).result().get_counts()
    return counts


def recover_factors(counts, a, n=15, limit=15, n_count=6):
    """Recover candidate periods from sampled outcomes and return the set
    of nontrivial factors {gcd(a^(r/2)+-1, n)} over valid periods."""
    factors = set()
    best = []
    for bitstring, count in counts.items():
        j = int(bitstring, 2)
        if j == 0:
            continue
        phase = j / float(1 << n_count)
        frac = Fraction(phase).limit_denominator(limit)
        r = frac.denominator
        if r < 1 or pow(a, r, n) != 1:
            continue
        best.append((count, j, r))
        if r % 2 == 0:
            half = pow(a, r // 2, n)
            if half % n == 1:
                continue
            for candidate in (gcd(half - 1, n), gcd(half + 1, n)):
                if 1 < candidate < n:
                    factors.add(candidate)
    best.sort(reverse=True)
    return factors, best


def run_shor(a=8, n=15, n_count=6, shots=2048, seed=42):
    """Full order-finding run: circuit, seeded sampling, period recovery,
    factor extraction. Returns a dict with counts, factors and periods."""
    qc = order_finding_circuit(a, n_count=n_count)
    counts = sample_counts(qc, shots=shots, seed=seed)
    factors, best = recover_factors(counts, a, n=n, n_count=n_count)
    periods = sorted({r for _, _, r in best})
    return {
        "counts": counts,
        "factors": factors,
        "periods": periods,
        "best": best,
    }


def main():
    result = run_shor(a=8)
    print("counts =", dict(sorted(result["counts"].items(), reverse=True)))
    print("periods =", result["periods"])
    print("factors =", sorted(result["factors"]))
    assert 3 in result["factors"] and 5 in result["factors"], "factors 3 and 5 not recovered"


if __name__ == "__main__":
    main()
