# Phase register round-trip patterns

## Concept
A "phase register" is an n-qubit register whose computational basis
states encode integer phases as kicked-back angles. Many subroutines
(QPE, amplitude estimation, Shor's order finding) load phases into
this register, perform inverse QFT, and then read the integer index.

## Loading a phase
For a desired phase phi in [0, 1):
1. Initialise the register to |+>^n via H.
2. For each qubit q (q = 0, ..., n-1), apply Rz(2*pi * phi * 2^q) on q.

After step 2, the register is in state
  (1/sqrt(2^n)) sum_k exp(2*pi*i*phi*k) |k>

## Reading back via inverse QFT
Apply QFT^{-1}, then measure. The most-likely outcome y satisfies
y/2^n ~= phi (rounded to n bits of precision).

## Round-trip simulation

```python
import numpy as np

def encode_phase_register(phi: float, n: int) -> np.ndarray:
    state = np.full(1 << n, 1.0 / np.sqrt(1 << n), dtype=complex)
    for k in range(1 << n):
        state[k] *= np.exp(2j * np.pi * phi * k)
    return state


def decode_phase_register(state: np.ndarray) -> float:
    n = (len(state)).bit_length() - 1
    # Inverse DFT (matrix-form for clarity)
    N = 1 << n
    j, k = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    iqft = np.exp(-2j * np.pi * j * k / N) / np.sqrt(N)
    out = iqft @ state
    y = int(np.argmax(np.abs(out) ** 2))
    return y / N
```

## Common pitfalls
- Off-by-one in the rotation angle: use `2*pi * phi * 2^q` for qubit q,
  not `2*pi * phi / 2^q` (the latter is the controlled-rotation angle
  in QFT, *not* the phase load).
- Decoded phase is only accurate to ~ 2^-n; use `n` large enough.
- For non-integer `phi * 2^n`, the inverse QFT smears probability
  across multiple bins; argmax gives the closest representable bin.
