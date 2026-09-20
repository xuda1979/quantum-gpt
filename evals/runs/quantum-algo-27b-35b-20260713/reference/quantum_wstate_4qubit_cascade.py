import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, SparsePauliOp, partial_trace, DensityMatrix

def build_w_state(n):
    """Build an n-qubit W state: |10...0> + |01..0> + ... + |0...01> (normalized)."""
    qc = QuantumCircuit(n)
    # Standard construction: ry rotations + controlled rotations
    # Start by preparing |10..0> amplitude on qubit 0
    # Use the recursive construction: ry(theta_1) on qubit 0 then split.
    # theta_k = arccos(sqrt(1/(n-k+1)))
    # Apply ry(theta_1) on qubit 0 to make sqrt(1/n)|0> + sqrt((n-1)/n)|1>
    qc.ry(2 * np.arccos(np.sqrt(1.0 / n)), 0)
    # Now |1..1> amplitude is sqrt((n-1)/n) on qubit 0 = 1. We want to split this
    # into the W state of qubits 1..n-1 scaled by sqrt((n-1)/n).
    # For each subsequent qubit k, apply a controlled-ry that rotates the
    # |1> amplitude of qubit k-1 into qubit k.
    for k in range(1, n):
        # Controlled rotation: when qubit k-1 is |1>, rotate qubit k by
        # theta_k = 2*arccos(sqrt(1/(n-k)))
        theta = 2 * np.arccos(np.sqrt(1.0 / (n - k)))
        # First, move the |1> on qubit k-1 to |0> via X so we can do a
        # controlled rotation with the standard control.
        # Actually, use CRY gate directly (control = qubit k-1, target = qubit k)
        qc.cry(theta, k - 1, k)
        # After the CRY, the |1> on qubit k-1 has been "consumed" into qubit k
        # We need to swap the |1> amplitude from k-1 to k for the next iteration.
        # Apply CX(k, k-1) to move the |1> from k-1 to k.
        qc.cx(k, k - 1)
    return qc

def main():
    n = 4
    qc = build_w_state(n)
    sv = Statevector.from_instruction(qc)
    # The W state has 4 basis states with amplitude 1/2 each:
    # |1000>, |0100>, |0010>, |0001>
    N = 2 ** n
    expected = np.zeros(N, dtype=complex)
    for k in range(n):
        idx = 1 << (n - 1 - k)  # qubit k is 1, rest are 0
        expected[idx] = 1.0
    expected /= np.linalg.norm(expected)
    fidelity = float(np.abs(np.vdot(expected, sv.data)) ** 2)
    # Also verify: exactly one qubit is 1 with probability 1
    probs = sv.probabilities()
    one_excitation_prob = 0.0
    for i, p in enumerate(probs):
        bits = format(i, f"0{n}b")
        if bits.count("1") == 1:
            one_excitation_prob += p
    # Symmetry: each of the 4 basis states has equal probability 0.25
    single_probs = []
    for k in range(n):
        idx = 1 << (n - 1 - k)
        single_probs.append(float(probs[idx]))
    equal = all(abs(p - 0.25) < 1e-9 for p in single_probs)
    print(f"W-state: {n} qubits")
    print(f"Fidelity = {fidelity:.6f}")
    print(f"One-excitation prob = {one_excitation_prob:.6f}")
    print(f"Per-qubit probs = {[round(p, 4) for p in single_probs]}")
    print(f"Equal weights: {equal}")
    print(f"Correct: {fidelity > 0.9999 and equal}")

if __name__ == "__main__":
    main()
