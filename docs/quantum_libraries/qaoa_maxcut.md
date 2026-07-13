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

## Qiskit answer template
Qiskit 2.x ecosystem. The latest Qiskit package target is qiskit 2.4.2
(Python >=3.10). Use the 2.4.x documentation/API as the target for code
generation and import repair.

Use this template first for generated QAOA Max-Cut answers. Detailed reference
material below is for repair and edge cases; do not copy every reference import
into a runnable answer.

### Minimal imports

Keep QAOA Max-Cut imports minimal: sampler, QAOA, optimizer, `Maxcut`, and
`MinimumEigenOptimizer` are enough for the application pattern. Do not repeat
imports, create unused aliases of already imported symbols, or add unused
framework classes such as `QuadraticProgram`,
`OptimizationAlgorithm`, `QuantumCircuit`, `CategoricalVariable`, or manual
converter imports.

For the standard application path, do not import anything from
`qiskit_optimization.converters`. `MinimumEigenOptimizer(qaoa).solve(problem)`
already uses the default `QuadraticProgramToQubo` conversion internally. Never
add placeholder, identity, or sense-converter imports just because Max-Cut is a
maximization problem.

```python
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_optimization.applications import Maxcut
from qiskit_optimization.algorithms import MinimumEigenOptimizer
```

### Canonical application pattern

```python
def solve_qaoa_maxcut(edges):
    maxcut = Maxcut(edges)
    problem = maxcut.to_quadratic_program()

    sampler = StatevectorSampler(seed=42)
    optimizer = COBYLA(maxiter=100)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=2)

    result = MinimumEigenOptimizer(qaoa).solve(problem)
    solution = [int(value) for value in result.x]
    set0, set1 = maxcut.interpret(result)
    cut_value = sum(1 for u, v in edges if solution[u] != solution[v])
    return solution, set0, set1, cut_value, result.fval
```

### Generation rules

- Read the solved assignment from `result.x` and cast it to Python integers
  before indexing or printing. `result.x` is an ordered array-like solution,
  not a dictionary; do not call `.items()` on it.
- Read the Max-Cut objective value directly from `result.fval`; do not negate
  it. `MinimumEigenOptimizer` maps the internal minimization result back to the
  original `QuadraticProgram` objective value.
- Set QAOA depth with `reps`; do not pass circuit resource-count keywords to
  QAOA.
- Pass `Maxcut(...).to_quadratic_program()` directly to
  `MinimumEigenOptimizer`; its default `QuadraticProgramToQubo` converter
  handles maximization sense conversion.
- Do not add any `qiskit_optimization.converters` import for standard Max-Cut
  QAOA code, including `Model2QUBO` or identity/sense-converter names. Fake or
  unnecessary converter names are the most common cause of import failures in
  this pattern.
- Build the application problem with `Maxcut(edges).to_quadratic_program()`.
  There is no `Maxcut.ingraph2qubit(...)` helper in the current API.
- Do not import or chain `Model2QUBO`, identity converters, or
  `Linear2Quadratic`; those are not current Qiskit Optimization converter
  classes for this pattern.
- Construct `Maxcut` with one graph argument only. Do not pass a separate node
  count as a second positional argument; if you know the number of vertices,
  use it only to build the graph or adjacency matrix before calling
  `Maxcut(graph)`.
- Qiskit's `qiskit_algorithms.minimum_eigensolvers.QAOA` class is an algorithm
  wrapper, not a `QuantumCircuit` constructor or CUDA-Q kernel. Do not carry
  CUDA-Q kernel arguments such as `qubit_count` or `layer_count` into Qiskit's
  `QAOA` constructor.
- The graph size is represented by the `QuadraticProgram` and its cost
  operator; the QAOA constructor needs `sampler`, `optimizer`, `reps`, and
  optional parameters such as `initial_point`. If you supply two initial angles, use `reps=1`; for p layers, provide `2 * p` angles.
- If `initial_point` is provided, its length must match the number of QAOA variational parameters. For standard QAOA this is `2 * reps`; a mismatch raises `ValueError` during solve.

### Optional deterministic seeding

If a snippet sets `algorithm_globals.random_seed`, import it explicitly with
`from qiskit_algorithms.utils import algorithm_globals`. For deterministic
sampler behavior, also pass a seed to the sampler.

```python
from qiskit_algorithms.utils import algorithm_globals

algorithm_globals.random_seed = 42
sampler = StatevectorSampler(seed=42)
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

Do not manually rebuild a Max-Cut problem as a negative minimization just because
QAOA is a minimum eigensolver. `MinimumEigenOptimizer` already applies the
standard QUBO conversion pipeline for supported `QuadraticProgram` instances.

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
| `Maxcut(edge_list_or_matrix)` | `__init__(self, graph: nx.Graph \| np.ndarray \| list)` | one positional `graph` parameter only; accepts an unweighted edge list or a symmetric adjacency matrix; do not pass a separate node count |
| `Maxcut.to_quadratic_program` | `(self) -> QuadraticProgram` | instance method, no arguments; call as `Maxcut(edges).to_quadratic_program()`, not `Maxcut.to_quadratic_program(edges)`; returns one `QuadraticProgram`, not a tuple |
| `QAOA.__init__` | `(self, sampler, optimizer, *, reps=1, initial_state=None, mixer=None, initial_point=None, aggregation=None, callback=None, transpiler=None, transpiler_options=None)` | no qubit-count or ancilla-count argument; the qubit count is inferred from the cost operator; set QAOA depth with `reps` |
| `MinimumEigenOptimizer.__init__` | `(self, min_eigen_solver, penalty=None, converters=None)` | keyword names are `min_eigen_solver` and `converters` (plural); default `converters` is `QuadraticProgramToQubo`, which already handles sense conversion — a `MAXIMIZE`-sense `QuadraticProgram` can be solved directly without manually negating coefficients |
| `qiskit_optimization.converters` module | exposes `InequalityToEquality`, `IntegerToBinary`, `LinearEqualityToPenalty`, `LinearInequalityToPenalty`, `MaximizeToMinimize`, `MinimizeToMaximize`, `QuadraticProgramToQubo` | no converter class named `MinimumD`, `MinimumToMaximize`, `MinimumToMaximizingConverter`, `MinimizationToMaximisation`, `Model2QUBO`, `Model2QubitOperator`, `Linear2Quadratic`, `QuadraticProgramToQuadraticProgram`, `SumOfSubproblems`, `Transformation`, or `MinimumToSum` exists |

`MinimumEigenOptimizer.solve(...)` returns an `OptimizationResult`. Use
`result.x` for the solution vector and `result.fval` for the objective value;
do not invent alternate solution-vector attribute names.
Do not read `result.feval`; the objective-value attribute is `result.fval`.
Do not read `result.fvalue`; the objective-value attribute is `result.fval`.
Do not negate the reported objective for application-generated problems;
`result.fval` is already the reported Max-Cut objective value.

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
- Keep generated imports minimal and non-repeated. Standard QAOA Max-Cut
  snippets do not need `OptimizationAlgorithm`, `QuantumCircuit`,
  `CategoricalVariable`, unused direct `QuadraticProgram` imports, duplicate
  `MinimumEigenOptimizer` aliases, or converter imports.
- Importing `QAOA` from `qiskit_optimization.algorithms` raises ImportError;
    import `QAOA` from `qiskit_algorithms.minimum_eigensolvers` or
    `qiskit_optimization.minimum_eigensolvers` instead.
- Instantiate `Maxcut` with graph data, then call `to_quadratic_program()` with no arguments. Do not split this into an empty application constructor plus a graph argument on `to_quadratic_program`.
- `Maxcut` takes one graph argument. Do not call `Maxcut(edges, node_count)`;
  include isolated vertices in the graph object or adjacency matrix if needed.
- Do not read node-count attributes from the `Maxcut` application object. Keep
  the graph size as local data, infer it from the graph input, or use the
  returned `QuadraticProgram` variables when needed.
- Qubit-count keywords are invalid for `QAOA`; the algorithm gets the qubit
  count from the cost operator generated by the optimizer wrapper. Use `reps`
  for QAOA depth.
- Do not carry CUDA-Q kernel arguments such as `qubit_count` or `layer_count`
  into Qiskit's `QAOA` constructor; they belong to hand-written kernel examples,
  not to `qiskit_algorithms.minimum_eigensolvers.QAOA`.
- Do not describe the solved Max-Cut assignment as a minimum cut. The internal
  eigensolver minimizes a converted Hamiltonian/QUBO representation, while the
  returned optimization result reports the Max-Cut objective.
- Passing ancilla-count keywords to `QAOA` raises `TypeError`; ancilla counts
  are circuit properties, not QAOA constructor arguments. Use
  `QAOA(..., reps=p)` for p-layer QAOA.
- `initial_point` length must match the ansatz parameter count. For standard QAOA this is `2 * reps`; a mismatch raises `ValueError` during solve.
- If code sets `algorithm_globals.random_seed`, it must import
  `algorithm_globals` from `qiskit_algorithms.utils`; otherwise the snippet
  raises `NameError` before QAOA runs.
- QAOA does not expose post-construction qubit-replacement setter methods. If a
  task asks for custom initial states or mixers, pass `initial_state=` or
  `mixer=` to the constructor.
- `MinimumEigenOptimizer` results use `result.x` for the solution vector.
- Do not read `result.x0`; the solution-vector attribute is `result.x`.
- Do not read `result.primal_values`; the solution-vector attribute is
  `result.x`.
- `result.x` is an ordered array-like solution, not a dictionary of variable
  names to values. Do not iterate with `result.x.items()`; cast with
  `[int(value) for value in result.x]` and use numeric vertex indices or
  `Maxcut.interpret(result)`.
- Prefer `result.x` and application-specific `interpret(result)` helpers for
  solved assignments; do not guess nested best-solution attributes unless the
  current result class documents them.
- `MinimumEigenOptimizationResult` does not require a nested best-feasible
  solution object for simple Max-Cut snippets; read the assignment from
  `result.x`.
- `MinimumEigenOptimizer` results use `result.fval` for the objective value;
  `result.feval` is not a valid field.
- `result.fvalue` is not a valid objective-value field; use `result.fval`.
- `result.fitness_value` is not a valid objective-value field; use
  `result.fval`.
- Do not negate `result.fval` for standard `Maxcut(...).to_quadratic_program()`
  results. The optimizer result reports the original objective sense.
- `MinimumEigenOptimizer` can solve the `MAXIMIZE`-sense `QuadraticProgram`
  returned by `Maxcut(...).to_quadratic_program()` directly through its default
  converters; do not add a nonexistent converter or rebuild the problem as a
  negative minimization unless a task explicitly asks for manual construction.
- There is no converter named `MinimumD`; do not invent abbreviated sense
  converters for Max-Cut examples.
- There is no converter named `MinimizationToMaximisation`; use the documented
  `MaximizeToMinimize` / `MinimizeToMaximize` names only when manual sense
  conversion is explicitly required.
- There is no converter named `MinimumToMaximizingConverter`; for standard
  Max-Cut snippets, do not import or instantiate a separate sense converter.
- There are no converters named `Model2QUBO`, `Model2QubitOperator`, or
  `Linear2Quadratic`; use `QuadraticProgramToQubo` only when a task explicitly
  asks for manual QUBO conversion.
- There is no identity converter named `QuadraticProgramToQuadraticProgram`;
  use the original `QuadraticProgram` directly when no conversion is required.
- There are no converter classes named `SumOfSubproblems` or `Transformation`;
  do not import generic chaining placeholders for standard Max-Cut QAOA code.
- There is no `Maxcut.ingraph2qubit(...)` method. Instantiate `Maxcut` with graph
  data and call `to_quadratic_program()` on that application object.
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
