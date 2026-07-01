# Grover search (oracle + diffusion)

## Concept
Grover's algorithm finds a marked element in an unstructured database of
N items in O(sqrt(N)) oracle calls vs O(N) classical. With M marked
items the optimal number of iterations is approximately
`(pi/4) * sqrt(N / M)`.

## Building blocks
- **Oracle U_f**: flips the sign of marked basis states:
    U_f |x> = -|x> if x is marked else |x>
- **Diffusion operator D**: reflection about the uniform superposition
    D = 2 |s><s| - I, where |s> = (1/sqrt(N)) sum_x |x>
  Equivalently:
    D = H^n (2 |0><0| - I) H^n

## Reference numpy

```python
import numpy as np

def grover_search_numpy(N: int, marked_indices, iters=None) -> np.ndarray:
    state = np.full(N, 1.0 / np.sqrt(N))
    if iters is None:
        M = max(len(marked_indices), 1)
        iters = max(1, int(round((np.pi / 4) * np.sqrt(N / M))))
    for _ in range(iters):
        # Oracle: flip sign of marked indices
        for m in marked_indices:
            state[m] *= -1
        # Diffusion: reflect about mean
        mean = state.mean()
        state = 2 * mean - state
    return state
```

## Evaluation-facing single-file API

For small pure-Python eval tasks, prefer this public interface. It keeps the
algorithm contract explicit and avoids confusing number-of-qubits with a list of
qubit objects.

```python
import math


def uniform_superposition(n_qubits: int) -> list[float]:
    n_states = 2 ** n_qubits
    return [1.0 / math.sqrt(n_states)] * n_states


def oracle(state: list[float], marked: int) -> list[float]:
    result = list(state)
    result[marked] = -result[marked]
    return result


def diffusion(state: list[float]) -> list[float]:
    mean = sum(state) / len(state)
    return [2 * mean - amplitude for amplitude in state]


def grover_search(n_qubits: int, marked: int, iterations: int) -> list[float]:
    state = uniform_superposition(n_qubits)
    for _ in range(iterations):
        state = diffusion(oracle(state, marked))
    return state
```

Use `n_qubits` only to compute the Hilbert-space size `2 ** n_qubits`.
The `marked` argument is a single basis-state index such as `3` for `|11>`.
Do not call `len(n_qubits)` and do not treat `marked` as a list unless the task
explicitly asks for multiple marked states.

Keep examples Python 3.9 compatible in this repository. Avoid PEP 604 union
annotations such as `int | None`; use no union annotation or import
`Optional` from `typing` instead. The local eval runner imports candidates with
Python 3.9.

The probability of measuring a marked index after k iterations on N=2^n
with M marked is
  sin((2k+1) * theta)^2  where theta = arcsin(sqrt(M/N))

## Library snippets
Qiskit: `qiskit.circuit.library.GroverOperator(oracle)` plus
`qiskit_algorithms.AmplificationProblem` and `Grover`.

Cirq: write the oracle as a circuit and reuse Z (or controlled-Z) for
phase flips.

## Common pitfalls
- Over-rotating: more iterations is *not* better. Use the analytical
  formula for the optimum.
- The oracle is a *phase* oracle (sign flip). A simple bit-flip oracle
  must be wrapped with an extra ancilla qubit (`|0> - |1>` trick).
- Diffusion (`D = 2|s><s| - I`) on a raw amplitude array reduces to a single
  elementwise step: take the mean of the *current* state vector, then
  compute `2 * mean - state`. Do not insert an extra transform (FFT, QFT,
  or an explicit Hadamard-matrix multiply) before computing that mean —
  applying one changes which vector the mean is taken over, so the
  reflection is computed in the wrong basis. The symptom is subtle:
  the code still runs and returns a normalized-looking vector, but the
  marked amplitude never grows across iterations and stays close to the
  starting `1/sqrt(N)` (or drops to exactly 0 for some marked indices),
  instead of climbing toward the expected `sin((2k+1) theta)^2` value.
- Diffusion can be implemented as H^n X^n CZ_{multi} X^n H^n with the
  multi-controlled Z acting as the "reflect about |0...0>" step.
