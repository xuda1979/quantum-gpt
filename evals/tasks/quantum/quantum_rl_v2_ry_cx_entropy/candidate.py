"""RY(1.1) on qubit 0 then CX(0,1): two-qubit statevector, reduced density
of qubit 0, base-2 von Neumann entropy, and the analytic binary entropy
h2(sin^2(theta/2)) cross-check (qiskit.quantum_info only)."""

import math

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, entropy, partial_trace


def ry_cx_statevector(theta):
    """Return the 4-component statevector of RY(theta)|0>_0 then CX(0,1)."""
    qc = QuantumCircuit(2)
    qc.ry(theta, 0)
    qc.cx(0, 1)
    return Statevector(qc)


def reduced_entropy(statevector):
    """Base-2 von Neumann entropy of qubit 0 after tracing out qubit 1."""
    rho0 = partial_trace(statevector, [0])
    return float(entropy(rho0, base=2))


def binary_entropy(p):
    """h2(p) = -p log2(p) - (1-p) log2(1-p), zero-log safe."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    q = 1.0 - p
    return -(p * math.log2(p) + q * math.log2(q))


def main():
    theta = 1.1
    sv = ry_cx_statevector(theta)
    s = reduced_entropy(sv)
    analytic = binary_entropy(math.sin(theta / 2.0) ** 2)
    print("reduced_entropy =", s)
    print("analytic h2 =", analytic)
    print("statevector =", sv.data)
    norm = sum(abs(a) ** 2 for a in sv.data)
    assert abs(norm - 1.0) < 1e-12, f"statevector not normalized: {norm}"
    assert abs(s - analytic) < 1e-12, f"entropy mismatch: {s} vs {analytic}"
    assert binary_entropy(0.0) == 0.0 and binary_entropy(1.0) == 0.0
    assert abs(binary_entropy(0.5) - 1.0) < 1e-12


if __name__ == "__main__":
    main()
