# Quantum error correction basics (bit-flip and Shor 9-qubit)

## Bit-flip code (3-qubit repetition)
Protects against a single X (bit flip) error.

- Encoding: |0> -> |000>, |1> -> |111>. Logical |psi> = a|000> + b|111>.
- Syndrome measurement: ZZI and IZZ. Outcomes (s1, s2):
  - (0, 0) -> no error
  - (1, 0) -> X on qubit 0
  - (1, 1) -> X on qubit 1
  - (0, 1) -> X on qubit 2
- Correction: apply X to the indicated qubit.

```python
def bitflip_decode_syndrome(s1: int, s2: int) -> int | None:
    table = {(0, 0): None, (1, 0): 0, (1, 1): 1, (0, 1): 2}
    return table[(s1, s2)]
```

## Phase-flip code
Same structure as bit-flip but in the Hadamard basis. Encoding uses
H on each qubit after the bit-flip encoding. Detects single Z errors.

## Shor 9-qubit code
Concatenates phase-flip and bit-flip codes; corrects one *arbitrary*
single-qubit Pauli error. Encoded states:

  |0_L> = (1/(2*sqrt(2))) (|000> + |111>)(|000> + |111>)(|000> + |111>)
  |1_L> = (1/(2*sqrt(2))) (|000> - |111>)(|000> - |111>)(|000> - |111>)

Stabilizer generators (8 total):
- Z1Z2, Z2Z3, Z4Z5, Z5Z6, Z7Z8, Z8Z9 (within-block bit-flip syndromes)
- X1X2X3X4X5X6, X4X5X6X7X8X9 (between-block phase-flip syndromes)

## Reference Python (syndrome lookup helper)

```python
SHOR_BIT_SYNDROMES = {
    (0, 0): None,
    (1, 0): 0,
    (1, 1): 1,
    (0, 1): 2,
}

def shor9_block_correction(s1: int, s2: int) -> int | None:
    return SHOR_BIT_SYNDROMES[(s1, s2)]
```

## Common pitfalls
- A "no error" syndrome does *not* certify the absence of error; it
  certifies that the syndrome subspace is consistent with no error.
- The bit-flip and phase-flip parts are corrected independently; do not
  apply the bit-flip correction to the entire 9-qubit register.
- Decoder lookup tables must enumerate *all* syndrome outcomes; missing
  entries are a common source of test failures.
