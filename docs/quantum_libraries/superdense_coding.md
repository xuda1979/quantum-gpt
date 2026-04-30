# Superdense coding

## Concept
Superdense coding lets Alice send 2 classical bits to Bob using a single
qubit, provided they pre-share an entangled Bell pair.

## Protocol
1. Pre-shared resource: |Phi+> = (|00> + |11>)/sqrt(2). Alice holds
   qubit 0, Bob holds qubit 1.
2. Alice encodes (b1, b0) by applying:
   - 00 -> I  (do nothing) -> |Phi+>
   - 01 -> X            -> |Psi+> = (|01> + |10>)/sqrt(2)
   - 10 -> Z            -> |Phi-> = (|00> - |11>)/sqrt(2)
   - 11 -> ZX (or iY)   -> |Psi-> = (|01> - |10>)/sqrt(2)
3. Alice sends her qubit to Bob.
4. Bob applies CNOT(0, 1) then H(0) (Bell-basis measurement) to recover
   the two classical bits.

## Encode/decode reference

```python
ENCODE_TABLE = {
    (0, 0): "I",
    (0, 1): "X",
    (1, 0): "Z",
    (1, 1): "ZX",
}

def encode(bits: tuple[int, int]) -> str:
    return ENCODE_TABLE[bits]

DECODE_TABLE = {
    (0, 0): (0, 0),
    (0, 1): (0, 1),
    (1, 0): (1, 0),
    (1, 1): (1, 1),
}
```

After Bob's measurement, the classical outcome (m0, m1) directly
matches Alice's input bits (b1, b0).

## State-vector simulation snippet

```python
import numpy as np

def superdense_state(b1: int, b0: int) -> np.ndarray:
    amp = 2 ** -0.5
    # start in |Phi+>
    state = np.array([amp, 0, 0, amp], dtype=complex)
    # Alice's encoding on qubit 0 (most significant in big-endian)
    if b1 == 0 and b0 == 0:
        pass
    elif b1 == 0 and b0 == 1:
        # X on qubit 0 swaps |0x><->|1x>
        state = state[[2, 3, 0, 1]]
    elif b1 == 1 and b0 == 0:
        # Z on qubit 0 flips sign of |1x>
        state = state * np.array([1, 1, -1, -1])
    else:  # 11
        state = state[[2, 3, 0, 1]] * np.array([1, 1, -1, -1])
    return state
```

## Common pitfalls
- The mapping bits -> Pauli depends on which qubit Alice holds. The
  table above assumes Alice = qubit 0 (control) and Bob = qubit 1.
- Order matters in "ZX": apply X first, then Z (left-to-right reading).
