# Amazon Braket basics

## Imports

```python
from braket.circuits import Circuit
from braket.devices import LocalSimulator
```

## Building a circuit

```python
circuit = Circuit().h(0).cnot(control=0, target=1).measure([0, 1])
```

Common gate methods (chainable):
- `.h(q)`, `.x(q)`, `.y(q)`, `.z(q)`, `.s(q)`, `.t(q)`
- `.rx(q, theta)`, `.ry(q, theta)`, `.rz(q, theta)`
- `.cnot(control, target)`, `.cz(control, target)`, `.swap(a, b)`
- `.ccnot(control1, control2, target)` (Toffoli)

## Local simulation

```python
device = LocalSimulator()
result = device.run(circuit, shots=1024).result()
counts = result.measurement_counts
```

For amplitudes: include `.state_vector()` result type.

```python
circuit.state_vector()
result = device.run(circuit, shots=0).result()
sv = result.values[0]
```

## Common pitfalls
- Braket uses big-endian indexing: qubit 0 is the most significant bit
  in the bitstring.
- `shots=0` is required for analytical (state vector / expectation)
  results; `shots>0` gives sampled outputs and disables many analytical
  result types.
- The remote AWS device interface (`AwsDevice`) requires AWS credentials;
  prefer `LocalSimulator` for local testing.
