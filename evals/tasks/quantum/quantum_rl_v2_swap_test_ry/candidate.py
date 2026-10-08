"""Qiskit SWAP test for |psi> = RY(0.4)|0> and |phi> = RY(1.7)|0>.

Ancilla-first SWAP test: H(ancilla), CSWAP(ancilla, psi, phi), H(ancilla),
measure the ancilla. P(ancilla = 0) = (1 + |<psi|phi>|^2)/2, so
|<psi|phi>|^2 = 2*P(0) - 1. The analytic value is
cos^2((0.4 - 1.7)/2); the shot estimate from StatevectorSampler with
20000 shots and seed 31415 must agree within 0.025.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector

THETA1 = 0.4
THETA2 = 1.7


def swap_test_circuit(theta1=THETA1, theta2=THETA2):
    """Ancilla-first SWAP test circuit with the ancilla measured into c[0]."""
    qc = QuantumCircuit(3, 1)
    qc.h(0)
    qc.ry(theta1, 1)
    qc.ry(theta2, 2)
    qc.cswap(0, 1, 2)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def swap_test_circuit_unmeasured(theta1=THETA1, theta2=THETA2):
    """The same SWAP test without the final measurement (for exactness)."""
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.ry(theta1, 1)
    qc.ry(theta2, 2)
    qc.cswap(0, 1, 2)
    qc.h(0)
    return qc


def analytic_overlap_sq(theta1=THETA1, theta2=THETA2):
    """|<psi|phi>|^2 = cos^2((theta1 - theta2)/2) for single-qubit RY states."""
    return float(np.cos((theta1 - theta2) / 2.0) ** 2)


def exact_ancilla_zero_probability(theta1=THETA1, theta2=THETA2):
    """P(ancilla = 0) from the exact statevector of the unmeasured circuit."""
    sv = Statevector(swap_test_circuit_unmeasured(theta1, theta2))
    p0 = sum(abs(sv.data[i]) ** 2 for i in range(8) if i & 1 == 0)
    return float(p0)


def estimate_overlap_sq(shots=20000, seed=31415, theta1=THETA1, theta2=THETA2):
    """|{<psi|phi>}|^2 estimated from 2*P(ancilla=0) - 1 with seeded shots."""
    qc = swap_test_circuit(theta1, theta2)
    sampler = StatevectorSampler(seed=seed)
    result = sampler.run([qc], shots=shots).result()
    counts = result[0].data.c.get_counts()
    n = float(sum(counts.values()))
    p0 = counts.get("0", 0) / n
    return 2.0 * p0 - 1.0


def swap_test_error(shots=20000, seed=31415):
    """Absolute error of the shot estimate vs the analytic value."""
    return abs(estimate_overlap_sq(shots, seed) - analytic_overlap_sq())


def main():
    analytic = analytic_overlap_sq()
    exact_p0 = exact_ancilla_zero_probability()
    est = estimate_overlap_sq()
    err = swap_test_error()
    print("analytic |<psi|phi>|^2 =", analytic)
    print("exact P(0) =", exact_p0, " (1 + analytic)/2 =", (1.0 + analytic) / 2.0)
    print("shot estimate =", est, " error =", err)
    assert abs(exact_p0 - (1.0 + analytic) / 2.0) < 1e-9
    assert err < 0.025, f"swap test error {err} not below 0.025"
    print("SWAP test OK")


if __name__ == "__main__":
    main()
