import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace


def main():
    qc = QuantumCircuit(3)
    # Prepare |+> on q2
    qc.h(2)
    # Prepare Bell pair on q0, q1
    qc.h(0); qc.cx(0, 1)
    # Bell measurement on q2, q1 (deferred: use CX and H, then classically-
    # controlled corrections replaced by direct CX/CZ)
    qc.cx(2, 1)
    qc.h(2)
    # Deferred corrections
    qc.cx(1, 0)
    qc.cz(2, 0)
    # Now q0 should be in |+>
    sv = Statevector.from_instruction(qc)
    # Trace out q1 and q2 (indices 1 and 2) to get q0's reduced state
    dm = DensityMatrix(sv)
    rho_q0 = partial_trace(dm, [1, 2])
    # |+><+| density matrix
    plus = np.array([1, 1]) / np.sqrt(2)
    rho_plus = np.outer(plus, plus)
    fidelity = np.real(np.trace(rho_q0.data @ rho_plus))
    print(f"fidelity = {fidelity:.3f}")
    print(f"teleported: {'True' if fidelity >= 0.999 else 'False'}")

if __name__ == "__main__":
    main()
