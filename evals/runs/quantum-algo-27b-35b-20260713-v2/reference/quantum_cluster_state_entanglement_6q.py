import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, DensityMatrix

def main():
    N = 6
    qc = QuantumCircuit(N)
    qc.h(range(N))
    for i in range(N - 1):
        qc.cz(i, i + 1)
    sv = Statevector.from_instruction(qc)
    norm = float(np.linalg.norm(sv.data))
    # Full density matrix
    dm = DensityMatrix(sv)
    # Reduced density matrix of first 3 qubits: trace out qubits 3, 4, 5
    rho_A = partial_trace(dm, [3, 4, 5]).data
    eigvals = np.linalg.eigvalsh(rho_A)
    eigvals = np.clip(eigvals, 0, None)
    # Von Neumann entropy (base 2)
    s_vn = -float(np.sum(eigvals * np.log2(eigvals + 1e-15)))
    # Renyi-2 entropy
    s_2 = -float(np.log2(np.sum(eigvals ** 2) + 1e-15))
    largest = float(np.sqrt(eigvals.max()))
    print(f"Statevector norm = {norm:.4f}")
    print(f"Von Neumann entropy = {s_vn:.4f}")
    print(f"Renyi-2 entropy = {s_2:.4f}")
    print(f"Largest Schmidt coeff = {largest:.4f}")

if __name__ == "__main__":
    main()
