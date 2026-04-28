# QAOA for MaxCut

## Evaluation helper signatures
For lightweight code-generation evals, implement these as module-level
functions, not class methods:

```python
import itertools


def _edge_weight(edge):
    if len(edge) == 2:
        u, v = edge
        return u, v, 1.0
    if len(edge) == 3:
        u, v, w = edge
        return u, v, float(w)
    raise ValueError("MaxCut edges must be (u, v) or (u, v, weight)")


def maxcut_cost(bitstring, edges):
    total = 0.0
    for edge in edges:
        u, v, w = _edge_weight(edge)
        if int(bitstring[u]) != int(bitstring[v]):
            total += w
    return int(total) if float(total).is_integer() else total


def qaoa_cost_landscape(n, edges):
    rows = []
    for bits in itertools.product([0, 1], repeat=n):
        bitstring = "".join(str(bit) for bit in bits)
        rows.append((bitstring, maxcut_cost(bitstring, edges)))
    return sorted(rows, key=lambda item: item[1], reverse=True)


def brute_force_maxcut(n, edges):
    return qaoa_cost_landscape(n, edges)[0]
```

For this helper interface, `qaoa_cost_landscape` is a classical exhaustive
landscape over bitstrings. Do not give it variational parameters, `depth`,
`gamma`, or `beta` arguments unless the tests explicitly ask for those.

## Concept
The Quantum Approximate Optimization Algorithm (QAOA) attacks
combinatorial optimization problems by alternating two parameterised
unitaries. For MaxCut on a graph G = (V, E) with edge weights w_uv:

- Cost Hamiltonian:  H_C = sum_{(u,v) in E} (w_uv / 2) * (I - Z_u Z_v)
- Mixer Hamiltonian: H_M = sum_v X_v

For depth p, parameters (gamma_1, ..., gamma_p, beta_1, ..., beta_p):

  |gamma, beta> = e^{-i beta_p H_M} e^{-i gamma_p H_C} ...
                  e^{-i beta_1 H_M} e^{-i gamma_1 H_C} |+>^n

## MaxCut cost function (classical bitstring evaluation)

```python
def _edge_weight(edge: tuple) -> tuple[int, int, float]:
    """Accept either unweighted (u, v) or weighted (u, v, w) edges."""
    if len(edge) == 2:
        u, v = edge
        return u, v, 1.0
    if len(edge) == 3:
        u, v, w = edge
        return u, v, float(w)
    raise ValueError("MaxCut edges must be (u, v) or (u, v, weight)")


def maxcut_cost(bitstring, edges: list[tuple]) -> float:
    total = 0.0
    for edge in edges:
        u, v, w = _edge_weight(edge)
        if int(bitstring[u]) != int(bitstring[v]):
            total += w
    return int(total) if float(total).is_integer() else total
```

Equivalently using +/-1 spins:

  cost = sum_{(u,v)} w_uv * (1 - s_u * s_v) / 2

## Reference Python (classical simulation of QAOA cost)

```python
import itertools

def qaoa_cost_landscape(n: int, edges: list[tuple]) -> list[tuple[str, float]]:
    rows = []
    for bits in itertools.product([0, 1], repeat=n):
        bitstring = "".join(str(bit) for bit in bits)
        rows.append((bitstring, maxcut_cost(bitstring, edges)))
    return sorted(rows, key=lambda item: item[1], reverse=True)


def brute_force_maxcut(n: int, edges: list[tuple]) -> tuple[str, float]:
    return qaoa_cost_landscape(n, edges)[0]
```

## Library snippets
Qiskit (high-level):
```python
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.algorithms import MinimumEigenOptimizer
```

PennyLane offers `qml.qaoa.maxcut` to build cost and mixer Hamiltonians
automatically.

## Common pitfalls
- Edge weights are *additive*; only count each edge once even if the
  graph is undirected.
- Evaluation tasks often use unweighted edge pairs `(u, v)` instead of
  weighted triples `(u, v, w)`. Treat missing weight as `1.0`.
- Keep snippets compatible with Python 3.9 evaluation environments; avoid
  `A | B` union annotations in generated candidate files.
- The quantum cost expectation <H_C> is shifted by `sum w / 2` from the
  classical cut value: <H_C>_psi = (sum w_uv) / 2 - sum w_uv/2 <Z_u Z_v>.
- For p=1, optimal (gamma, beta) for triangle-free graphs is roughly
  gamma = pi/8, beta = pi/8 (use grid search to confirm).
