from typing import List, Tuple

def density_from_state(state: List[float]) -> List[List[float]]:
    """Compute the density matrix rho = |psi><psi| from a state vector."""
    n = len(state)
    return [[state[i] * state[j] for j in range(n)] for i in range(n)]

def tensor_product(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    """Compute the Kronecker (tensor) product of two square matrices."""
    da = len(a)
    db = len(b)
    size = da * db
    result = [[0.0] * size for _ in range(size)]
    for i in range(da):
        for j in range(da):
            for k in range(db):
                for l in range(db):
                    result[i * db + k][j * db + l] = a[i][j] * b[k][l]
    return result

def partial_trace(rho: List[List[float]], dim_a: int, dim_b: int, trace_out: str) -> List[List[float]]:
    """
    Compute the partial trace of a bipartite density matrix.

    rho: (dim_a * dim_b) x (dim_a * dim_b) density matrix
    trace_out: 'A' to trace out subsystem A, 'B' to trace out subsystem B
    """
    if trace_out == "B":
        # Trace out B -> result is dim_a x dim_a
        result = [[0.0] * dim_a for _ in range(dim_a)]
        for i in range(dim_a):
            for j in range(dim_a):
                for k in range(dim_b):
                    result[i][j] += rho[i * dim_b + k][j * dim_b + k]
        return result
