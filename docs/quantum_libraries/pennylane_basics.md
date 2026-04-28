# PennyLane basics

## Imports

```python
import pennylane as qml
import pennylane.numpy as np
```

## Devices and qnodes

```python
dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuit(theta):
    qml.RY(theta, wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0))
```

A QNode wraps a quantum function and ties it to a device. Returning
`qml.state()`, `qml.probs(wires=[...])`, `qml.expval(obs)`, or
`qml.sample(obs)` controls what is observed.

## Gates
- `qml.Hadamard(wire)`, `qml.PauliX(wire)`, `qml.PauliY(wire)`, `qml.PauliZ(wire)`
- `qml.RX(theta, wire)`, `qml.RY(theta, wire)`, `qml.RZ(theta, wire)`
- `qml.CNOT(wires=[c, t])`, `qml.CZ(wires=[c, t])`, `qml.SWAP(wires=[a, b])`
- `qml.Toffoli(wires=[c1, c2, t])`, `qml.CSWAP(wires=[c, a, b])`

## Hamiltonians and templates

```python
H = qml.Hamiltonian(
    coeffs=[1.0, -0.5, 0.3],
    observables=[qml.PauliZ(0) @ qml.PauliZ(1), qml.PauliX(0), qml.PauliY(1)],
)
```

Templates: `qml.AngleEmbedding`, `qml.BasicEntanglerLayers`,
`qml.StronglyEntanglingLayers`, `qml.QFT`, `qml.QuantumPhaseEstimation`.

## QAOA helpers

```python
from pennylane import qaoa
graph = [(0, 1), (1, 2), (0, 2)]
cost_h, mixer_h = qaoa.maxcut(graph)
```

## Common pitfalls
- The default device differentiates analytically; for `shots != None`
  you usually want `qml.device("default.qubit", wires=n, shots=1024)`.
- `pennylane.numpy.array(..., requires_grad=True)` is needed for
  trainable parameters; plain numpy arrays will not be optimised.
- `wires=[0, 1]` is required as a list for multi-wire gates; passing a
  tuple may work but is brittle.
