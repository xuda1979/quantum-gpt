import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix


def main():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    rho = DensityMatrix(qc)
    mat = rho.data
    purity = float(np.real(np.trace(mat @ mat)))
    eigvals = np.linalg.eigvalsh(mat)
    eigvals = np.clip(eigvals, 0, None)
    entropy = float(-np.sum(eigvals * np.log2(eigvals + 1e-30)))
    print(f"Purity = {purity:.6f}")
    print(f"Entropy = {entropy:.6f}")

if __name__ == "__main__":
    main()
