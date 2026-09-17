"""Repaired 2-qubit QFT implementation.

The hand-written original had three defects:
  1. wrong controlled-phase sign (cp(-pi/2) instead of cp(+pi/2)),
  2. the final bit-reversal SWAP was omitted,
  3. little-endian basis indices were confused with displayed bitstrings.

Convention (declared): statevector index j has binary bits (q1 q0), qubit 0
is the least significant bit; the QFT matrix is F[j, k] = i**(j*k)/sqrt(2)
with omega = i = exp(2 pi i / 4). The repaired circuit-style routine is
  H(q1); cp(pi/2, control=q1, target=q0); H(q0); SWAP(q0, q1).
An independent dense DFT reference is built from the formula directly.
"""

import numpy as np

S2 = np.sqrt(2.0)


def buggy_qft2_statevector(state):
    """The ORIGINAL buggy routine (kept for regression demonstration):
    wrong cp sign and no final swap."""
    s = np.asarray(state, dtype=complex).reshape(-1)
    s = s.reshape(2, 2)  # index bits (q1 q0)
    out = np.zeros_like(s)
    # H on q1
    out[0, :] = (s[0, :] + s[1, :]) / S2
    out[1, :] = (s[0, :] - s[1, :]) / S2
    s = out
    # cp(-pi/2, control=q1, target=q0) -- BUG: wrong sign
    s[1, 1] = s[1, 1] * np.exp(-1.0j * np.pi / 2.0)
    # H on q0
    out = np.zeros_like(s)
    out[:, 0] = (s[:, 0] + s[:, 1]) / S2
    out[:, 1] = (s[:, 0] - s[:, 1]) / S2
    s = out
    # BUG: final SWAP(q0, q1) omitted
    return s.reshape(-1)


def qft2_statevector(state):
    """Repaired circuit-style 2-qubit QFT:
    H(q1); cp(pi/2, control=q1, target=q0); H(q0); SWAP(q0, q1)."""
    s = np.asarray(state, dtype=complex).reshape(-1)
    s = s.reshape(2, 2)  # index bits (q1 q0)
    # H on q1
    out = np.zeros_like(s)
    out[0, :] = (s[0, :] + s[1, :]) / S2
    out[1, :] = (s[0, :] - s[1, :]) / S2
    s = out
    # cp(+pi/2, control=q1, target=q0)
    s[1, 1] = s[1, 1] * np.exp(1.0j * np.pi / 2.0)
    # H on q0
    out = np.zeros_like(s)
    out[:, 0] = (s[:, 0] + s[:, 1]) / S2
    out[:, 1] = (s[:, 0] - s[:, 1]) / S2
    s = out
    # final bit-reversal SWAP(q0, q1)
    return s.T.reshape(-1)


def iqft2_statevector(state):
    """Inverse 2-qubit QFT: SWAP(q0,q1); H(q0); cp(-pi/2, c=q1, t=q0);
    H(q1)."""
    s = np.asarray(state, dtype=complex).reshape(-1)
    s = s.reshape(2, 2).T  # SWAP(q0, q1)
    out = np.zeros_like(s)
    out[:, 0] = (s[:, 0] + s[:, 1]) / S2
    out[:, 1] = (s[:, 0] - s[:, 1]) / S2
    s = out
    s[1, 1] = s[1, 1] * np.exp(-1.0j * np.pi / 2.0)
    out = np.zeros_like(s)
    out[0, :] = (s[0, :] + s[1, :]) / S2
    out[1, :] = (s[0, :] - s[1, :]) / S2
    return out.reshape(-1)


def dft2_matrix():
    """Independent dense DFT reference: F[j, k] = i**(j*k)/sqrt(N) with
    N = 4 (2 qubits), i.e. i**(j*k)/2."""
    f = np.zeros((4, 4), dtype=complex)
    for j in range(4):
        for k in range(4):
            f[j, k] = (1.0j ** (j * k)) / 2.0
    return f


def qft2_matrix():
    """Circuit-style QFT as a 4x4 matrix (columns = basis inputs)."""
    m = np.zeros((4, 4), dtype=complex)
    for k in range(4):
        e = np.zeros(4, dtype=complex)
        e[k] = 1.0
        m[:, k] = qft2_statevector(e)
    return m


def align_global_phase(a, b):
    """b scaled by the scalar best aligning it to a."""
    phase = np.angle(np.vdot(a.reshape(-1), b.reshape(-1)))
    return b * np.exp(-1.0j * phase)


def forward_inverse_roundtrip(state):
    """iqft(qft(state)) == state up to global phase."""
    s = np.asarray(state, dtype=complex).reshape(-1)
    back = iqft2_statevector(qft2_statevector(s))
    scale = np.vdot(s, back) / np.vdot(back, back)
    return back * scale, s


def regression_checks():
    """Regression test: would fail if the phase sign is wrong or the final
    SWAP is omitted. Returns the observed buggy-vs-DFT deviation."""
    f = dft2_matrix()
    m = qft2_matrix()
    diff_repaired = float(np.max(np.abs(m - f)))
    assert diff_repaired < 1e-9, f"repaired QFT deviates from DFT: {diff_repaired}"
    # demonstrate the buggy routine is actually caught
    m_buggy = np.zeros((4, 4), dtype=complex)
    for k in range(4):
        e = np.zeros(4, dtype=complex)
        e[k] = 1.0
        m_buggy[:, k] = buggy_qft2_statevector(e)
    diff_buggy = float(np.max(np.abs(m_buggy - f)))
    assert diff_buggy > 0.1, "buggy routine unexpectedly matches the DFT"
    return diff_buggy


def main():
    f = dft2_matrix()
    m = qft2_matrix()
    print("repaired max dev from DFT:", float(np.max(np.abs(m - f))))
    print("regression buggy deviation:", regression_checks())
    assert float(np.max(np.abs(m - f))) < 1e-9
    assert float(np.max(np.abs(m.conj().T @ m - np.eye(4, dtype=complex)))) < 1e-9
    for k in range(4):
        e = np.zeros(4, dtype=complex)
        e[k] = 1.0
        back, orig = forward_inverse_roundtrip(e)
        assert float(np.max(np.abs(back - orig))) < 1e-9, f"round trip failed for |{k}>"
    print("QFT repair OK")


if __name__ == "__main__":
    main()
