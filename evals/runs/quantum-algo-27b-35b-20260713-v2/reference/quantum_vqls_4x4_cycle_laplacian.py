import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

def matrix_A():
    return np.array([[2, -1, 0, -1],
                     [-1, 2, -1, 0],
                     [0, -1, 2, -1],
                     [-1, 0, -1, 2]], dtype=float)

def pauli_decompose_4x4(A):
    """Decompose a 4x4 Hermitian matrix as a sum of 2-qubit Pauli strings."""
    Pauli = {
        "I": np.eye(2, dtype=complex),
        "X": np.array([[0, 1], [1, 0]], dtype=complex),
        "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    }
    labels = ["II", "IX", "IY", "IZ", "XI", "XX", "XY", "XZ",
              "YI", "YX", "YY", "YZ", "ZI", "ZX", "ZY", "ZZ"]
    # qiskit Pauli string: leftmost = qubit 0
    # Matrix for label "AB" (A on q0, B on q1) = kron(A, B).
    terms = []
    for lab in labels:
        A_op = Pauli[lab[0]]
        B_op = Pauli[lab[1]]
        M = np.kron(A_op, B_op)
        coeff = float(np.real(np.trace(A @ M.conj().T)) / 4.0)
        if abs(coeff) > 1e-9:
            terms.append((lab, coeff))
    return terms

def ansatz(alpha):
    qc = QuantumCircuit(2)
    qc.ry(alpha[0], 0)
    qc.ry(alpha[1], 1)
    qc.cx(0, 1)
    qc.ry(alpha[2], 0)
    qc.ry(alpha[3], 1)
    return qc

def cost(alpha, A, b):
    qc = ansatz(alpha)
    sv = Statevector.from_instruction(qc).data
    psi = A @ sv
    b_norm = b / np.linalg.norm(b)
    num = float(np.real(psi.conj() @ psi))
    den = float(np.real(b_norm @ b_norm))
    return num / den

def main():
    A = matrix_A()
    b = np.array([1, 1, 1, 1], dtype=float)
    res = minimize(lambda x: cost(x, A, b), x0=[0.5, 0.5, 0.5, 0.5],
                   method="COBYLA", maxiter=500, tol=1e-6)
    final_cost = res.fun
    qc = ansatz(res.x)
    x = Statevector.from_instruction(qc).data.real
    x_norm = x / np.linalg.norm(x)
    # Exact solution
    x_exact = np.linalg.solve(A, b)
    x_exact_norm = x_exact / np.linalg.norm(x_exact)
    fidelity = float(abs(x_norm.conj() @ x_exact_norm) ** 2)
    residual = float(np.linalg.norm(A @ x_norm - b / np.linalg.norm(b))
                     / np.linalg.norm(b / np.linalg.norm(b)))
    print(f"VQLS cost = {final_cost:.4f}")
    print(f"Solution fidelity = {fidelity:.4f}")
    print(f"Relative residual = {residual:.4f}")

if __name__ == "__main__":
    main()
