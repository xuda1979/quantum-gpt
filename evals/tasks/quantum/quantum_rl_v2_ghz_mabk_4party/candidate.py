"""4-qubit GHZ state with the standard four-party MABK (Ardehali) witness.

Sign convention (defined explicitly here, in code):
  M4 = 1/2 * (XXXX - YYYY + XXYY + XYYX + XYXY + YXXY + YXYX + YYXX)

On |GHZ4> = (|0000> + |1111>)/sqrt(2):
  <XXXX> = <YYYY> = +1 and each two-Y correlator = -1, so
  M4 = 1/2 * (1 - 1 - 6) = -3  ->  |M4| = 3.
The local-hidden-variable (MABK) bound is |M4| <= 2*sqrt(2) = 2.828,
so |M4| = 3 > 2.828 witnesses genuine four-party entanglement.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp, Statevector

S2 = np.sqrt(2.0)


def ghz4_circuit():
    """4-qubit GHZ: (|0000> + |1111>)/sqrt(2)."""
    qc = QuantumCircuit(4)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.cx(0, 3)
    return qc


def mabk_sign_convention():
    """Explicit (label, sign) convention for the eight MABK correlators;
    signs are applied inside the 1/2 * sum. Returns {label: sign}."""
    return {
        "XXXX": +1.0,
        "YYYY": -1.0,
        "XXYY": +1.0,
        "XYYX": +1.0,
        "XYXY": +1.0,
        "YXXY": +1.0,
        "YXYX": +1.0,
        "YYXX": +1.0,
    }


def mabk_observables():
    """The eight correlator observables as SparsePauliOps (q3 q2 q1 q0)."""
    return [SparsePauliOp(label) for label in mabk_sign_convention()]


def mabk_correlators():
    """<XXXX>, <YYYY>, <XXYY>, <XYYX>, <XYXY>, <YXXY>, <YXYX>, <YYXX>."""
    qc = ghz4_circuit()
    estimator = StatevectorEstimator()
    result = estimator.run([(qc, mabk_observables())]).result()[0]
    return [float(ev) for ev in result.data.evs]


def mabk_value():
    """M4 = 1/2 * (XXXX - YYYY + XXYY + XYYX + XYXY + YXXY + YXYX + YYXX)."""
    evs = dict(zip(mabk_sign_convention(), mabk_correlators(), strict=False))
    total = 0.0
    for label, sign in mabk_sign_convention().items():
        total += sign * evs[label]
    return 0.5 * total


def mabk_value_matrix():
    """Direct matrix calculation with explicit Pauli kron products."""
    x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
    pauli = {"X": x, "Y": y}

    om = None
    for label, sign in mabk_sign_convention().items():
        op = pauli[label[0]]
        for c in label[1:]:
            op = np.kron(op, pauli[c])
        om = sign * op if om is None else om + sign * op

    sv = Statevector(ghz4_circuit())
    rho = np.outer(sv.data, sv.data.conj())
    return 0.5 * float(np.real(np.trace(rho @ om)))


def mabk_violation():
    """|M4| - 2*sqrt(2) > 0 witnesses four-party entanglement."""
    return abs(mabk_value()) - 2.0 * S2


def main():
    evs = mabk_correlators()
    for label, v in zip(mabk_sign_convention(), evs, strict=False):
        print(label, v)
    m = mabk_value()
    print("M4 =", m, " violation =", mabk_violation())
    assert abs(m - mabk_value_matrix()) < 1e-9
    assert abs(abs(m) - 3.0) < 1e-9, f"|M4|={abs(m)} != 3"
    assert mabk_violation() > 0.0, "MABK inequality not violated"


if __name__ == "__main__":
    main()
