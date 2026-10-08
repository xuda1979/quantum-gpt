# Quantum teleportation

## Concept
Teleportation transfers the *state* of a qubit from Alice to Bob using
two classical bits and one pre-shared Bell pair, without physically
moving the qubit.

## Protocol
Initial state: |psi>_A (alpha|0> + beta|1>) plus shared Bell pair
|Phi+>_{B,C} between Alice (qubit B) and Bob (qubit C).

1. Alice applies CNOT(A, B), then H(A).
2. Alice measures qubits A and B in the computational basis -> two
   classical bits (m1, m2).
3. Alice sends (m1, m2) to Bob.
4. Bob applies a correction on his qubit C:
   - (0, 0) -> I
   - (0, 1) -> X
   - (1, 0) -> Z
   - (1, 1) -> ZX (apply X then Z)
5. Bob's qubit is now in state |psi>.

## Correction table

```python
CORRECTIONS = {
    (0, 0): "I",
    (0, 1): "X",
    (1, 0): "Z",
    (1, 1): "ZX",
}

def teleport_correction(m1: int, m2: int) -> str:
    return CORRECTIONS[(m1, m2)]
```

`m1` is Alice's measurement of qubit A (post H), `m2` is Alice's
measurement of qubit B (post CNOT).

## Reference circuit

```python
import numpy as np

def teleport(alpha: complex, beta: complex, m1: int, m2: int) -> np.ndarray:
    # Bob's recovered state after applying correction (m1, m2)
    psi = np.array([alpha, beta], dtype=complex)
    if m2 == 1:
        psi = np.array([psi[1], psi[0]])  # X
    if m1 == 1:
        psi = psi * np.array([1, -1])     # Z
    return psi
```

## Common pitfalls
- The (m1, m2) -> Pauli table is *not* symmetric. Verify which bit
  came from which measurement. A common bug is to swap m1 and m2.
- The two classical bits are sent over a *classical* channel; this is
  why teleportation does not violate no-faster-than-light signalling.
- Without the corrections, Bob's qubit is a uniformly random mixture of
  the four possible Bell-decoded outcomes.
