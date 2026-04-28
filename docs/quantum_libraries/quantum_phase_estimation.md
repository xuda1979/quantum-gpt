# Quantum Phase Estimation (QPE)

## Concept
Given a unitary U with eigenvector |psi> and unknown eigenvalue
exp(2*pi*i*phi), QPE estimates `phi` (a real number in [0, 1)) using
two registers:
- `t` counting qubits in the upper register (precision)
- the eigenvector |psi> in the lower register

## Protocol
1. Initialise upper register to |+>^t (apply H on each).
2. Apply controlled-U^(2^k) for k = 0, ..., t-1 with control qubit k.
3. Apply inverse QFT on the upper register.
4. Measure the upper register; the integer y satisfies y/2^t ~= phi.

## Returned phase
The protocol returns an integer `y` in {0, ..., 2^t - 1}. Convert to
phase via `phi_estimate = y / 2**t`. With perfect alignment phi can be
recovered exactly when `phi * 2**t` is integer.

## Reference Python (single eigenphase)

```python
import numpy as np

def estimate_phase(true_phase: float, t: int) -> float:
    """Idealised QPE: returns phi rounded to t bits."""
    y = round(true_phase * (1 << t)) % (1 << t)
    return y / (1 << t)


def qpe_unitary_eigenvalue(unitary: np.ndarray, eigenvector: np.ndarray,
                            t: int = 8) -> complex:
    # Find eigenvalue exp(2*pi*i*phi) corresponding to eigenvector.
    Uv = unitary @ eigenvector
    # Inner product gives e^{2*pi*i*phi}
    eigval = np.vdot(eigenvector, Uv)
    phi = (np.angle(eigval) / (2 * np.pi)) % 1.0
    phi_est = estimate_phase(phi, t)
    return np.exp(2j * np.pi * phi_est)
```

## Library snippets

Qiskit:
```python
from qiskit.circuit.library import PhaseEstimation
qpe = PhaseEstimation(num_evaluation_qubits=t, unitary=U_circuit)
```

Cirq exposes phase estimation in `cirq.contrib.algorithms`. PennyLane
offers `qml.QuantumPhaseEstimation`.

## Common pitfalls
- `t` controls precision: the worst-case error in phi is ~ 2^-t.
- Apply controlled-U^(2^k), not k controlled-Us. The exponentiation is
  often the most expensive step.
- The inverse QFT (not the forward QFT) goes on the upper register.
- Endianness of the integer measurement result depends on the SDK; some
  return bit-reversed integers.
