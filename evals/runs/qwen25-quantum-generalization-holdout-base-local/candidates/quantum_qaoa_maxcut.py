from typing import List, Tuple

def maxcut_cost(bitstring: str, edges: List[Tuple[int, int]]) -> int:
    cost = 0
    for u, v in edges:
        if bitstring[u] != bitstring[v]:
            cost += 1
    return cost

def brute_force_maxcut(n_nodes: int, edges: List[Tuple[int, int]]) -> Tuple[str, int]:
    best_bs = "0" * n_nodes
    best_cost = 0
    for i in range(1 << n_nodes):
        bs = format(i, f"0{n_nodes}b")
        c = maxcut_cost(bs, edges)
        if c > best_cost:
            best_cost = c
            best_bs = bs
    return (best_bs, best_cost)

def qaoa_cost_landscape(n_nodes: int, edges: List[Tuple[int, int]]) -> List[Tuple[str, int]]:
    results = []
    for i in range(1 << n_nodes):
        bs = format(i, f"0{n_nodes}b")
        results.append((bs, maxcut_cost(bs, edges)))
    results.sort(key=lambda x: (-x[1], x[0]))
    return results
