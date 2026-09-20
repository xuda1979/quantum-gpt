import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, random_statevector

def build_teleportation_circuit(state_to_send):
    qc = QuantumCircuit(3, 3)
    qc.initialize(state_to_send, 0)
    # Bell pair on qubits 1 and 2
    qc.h(1); qc.cx(1, 2)
    # Alice's Bell measurement on qubits 0 and 1
    qc.cx(0, 1); qc.h(0)
    qc.measure(0, 0); qc.measure(1, 1)
    # Classical corrections on qubit 2 (use c_if via separate branches in sim)
    return qc

def simulate_teleportation(state_to_send):
    # Simulate by computing the output state conditioned on each measurement
    # outcome using statevector evolution with classical feedback.
    from qiskit.quantum_info import DensityMatrix, partial_trace
    # Build the full unitary part (no measurement)
    qc = QuantumCircuit(3)
    qc.initialize(state_to_send, 0)
    qc.h(1); qc.cx(1, 2)
    qc.cx(0, 1); qc.h(0)
    sv = Statevector.from_instruction(qc)
    # Measurement probabilities and post-measurement states
    dm = DensityMatrix(sv)
    # Trace out nothing - compute probability of each (c0, c1) outcome
    # by projecting q0, q1 onto |0>/<1> basis
    outcomes = {}
    for c0 in [0, 1]:
        for c1 in [0, 1]:
            proj = np.eye(8, dtype=complex)
            # project q0 onto |c0>, q1 onto |c1>
            for k in range(8):
                b0 = (k >> 0) & 1
                b1 = (k >> 1) & 1
                if b0 != c0 or b1 != c1:
                    proj[k, k] = 0
            projected = proj @ dm.data @ proj
            prob = float(np.real(np.trace(projected)))
            if prob < 1e-12:
                outcomes[(c0, c1)] = (0.0, None)
                continue
            post = projected / prob
            # Apply corrections to q2: if c1=1 apply X, if c0=1 apply Z
            X = np.array([[0, 1], [1, 0]]); Z = np.array([[1, 0], [0, -1]])
            I = np.eye(2)
            corr = np.kron(np.kron(I, I), (X if c1 else I)) @ np.kron(np.kron(I, I), (Z if c0 else I))
            post = corr @ post @ corr.conj().T
            outcomes[(c0, c1)] = (prob, post)
    return outcomes

def main():
    rng = np.random.default_rng(42)
    # Random pure state to teleport
    psi = random_statevector(2, seed=42).data
    outcomes = simulate_teleportation(psi)
    # Average fidelity over measurement outcomes
    total_fid = 0.0
    total_prob = 0.0
    for (c0, c1), (prob, post) in outcomes.items():
        if prob == 0.0 or post is None:
            continue
        # Reduced density matrix of qubit 2
        from qiskit.quantum_info import DensityMatrix, partial_trace
        dm_post = DensityMatrix(post)
        rho2 = partial_trace(dm_post, [0, 1])
        fid = float(np.real(rho2.data @ np.outer(psi, psi.conj())).trace())
        total_fid += prob * fid
        total_prob += prob
    avg_fid = total_fid / total_prob if total_prob > 0 else 0.0
    print(f"Teleported state: random pure 1-qubit")
    print(f"Average fidelity = {avg_fid:.4f}")
    print(f"Classical limit = 0.6667")
    print(f"Beats classical: {avg_fid > 0.6667}")
    print(f"Perfect teleport: {abs(avg_fid - 1.0) < 1e-6}")

if __name__ == "__main__":
    main()
