# QAOA for MaxCut

## Concept
The Quantum Approximate Optimization Algorithm (QAOA) attacks
combinatorial optimization problems by alternating two parameterised
unitaries. For MaxCut on a graph G = (V, E) with edge weights w_uv:

- Cost Hamiltonian:  H_C = sum_{(u,v) in E} (w_uv / 2) * (I - Z_u Z_v)
- Mixer Hamiltonian: H_M = sum_v X_v

For depth p, parameters (gamma_1, ..., gamma_p, beta_1, ..., beta_p):

  |gamma, beta> = e^{-i beta_p H_M} e^{-i gamma_p H_C} ...
                  e^{-i beta_1 H_M} e^{-i gamma_1 H_C} |+>^n

## Classical bitstring cost evaluation
The classical MaxCut cost of a bitstring assignment is

  cost(x) = sum_{(u,v) in E} w_uv * [x_u != x_v]

Equivalently using +/-1 spins:

  cost = sum_{(u,v)} w_uv * (1 - s_u * s_v) / 2

For brute-force enumeration, exhaustive ranking, and bitstring-cost helper
implementations, see `maxcut_classical_helpers.md` in this same directory.

## Library snippets
Qiskit 2.x ecosystem. The latest Qiskit package target is qiskit 2.4.2
(Python >=3.10). Use the 2.4.x documentation/API as the target for code
generation and import repair.

```python
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_algorithms.utils import algorithm_globals
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.algorithms import MinimumEigenOptimizer

algorithm_globals.random_seed = 42

# edges: any list of (u, v) unweighted or (u, v, weight) weighted tuples
edges = [(0, 1), (1, 2), (2, 0)]
maxcut = Maxcut(edges)
quadratic_program = maxcut.to_quadratic_program()

sampler = StatevectorSampler(seed=42)
optimizer = COBYLA(maxiter=100)
qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)

result = MinimumEigenOptimizer(qaoa).solve(quadratic_program)
cut_value = result.fval
nodes_set0, nodes_set1 = maxcut.interpret(result)
print(result.x, nodes_set0, nodes_set1, cut_value)
```

For complete runnable answer snippets, read the solved assignment from
`result.x` and cast it to Python integers before indexing or printing. QAOA
depth is set with `reps`; do not pass circuit resource-count keywords to QAOA.

```python
def solve_qaoa_maxcut(edges):
  maxcut = Maxcut(edges)
  problem = maxcut.to_quadratic_program()
  sampler = StatevectorSampler(seed=42)
  qaoa = QAOA(sampler=sampler, optimizer=COBYLA(maxiter=100), reps=2)
  result = MinimumEigenOptimizer(qaoa).solve(problem)

  solution = [int(value) for value in result.x]
  set0, set1 = maxcut.interpret(result)
  cut_value = sum(1 for u, v in edges if solution[u] != solution[v])
  return solution, set0, set1, cut_value
```

If repairing an import error, do not use this invalid form:

```python
from qiskit_optimization.algorithms import QAOA
```

`qiskit_optimization.algorithms` exposes optimization wrappers such as
`MinimumEigenOptimizer`; QAOA belongs in `qiskit_algorithms` or in
`qiskit_optimization.minimum_eigensolvers`:

```python
from qiskit_algorithms.minimum_eigensolvers import QAOA
# or: from qiskit_optimization.minimum_eigensolvers import QAOA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
```

For manually building a Qiskit Optimization Max-Cut problem, do not call
nonexistent methods such as `linear_term()` or `quadratic_term()`. Use
`QuadraticProgram.maximize(linear=..., quadratic=...)`. The Max-Cut objective is
not a minimization; for each weighted edge `(u, v, w)`, maximize
`w*x_u + w*x_v - 2*w*x_u*x_v`.

```python
from qiskit_optimization import QuadraticProgram

edges = [(0, 1, 1.0), (1, 2, 1.0), (2, 0, 1.0)]
problem = QuadraticProgram("manual_maxcut")
for node in range(3):
    problem.binary_var(name=f"x{node}")

linear = {f"x{node}": 0.0 for node in range(3)}
quadratic = {}
for u, v, weight in edges:
    linear[f"x{u}"] += weight
    linear[f"x{v}"] += weight
    pair = (f"x{u}", f"x{v}")
    quadratic[pair] = quadratic.get(pair, 0.0) - 2.0 * weight

problem.maximize(linear=linear, quadratic=quadratic)
```

For weighted or matrix-style graph construction, build a symmetric adjacency
matrix before creating `Maxcut`:

```python
import numpy as np

weighted_edges = [(0, 1, 2.0), (1, 2, 1.0), (2, 0, 3.0)]
adjacency = np.zeros((3, 3))
for u, v, weight in weighted_edges:
    adjacency[u, v] = weight
    adjacency[v, u] = weight

maxcut = Maxcut(adjacency)
```

PennyLane offers `qml.qaoa.maxcut` to build cost and mixer Hamiltonians
automatically.

## Key class signatures (reference)

Actual constructor/method signatures in the current qiskit-optimization /
qiskit-algorithms release:

| Class / method | Signature | Notes |
| --- | --- | --- |
| `Maxcut(edge_list_or_matrix)` | `__init__(self, graph: nx.Graph \| np.ndarray \| list)` | positional-only `graph` parameter; accepts an unweighted edge list or a symmetric adjacency matrix |
| `Maxcut.to_quadratic_program` | `(self) -> QuadraticProgram` | instance method, no arguments; call as `Maxcut(edges).to_quadratic_program()`, not `Maxcut.to_quadratic_program(edges)`; returns one `QuadraticProgram`, not a tuple |
| `Maxcut.interpret` | `(self, result) -> tuple[list[int], list[int]]` | returns the two partitions directly from a solved result |
| `QAOA.__init__` | `(self, sampler, optimizer, *, reps=1, initial_state=None, mixer=None, initial_point=None, aggregation=None, callback=None, transpiler=None, transpiler_options=None)` | no qubit-count or ancilla-count argument; the qubit count is inferred from the cost operator; set QAOA depth with `reps` |
| `MinimumEigenOptimizer.__init__` | `(self, min_eigen_solver, penalty=None, converters=None)` | keyword names are `min_eigen_solver` and `converters` (plural); default `converters` is `QuadraticProgramToQubo`, which already handles sense conversion — a `MAXIMIZE`-sense `QuadraticProgram` can be solved directly without manually negating coefficients |
| `qiskit_optimization.converters` module | exposes `InequalityToEquality`, `IntegerToBinary`, `LinearEqualityToPenalty`, `LinearInequalityToPenalty`, `MaximizeToMinimize`, `MinimizeToMaximize`, `QuadraticProgramToQubo` | no `MinimumToSum` class exists |

`MinimumEigenOptimizer.solve(...)` returns an `OptimizationResult`. Use
`result.x` for the solution vector and `result.fval` for the objective value;
do not invent alternate solution-vector attribute names.

Python dicts do not support unary `-`; negating a dict directly (`-coeffs`)
raises `TypeError: bad operand type for unary -: 'dict'`. Negate the values
via a dict comprehension instead: `{k: -v for k, v in coeffs.items()}`.

## Common pitfalls
- Edge weights are *additive*; only count each edge once even if the
  graph is undirected.
- Evaluation tasks often use unweighted edge pairs `(u, v)` instead of
  weighted triples `(u, v, w)`. Treat missing weight as `1.0`.
- In current Qiskit, import optimizers such as `COBYLA` from
    `qiskit_algorithms.optimizers`, not directly from `qiskit_algorithms`.
- Importing `QAOA` from `qiskit_optimization.algorithms` raises ImportError;
    import `QAOA` from `qiskit_algorithms.minimum_eigensolvers` or
    `qiskit_optimization.minimum_eigensolvers` instead.
- Passing ancilla-count keywords to `QAOA` raises `TypeError`; ancilla counts
  are circuit properties, not QAOA constructor arguments. Use
  `QAOA(..., reps=p)` for p-layer QAOA.
- `MinimumEigenOptimizer` results use `result.x` for the solution vector.
- `QuadraticProgram` has no `linear_term()` or `quadratic_term()` objective
    builder methods; pass dictionaries to `maximize` or `minimize`.
- Standard Max-Cut should use `maximize`, not `minimize`, with edge term
    `x_u + x_v - 2*x_u*x_v` for unit weights.
- `Maxcut(edges)` accepts an unweighted edge list in current
    qiskit-optimization, but an adjacency matrix is clearer for weighted graphs.
- Complement bitstrings represent the same MaxCut partition on any graph:
    flipping every bit swaps which side each set label refers to, but the
    cut value (number of crossing edges) is unchanged.
- Keep snippets compatible with Python 3.9 evaluation environments; avoid
  `A | B` union annotations in generated candidate files.
- The quantum cost expectation <H_C> is shifted by `sum w / 2` from the
  classical cut value: <H_C>_psi = (sum w_uv) / 2 - sum w_uv/2 <Z_u Z_v>.
- For p=1, optimal (gamma, beta) for triangle-free graphs is roughly
  gamma = pi/8, beta = pi/8 (use grid search to confirm).
