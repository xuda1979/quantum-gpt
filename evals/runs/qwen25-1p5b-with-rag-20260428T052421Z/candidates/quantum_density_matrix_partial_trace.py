from typing import List

def density_from_state(state: List[float]) -> List[List[float]]:
    return [[x * y for y in state] for x in state]

def tensor_product(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    dim_a = len(a)
    dim_b = len(b)
    out = [[0.0] * (dim_a * dim_b) for _ in range(dim_a * dim_b)]
    for i in range(dim_a):
        for j in range(dim_a):
            for k in range(dim_b):
                for l in range(dim_b):
                    out[i * dim_b + k][j * dim_b + l] = a[i][j] * b[k][l]
    return out

def partial_trace(rho: List[List[float]], dim_a: int, dim_b: int, trace_out: str) -> List[List[float]]:
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

def purity(rho: List[List[float]]) -> float:
    return sum(rho[i][j] * rho[j][i] for i in range(len(rho)) for j in range(len(rho)))

if __name__ == "__main__":
    result = run_tests(__file__)
    print(result)
