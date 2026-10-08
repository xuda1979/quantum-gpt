import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

def build_hadamard_test_gate(U, q, controlled=True):
    """Return a gate that applies U controlled by q (or just U if not controlled)."""
    if controlled:
        return U.control(1)
    return U

def hadamard_test_expectation(U, V_dag, phi):
    """Compute Re[<0| V^dag U |0>] for a single-qubit test using direct
    statevector simulation. Here we use a simpler approach: compute the
    expectation of the cost Hamiltonian directly via statevector overlaps."""
    # For the VQLS cost, we use the local cost C_L = 1 - (1/N) * sum_i Re[<b| V^dag U^dag A_i U V |b> <psi_i|phi>]
    # For a 2x2 system with A = sigma_z, b = |0>, this simplifies.
    pass

def vqls_solve(A, b, ansatz_params):
    """Solve A x = b for a 2x2 system using a parameterized ansatz.
    For simplicity, use a 1-qubit Ry ansatz V(theta) = Ry(theta).
    The cost is C(theta) = <phi| H_C |phi> where |phi> = V(theta)|0>
    and H_C = V^dag A^dag (I - |b><b|) A V... actually for VQLS the cost
    involves the normalized pseudo-inverse. For a 2x2 problem we can use the
    simpler cost C = || A V(theta)|0> - b ||^2 / ||b||^2."""
    n = 1
    theta = ansatz_params[0]
    # Ansatz state
    qc = QuantumCircuit(n)
    qc.ry(theta, 0)
    sv = Statevector.from_instruction(qc)
    phi = sv.data  # 2-dim complex vector
    # Cost: || A phi - b ||^2
    diff = A @ phi - b
    return float(np.real(np.vdot(diff, diff)))

def main():
    # Solve A x = b for a simple 2x2 system
    A = np.array([[1.0, 0.0], [0.0, 2.0]])  # diagonal
    b = np.array([1.0, 1.0]) / np.sqrt(2)   # |+>
    # Exact solution: x = A^{-1} b / ||A^{-1} b||
    x_exact = np.linalg.solve(A, b)
    x_exact_normalized = x_exact / np.linalg.norm(x_exact)
    # VQLS with 1-qubit Ry ansatz
    x0 = np.array([0.5])
    res = minimize(vqls_solve, x0, args=(A, b), method="COBYLA",
                   options={"maxiter": 200, "tol": 1e-8})
    theta_opt = res.x[0]
    # Build the final ansatz state
    qc = QuantumCircuit(1)
    qc.ry(theta_opt, 0)
    sv = Statevector.from_instruction(qc)
    x_vqls = sv.data
    # Compare to exact normalized solution
    # The VQLS state approximates x / ||x||, so compare up to a global phase
    overlap = float(np.abs(np.vdot(x_exact_normalized, x_vqls)) ** 2)
    # Also compute the cost
    cost = vqls_solve([theta_opt], A, b)
    print(f"System: A = diag(1, 2), b = |+>")
    print(f"VQLS theta = {theta_opt:.6f}")
    print(f"VQLS cost = {cost:.6f}")
    print(f"Overlap with exact = {overlap:.6f}")
    print(f"Converged: {overlap > 0.99}")
    print(f"Correct: {overlap > 0.99 and cost < 0.01}")

if __name__ == "__main__":
    main()
