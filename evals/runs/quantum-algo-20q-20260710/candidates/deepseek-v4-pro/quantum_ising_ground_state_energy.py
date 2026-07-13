import numpy as np


def main():
    # Pauli matrices
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    I = np.eye(2, dtype=complex)

    # Kronecker products
    Z_Z = np.kron(Z, Z)
    X_I = np.kron(X, I)
    I_X = np.kron(I, X)

    # Hamiltonian
    H = -Z_Z - 0.5 * (X_I + I_X)

    # Ground-state energy
    eigenvalues = np.linalg.eigvalsh(H)
    E0 = np.min(eigenvalues).real

    print(f"  Ground state energy = {E0:.6f}")

if __name__ == "__main__":
    main()
