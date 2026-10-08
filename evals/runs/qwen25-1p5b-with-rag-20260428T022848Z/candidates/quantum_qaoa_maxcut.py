from typing import List, Tuple, Union

def _edge_weight(edge: tuple) -> Tuple[int, int, float]:
    """Accept either unweighted (u, v) or weighted (u, v, w) edges."""
    if len(edge) == 2:
        u, v = edge
        return u, v, 1.0
    if len(edge) == 3:
        u, v, w = edge
        return u, v, float(w)
    raise ValueError("MaxCut edges must be (u, v) or (u, v, weight)")

def maxcut_cost(bitstring: str, edges: List[Tuple[int, int]]) -> Union[int, float]:
    total = 0.0
    for edge in edges:
        u, v, w = _edge_weight(edge)
        if int(bitstring[u]) != int(bitstring[v]):
            total += w
    return int(total) if float(total).is_integer() else total

def brute_force_maxcut(n: int, edges: List[Tuple[int, int]]) -> Tuple[str, int]:
    from itertools import product
    best_bitstring = ""
    best_cost = float('-inf')
    for bits in product([0, 1], repeat=n):
        current_cost = maxcut_cost(bits, edges)
        if current_cost > best_cost:
            best_cost = current_cost
            best_bitstring = ''.join(map(str, bits))
    return best_bitstring, best_cost
