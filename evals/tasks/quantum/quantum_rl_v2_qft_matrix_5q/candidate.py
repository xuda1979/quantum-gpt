"""5-qubit QFT matrix: direct omega**(j*k)/sqrt(N) construction versus
multiplication of embedded H, controlled-phase, and SWAP gate matrices.

Convention (declared): little-endian indices -- qubit 0 is the least
significant bit, state |k> has index k with bits (q0 q1 q2 q3 q4).
The direct matrix is F[j, k] = omega**(j*k)/sqrt(N) with
omega = exp(2 pi i / N), N = 2**5. The gate-based construction follows
the standard QFT circuit order (H, then controlled phases cp on higher
targets, then bit-reversal SWAPs), and the two matrices are compared
after global-phase alignment.
"""

import numpy as np

I2 = np.eye(2, dtype=complex)
H2 = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / np.sqrt(2.0)


def qft_matrix(n=5):
    """Direct DFT matrix F[j,k] = omega**(j*k)/sqrt(N), N = 2**n."""
    n_states = 1 << n
    omega = np.exp(2.0j * np.pi / n_states)
    j = np.arange(n_states).reshape(-1, 1)
    k = np.arange(n_states).reshape(1, -1)
    return (omega ** (j * k)) / np.sqrt(n_states)


def _h_matrix(n, qubit):
    """Full 2^n x 2^n matrix of H acting on `qubit`."""
    full = np.eye(1 << n, dtype=complex)
    for b in range(1 << n):
        bit = (b >> qubit) & 1
        nb = b ^ (1 << qubit)
        full[b, b] = H2[bit, bit]
        full[b, nb] = H2[bit, 1 - bit]
        full[nb, b] = H2[1 - bit, bit]
        full[nb, nb] = H2[1 - bit, 1 - bit]
    return full


def _cp_matrix(n, angle, control, target):
    """Full 2^n x 2^n matrix of cp(angle) with `control` and `target`."""
    full = np.eye(1 << n, dtype=complex)
    for b in range(1 << n):
        cb = (b >> control) & 1
        tb = (b >> target) & 1
        if cb == 1 and tb == 1:
            full[b, b] = np.exp(1.0j * angle)
    return full


def _swap_matrix(n, i, j):
    """Full 2^n x 2^n permutation matrix swapping bits i and j."""
    full = np.zeros((1 << n, 1 << n), dtype=complex)
    for b in range(1 << n):
        bi = (b >> i) & 1
        bj = (b >> j) & 1
        if bi == bj:
            nb = b
        else:
            nb = b ^ (1 << i) ^ (1 << j)
        full[nb, b] = 1.0
    return full


def qft_gate_matrix(n=5):
    """QFT unitary by multiplying embedded gate matrices in circuit order
    (the standard QFT: H on the highest qubit first):
    for j in n-1..0: H(j), then cp(2 pi / 2**(j-k+1), control=j, target=k)
    for k < j; finally SWAP(i, n-1-i) for i < n/2. Gates are applied
    left-to-right, so the product pre-multiplies each gate."""
    u = np.eye(1 << n, dtype=complex)
    for j in range(n - 1, -1, -1):
        u = _h_matrix(n, j) @ u
        for k in range(j - 1, -1, -1):
            u = _cp_matrix(n, 2.0 * np.pi / 2.0 ** (j - k + 1), j, k) @ u
    for i in range(n // 2):
        u = _swap_matrix(n, i, n - 1 - i) @ u
    return u


def align_global_phase(a, b):
    """Return b multiplied by the scalar that best aligns it to a."""
    overlap = float(np.real(np.trace(a.conj().T @ b)))
    norm_b = float(np.real(np.trace(b.conj().T @ b)))
    if norm_b <= 0.0:
        return b
    phase = np.angle(complex(overlap))
    return b * np.exp(-1.0j * phase)


def matrix_max_diff(a, b):
    return float(np.max(np.abs(a - b)))


def is_unitary(u, tol=1e-9):
    return float(np.max(np.abs(u.conj().T @ u - np.eye(u.shape[0], dtype=complex)))) < tol


def basis_image(u, j, n=5):
    """u applied to basis state |j> (index j), as a numpy array."""
    e = np.zeros(1 << n, dtype=complex)
    e[j] = 1.0
    return u @ e


def main():
    n = 5
    direct = qft_matrix(n)
    gates = align_global_phase(direct, qft_gate_matrix(n))
    diff = matrix_max_diff(direct, gates)
    print("matrix max diff after alignment:", diff)
    assert diff < 1e-9
    assert is_unitary(direct) and is_unitary(qft_gate_matrix(n))
    n_states = 1 << n
    omega = np.exp(2.0j * np.pi / n_states)
    img = basis_image(qft_gate_matrix(n), 1, n)
    expected = np.array([omega**j / np.sqrt(n_states) for j in range(n_states)])
    assert matrix_max_diff(img, expected) < 1e-9
    # inverse round trip on |1>
    back = basis_image(direct.conj().T, 1, n)
    e1 = np.zeros(n_states, dtype=complex)
    e1[1] = 1.0
    assert matrix_max_diff(back, e1) < 1e-9
    print("QFT 5q matrix construction OK")


if __name__ == "__main__":
    main()
