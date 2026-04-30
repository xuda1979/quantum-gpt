# Density matrices and partial trace

## Evaluation-facing single-file API

Small no-dependency eval tasks often expect plain Python lists rather than
NumPy arrays. Use these public function names and signatures when the tests ask
for density-matrix utilities:

Do not import NumPy for this eval-style API. Return nested Python lists and
avoid writing self-tests or calling test functions at module import time.

```python
def density_from_state(state: list[float]) -> list[list[float]]:
    return [[state[i] * state[j] for j in range(len(state))] for i in range(len(state))]


def tensor_product(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    dim_a = len(a)
    dim_b = len(b)
    result = [[0.0] * (dim_a * dim_b) for _ in range(dim_a * dim_b)]
    for i in range(dim_a):
        for j in range(dim_a):
            for k in range(dim_b):
                for l in range(dim_b):
                    result[i * dim_b + k][j * dim_b + l] = a[i][j] * b[k][l]
    return result


def partial_trace(
    rho: list[list[float]], dim_a: int, dim_b: int, trace_out: str
) -> list[list[float]]:
    if trace_out == "B":
        reduced = [[0.0] * dim_a for _ in range(dim_a)]
        for i in range(dim_a):
            for j in range(dim_a):
                for k in range(dim_b):
                    reduced[i][j] += rho[i * dim_b + k][j * dim_b + k]
        return reduced
    if trace_out == "A":
        reduced = [[0.0] * dim_b for _ in range(dim_b)]
        for k in range(dim_b):
            for l in range(dim_b):
                for i in range(dim_a):
                    reduced[k][l] += rho[i * dim_b + k][i * dim_b + l]
        return reduced
    raise ValueError("trace_out must be 'A' or 'B'")


def purity(rho: list[list[float]]) -> float:
    return sum(rho[i][j] * rho[j][i] for i in range(len(rho)) for j in range(len(rho)))
```

For real-valued educational states the simple `state[i] * state[j]` outer
product is enough. For complex states, use the conjugate in the bra entry:
`state[i] * state[j].conjugate()`.

## Density matrix
For a pure state |psi>, the density matrix is rho = |psi><psi|. For a
mixed state, rho = sum_i p_i |psi_i><psi_i|. Properties:

- Hermitian: rho = rho^dagger
- Positive semidefinite: rho >= 0
- Unit trace: Tr(rho) = 1

For a NumPy state vector `psi` of length 2^n, `rho = np.outer(psi, psi.conj())`.
For repository eval tasks that pass plain Python lists, do not call
`state.conj()` or `.reshape()` on the input list; either use list loops or first
convert to a NumPy array. The safest eval answer is the plain-Python API below.

## Partial trace
For a bipartite system AB with state rho_AB, the reduced density matrix
on A is rho_A = Tr_B(rho_AB). In matrix elements:

  rho_A[i, j] = sum_k rho_AB[i*d_B + k, j*d_B + k]

where d_B = dim(H_B). This is the canonical "trace out subsystem B"
formula assuming the *first* subsystem is A and the *second* is B.

## Reference numpy

For array-based code, reshape a bipartite density matrix to
`rho4[a, b, a2, b2]` with shape `(dim_a, dim_b, dim_a, dim_b)`. The canonical
trace over subsystem B is `np.einsum("aibi->ab", rho4)`, returning the reduced
matrix on A. The canonical trace over subsystem A is
`np.einsum("aibj->ij", rho4)`, returning the reduced matrix on B.

## Properties to verify
- `Tr(partial_trace(rho)) == 1` (within numerical tolerance)
- `partial_trace(rho)` is Hermitian: `rho_A == rho_A.conj().T`
- For a pure product state `rho_A = |a><a|` is rank-1.
- For a maximally entangled state, the reduced state is I/d.

## Library snippets
- `qiskit.quantum_info.partial_trace(state, qargs)`
- `cirq.partial_trace(state, keep_indices)`
- `pennylane.math.reduce_dm(rho, indices)`

## Common pitfalls
- Index ordering: many libraries use little-endian, so qubit 0 might be
  the *least* significant index. Test fixtures usually clarify.
- Forgetting to reshape to a 4-tensor before the einsum is the most
  common bug.
