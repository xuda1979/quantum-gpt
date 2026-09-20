import numpy as np

def main():
    # Build the 4-qubit state in the computational basis (qiskit order: q0 is MSB).
    # |psi> = (1/sqrt2)(|0000> + |1111>) + (1/sqrt6)(|0011> + |1100>)
    state = np.zeros(16, dtype=complex)
    # q0 q1 q2 q3 -> index = (q0<<3) | (q1<<2) | (q2<<1) | q3
    state[(0<<3) | (0<<2) | (0<<1) | 0] += 1.0 / np.sqrt(2)
    state[(1<<3) | (1<<2) | (1<<1) | 1] += 1.0 / np.sqrt(2)
    state[(0<<3) | (0<<2) | (1<<1) | 1] += 1.0 / np.sqrt(6)
    state[(1<<3) | (1<<2) | (0<<1) | 0] += 1.0 / np.sqrt(6)
    norm = float(np.linalg.norm(state))
    # Reshape: rows = q0 q1 (4 rows), cols = q2 q3 (4 cols)
    # Index layout: q0 q1 q2 q3 -> (q0 q1, q2 q3) = ((idx >> 2), (idx & 3))
    M = state.reshape((4, 4))
    U, S, Vh = np.linalg.svd(M)
    tol = 1e-9
    nonzero = S[S > tol]
    rank = len(nonzero)
    largest = float(nonzero[0]) if rank > 0 else 0.0
    smallest = float(nonzero[-1]) if rank > 0 else 0.0
    # Entropy of the reduced density matrix
    p = nonzero ** 2
    entropy = -float(np.sum(p * np.log2(p + 1e-15)))
    print(f"State norm = {norm:.4f}")
    print(f"Schmidt rank = {rank}")
    print(f"Largest Schmidt coeff = {largest:.4f}")
    print(f"Smallest nonzero Schmidt coeff = {smallest:.4f}")
    print(f"Entropy = {entropy:.4f}")

if __name__ == "__main__":
    main()
