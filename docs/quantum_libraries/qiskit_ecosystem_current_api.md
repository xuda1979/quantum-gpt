# Qiskit ecosystem current API

Use this page for repair tasks involving current Qiskit core plus the common
ecosystem packages qiskit-aer, qiskit-algorithms, and qiskit-optimization.
Latest Qiskit package target: qiskit 2.4.2 from PyPI, released 2026-06-13,
with Python >=3.10 required. Use the 2.4.x documentation/API as the target for
code generation and import repair.

## Install surface

```bash
pip install qiskit qiskit-aer qiskit-algorithms qiskit-optimization
```

## Import surface

```python
from qiskit import QuantumCircuit, transpile
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector, Operator
from qiskit_aer import AerSimulator
from qiskit_algorithms.minimum_eigensolvers import QAOA, VQE
from qiskit_algorithms.optimizers import COBYLA, SPSA
from qiskit_algorithms.utils import algorithm_globals
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_optimization import QuadraticProgram
```

Do not import optimizers like `COBYLA` or `SPSA` directly from
`qiskit_algorithms`; they are in `qiskit_algorithms.optimizers`.

Do not import `QAOA` from `qiskit_optimization.algorithms`; that module contains
optimization wrappers such as `MinimumEigenOptimizer`, not QAOA itself. If code
raises `ImportError: cannot import name 'QAOA' from 'qiskit_optimization.algorithms'`,
replace the import with one of these valid forms:

```python
from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
```

or, when following qiskit-optimization's minimum-eigensolver wrappers:

```python
from qiskit_optimization.minimum_eigensolvers import QAOA
from qiskit_optimization.optimizers import COBYLA
from qiskit_optimization.algorithms import MinimumEigenOptimizer
```

## QAOA MaxCut repair pattern

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
nodes_set0, nodes_set1 = maxcut.interpret(result)
print(result.x, nodes_set0, nodes_set1, result.fval)
```

For weighted MaxCut inputs, prefer a symmetric adjacency matrix:

```python
import numpy as np

weighted_edges = [(0, 1, 2.0), (1, 2, 1.0), (2, 0, 3.0)]
adjacency = np.zeros((3, 3))
for u, v, weight in weighted_edges:
    adjacency[u, v] = weight
    adjacency[v, u] = weight

maxcut = Maxcut(adjacency)
```

## QuadraticProgram objective API

Current `QuadraticProgram` does not have `linear_term()` or `quadratic_term()`
methods for incrementally adding objective terms. Build the full objective with
`minimize(...)` or `maximize(...)` and pass dictionaries for linear and quadratic
coefficients.

For a manual Max-Cut quadratic program, maximize the cut expression. For each
edge `(u, v)` with weight `w`, the contribution is `w*x_u + w*x_v - 2*w*x_u*x_v`.

```python
from qiskit_optimization import QuadraticProgram

edges = [(0, 1, 1.0), (1, 2, 1.0)]
problem = QuadraticProgram("maxcut")
for node in range(3):
  problem.binary_var(name=f"x{node}")

linear = {f"x{node}": 0.0 for node in range(3)}
quadratic = {}
for u, v, weight in edges:
  linear[f"x{u}"] += weight
  linear[f"x{v}"] += weight
  quadratic[(f"x{u}", f"x{v}")] = quadratic.get((f"x{u}", f"x{v}"), 0.0) - 2.0 * weight

problem.maximize(linear=linear, quadratic=quadratic)
```

Do not use `problem.minimize(...)` for the standard Max-Cut objective above; it
will prefer the zero-cut assignment instead of the maximum cut.

## Primitive notes

`StatevectorSampler` is a statevector-based implementation of the sampler
primitive. Instantiate it as `StatevectorSampler(seed=42)` for deterministic
algorithm tests, then pass it into classes such as `QAOA`.

## Key class signatures (reference)

These are the actual constructor/method signatures in the current
qiskit-optimization / qiskit-algorithms release. Consult this table before
guessing keyword argument names or return shapes.

| Class / method | Signature | Notes |
| --- | --- | --- |
| `Maxcut(edge_list_or_matrix)` | `__init__(self, graph: nx.Graph \| np.ndarray \| list)` | positional-only `graph` parameter; accepts an unweighted edge list or a symmetric adjacency matrix |
| `Maxcut.to_quadratic_program` | `(self) -> QuadraticProgram` | instance method, no arguments; call as `Maxcut(edges).to_quadratic_program()`, not `Maxcut.to_quadratic_program(edges)`; returns one `QuadraticProgram`, not a tuple |
| `Maxcut.interpret` | `(self, result) -> tuple[list[int], list[int]]` | returns the two partitions directly from a solved result |
| `QAOA.__init__` | `(self, sampler, optimizer, *, reps=1, initial_state=None, mixer=None, initial_point=None, aggregation=None, callback=None, transpiler=None, transpiler_options=None)` | no `num_qubits` argument; the qubit count is inferred from the cost operator |
| `MinimumEigenOptimizer.__init__` | `(self, min_eigen_solver, penalty=None, converters=None)` | keyword names are `min_eigen_solver` and `converters` (plural); default `converters` is `QuadraticProgramToQubo`, which already handles sense conversion — a `MAXIMIZE`-sense `QuadraticProgram` can be solved directly without manually negating coefficients |
| `qiskit_optimization.converters` module | exposes `InequalityToEquality`, `IntegerToBinary`, `LinearEqualityToPenalty`, `LinearInequalityToPenalty`, `MaximizeToMinimize`, `MinimizeToMaximize`, `QuadraticProgramToQubo` | no `MinimumToSum` class exists |

```python
qaoa = QAOA(sampler=StatevectorSampler(seed=42), optimizer=COBYLA(), reps=2)
meo = MinimumEigenOptimizer(qaoa)  # or MinimumEigenOptimizer(qaoa, converters=QuadraticProgramToQubo())
```

Python dicts do not support unary `-`; negating a dict directly (`-coeffs`)
raises `TypeError: bad operand type for unary -: 'dict'`. Negate the values
via a dict comprehension instead: `{k: -v for k, v in coeffs.items()}`.

## Common pitfalls

- `from qiskit_algorithms import QAOA, COBYLA` is stale; split the imports and
  prefer `from qiskit_algorithms.minimum_eigensolvers import QAOA`.
- `from qiskit_optimization.algorithms import QAOA` is invalid; use
  `qiskit_algorithms.minimum_eigensolvers.QAOA` or
  `qiskit_optimization.minimum_eigensolvers.QAOA`.
- `QuadraticProgram.linear_term()` and `QuadraticProgram.quadratic_term()` are
  not current APIs; use `maximize(linear=..., quadratic=...)` or
  `minimize(linear=..., quadratic=...)`.
- Max-Cut is a maximization objective; for each edge use
  `x_u + x_v - 2*x_u*x_v` and call `maximize`.
- `Maxcut(edges)` works for unweighted edge pairs; use an adjacency matrix for
  weights or when input shape is ambiguous.
- MaxCut has complement symmetry on any graph: flipping every bit in a
  solution bitstring swaps which set label each side gets, but the cut value
  (number of crossing edges) is unchanged.
- Qiskit on Python 3.9 is deprecated in the 2.x series; prefer Python 3.10+
  for new environments.