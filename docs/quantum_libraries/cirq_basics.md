# Cirq basics

## Imports

```python
import cirq
import numpy as np
```

## Qubits and circuits

```python
q0, q1, q2 = cirq.LineQubit.range(3)
circuit = cirq.Circuit([
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.CNOT(q1, q2),
])
```

`cirq.GridQubit(row, col)` is preferred for hardware-realistic
topologies.

## Gates
- Single-qubit: `cirq.H`, `cirq.X`, `cirq.Y`, `cirq.Z`, `cirq.S`, `cirq.T`
- Rotations: `cirq.rx(theta)`, `cirq.ry(theta)`, `cirq.rz(theta)`
- Two-qubit: `cirq.CNOT`, `cirq.CZ`, `cirq.SWAP`, `cirq.ISWAP`
- Three-qubit: `cirq.TOFFOLI`, `cirq.CSWAP`

## Simulation

```python
sim = cirq.Simulator()
result = sim.simulate(circuit)
print(result.final_state_vector)
```

For sampling:
```python
result = sim.run(circuit + [cirq.measure(q0, q1, q2, key="m")], repetitions=1024)
print(result.histogram(key="m"))
```

## Endianness
Cirq uses big-endian: the first qubit you list is the most significant
bit. The state vector is indexed by `sum_i b_i * 2^(n-1-i)` for qubits
listed in order.

## Common pitfalls
- `cirq.Circuit(operations)` lays out gates into "moments" automatically;
  use `cirq.InsertStrategy.NEW_THEN_INLINE` if order matters.
- `cirq.unitary(circuit)` returns the full unitary; only valid if all
  operations are unitary (no measurement).
- Qubit objects are not interchangeable across `LineQubit` and
  `GridQubit`; pick one.
