import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

def build_hamiltonian():
    # H = -J*(Z0Z1 + Z1Z2) - h*(X0 + X1 + X2), J=1.0, h=0.5
    J, h = 1.0, 0.5
    return SparsePauliOp.from_list([
        ("ZZI", -J), ("IZZ", -J),
        ("IXX", 0.0),  # placeholder to keep ordering; we use XIII below
    ]) + SparsePauliOp.from_list([
        ("XII", -h), ("IXI", -h), ("IIX", -h),
    ])

def ansatz(params, n=3, layers=2):
    qc = QuantumCircuit(n)
    idx = 0
    for _ in range(layers):
        for q in range(n):
            qc.ry(params[idx], q); idx += 1
        for q in range(n - 1):
            qc.cx(q, q + 1)
    return qc

def expectation(params, ham):
    qc = ansatz(params)
    sv = Statevector.from_instruction(qc)
    return float(sv.expectation_value(ham).real)

def main():
    ham = build_hamiltonian()
    n_params = 3 * 2
    x0 = np.array([0.1 * i for i in range(n_params)])
    res = minimize(expectation, x0, args=(ham,), method="COBYLA",
                   options={"maxiter": 400, "tol": 1e-6})
    # Brute-force ground state for verification: 8-dimensional diagonalization
    Z = np.diag([1, -1]); X = np.array([[0, 1], [1, 0]]); I = np.eye(2)
    def kron3(a, b, c): return np.kron(np.kron(a, b), c)
    H = -1.0*(kron3(Z, Z, I) + kron3(I, Z, Z)) - 0.5*(kron3(X, I, I) + kron3(I, X, I) + kron3(I, I, X))
    eigs = np.linalg.eigvalsh(H)
    gs_exact = float(eigs[0])
    vqe = res.fun
    print(f"VQE energy = {vqe:.4f}")
    print(f"Exact GS = {gs_exact:.4f}")
    print(f"Abs error = {abs(vqe - gs_exact):.4f}")
    print(f"Converged: {abs(vqe - gs_exact) < 0.05}")

if __name__ == "__main__":
    main()
