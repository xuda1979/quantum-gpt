import numpy as np
from qiskit.quantum_info import SparsePauliOp

def build_H():
    J, h = 1.0, 0.3
    terms = [
        ("XXI", J), ("IXX", J),
        ("YYI", J), ("IYY", J),
        ("ZZI", J), ("IZZ", J),
        ("ZII", h), ("IZI", h), ("IIZ", h),
    ]
    return SparsePauliOp.from_list(terms)

def main():
    H = build_H()
    Hmat = H.to_matrix()
    eigs, vecs = np.linalg.eigh(Hmat)
    gs = float(eigs[0])
    # Initial state |++> = |+>|+>|+>
    plus = np.array([1, 1]) / np.sqrt(2)
    psi0 = np.kron(np.kron(plus, plus), plus)
    # Imaginary-time evolution: exp(-H*dt)
    dt = 0.1
    # exp(-H*dt) = V diag(exp(-eigs*dt)) V^dagger
    U_it = vecs @ np.diag(np.exp(-eigs * dt)) @ vecs.T.conj()
    psi_unnorm = U_it @ psi0
    norm = float(np.linalg.norm(psi_unnorm))
    psi = psi_unnorm / norm
    energy = float(np.real(psi.conj() @ Hmat @ psi))
    print(f"ITE energy = {energy:.4f}")
    print(f"Exact GS = {gs:.4f}")
    print(f"Energy gap = {energy - gs:.4f}")
    print(f"State norm = {norm:.4f}")

if __name__ == "__main__":
    main()
