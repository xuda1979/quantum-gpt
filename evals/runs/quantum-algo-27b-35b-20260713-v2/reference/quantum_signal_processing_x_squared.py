import numpy as np

def signal_operator(x):
    # W(x) = [[x, i*sqrt(1-x^2)], [i*sqrt(1-x^2), -x]]
    s = np.sqrt(1 - x * x)
    return np.array([[x, 1j * s], [1j * s, -x]], dtype=complex)

def phase_matrix(phi):
    return np.array([[np.exp(1j * phi), 0], [0, np.exp(-1j * phi)]], dtype=complex)

def qsp_unitary(x, phis):
    Q = phase_matrix(phis[0])
    for k in range(1, len(phis)):
        Q = Q @ signal_operator(x) @ phase_matrix(phis[k])
    # The standard QSP sequence also has a final W(x); we follow the
    # definition: Q(x) = e^{i phi_0 Z} W(x) e^{i phi_1 Z} W(x) ... e^{i phi_n Z}
    # Here phis has length n+1, applied as: e^{i phi_0 Z} W e^{i phi_1 Z} W ... W e^{i phi_n Z}
    # But the loop above applied W before each phase except the first, so:
    # Q = e^{i phi_0 Z} W e^{i phi_1 Z} W e^{i phi_2 Z} ... W e^{i phi_n Z}
    # which is the correct QSP form.
    return Q

def main():
    x = 0.7
    phis = np.array([0.5, -0.3, 0.8, -0.6, 0.2, -0.1])
    Q = qsp_unitary(x, phis)
    target = x * x
    q00_real = float(np.real(Q[0, 0]))
    q00_imag = float(np.imag(Q[0, 0]))
    trace = float(np.real(np.trace(Q)))
    det = float(np.real(np.linalg.det(Q)))
    print(f"Target f(0.7) = {target:.4f}")
    print(f"QSP (0,0) real = {q00_real:.4f}")
    print(f"QSP (0,0) imag = {q00_imag:.4f}")
    print(f"Trace = {trace:.4f}")
    print(f"Determinant = {det:.4f}")

if __name__ == "__main__":
    main()
