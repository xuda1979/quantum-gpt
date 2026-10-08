# Quantum Fourier Transform (QFT)

## Concept
The QFT is the quantum analogue of the discrete Fourier transform on
2^n basis states. For a basis state |x>:

  QFT |x> = (1/sqrt(N)) * sum_{k=0}^{N-1} exp(2*pi*i * x*k / N) |k>

where N = 2^n. It is the workhorse subroutine for phase estimation,
Shor's algorithm, and many others.

## Phase pattern
Given input |x>, the QFT output amplitudes are equal-magnitude but with
phases `2*pi*x*k/N` at index k. The hallmark "QFT phase pattern" is
just this evenly spaced phase progression; any test that asks for the
phase angles of QFT|x> expects:

  phases[k] = (2 * pi * x * k / N) mod 2*pi

## Reference matrix
Element (j, k) of the QFT matrix is `exp(2*pi*i * j*k / N) / sqrt(N)`.

```python
import numpy as np

def qft_matrix(n: int) -> np.ndarray:
    N = 1 << n
    j, k = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    return np.exp(2j * np.pi * j * k / N) / np.sqrt(N)
```

## Reference circuit (n qubits)
For each qubit q (top to bottom):
1. Apply H on q.
2. For each subsequent qubit p > q, apply controlled-Rz with angle
   `2*pi / 2**(p - q + 1)` controlled on p, target q.
3. After all qubits processed, swap qubit i with qubit n-1-i for all i
   to fix bit ordering.

## Inverse QFT
QFT_inv = QFT_dagger. To invert: reverse the order of operations and
negate all rotation angles.

## Library snippets
Qiskit provides `QFT` and `QFT(num_qubits).inverse()` from
`qiskit.circuit.library`. Cirq has `cirq.QuantumFourierTransformGate`.

## Common pitfalls
- The trailing SWAPs are *required* if you care about the standard
  output ordering. Many tutorials omit them and silently work in
  reversed order.
- Phases must be reduced mod 2*pi for stable comparison.
