import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector, DensityMatrix, Pauli, partial_trace
from qiskit.quantum_info import Kraus

def ghz_circuit_folded(n=3, fold=1):
    # Build a GHZ circuit where each H and CX is folded `fold` times.
    # Folding: G -> (G G^dag)^( (fold-1)/2 ) G  for odd fold.
    qc = QuantumCircuit(n)
    # H on q0
    for _ in range(fold):
        qc.h(0)
    # CX(0,1) and CX(0,2) folded
    for _ in range(fold):
        qc.cx(0, 1)
    for _ in range(fold):
        qc.cx(0, 2)
    return qc

def apply_depolarizing_after_gates(state_density, p):
    """Apply depolarizing noise p to every qubit (single-qubit depolarizing)."""
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    n = int(np.log2(state_density.shape[0]))
    # Single-qubit depolarizing Kraus: K0 = sqrt(1-p) I, K1 = sqrt(p/3) X, etc.
    Ks = [np.sqrt(1 - p) * I,
          np.sqrt(p / 3) * X,
          np.sqrt(p / 3) * Y,
          np.sqrt(p / 3) * Z]
    # Apply to each qubit in sequence
    rho = state_density
    for q in range(n):
        # Build the full Kraus operators acting on qubit q
        new_rho = np.zeros_like(rho)
        for K in Ks:
            full = np.eye(1, dtype=complex)
            for i in range(n):
                full = np.kron(full, K if i == q else I)
            new_rho += full @ rho @ full.conj().T
        rho = new_rho
    return rho

def zpair_expectation(rho, n=3):
    """Compute <Z0 Z1> + <Z1 Z2> + <Z0 Z2> from a 3-qubit density matrix."""
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    I = np.eye(2, dtype=complex)
    def kron3(a, b, c): return np.kron(np.kron(a, b), c)
    ZZ01 = kron3(Z, Z, I)
    ZZ12 = kron3(I, Z, Z)
    ZZ02 = kron3(Z, I, Z)
    return (float(np.real(np.trace(ZZ01 @ rho))) +
            float(np.real(np.trace(ZZ12 @ rho))) +
            float(np.real(np.trace(ZZ02 @ rho))))

def simulate_folded(fold, p=0.02, n=3):
    qc = ghz_circuit_folded(n=n, fold=fold)
    sv = Statevector.from_instruction(qc)
    rho = np.outer(sv.data, sv.data.conj())
    rho_noisy = apply_depolarizing_after_gates(rho, p)
    return zpair_expectation(rho_noisy, n=n)

def main():
    p = 0.02
    folds = [1, 3, 5]
    E = [simulate_folded(f, p=p) for f in folds]
    # Linear ZNE: fit line (f, E) and extrapolate to f=0.
    coeffs = np.polyfit(folds, E, 1)
    mitigated = float(np.polyval(coeffs, 0))
    ideal = 3.0
    print(f"Ideal expectation = {ideal:.4f}")
    print(f"Noisy (f=1) = {E[0]:.4f}")
    print(f"Noisy (f=3) = {E[1]:.4f}")
    print(f"Noisy (f=5) = {E[2]:.4f}")
    print(f"Mitigated = {mitigated:.4f}")
    print(f"Mitigation improvement = {mitigated - E[0]:.4f}")

if __name__ == "__main__":
    main()
