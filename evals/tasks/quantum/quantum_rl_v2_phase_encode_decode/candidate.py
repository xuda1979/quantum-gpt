"""Phase encoding and decoding with an explicitly constructed inverse QFT.

encode_phase(phi, n) = (1/sqrt(N)) sum_k exp(2 pi i k phi) |k>, k = 0..N-1
with N = 2^n. Applying the inverse QFT (explicitly constructed as the
dense inverse-DFT matrix, then checked unitarity) concentrates the
probability on the grid point nearest to phi; decode_phase picks the
maximum-likelihood grid phase k/2^n and reports the circular absolute
error. The exactly representable case phi = 0.25 (n=10) decodes to exactly
0.25 via executable assertions."""

import math

import numpy as np


def encode_phase(phi, n):
    """Normalized phase-encoded state (1/sqrt(N)) sum_k e^{2 pi i k phi} |k>."""
    n_states = 1 << n
    amps = np.zeros(n_states, dtype=complex)
    for k in range(n_states):
        amps[k] = np.exp(2j * np.pi * k * phi)
    return amps / np.sqrt(n_states)


def inverse_qft(state):
    """Explicitly constructed inverse QFT applied to a state vector.

    The inverse-QFT matrix M[j, k] = (1/sqrt(N)) e^{-2 pi i j k / N} is
    built directly and its unitarity is verified before application.
    """
    n = len(state)
    size = int(round(math.log2(n)))
    assert 1 << size == n, "state length must be a power of two"
    mat = np.zeros((n, n), dtype=complex)
    for j in range(n):
        for k in range(n):
            mat[j, k] = np.exp(-2j * np.pi * j * k / n) / np.sqrt(n)
    if not np.allclose(mat.conj().T @ mat, np.eye(n), atol=1e-9):
        raise AssertionError("inverse QFT matrix is not unitary")
    return mat @ np.asarray(state, dtype=complex)


def probabilities(state):
    """|amplitude|^2 per basis state; sums to one for normalized input."""
    return [abs(a) ** 2 for a in np.asarray(state, dtype=complex)]


def decode_phase(probs, n):
    """Maximum-likelihood grid phase: argmax_k p(k) -> k / 2^n."""
    idx = int(np.argmax(probs))
    return idx / float(1 << n)


def circular_error(est, target):
    """Circular absolute error between two phases in [0, 1)."""
    diff = abs((est - target) % 1.0)
    return min(diff, 1.0 - diff)


def nearest_grid_point(phi, n):
    """Nearest k/2^n grid point to phi (ties round to the larger k)."""
    return round(phi * (1 << n)) / float(1 << n)


def main():
    phi = 0.9
    n = 10
    state = encode_phase(phi, n)
    probs = probabilities(state)
    assert abs(sum(probs) - 1.0) < 1e-12, "probabilities do not normalize"
    decoded = inverse_qft(state)
    dprobs = probabilities(decoded)
    assert abs(sum(dprobs) - 1.0) < 1e-9, "decoded probabilities do not normalize"
    est = decode_phase(dprobs, n)
    err = circular_error(est, phi)
    nearest = nearest_grid_point(phi, n)
    assert err <= 1.0 / (1 << n) + 1e-12, f"circular error {err} too large"
    assert abs(err - circular_error(nearest, phi)) < 1e-9

    # exactly representable case: phi = 0.25 decodes exactly
    state25 = encode_phase(0.25, n)
    d25 = inverse_qft(state25)
    p25 = probabilities(d25)
    est25 = decode_phase(p25, n)
    assert est25 == 0.25, f"representable phase decoded as {est25}"
    assert circular_error(est25, 0.25) < 1e-12

    print("phi =", phi)
    print("nearest grid point =", nearest)
    print("decoded =", est)
    print("circular error =", err)
    print("phi=0.25 decoded exactly =", est25)


if __name__ == "__main__":
    main()
