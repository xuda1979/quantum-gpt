"""Two-qubit Phi+ Bell state in Qiskit with a CHSH operator evaluated by
StatevectorEstimator. The measurement observables are chosen so the
expected S = <A0B0> + <A0B1> + <A1B0> - <A1B1> equals 2*sqrt(2) exactly:
A0 = Z, A1 = X on qubit 0; B0 = (Z+X)/sqrt(2), B1 = (Z-X)/sqrt(2) on
qubit 1."""

import math

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp, Statevector

TARGET = 2.0 * math.sqrt(2.0)
S2 = 1.0 / math.sqrt(2.0)


def bell_circuit():
    """Circuit preparing the Phi+ Bell state (|00> + |11>)/sqrt(2)."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def chsh_observables():
    """The four CHSH observables as SparsePauliOps (tensor order: qubit 0 on
    the left, qubit 1 on the right)."""
    b0 = SparsePauliOp.from_list([("ZZ", S2), ("ZX", S2)])
    b1 = SparsePauliOp.from_list([("ZZ", S2), ("ZX", -S2)])
    c0 = SparsePauliOp.from_list([("XZ", S2), ("XX", S2)])
    c1 = SparsePauliOp.from_list([("XZ", S2), ("XX", -S2)])
    return [b0, b1, c0, c1]


def chsh_correlators():
    """Exact correlator values from StatevectorEstimator:
    [<A0B0>, <A0B1>, <A1B0>, <A1B1>]."""
    estimator = StatevectorEstimator()
    result = estimator.run([(bell_circuit(), chsh_observables())]).result()
    return [float(v) for v in result[0].data.evs]


def chsh_value(correlators=None):
    """S = <A0B0> + <A0B1> + <A1B0> - <A1B1>."""
    if correlators is None:
        correlators = chsh_correlators()
    return correlators[0] + correlators[1] + correlators[2] - correlators[3]


def statevector_amplitudes():
    """Phi+ amplitudes as a length-4 list."""
    return list(Statevector(bell_circuit()))


def run_chsh():
    """Return all verifiable CHSH quantities."""
    correlators = chsh_correlators()
    s = chsh_value(correlators)
    return {
        "correlators": correlators,
        "s": float(s),
        "target": float(TARGET),
        "exceeds_classical": float(s) > 2.0,
        "amplitudes": statevector_amplitudes(),
    }


def main():
    result = run_chsh()
    print("correlators =", [round(c, 8) for c in result["correlators"]])
    print("S =", result["s"])
    print("target 2*sqrt(2) =", result["target"])
    sv = result["amplitudes"]
    assert abs(abs(complex(sv[0])) - S2) < 1e-12, "Phi+ amplitude wrong"
    assert abs(abs(complex(sv[3])) - S2) < 1e-12, "Phi+ amplitude wrong"
    assert sum(abs(complex(a)) ** 2 for a in sv[1:3]) < 1e-12, "not Phi+"
    assert abs(result["s"] - TARGET) < 1e-12, "S must equal 2*sqrt(2) exactly"
    assert result["s"] > 2.0, "S must exceed the classical bound"


if __name__ == "__main__":
    main()
