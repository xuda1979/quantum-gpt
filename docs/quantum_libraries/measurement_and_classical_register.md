# Measurement and classical registers

## Born rule
For a state |psi> with amplitudes a_k, measuring in the computational
basis yields outcome k with probability |a_k|^2. Sum of probabilities
must be 1; if not, normalise:

  state /= np.linalg.norm(state)

## Sampling

```python
import numpy as np

def sample_outcomes(state: np.ndarray, shots: int = 1024,
                    rng: np.random.Generator | None = None) -> dict[int, int]:
    rng = rng or np.random.default_rng(0)
    probs = np.abs(state) ** 2
    samples = rng.choice(len(state), size=shots, p=probs)
    counts: dict[int, int] = {}
    for s in samples:
        counts[int(s)] = counts.get(int(s), 0) + 1
    return counts
```

## Measuring single qubits and partial collapse
After measuring qubit q and observing outcome b in {0, 1}:
- The post-measurement state is the projection P_b |psi> renormalised:
  |psi'> = P_b |psi> / sqrt(p_b)
- Other qubits' amplitudes are conditioned on the observed b.

```python
def measure_qubit(state: np.ndarray, q: int, n: int, b: int) -> np.ndarray:
    state = state.reshape([2] * n)
    idx = [slice(None)] * n
    idx[n - 1 - q] = b
    sub = state[tuple(idx)]
    norm = np.linalg.norm(sub)
    if norm == 0:
        raise ValueError("Outcome has zero probability")
    full = np.zeros_like(state)
    full[tuple(idx)] = sub / norm
    return full.reshape(-1)
```

## Bitstring conversion

```python
def index_to_bits(k: int, n: int, big_endian: bool = True) -> list[int]:
    bits = [(k >> i) & 1 for i in range(n)]
    return list(reversed(bits)) if big_endian else bits

def bits_to_index(bits: list[int], big_endian: bool = True) -> int:
    if big_endian:
        bits = list(reversed(bits))
    return sum(b << i for i, b in enumerate(bits))
```

## Common pitfalls
- Treat `shots=0` (no sampling) and `shots>0` (sampled counts) as
  different return types.
- Always normalise probabilities before passing to `numpy.random.choice`
  to avoid `ValueError: probabilities do not sum to 1` on float drift.
- For deterministic tests, seed the RNG explicitly with
  `np.random.default_rng(seed)`.
