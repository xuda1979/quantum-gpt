import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

N = 6
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]

def cost_hamiltonian():
    # H_C = sum_{(i,j)} (1 - Z_i Z_j) / 2
    # Constant 1/2 per edge (total = N/2 = 3); the -Z_i Z_j / 2 terms.
    terms = [("I" * N, 0.5 * len(EDGES))]
    for (i, j) in EDGES:
        zstr = ["I"] * N
        zstr[i] = "Z"; zstr[j] = "Z"
        terms.append(("".join(zstr), -0.5))
    return SparsePauliOp.from_list(terms)

def mixer_hamiltonian():
    # H_M = sum_i X_i (just for reference; we use it as gates).
    return SparsePauliOp.from_list([("X" * N, 0.0)])  # dummy, not used directly

def qaoa_circuit(gamma, beta, p=2):
    qc = QuantumCircuit(N)
    qc.h(range(N))
    for k in range(p):
        # Cost unitary: exp(-i gamma_k * H_C) -> for each edge, RZZ(2*gamma_k)
        for (i, j) in EDGES:
            qc.rzz(2 * gamma[k], i, j)
        # Mixer unitary: exp(-i beta_k * H_M) -> for each qubit, RX(2*beta_k)
        for i in range(N):
            qc.rx(2 * beta[k], i)
    return qc

def cost_value(gamma_beta, H_C, p=2):
    g = gamma_beta[:p]
    b = gamma_beta[p:]
    qc = qaoa_circuit(g, b, p=p)
    sv = Statevector.from_instruction(qc)
    return float(sv.expectation_value(H_C).real)

def main():
    H_C = cost_hamiltonian()
    p = 2
    x0 = np.array([0.1, 0.2, 0.3, 0.4])
    res = minimize(lambda x: cost_value(x, H_C, p=p), x0=x0,
                   method="COBYLA", maxiter=1000, tol=1e-6)
    exp_H_C = res.fun
    qaoa_energy = -exp_H_C
    qaoa_cut = (6 - exp_H_C) / 2.0
    approx = qaoa_cut / 5.0
    print(f"QAOA energy = {qaoa_energy:.4f}")
    print(f"QAOA cut value = {round(qaoa_cut)}")
    print(f"Exact MaxCut = 5")
    print(f"Approx ratio = {approx:.4f}")

if __name__ == "__main__":
    main()
