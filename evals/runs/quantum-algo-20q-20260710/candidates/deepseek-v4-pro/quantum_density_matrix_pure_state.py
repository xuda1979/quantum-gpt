import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix


def main():
    # 1. Build Bell state |Phi+>
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    # 2. Compute density matrix
    rho = DensityMatrix.from_instruction(qc)

    # 3. Compute purity Tr(rho^2)
    purity = np.real(np.trace(rho.data @ rho.data))

    # Compute von-Neumann entropy S(rho) = -Tr(rho log2 rho)
    eigenvalues = np.linalg.eigvalsh(rho.data)
    # Filter out zero eigenvalues to avoid log(0)
    nonzero_ev = eigenvalues[eigenvalues > 1e-12]
    entropy = -np.sum(nonzero_ev * np.log2(nonzero_ev))

    print(f"Purity = {purity:.6f}")
    print(f"Entropy = {entropy:.6f}")

if __name__ == "__main__":
    main()
