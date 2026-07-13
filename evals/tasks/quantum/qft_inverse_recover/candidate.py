import cmath
import math


def inverse_qft_amplitudes(state: list[complex]) -> list[complex]:
    """Apply the inverse Quantum Fourier Transform to an n-qubit state.

    The QFT on N = 2^n dimensions is
        QFT|j> = (1/sqrt(N)) sum_{k=0}^{N-1} exp(2*pi*i*j*k/N) |k>
    The inverse QFT is the conjugate transpose:
        QFT^dagger|k> = (1/sqrt(N)) sum_{j=0}^{N-1} exp(-2*pi*i*j*k/N) |j>

    Returns the resulting complex amplitude vector of the same length.
    """
    N = len(state)
    if N <= 0 or (N & (N - 1)) != 0:
        raise ValueError("state length must be a positive power of 2")
    out = [0j] * N
    norm = 1.0 / math.sqrt(N)
    for k in range(N):
        acc = 0j
        for j in range(N):
            acc += state[j] * cmath.exp(-2j * cmath.pi * j * k / N)
        out[k] = acc * norm
    return out


def qft_amplitudes(state: list[complex]) -> list[complex]:
    """Apply the forward Quantum Fourier Transform."""
    N = len(state)
    if N <= 0 or (N & (N - 1)) != 0:
        raise ValueError("state length must be a positive power of 2")
    out = [0j] * N
    norm = 1.0 / math.sqrt(N)
    for j in range(N):
        acc = 0j
        for k in range(N):
            acc += state[k] * cmath.exp(2j * cmath.pi * j * k / N)
        out[j] = acc * norm
    return out
