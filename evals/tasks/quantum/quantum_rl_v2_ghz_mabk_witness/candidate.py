"""3-qubit GHZ state with the four-correlator MABK witness
M = <XXX> - <XYY> - <YXY> - <YYX> evaluated via StatevectorEstimator,
cross-checked against a direct matrix calculation.

For |GHZ> = (|000> + |111>)/sqrt(2):
  <XXX> = +1, <XYY> = <YXY> = <YYX> = -1  ->  M = 4
The classical (local-hidden-variable) bound is M <= 2.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp, Statevector

S2 = np.sqrt(2.0)


def ghz_circuit():
    """3-qubit GHZ: (|000> + |111>)/sqrt(2)."""
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    return qc


def mabk_observables():
    """The four MABK correlators as SparsePauliOps (string = q2 q1 q0)."""
    return [
        SparsePauliOp("XXX"),
        SparsePauliOp("XYY"),
        SparsePauliOp("YXY"),
        SparsePauliOp("YYX"),
    ]


def mabk_correlators():
    """<XXX>, <XYY>, <YXY>, <YYX> via StatevectorEstimator."""
    qc = ghz_circuit()
    estimator = StatevectorEstimator()
    result = estimator.run([(qc, mabk_observables())]).result()[0]
    return [float(ev) for ev in result.data.evs]


def mabk_value():
    """M = <XXX> - <XYY> - <YXY> - <YYX>."""
    exxx, exyy, eyxy, eyyx = mabk_correlators()
    return exxx - exyy - eyxy - eyyx


def mabk_value_matrix():
    """Direct matrix calculation of M = Tr(rho_GHZ O_M) with
    O_M = XXX - XYY - YXY - YYX, using explicit Pauli kron products."""
    x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)

    def pauli(letter):
        return {"X": x, "Y": y, "Z": z}[letter]

    om = None
    for label in ["XXX", "XYY", "YXY", "YYX"]:
        op = pauli(label[0])
        for c in label[1:]:
            op = np.kron(op, pauli(c))
        sign = -1.0 if label != "XXX" else 1.0
        om = op if om is None else om + sign * op

    sv = Statevector(ghz_circuit())
    rho = np.outer(sv.data, sv.data.conj())
    return float(np.real(np.trace(rho @ om)))


def witness_violation():
    """M > 2 signals genuine tripartite entanglement (MABK inequality)."""
    return mabk_value() - 2.0


def main():
    exxx, exyy, eyxy, eyyx = mabk_correlators()
    m = mabk_value()
    m_direct = mabk_value_matrix()
    print("correlators:", exxx, exyy, eyxy, eyyx)
    print("M (estimator) =", m)
    print("M (matrix)    =", m_direct)
    assert abs(m - 4.0) < 1e-9, f"M={m} != 4"
    assert abs(m - m_direct) < 1e-9, "estimator/matrix mismatch"
    assert m > 2.0, "MABK inequality not violated"
    assert abs(exxx - 1.0) < 1e-9 and abs(exyy + 1.0) < 1e-9
    assert abs(eyxy + 1.0) < 1e-9 and abs(eyyx + 1.0) < 1e-9


if __name__ == "__main__":
    main()
