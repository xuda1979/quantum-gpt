from typing import List

def density_from_state(state: List[float]) -> List[List[float]]:
    return [[state[i] * state[j] for j in range(len(state))] for i in range(len(state))]

def tensor_product(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    dim_a = len(a)
    dim_b = len(b)
    result = [[0.0] * (dim_a * dim_b) for _ in range(dim_a * dim_b)]
    for i in range(dim_a):
        for j in range(dim_a):
            for k in range(dim_b):
                for l in range(dim_b):
                    result[i * dim_b + k][j * dim_b + l] = a[i][j] * b[k][l]
    return result

def partial_trace(rho: List[List[float]], dim_a: int, dim_b: int, trace_out: str) -> List[List[float]]:
    if trace_out == "B":
        reduced = [[0.0] * dim_a for _ in range(dim_a)]
        for i in range(dim_a):
            for j in range(dim_a):
                for k in range(dim_b):
                    reduced[i][j] += rho[i * dim_b + k][j * dim_b + k]
        return reduced
    if trace_out == "A":
        reduced = [[0.0] * dim_b for _ in range(dim_b)]
