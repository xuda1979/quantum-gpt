# Single-qubit and multi-qubit gate reference

## Standard single-qubit gates

| Symbol | Name | Matrix |
| --- | --- | --- |
| I | Identity | [[1,0],[0,1]] |
| X | Pauli-X (NOT) | [[0,1],[1,0]] |
| Y | Pauli-Y | [[0,-i],[i,0]] |
| Z | Pauli-Z | [[1,0],[0,-1]] |
| H | Hadamard | (1/sqrt(2)) [[1,1],[1,-1]] |
| S | Phase | [[1,0],[0,i]] |
| Sdg | S-dagger | [[1,0],[0,-i]] |
| T | pi/8 | [[1,0],[0,exp(i*pi/4)]] |
| Tdg | T-dagger | [[1,0],[0,exp(-i*pi/4)]] |

Rotation gates: Rx(t)=exp(-i*t/2 * X), Ry(t)=exp(-i*t/2 * Y),
Rz(t)=exp(-i*t/2 * Z). Closed forms:
- Rx(t) = [[cos(t/2), -i*sin(t/2)], [-i*sin(t/2), cos(t/2)]]
- Ry(t) = [[cos(t/2), -sin(t/2)], [sin(t/2), cos(t/2)]]
- Rz(t) = [[exp(-i*t/2), 0], [0, exp(i*t/2)]]

## Two-qubit gates

| Symbol | Name | Action |
| --- | --- | --- |
| CX (CNOT) | Controlled-X | flips target if control is |1> |
| CY | Controlled-Y | applies Y to target if control |1> |
| CZ | Controlled-Z | sign-flips |11> |
| SWAP | Swap | exchange qubit states |
| CH | Controlled-H | apply H to target conditioned on control |
| CRZ(t) | Controlled-Rz | applies Rz(t) on target if control |1> |

## Three-qubit gates

- **Toffoli (CCX/CCNOT)**: flips target if both controls are |1>.
- **Fredkin (CSWAP)**: swaps two targets if control is |1>.

## Casefold and alias normalization (very common in repair tasks)

Aliases that should canonicalize to a single symbol. After
`gate.strip().lower()` the lookup table is:

```
{
  "h": "H", "hadamard": "H",
  "x": "X", "pauli_x": "X", "not": "X",
  "y": "Y", "pauli_y": "Y",
  "z": "Z", "pauli_z": "Z",
  "s": "S", "phase": "S",
  "t": "T",
  "cx": "CX", "cnot": "CX", "controlled_x": "CX", "cnot_": "CX",
  "cy": "CY",
  "cz": "CZ",
  "swap": "SWAP",
  "ccx": "CCX", "toffoli": "CCX",
  "cswap": "CSWAP", "fredkin": "CSWAP",
}
```

Unknown aliases should raise `ValueError(f"unknown gate: {gate}")`.
Rules of thumb for canonicalization in tests:
1. `gate.strip().lower()` first
2. Look up in alias dict
3. Raise `ValueError` for misses (do *not* return the original token)
