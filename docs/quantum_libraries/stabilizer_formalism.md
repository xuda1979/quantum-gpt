# Stabilizer formalism and tableau update

## Concept
A stabilizer state is the unique +1 eigenstate of a maximal abelian
subgroup of the n-qubit Pauli group. Any stabilizer state can be
described compactly by its stabilizer generators (a list of n Pauli
strings), or equivalently by a binary "tableau" of size 2n x (2n+1).

Stabilizer circuits are exactly the Clifford circuits: H, S, CNOT.
They can be simulated efficiently in O(n^2) per gate via the Aaronson-
Gottesman tableau algorithm.

## Tableau layout
Rows: 2n stabilizer generators (n destabilizers + n stabilizers).
Columns: 2n binary symplectic + 1 sign column.

For each row r:
- x bits: r[0:n]
- z bits: r[n:2n]
- sign:  r[2n] (1 means -)

A Pauli operator is X^x Z^z up to a global phase set by the sign bit.

## Update rules
- **H on qubit q**: swap x_q and z_q in every row; flip sign if x_q AND z_q in that row.
- **S on qubit q**: z_q ^= x_q; flip sign if x_q AND z_q in that row.
- **CNOT(c, t)**: x_t ^= x_c; z_c ^= z_t; flip sign if `x_c & z_t & (x_t ^ z_c ^ 1)`.

```python
def apply_h(tableau, n, q):
    for r in tableau:
        x = r[q]
        z = r[n + q]
        # sign update first, while we still have the original bits
        r[2 * n] ^= x & z
        r[q], r[n + q] = z, x


def apply_s(tableau, n, q):
    for r in tableau:
        x = r[q]
        z = r[n + q]
        r[2 * n] ^= x & z
        r[n + q] ^= x


def apply_cnot(tableau, n, c, t):
    for r in tableau:
        xc, xt = r[c], r[t]
        zc, zt = r[n + c], r[n + t]
        r[2 * n] ^= xc & zt & (xt ^ zc ^ 1)
        r[t] ^= xc
        r[n + c] ^= zt
```

## Common pitfalls
- The sign update uses *pre-update* bits; computing it after mutating
  the row is the most common bug.
- Destabilizer rows must be tracked alongside stabilizer rows even if
  you only care about the stabilizer subspace.
- Measurement is the trickiest gate: it requires distinguishing the
  deterministic vs random cases (whether any stabilizer anticommutes
  with the measured Pauli).
