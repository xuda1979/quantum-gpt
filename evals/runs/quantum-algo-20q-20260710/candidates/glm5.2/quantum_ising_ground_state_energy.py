import numpy as np


def build_hamiltonian():
    Z = np.array([[1, 0], [0, -1]], dtype=float)
    X = np.array([[0, 1], [1, 0]], dtype=float)
    I = np.eye(2, dtype=float)
    return -np.kron(Z, Z) - 0.5 * (np.kron(X, I) + np.kron(I, X))

def main():
    H = build_hamiltonian()
    E0 = np.min(np.linalg.eigvalsh(H))
    print(f"Ground state energy = {E0:.6f}")

if __name__ == "__main__":
    main()
