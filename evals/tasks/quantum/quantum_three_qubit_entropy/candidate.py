import itertools
import math


def density_from_state(state: list[float]) -> list[list[float]]:
    """Compute the density matrix rho = |psi><psi| from a state vector."""
    n = len(state)
    return [[state[i] * state[j] for j in range(n)] for i in range(n)]


def tensor_product(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
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


def _split_index(idx: int, dims: list[int]) -> list[int]:
    """Decompose a flat row-major index into per-subsystem indices."""
    parts = [0] * len(dims)
    for p in range(len(dims) - 1, -1, -1):
        parts[p] = idx % dims[p]
        idx //= dims[p]
    return parts


def _join_index(parts: list[int], dims: list[int]) -> int:
    """Compose per-subsystem indices into a flat row-major index."""
    idx = 0
    for p, d in zip(parts, dims):
        idx = idx * d + p
    return idx


def partial_trace(
    rho: list[list[float]], dims: list[int], trace_out: list[int]
) -> list[list[float]]:
    """
    Partial trace of a multi-partite density matrix.

    dims: dimensions of each subsystem in order (e.g. [2, 2, 2] for 3 qubits).
    trace_out: 0-based indices of the subsystems to trace out.
    Returns the reduced density matrix over the remaining subsystems, with
    rows/columns indexed by the kept subsystem dimensions in ascending order.
    """
    n = len(dims)
    kept = [i for i in range(n) if i not in trace_out]
    kept_dims = [dims[i] for i in kept]
    traced_dims = [dims[i] for i in trace_out]
    out_dim = 1
    for d in kept_dims:
        out_dim *= d
    result = [[0.0] * out_dim for _ in range(out_dim)]

    kept_vals = list(itertools.product(*(range(d) for d in kept_dims)))
    traced_vals = list(itertools.product(*(range(d) for d in traced_dims)))

    for kv_row in kept_vals:
        for kv_col in kept_vals:
            ri = _join_index(list(kv_row), kept_dims)
            ci = _join_index(list(kv_col), kept_dims)
            for tv in traced_vals:
                parts_row = [0] * n
                parts_col = [0] * n
                for ki, k in enumerate(kept):
                    parts_row[k] = kv_row[ki]
                    parts_col[k] = kv_col[ki]
                for ti, t in enumerate(trace_out):
                    parts_row[t] = tv[ti]
                    parts_col[t] = tv[ti]
                row = _join_index(parts_row, dims)
                col = _join_index(parts_col, dims)
                result[ri][ci] += rho[row][col]
    return result


def von_neumann_entropy(rho: list[list[float]], base: float = 2.0) -> float:
    """Compute S(rho) = -Tr(rho log_base(rho)) from a density matrix."""
    import numpy as np

    evals = np.linalg.eigvalsh(np.asarray(rho, dtype=complex))
    total = 0.0
    for lam in evals:
        if lam > 1e-12:
            total -= float(lam) * math.log(float(lam)) / math.log(base)
    return total
