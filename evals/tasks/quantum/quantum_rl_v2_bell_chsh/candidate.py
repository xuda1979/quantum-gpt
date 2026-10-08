"""Singlet Bell state |Psi-> = (|01> - |10>)/sqrt(2) in Qiskit, with the
CHSH operator evaluated via StatevectorEstimator. Measurement observables
are chosen consistently so that |S| = 2*sqrt(2):

  A  = Z,        A' = X                        (Alice, qubit 0)
  B  = (Z+X)/sqrt(2),   B' = (Z-X)/sqrt(2)     (Bob, qubit 1)

For the singlet <(a.sigma) (b.sigma)> = -a.b, giving
E(A,B)=E(A',B)=E(A,B')=-1/sqrt(2), E(A',B')=+1/sqrt(2), so
S = E(A,B) + E(A',B) + E(A,B') - E(A',B') = -2*sqrt(2)."""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp, Statevector, state_fidelity

S2 = np.sqrt(2.0)


def singlet_circuit():
    """Prepare |Psi-> = (|01> - |10>)/sqrt(2)."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)  # (|00> + |11>)/sqrt(2)
    qc.z(1)  # (|00> - |11>)/sqrt(2) = |Phi->
    qc.x(1)  # (|01> - |10>)/sqrt(2) = |Psi->
    return qc


def chsh_observables():
    """The four two-qubit observables of the CHSH test, as SparsePauliOps."""
    a = SparsePauliOp("ZI")  # Z on qubit 0
    ap = SparsePauliOp("XI")  # X on qubit 0
    b = (SparsePauliOp("IZ") + SparsePauliOp("IX")) / S2
    bp = (SparsePauliOp("IZ") - SparsePauliOp("IX")) / S2
    return [a.compose(b), ap.compose(b), a.compose(bp), ap.compose(bp)]


def chsh_correlators():
    """E(A,B), E(A',B), E(A,B'), E(A',B') via StatevectorEstimator."""
    qc = singlet_circuit()
    estimator = StatevectorEstimator()
    obs = chsh_observables()
    result = estimator.run([(qc, [o for o in obs])]).result()[0]
    evs = result.data.evs
    return [float(ev) for ev in evs]


def chsh_value():
    """S = E(A,B) + E(A',B) + E(A,B') - E(A',B')."""
    e_ab, e_apb, e_abp, e_apbp = chsh_correlators()
    return e_ab + e_apb + e_abp - e_apbp


def singlet_fidelity(statevector):
    """Fidelity of the prepared state with the ideal singlet."""
    ideal = Statevector(np.array([0.0, 1.0, -1.0, 0.0]) / S2)
    return float(state_fidelity(Statevector(statevector), ideal))


def main():
    sv = Statevector(singlet_circuit())
    fid = singlet_fidelity(sv)
    assert abs(fid - 1.0) < 1e-12, f"singlet fidelity {fid}"
    e_ab, e_apb, e_abp, e_apbp = chsh_correlators()
    s = chsh_value()
    assert abs(abs(s) - 2.0 * S2) < 1e-12, f"|S|={abs(s)} != 2*sqrt(2)"
    assert abs(s) > 2.0, "CHSH bound not violated"
    print("E(A,B) =", e_ab)
    print("E(A',B) =", e_apb)
    print("E(A,B') =", e_abp)
    print("E(A',B') =", e_apbp)
    print("S =", s)
    print("|S| =", abs(s), "2*sqrt(2) =", 2.0 * S2)


if __name__ == "__main__":
    main()
