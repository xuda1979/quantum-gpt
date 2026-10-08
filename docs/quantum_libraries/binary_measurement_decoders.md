# Binary measurement decoders and Pauli routers

## Bit-flip syndrome decoder
For the 3-qubit bit-flip code, syndrome bits (s1, s2) come from
measuring Z0Z1 (s1) and Z1Z2 (s2). Decoder:

```python
SYNDROMES = {
    (0, 0): None,  # no error
    (1, 0): 0,     # X on qubit 0
    (1, 1): 1,     # X on qubit 1
    (0, 1): 2,     # X on qubit 2
}
```

## Bell measurement decoder
Bell-basis measurement of two qubits returns a pair of classical bits
(m1, m2) identifying which Bell state was observed:

```python
BELL_LABELS = {
    (0, 0): "Phi+",
    (0, 1): "Psi+",
    (1, 0): "Phi-",
    (1, 1): "Psi-",
}
```

## Pauli router (superdense / teleport variants)
Maps a 2-bit input to a single-qubit Pauli operation on a target qubit:

```python
PAULI_ROUTER = {
    (0, 0): "I",
    (0, 1): "X",
    (1, 0): "Z",
    (1, 1): "Y",  # or "ZX" depending on convention
}
```

When the convention is "ZX = apply X first then Z", the (1, 1) entry is
equivalent to applying iY (up to a global phase).

## Identity-lookup helpers
Some tasks ask for the *table* itself rather than logic. Return the
canonical 4-row lookup mapping bits -> operation, never invent a
formulaic mapping.

## Pattern: dispatcher

```python
def apply_correction(state, m1: int, m2: int):
    op = PAULI_ROUTER[(m1, m2)]
    if op == "I":
        return state
    if op == "X":
        return apply_x(state)
    if op == "Z":
        return apply_z(state)
    if op == "Y":
        return apply_y(state)
    raise KeyError(op)
```

## Common pitfalls
- (m1, m2) order is *not* swappable; tests pin it down. Keep dict keys
  consistent with the task's measurement order.
- "ZX" vs "Y" differs only by a global phase but matters in some test
  fixtures that compare matrices, not state vectors.
- Convention for which classical bit is "first" varies; double-check the
  task's docstring.
