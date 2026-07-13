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

## Code-generation priority

Task-specific templates outrank the broad reference imports below. For QAOA
Max-Cut answers, copy the minimal import block from `qaoa_maxcut.md` or use this
small set only:

```python
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.algorithms import MinimumEigenOptimizer
```

The general import surface is reference only, not an answer template. Do not
copy every line from it into generated code; include only symbols used by the
snippet.

## General import surface (reference only)

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

For QAOA Max-Cut snippets, keep the import block minimal and import each symbol once. Do not add generic framework classes such as `OptimizationAlgorithm`,
unused `QuantumCircuit`, unused direct `QuadraticProgram` imports, duplicate
aliases of already imported symbols, or nonexistent root symbols such as
`CategoricalVariable` unless the snippet actually uses them.

For the standard Max-Cut application path, do not import anything from
`qiskit_optimization.converters`. `MinimumEigenOptimizer(qaoa).solve(problem)`
already uses the default `QuadraticProgramToQubo` conversion internally. Do not
add placeholder, identity, or sense-converter imports just because Max-Cut is a
maximization problem.

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

When formatting a complete answer, convert the optimization result explicitly:

```python
solution = [int(value) for value in result.x]
set0, set1 = maxcut.interpret(result)
cut_value = sum(1 for u, v in edges if solution[u] != solution[v])
```

`MinimumEigenOptimizer.solve(...)` returns an `OptimizationResult` with `x` and
`fval`. `result.x` is an ordered array-like solution, not a dictionary; do not
call `.items()` on it. Do not invent alternate solution-vector attribute names. Do not pass
circuit resource-count keywords to `QAOA`; set QAOA depth with `reps`.
Read the Max-Cut objective value directly from `result.fval`; do not negate it.
`MinimumEigenOptimizer` maps the internal minimization result back to the
original `QuadraticProgram` objective value.
For `Maxcut(...).to_quadratic_program()`, pass the returned problem directly to
`MinimumEigenOptimizer`; its default converters handle maximization sense
conversion.
Do not add any `qiskit_optimization.converters` import for standard Max-Cut
QAOA code, including `Model2QUBO` or identity/sense-converter names. Fake or
unnecessary converter names are the most common cause of import failures in this
pattern.
Do not import or chain `Model2QUBO`, identity converters, or `Linear2Quadratic`;
those are not current Qiskit Optimization converter classes for this pattern.

Construct `Maxcut` with one graph argument only. Do not pass a separate node
count as a second positional argument; if you know the number of vertices, use
it only to build the graph or adjacency matrix before calling `Maxcut(graph)`.

If a snippet sets `algorithm_globals.random_seed`, import it explicitly with
`from qiskit_algorithms.utils import algorithm_globals`. For deterministic
sampler behavior, also pass a seed to the sampler, for example
`StatevectorSampler(seed=42)`.

Qiskit's `qiskit_algorithms.minimum_eigensolvers.QAOA` is not a
`QuantumCircuit` constructor or CUDA-Q kernel factory. Do not carry CUDA-Q
kernel arguments such as `qubit_count` or `layer_count` into Qiskit's `QAOA`
constructor. The graph size is represented by the `QuadraticProgram` and its
cost operator; the constructor needs `sampler`, `optimizer`, `reps`, and
optional parameters such as `initial_point`. If you supply two initial angles, use `reps=1`; for p layers, provide `2 * p` angles.
If `initial_point` is provided, its length must match the number of QAOA variational parameters. For standard QAOA this is `2 * reps`; a mismatch raises `ValueError` during solve.

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

Do not manually negate or rebuild a `Maxcut` application problem just because a
minimum eigensolver is used. `MinimumEigenOptimizer` wraps the solver and applies
the supported QUBO conversion pipeline for the `QuadraticProgram`.

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
| `Maxcut(edge_list_or_matrix)` | `__init__(self, graph: nx.Graph \| np.ndarray \| list)` | one positional `graph` parameter only; accepts an unweighted edge list or a symmetric adjacency matrix; do not pass a separate node count |
| `Maxcut.to_quadratic_program` | `(self) -> QuadraticProgram` | instance method, no arguments; call as `Maxcut(edges).to_quadratic_program()`, not `Maxcut.to_quadratic_program(edges)`; returns one `QuadraticProgram`, not a tuple |
| `Maxcut.interpret` | `(self, result) -> tuple[list[int], list[int]]` | returns the two partitions directly from a solved result |
| `QAOA.__init__` | `(self, sampler, optimizer, *, reps=1, initial_state=None, mixer=None, initial_point=None, aggregation=None, callback=None, transpiler=None, transpiler_options=None)` | no qubit-count or ancilla-count argument; the qubit count is inferred from the cost operator; set depth with `reps` |
| `MinimumEigenOptimizer.__init__` | `(self, min_eigen_solver, penalty=None, converters=None)` | keyword names are `min_eigen_solver` and `converters` (plural); default `converters` is `QuadraticProgramToQubo`, which already handles sense conversion — a `MAXIMIZE`-sense `QuadraticProgram` can be solved directly without manually negating coefficients |
| `qiskit_optimization.converters` module | exposes `InequalityToEquality`, `IntegerToBinary`, `LinearEqualityToPenalty`, `LinearInequalityToPenalty`, `MaximizeToMinimize`, `MinimizeToMaximize`, `QuadraticProgramToQubo` | no converter class named `MinimumD`, `MinimumToMaximize`, `MinimumToMaximizingConverter`, `MinimizationToMaximisation`, `Model2QUBO`, `Model2QubitOperator`, `Linear2Quadratic`, `QuadraticProgramToQuadraticProgram`, `SumOfSubproblems`, `Transformation`, or `MinimumToSum` exists |

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
- Keep generated imports minimal and non-repeated. Standard QAOA Max-Cut
  snippets do not need `OptimizationAlgorithm`, `QuantumCircuit`, unused direct
  `QuadraticProgram` imports, duplicate `MinimumEigenOptimizer` aliases, or
  converter imports.
- `CategoricalVariable` is not a root `qiskit_optimization` import for these
  snippets; do not add it to Max-Cut examples.
- Instantiate `Maxcut` with graph data, then call `to_quadratic_program()` with no arguments. Do not split this into an empty application constructor plus a graph argument on `to_quadratic_program`.
- `Maxcut` takes one graph argument. Do not call `Maxcut(edges, node_count)`;
  include isolated vertices in the graph object or adjacency matrix if needed.
- Do not read node-count attributes from the `Maxcut` application object. Keep
  graph size in local variables, infer it from the graph input, or inspect the
  returned `QuadraticProgram` variables when needed.
- Qubit-count keywords are invalid for `QAOA`; the algorithm gets the qubit
  count from the cost operator generated by the optimizer wrapper. Use `reps`
  for QAOA depth.
- Do not carry CUDA-Q kernel arguments such as `qubit_count` or `layer_count`
  into Qiskit's `QAOA` constructor; Qiskit gets the graph size from the
  converted optimization problem.
- Do not describe the solved Max-Cut assignment as a minimum cut. The internal
  eigensolver minimizes a converted Hamiltonian/QUBO representation, while the
  returned optimization result reports the Max-Cut objective.
- Ancilla-count keywords are invalid for `QAOA`; constructor arguments include
  `sampler`, `optimizer`, and keyword-only `reps`, not circuit resource counts.
- `initial_point` length must match the ansatz parameter count. For standard QAOA this is `2 * reps`; a mismatch raises `ValueError` during solve.
- If code sets `algorithm_globals.random_seed`, it must import
  `algorithm_globals` from `qiskit_algorithms.utils`; otherwise the snippet
  raises `NameError` before QAOA runs.
- QAOA has no post-construction qubit-replacement setter methods. Configure
  custom `initial_state` or `mixer` through constructor keywords when needed.
- `MinimumEigenOptimizer.solve(...)` results expose `result.x` and
  `result.fval`.
- Do not read `result.x0`; the solution-vector attribute is `result.x`.
- Do not read `result.primal_values`; the solution-vector attribute is
  `result.x`.
- `result.x` is an ordered array-like solution, not a dictionary of variable
  names to values. Do not call `result.x.items()`; cast values to Python ints
  and use numeric indices or application `interpret(result)` helpers.
- Prefer `result.x` plus application `interpret(result)` helpers for solved
  assignments; do not guess nested best-solution attribute paths unless the
  current result class documents them.
- `MinimumEigenOptimizationResult` does not require a nested best-feasible
  solution object for simple Max-Cut snippets; read the assignment from
  `result.x`.
- The objective value field is `result.fval`; `result.feval` is not valid.
- `result.fvalue` is not a valid objective-value field; use `result.fval`.
- `result.fitness_value` is not a valid objective-value field; use
  `result.fval`.
- Do not negate `result.fval` for standard `Maxcut(...).to_quadratic_program()`
  results. The optimizer result reports the original objective sense.
- `Maxcut(...).to_quadratic_program()` can be solved directly by
  `MinimumEigenOptimizer`. Its default `QuadraticProgramToQubo` converter handles
  maximization-to-minimization conversion, so a separate converter is usually
  unnecessary for standard Max-Cut snippets.
- There is no `MinimumD` converter. Do not invent abbreviated converter names
  for maximization-to-minimization handling.
- There is no `MinimizationToMaximisation` converter; use the documented
  `MaximizeToMinimize` / `MinimizeToMaximize` names only when manual sense
  conversion is explicitly required.
- There is no `MinimumToMaximize` converter. Use `MaximizeToMinimize` or
  `MinimizeToMaximize` only when a task explicitly requires manual sense
  conversion.
- There is no `MinimumToMaximizingConverter`; for standard Max-Cut snippets,
  do not import or instantiate a separate sense converter.
- There are no converters named `Model2QUBO`, `Model2QubitOperator`, or
  `Linear2Quadratic`; use `QuadraticProgramToQubo` only when a task explicitly
  asks for manual QUBO conversion.
- There is no `QuadraticProgramToQuadraticProgram` converter. If no conversion
  is needed, pass the existing `QuadraticProgram` directly.
- There are no converter classes named `SumOfSubproblems` or `Transformation`;
  do not import generic chaining placeholders for standard Max-Cut QAOA code.
- There is no `Maxcut.ingraph2qubit(...)` method. Instantiate `Maxcut` with graph
  data and call `to_quadratic_program()` on that application object.
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
