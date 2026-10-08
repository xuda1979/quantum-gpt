# Depolarizing channel and Kraus operators

## Concept
The single-qubit depolarizing channel with parameter p in [0, 1] mixes
the input state with the maximally mixed state I/2:

  E(rho) = (1 - p) * rho + p * I / 2

Equivalently in Pauli form:

  E(rho) = (1 - 3p/4) * rho + (p/4) * (X rho X + Y rho Y + Z rho Z)

so each non-identity Pauli error occurs with probability p/4.

## Kraus representation
Kraus operators (for the equivalent rewriting above):

```python
import numpy as np

def depolarizing_kraus(p: float) -> list[np.ndarray]:
    a = np.sqrt(1 - 3 * p / 4)
    b = np.sqrt(p / 4)
    I = np.eye(2)
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]])
    return [a * I, b * X, b * Y, b * Z]
```

These satisfy sum_i K_i^dagger K_i = I.

## Action on density matrix

```python
def apply_channel(kraus_ops, rho):
    out = np.zeros_like(rho, dtype=complex)
    for K in kraus_ops:
        out += K @ rho @ K.conj().T
    return out
```

## Multi-qubit generalisation
For n qubits, the depolarizing channel mixes with I / 2^n:

  E(rho) = (1 - p) rho + p * I / 2^n

The Kraus form has 4^n operators (one per n-qubit Pauli string).

## Common pitfalls
- The p in `(1-p) rho + p I/2` is *not* the same as the per-Pauli error
  probability p/4. Be explicit about which definition the problem uses.
- For p=1 the output is fully mixed (`I/d`), not zero.
- Numerical CPTP checks: ensure `sum K_i^dagger K_i ~= I` and that the
  output is Hermitian + positive semi-definite + has trace 1.
