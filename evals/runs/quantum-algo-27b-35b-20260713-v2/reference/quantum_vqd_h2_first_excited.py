import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

def build_hamiltonian():
    terms = [
        ("IIII", -0.810547980537),
        ("ZIII", 0.17218393212),
        ("IZII", 0.17218393212),
        ("ZZII", -0.225753492224),
        ("IIZZ", -0.225753492224),
        ("ZZZZ", 0.120912632617),
        ("ZIZI", 0.168927538701),
        ("IZIZ", 0.168927538701),
        ("ZIIZ", 0.045232799946),
        ("IZZI", 0.045232799946),
    ]
    return SparsePauliOp.from_list(terms)

def ansatz_state(theta):
    # 2-qubit ansatz on qubits 2 and 3 of a 4-qubit system.
    # Active qubits in the Pauli string layout: q2, q3.
    qc = QuantumCircuit(4)
    qc.ry(theta[0], 2)
    qc.ry(theta[1], 3)
    qc.cx(2, 3)
    qc.ry(theta[2], 2)
    qc.ry(theta[3], 3)
    return Statevector.from_instruction(qc)

def energy(theta, H):
    sv = ansatz_state(theta)
    return float(sv.expectation_value(H).real)

def overlap(theta, sv0):
    sv = ansatz_state(theta)
    return abs(sv.conjugate().inner(sv0)) ** 2

def vqd_objective(theta, H, sv0, beta):
    return energy(theta, H) + beta * overlap(theta, sv0)

def main():
    H = build_hamiltonian()
    # Ground state
    res0 = minimize(lambda x: energy(x, H), x0=[0.1, 0.2, 0.3, 0.4],
                    method="COBYLA", maxiter=500, tol=1e-6)
    sv0 = ansatz_state(res0.x)
    # Excited state with VQD
    res1 = minimize(lambda x: vqd_objective(x, H, sv0, beta=5.0),
                    x0=[1.5, 0.0, 0.5, 1.0], method="COBYLA", maxiter=500, tol=1e-6)
    vqe_g = res0.fun
    vqd_e = res1.fun
    # Exact
    Hmat = H.to_matrix()
    eigs = np.linalg.eigvalsh(Hmat)
    e0 = float(eigs[0]); e1 = float(eigs[1])
    print(f"VQE ground = {vqe_g:.4f}")
    print(f"VQD excited = {vqd_e:.4f}")
    print(f"Exact GS = {e0:.4f}")
    print(f"Exact ES = {e1:.4f}")
    print(f"GS error = {abs(vqe_g - e0):.4f}")
    print(f"ES error = {abs(vqd_e - e1):.4f}")

if __name__ == "__main__":
    main()
