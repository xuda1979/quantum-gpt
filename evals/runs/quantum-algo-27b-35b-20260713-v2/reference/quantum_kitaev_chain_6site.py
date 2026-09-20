import numpy as np

def jw_operators(N):
    """Return c_i, c_i^dagger as 2^N x 2^N matrices (Jordan-Wigner)."""
    Pauli = {"I": np.eye(2, dtype=complex),
             "X": np.array([[0, 1], [1, 0]], dtype=complex),
             "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
             "Z": np.array([[1, 0], [0, -1]], dtype=complex)}
    def kron_all(ops):
        out = ops[0]
        for op in ops[1:]:
            out = np.kron(out, op)
        return out
    c_list = []
    cdag_list = []
    for i in range(N):
        ops_c = [Pauli["I"]] * N
        ops_cd = [Pauli["I"]] * N
        for j in range(i):
            ops_c[j] = Pauli["Z"]
            ops_cd[j] = Pauli["Z"]
        ops_c[i] = (Pauli["X"] + 1j * Pauli["Y"]) / 2.0
        ops_cd[i] = (Pauli["X"] - 1j * Pauli["Y"]) / 2.0
        c_list.append(kron_all(ops_c))
        cdag_list.append(kron_all(ops_cd))
    return c_list, cdag_list

def build_kitaev(N=6, J=1.0, Delta=0.8, mu=0.5):
    c, cd = jw_operators(N)
    H = np.zeros((2**N, 2**N), dtype=complex)
    for i in range(N - 1):
        # -J * (c_i^dag c_{i+1} + h.c.)
        H += -J * (cd[i] @ c[i+1] + cd[i+1] @ c[i])
        # Delta * (c_i c_{i+1} + c_{i+1}^dag c_i^dag)
        H += Delta * (c[i] @ c[i+1] + cd[i+1] @ cd[i])
    for i in range(N):
        # -mu * (n_i - 1/2)
        n_i = cd[i] @ c[i]
        H += -mu * (n_i - 0.5 * np.eye(2**N))
    return H, c, cd

def bdg_spectrum(N=6, J=1.0, Delta=0.8, mu=0.5):
    # BdG matrix in the basis (c, c^dag).
    # H_BdG = [[ h,  Delta_mat ], [ -Delta_mat*, -h* ]]
    # h_{ij} = -J (delta_{i,j+1} + delta_{i,j-1}) - mu delta_{ij}
    h = np.zeros((N, N))
    for i in range(N - 1):
        h[i, i+1] = -J
        h[i+1, i] = -J
    for i in range(N):
        h[i, i] = -mu
    Delta_mat = np.zeros((N, N))
    for i in range(N - 1):
        Delta_mat[i, i+1] = Delta
        Delta_mat[i+1, i] = -Delta
    H_bdg = np.block([[h, Delta_mat], [-Delta_mat.conj().T, -h.conj().T]])
    eigs = np.linalg.eigvalsh(H_bdg)
    # Lowest positive eigenvalue
    pos = sorted([e for e in eigs if e > 1e-9])
    return pos[0] if pos else 0.0

def main():
    N = 6; J = 1.0; Delta = 0.8; mu = 0.5
    H, c, cd = build_kitaev(N, J, Delta, mu)
    eigs, vecs = np.linalg.eigh(H)
    E0 = float(eigs[0])
    gs = vecs[:, 0]
    # Fermionic parity: P = (-1)^{N_particles} = product_i (1 - 2 n_i)
    P_op = np.eye(2**N, dtype=complex)
    for i in range(N):
        n_i = cd[i] @ c[i]
        P_op = P_op @ (np.eye(2**N) - 2 * n_i)
    parity = float(np.real(gs.conj() @ P_op @ gs))
    bdg_gap = bdg_spectrum(N, J, Delta, mu)
    majorana = float(np.real(gs.conj() @ (c[0] + cd[0]) @ gs))
    print(f"Ground state energy = {E0:.4f}")
    print(f"Ground state parity = {'+1' if parity > 0 else '-1'}")
    print(f"BdG gap = {bdg_gap:.4f}")
    print(f"Majorana overlap = {majorana:.4f}")

if __name__ == "__main__":
    main()
