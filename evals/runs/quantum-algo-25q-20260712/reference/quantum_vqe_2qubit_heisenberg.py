"""VQE for the 2-qubit Heisenberg Hamiltonian H = X⊗X + Y⊗Y + Z⊗Z.

The ground state of H = X⊗X + Y⊗Y + Z⊗Z is the singlet |Psi-> with
energy -3. We use a 4-parameter Ry-CNOT-Ry ansatz and minimize via
Nelder-Mead, with a brute-force scan to find a good starting point.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorEstimator
from qiskit.quantum_info import SparsePauliOp
from scipy.optimize import minimize


def ansatz(params) -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.ry(params[0], 0)
    qc.ry(params[1], 1)
    qc.cx(0, 1)
    qc.ry(params[2], 0)
    qc.ry(params[3], 1)
    return qc


def cost(params, H, est):
    qc = ansatz(params)
    result = est.run([(qc, H)]).result()
    return result[0].data.evs


def main():
    H = SparsePauliOp.from_list([("XX", 1.0), ("YY", 1.0), ("ZZ", 1.0)])
    est = StatevectorEstimator()
    # Brute-force scan for good starting point
    best_E, best_p = 1e9, None
    rng = np.random.default_rng(42)
    for _ in range(200):
        p = rng.uniform(0, 2 * np.pi, 4)
        E = cost(p, H, est)
        if E < best_E:
            best_E, best_p = E, p
    res = minimize(cost, best_p, args=(H, est), method="Nelder-Mead",
                   options={"xatol": 1e-6, "fatol": 1e-6})
    E_vqe = float(res.fun)
    H_mat = H.to_matrix()
    eigvals = np.linalg.eigvalsh(H_mat)
    E_exact = float(eigvals[0])
    print(f"VQE energy = {E_vqe:.4f}")
    print(f"exact = {E_exact:.4f}")
    print(f"converged: {abs(E_vqe - E_exact) < 0.05}")


if __name__ == "__main__":
    main()
