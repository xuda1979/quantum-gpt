# Qiskit basics (current 2.x core API)

Latest Qiskit package target: qiskit 2.4.2 from PyPI, released 2026-06-13,
with Python >=3.10 required. Do not infer the latest API from an older local
Python 3.9 environment.

## Import surface

```python
from qiskit import QuantumCircuit, transpile
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector, Operator, partial_trace
from qiskit_aer import AerSimulator
```

## Building a circuit

```python
qc = QuantumCircuit(2, 2)  # 2 qubits, 2 classical bits
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
```

Common gate methods on `QuantumCircuit`:
- `.h(q)`, `.x(q)`, `.y(q)`, `.z(q)`, `.s(q)`, `.t(q)`
- `.rx(theta, q)`, `.ry(theta, q)`, `.rz(theta, q)`
- `.cx(c, t)`, `.cy(c, t)`, `.cz(c, t)`
- `.ccx(c1, c2, t)` (Toffoli), `.swap(a, b)`, `.cswap(c, a, b)`
- `.barrier()`, `.reset(q)`, `.measure(q, c)`

## Simulating with Statevector

```python
sv = Statevector.from_instruction(qc)
print(sv.data)         # complex amplitudes (little-endian)
print(sv.probabilities())
```

To get the matrix of a unitary circuit: `Operator(qc).data`.

## Running with Aer

```python
sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=1024).result()
counts = result.get_counts(tqc)
```

## StatevectorSampler primitive

```python
sampler = StatevectorSampler(seed=42)
job = sampler.run([qc], shots=1024)
primitive_result = job.result()
```

Use the primitive interface for current Qiskit algorithm classes such as
`qiskit_algorithms.QAOA`. Use AerSimulator when you need a backend-like
simulator result object and counts through `get_counts`.

For algorithm-level reproducibility, use
`from qiskit_algorithms.utils import algorithm_globals` before assigning
`algorithm_globals.random_seed`. For sampler reproducibility, prefer explicit
sampler seeds such as `StatevectorSampler(seed=42)`.

## Qiskit algorithms versus circuit/kernel APIs

`qiskit_algorithms.minimum_eigensolvers.QAOA` is not a `QuantumCircuit` constructor or CUDA-Q kernel factory. It receives a sampler, an optimizer,
`reps`, and optional algorithm parameters such as `initial_point`. Do not pass
graph size, qubit-count, or layer-count kernel arguments to that constructor;
Qiskit algorithm classes get problem size from the operator or optimization
problem they solve.

## Endianness gotcha
Qiskit displays bitstrings with qubit 0 as the *rightmost* character
(little-endian). The Statevector vector index k = sum_i b_i * 2^i where
b_i is the value of qubit i.

## Common pitfalls
- Forgetting `transpile` before running on Aer (works but is slower).
- Confusing classical-bit index order in `.measure([qubits], [cbits])`.
- The default basis for parameterised gates is in radians; multiply by
  pi explicitly for angles like 90 degrees.
- Optimizers such as `COBYLA` live in `qiskit_algorithms.optimizers`, while
  algorithm classes such as `QAOA` should be imported from explicit algorithm
  submodules such as `qiskit_algorithms.minimum_eigensolvers`.
- Qiskit `QAOA` is an algorithm wrapper, not a circuit/kernel constructor; set
  QAOA depth with `reps` and let the solved operator or optimization problem
  determine the qubit count.
- Import `algorithm_globals` before assigning `algorithm_globals.random_seed`;
  otherwise the code raises `NameError` before any algorithm executes.
- `qiskit_optimization.algorithms` is for optimizers/wrappers such as
  `MinimumEigenOptimizer`; it is not the import path for `QAOA`.
