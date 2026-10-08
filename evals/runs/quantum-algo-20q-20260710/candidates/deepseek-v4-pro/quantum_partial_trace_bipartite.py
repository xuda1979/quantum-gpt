import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, partial_trace


def main():
    # Build 3-qubit GHZ state
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)

    # Get density matrix of the full state
    rho = DensityMatrix.from_instruction(qc)

    # Partial trace over qubits [1, 2] to get reduced density matrix on qubit 0
    rho_A = partial_trace(rho, [1, 2])

    # Convert to numpy array
    rho_A_array = rho_A.data

    # Extract real parts and round to 4 decimals
    a = round(rho_A_array[0, 0].real, 4)
    b = round(rho_A_array[0, 1].real, 4)
    c = round(rho_A_array[1, 0].real, 4)
    d = round(rho_A_array[1, 1].real, 4)

    # Compute purity = Tr(rho_A^2)
    rho_A_sq = rho_A @ rho_A
    purity = np.trace(rho_A_sq.data).real
    purity_rounded = round(purity, 6)

    print("Reduced density matrix:")
    print(f"  [[{a}, {b}], [{c}, {d}]]")
    print(f"Purity = {purity_rounded}")

if __name__ == "__main__":
    main()
