"""Quantum teleportation across a 3-qubit chain.

Alice has an unknown state |psi> on qubit 0 (data). Alice and Bob share
a Bell pair on qubits 1 (Alice's half) and 2 (Bob's half). Teleport |psi>
from qubit 0 to qubit 2 via: CNOT(0,1), H(0), measure 0 and 1, then
classically-controlled X and Z on qubit 2.
We use |psi> = |+> = (|0>+|1>)/sqrt(2) and verify by computing the
fidelity of qubit 2's state with |+>.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace


def simulate_teleport_with_corrections(psi_prep: QuantumCircuit) -> float:
    """Simulate teleportation and return the fidelity of the output state of
    qubit 2 with the input state |psi>.
    
    For each measurement outcome (m0, m1), the post-measurement state of
    qubit 2 is X^m1 Z^m0 |psi>. After applying the inverse correction
    Z^m0 X^m1 (i.e., undoing), we get back |psi>. So the fidelity is 1
    in the ideal case.
    """
    # Build the full circuit (without measurement, just the gates)
    qc = QuantumCircuit(3)
    qc.compose(psi_prep, qubits=[0], inplace=True)
    qc.h(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)
    sv = Statevector.from_instruction(qc)
    # Compute the target state |psi> (the state that was on qubit 0)
    psi_sv = Statevector.from_instruction(psi_prep)
    # For each measurement outcome (m0, m1) in {00, 01, 10, 11}, compute the
    # conditional state of qubit 2 after applying the correction.
    # After Bell measurement of qubits 0, 1: the state of qubit 2 is one of
    # {|psi>, X|psi>, Z|psi>, XZ|psi>} up to normalization.
    # The correction X^m1 Z^m0 brings it back to |psi>.
    # Compute the conditional probability of each outcome and the resulting
    # state of qubit 2 (after correction). All corrections yield |psi>.
    # So the fidelity of qubit 2's state with |psi> is 1.
    # But to make this concrete, let's compute it via density matrices.
    probs = np.abs(sv.data) ** 2
    # Compute marginal density matrix of qubit 2 (before correction)
    dm = DensityMatrix(sv)
    rho_2 = partial_trace(dm, [0, 1])
    # After correction (averaged over measurement outcomes with appropriate
    # corrections), the state of qubit 2 should be |psi><psi|.
    # Compute the corrected density matrix:
    # rho_2_corrected = sum_{m0,m1} P(m0,m1) * X^m1 Z^m0 rho_2_conditional(m0,m1) Z^m0 X^m1
    # But after correction, each conditional state becomes |psi><psi|, so:
    # rho_2_corrected = |psi><psi| * sum P(m0,m1) = |psi><psi|
    # Compute fidelity with |psi>
    target_dm = DensityMatrix(psi_sv)
    fid = np.real(np.trace(rho_2.data @ target_dm.data.conj().T))
    # Note: This is the fidelity BEFORE correction. After correction it would be 1.
    # For the eval, we use a statevector-based approach that explicitly simulates
    # the corrections. Let's compute the corrected fidelity:
    # The corrected state of qubit 2 is |psi><psi| (since the corrections perfectly undo).
    corrected_fid = 1.0  # theoretical
    # But to actually verify via simulation, let's compute it properly:
    # For each (m0, m1), find the conditional state of qubit 2, apply correction,
    # compute fidelity with |psi>, then average weighted by P(m0, m1).
    fid_sum = 0.0
    for m0 in [0, 1]:
        for m1 in [0, 1]:
            # Probability of this outcome
            p_outcome = 0.0
            for idx in range(8):
                q0 = idx & 1
                q1 = (idx >> 1) & 1
                q2 = (idx >> 2) & 1
                if q0 == m0 and q1 == m1:
                    p_outcome += probs[idx]
            if p_outcome < 1e-12:
                continue
            # Conditional state of qubit 2
            cond_state = np.zeros(2, dtype=complex)
            for idx in range(8):
                q0 = idx & 1
                q1 = (idx >> 1) & 1
                q2 = (idx >> 2) & 1
                if q0 == m0 and q1 == m1:
                    cond_state[q2] = sv.data[idx] / np.sqrt(p_outcome)
            # Apply correction X^m1 Z^m0
            X = np.array([[0, 1], [1, 0]], dtype=complex)
            Z = np.array([[1, 0], [0, -1]], dtype=complex)
            correction = np.linalg.matrix_power(X, m1) @ np.linalg.matrix_power(Z, m0)
            corrected_state = correction @ cond_state
            # Fidelity with |psi>
            fid = np.abs(np.vdot(psi_sv.data, corrected_state)) ** 2
            fid_sum += p_outcome * fid
    return float(fid_sum)


def main():
    # Prepare |psi> = |+> on qubit 0
    psi_prep = QuantumCircuit(1)
    psi_prep.h(0)
    fidelity = simulate_teleport_with_corrections(psi_prep)
    print(f"fidelity = {fidelity:.3f}")
    print(f"teleported: {fidelity > 0.99}")


if __name__ == "__main__":
    main()
