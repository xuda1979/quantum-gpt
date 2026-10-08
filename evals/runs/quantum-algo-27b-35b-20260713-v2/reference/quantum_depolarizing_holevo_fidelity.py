import numpy as np

def kraus_depolarizing(p):
    I = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    K0 = np.sqrt(1 - p) * I
    K1 = np.sqrt(p / 3.0) * X
    K2 = np.sqrt(p / 3.0) * Y
    K3 = np.sqrt(p / 3.0) * Z
    return [K0, K1, K2, K3]

def apply_channel(rho, kraus):
    return sum(K @ rho @ K.conj().T for K in kraus)

def von_neumann_entropy_bits(rho):
    eigs = np.linalg.eigvalsh(rho)
    eigs = np.clip(eigs, 0, None)
    return -float(np.sum(eigs * np.log2(eigs + 1e-15)))

def main():
    p = 0.3
    kraus = kraus_depolarizing(p)
    rho0 = np.array([[1, 0], [0, 0]], dtype=complex)
    rho1 = np.array([[0, 0], [0, 1]], dtype=complex)
    out0 = apply_channel(rho0, kraus)
    out1 = apply_channel(rho1, kraus)
    avg = 0.5 * out0 + 0.5 * out1
    S_avg = von_neumann_entropy_bits(avg)
    S0 = von_neumann_entropy_bits(out0)
    S1 = von_neumann_entropy_bits(out1)
    chi = S_avg - 0.5 * S0 - 0.5 * S1
    # Entanglement fidelity: F_e = (1/4) sum_i |Tr(K_i)|^2
    F_e = 0.25 * sum(abs(np.trace(K)) ** 2 for K in kraus)
    trace_out = float(np.real(np.trace(out0)))
    print(f"Output state trace = {trace_out:.4f}")
    print(f"Holevo info = {chi:.4f}")
    print(f"Entanglement fidelity = {float(np.real(F_e)):.4f}")
    print(f"Depolarizing p = {p:.4f}")

if __name__ == "__main__":
    main()
