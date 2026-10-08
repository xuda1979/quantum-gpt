import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, partial_trace


def main():
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    rho = DensityMatrix(qc)
    rho_A = partial_trace(rho, [1, 2])
    m = rho_A.data
    a = float(np.real(m[0, 0]))
    b = float(np.real(m[0, 1]))
    c = float(np.real(m[1, 0]))
    d = float(np.real(m[1, 1]))
    purity = float(np.real(np.trace(m @ m)))
    print("Reduced density matrix:")
    print(f"  [[{a:.4f}, {b:.4f}], [{c:.4f}, {d:.4f}]]")
    print(f"Purity = {purity:.6f}")

if __name__ == "__main__":
    main()
