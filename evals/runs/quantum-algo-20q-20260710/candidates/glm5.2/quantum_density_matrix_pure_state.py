import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix


def main():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)

    rho = DensityMatrix(qc)
    data = rho.data

    purity = float(np.trace(data @ data).real)

    eigvals = np.linalg.eigvalsh(data)
    eigvals = np.maximum(eigvals, 0.0)
    mask = eigvals > 1e-12
    entropy = float(-np.sum(eigvals[mask] * np.log2(eigvals[mask])))

    print(f"Purity = {purity:.6f}")
    print(f"Entropy = {entropy:.6f}")

if __name__ == "__main__":
    main()
