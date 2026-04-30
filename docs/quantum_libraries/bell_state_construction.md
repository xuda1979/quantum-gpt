# Bell pair construction

## Concept
A Bell pair is a maximally entangled two-qubit state. The four Bell
states are:

- |Phi+> = (|00> + |11>) / sqrt(2)
- |Phi-> = (|00> - |11>) / sqrt(2)
- |Psi+> = (|01> + |10>) / sqrt(2)
- |Psi-> = (|01> - |10>) / sqrt(2)

The default "Bell pair" is |Phi+>.

## Amplitudes
Indexing in the computational basis (|00>, |01>, |10>, |11>):

```
phi_plus  = [1/sqrt(2), 0, 0, 1/sqrt(2)]
phi_minus = [1/sqrt(2), 0, 0, -1/sqrt(2)]
psi_plus  = [0, 1/sqrt(2), 1/sqrt(2), 0]
psi_minus = [0, 1/sqrt(2), -1/sqrt(2), 0]
```

In Python, `2 ** -0.5` is the canonical idiom for 1/sqrt(2).

## Reference circuit (|Phi+>)
1. Apply H to qubit 0
2. Apply CNOT with qubit 0 as control, qubit 1 as target

```python
def bell_pair_state():
    amp = 2 ** -0.5
    return [amp, 0.0, 0.0, amp]  # |Phi+>
```

## Library snippets

Qiskit:
```python
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0); qc.cx(0, 1)
```

Cirq:
```python
import cirq
q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit([cirq.H(q0), cirq.CNOT(q0, q1)])
```

PennyLane:
```python
import pennylane as qml
@qml.qnode(qml.device("default.qubit", wires=2))
def bell():
    qml.Hadamard(0); qml.CNOT([0, 1])
    return qml.state()
```

## Common pitfalls
- Use `math.isclose` (or `numpy.isclose`) with rel_tol=1e-9 to compare
  floating-point amplitudes; never use exact equality.
- Endianness varies between SDKs. Qiskit uses little-endian by default;
  Cirq/PennyLane use big-endian. Tests usually expect big-endian
  amplitudes [|00>, |01>, |10>, |11>] from explicit list construction.
