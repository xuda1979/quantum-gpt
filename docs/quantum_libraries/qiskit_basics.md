# Qiskit basics (v1.x API)

## Import surface

```python
from qiskit import QuantumCircuit, transpile
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

## Endianness gotcha
Qiskit displays bitstrings with qubit 0 as the *rightmost* character
(little-endian). The Statevector vector index k = sum_i b_i * 2^i where
b_i is the value of qubit i.

## Common pitfalls
- Forgetting `transpile` before running on Aer (works but is slower).
- Confusing classical-bit index order in `.measure([qubits], [cbits])`.
- The default basis for parameterised gates is in radians; multiply by
  pi explicitly for angles like 90 degrees.
