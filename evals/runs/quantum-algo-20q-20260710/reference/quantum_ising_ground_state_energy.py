import numpy as np


def main():
    I = np.array([[1, 0], [0, 1]], dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    H = -np.kron(Z, Z) - 0.5 * (np.kron(X, I) + np.kron(I, X))
    E0 = float(np.min(np.linalg.eigvalsh(H)))
    print(f"Ground state energy = {E0:.6f}")

if __name__ == "__main__":
    main()
