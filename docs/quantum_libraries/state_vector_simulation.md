# State vector simulation in pure NumPy

## Representation
An n-qubit pure state is a complex vector of length 2^n. Index k
(0 <= k < 2^n) corresponds to the computational basis state |b_{n-1} ... b_0>
written in big-endian binary, e.g. for n=3:

  index 5 = 0b101 -> |1, 0, 1> -> qubit 0 in state |1>, qubit 2 in state |1>

(Some libraries reverse this; pick a convention and stick to it.)

## Applying single-qubit gates

```python
import numpy as np

def apply_single(state: np.ndarray, gate: np.ndarray, target: int, n: int) -> np.ndarray:
    state = state.reshape([2] * n)
    state = np.tensordot(gate, state, axes=([1], [n - 1 - target]))
    # Move new axis back into place
    state = np.moveaxis(state, 0, n - 1 - target)
    return state.reshape(-1)
```

## Applying CNOT (control, target)

```python
def apply_cnot(state: np.ndarray, control: int, target: int, n: int) -> np.ndarray:
    state = state.reshape([2] * n).copy()
    # Slice over control == 1 dimension and swap target axis
    idx = [slice(None)] * n
    idx[n - 1 - control] = 1
    sub = state[tuple(idx)]
    sub = np.swapaxes(sub, 0, n - 2 - target if target < control else n - 1 - target)
    state[tuple(idx)] = sub
    return state.reshape(-1)
```

(For clarity, a brute-force matrix-form `kron`-ed gate is often easier
in tests; performance matters only for large n.)

## Probabilities and measurement

```python
def measurement_probs(state: np.ndarray) -> np.ndarray:
    return np.abs(state) ** 2

def sample(state: np.ndarray, shots: int = 1024,
           rng: np.random.Generator | None = None) -> np.ndarray:
    rng = rng or np.random.default_rng(0)
    probs = measurement_probs(state)
    return rng.choice(len(state), size=shots, p=probs)
```

## Tensor products and gates

```python
def kron_gate(local_gate: np.ndarray, target: int, n: int) -> np.ndarray:
    full = np.array([[1.0]])
    for q in range(n):
        full = np.kron(full, local_gate if q == target else np.eye(2))
    return full
```

## Common pitfalls
- Endianness: decide once whether qubit 0 is the leading or trailing
  bit and stay consistent across gate matrices and measurement parsing.
- Float precision: amplitude norms drift if you ignore renormalisation
  after applying many gates. `state /= np.linalg.norm(state)` periodically.
- Use `np.complex128` consistently; mixing real and complex types causes
  silent precision loss.
