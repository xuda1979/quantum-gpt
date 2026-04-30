# Density matrix eval API

For `quantum_density_matrix_partial_trace`, return one Python file with these
four public functions. Use plain lists only; do not import NumPy; do not run
self-tests at import time.

```python
def density_from_state(state):
    return [[x * y for y in state] for x in state]


def tensor_product(a, b):
    dim_a = len(a)
    dim_b = len(b)
    out = [[0.0] * (dim_a * dim_b) for _ in range(dim_a * dim_b)]
    for i in range(dim_a):
        for j in range(dim_a):
            for k in range(dim_b):
                for l in range(dim_b):
                    out[i * dim_b + k][j * dim_b + l] = a[i][j] * b[k][l]
    return out


def partial_trace(rho, dim_a, dim_b, trace_out):
    if trace_out == "B":
        out = [[0.0] * dim_a for _ in range(dim_a)]
        for i in range(dim_a):
            for j in range(dim_a):
                for k in range(dim_b):
                    out[i][j] += rho[i * dim_b + k][j * dim_b + k]
        return out
    if trace_out == "A":
        out = [[0.0] * dim_b for _ in range(dim_b)]
        for k in range(dim_b):
            for l in range(dim_b):
                for i in range(dim_a):
                    out[k][l] += rho[i * dim_b + k][i * dim_b + l]
        return out
    raise ValueError("trace_out must be 'A' or 'B'")


def purity(rho):
    return sum(rho[i][j] * rho[j][i] for i in range(len(rho)) for j in range(len(rho)))
```

Indexing is `A * dim_b + B`. Tracing out `"B"` returns subsystem A. Tracing
out `"A"` returns subsystem B.
