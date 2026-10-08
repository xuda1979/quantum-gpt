# Trotter (Suzuki-Trotter) decomposition for Hamiltonian evolution

## Concept
For non-commuting H = A + B, the exponential `exp(-i H t)` is hard to
compute directly. The first-order Trotter formula approximates:

  exp(-i (A + B) t) ~= [exp(-i A t/n) exp(-i B t/n)]^n

with error O(t^2 / n) per step (commutator-dependent).

Second-order (symmetric) Trotter:

  S2(t) = exp(-i A t/2) exp(-i B t) exp(-i A t/2)

then `exp(-i H t) ~= S2(t/n)^n` with error O(t^3 / n^2).

## Higher-order
Suzuki recursion for order 2k:
  S_{2k}(t) = S_{2k-2}(s_k t)^2 S_{2k-2}((1 - 4 s_k) t) S_{2k-2}(s_k t)^2
with s_k = 1 / (4 - 4^{1/(2k-1)}).

## Reference numpy (1st-order Trotter for sum of Paulis)

```python
import numpy as np
from scipy.linalg import expm

def trotter_step(hamiltonian_terms: list[np.ndarray], dt: float) -> np.ndarray:
    U = np.eye(hamiltonian_terms[0].shape[0], dtype=complex)
    for term in hamiltonian_terms:
        U = expm(-1j * term * dt) @ U
    return U


def trotter_evolve(hamiltonian_terms, t: float, n_steps: int) -> np.ndarray:
    dt = t / n_steps
    U = trotter_step(hamiltonian_terms, dt)
    return np.linalg.matrix_power(U, n_steps)
```

For Pauli Hamiltonians H_j = c_j P_j on n qubits, each `exp(-i c_j P_j dt)`
becomes a single-qubit or controlled rotation; the Trotter step
translates directly into a quantum circuit.

## Library snippets
- Qiskit: `qiskit.synthesis.SuzukiTrotter` (and friends in
  `qiskit.synthesis.product_formula`).
- PennyLane: `qml.ApproxTimeEvolution(H, t, n)` performs Trotter by
  default.

## Common pitfalls
- Step size choice: small `dt` reduces Trotter error but increases
  circuit depth; balance with target precision.
- Order matters when terms anticommute; reorder for cancellation if
  possible.
- Don't conflate `dt` (per-step) with `t` (total evolution).
