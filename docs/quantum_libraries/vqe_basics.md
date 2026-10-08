# Variational Quantum Eigensolver (VQE)

## Concept
VQE estimates the lowest eigenvalue of a Hermitian operator H using a
parameterised circuit ansatz |psi(theta)> and a classical optimiser:

  E(theta) = <psi(theta)| H |psi(theta)>

The optimiser minimises E(theta) over theta. The result is an upper
bound on the true ground-state energy by the variational principle.

## Workflow
1. Encode H as a sum of Pauli strings: H = sum_i c_i P_i.
2. Choose an ansatz (hardware-efficient layers of Ry/Rz + entanglers, or
   UCC, or HEA).
3. For each measurement basis (Pauli string), prepare |psi(theta)>,
   rotate to the measurement basis, sample, and combine to produce
   <H>(theta).
4. Pass E(theta) to a classical optimiser (COBYLA, SPSA, L-BFGS-B).

## Reference numpy (exact expectation, no shots)

```python
import numpy as np

def expectation(state: np.ndarray, hamiltonian: np.ndarray) -> float:
    return float(np.real(np.vdot(state, hamiltonian @ state)))
```

## Library snippets
Qiskit:
```python
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import COBYLA
from qiskit.circuit.library import RealAmplitudes
```

PennyLane:
```python
import pennylane as qml
ansatz = qml.SimplifiedTwoDesign
qnode = qml.QNode(circuit, dev)
opt = qml.AdamOptimizer(0.05)
```

## Common pitfalls
- Choose an ansatz that can express the ground state (expressibility)
  while remaining trainable (avoid barren plateaus from too many
  layers).
- Group commuting Paulis to reduce the number of measurement bases.
- Always seed your optimiser; gradient-free optimisers are highly
  sensitive to starting points.
