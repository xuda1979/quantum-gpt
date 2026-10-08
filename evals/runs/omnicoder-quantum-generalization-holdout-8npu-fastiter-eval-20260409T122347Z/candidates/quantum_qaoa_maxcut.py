# Reference implementation
def maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    """Count cut edges for a given bitstring assignment."""
    if len(bitstring) != len(set(bitstring)):
        raise ValueError("bitstring length must match number of nodes")
    return sum(
        int(bitstring[u]) != int(bitstring[v])
        for u, v in edges
    )


def brute_force_maxcut(n_nodes: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    """Return the best bitstring and its cut size for n_nodes."""
    best = ""
    best_cost = -1
    for raw in format(2 ** n_nodes - 1, f"0{n_nodes}b"):
        cost = maxcut_cost(raw, edges)
        if cost > best_cost:
            best_cost = cost
            best = raw
    return best, best_cost


def qaoa_cost_landscape(n_nodes: int, edges: list[tuple[int, int]]) -> list[tuple[str, int]]:
    """Return all bitstring/cost pairs sorted by cost descending."""
    return sorted(
        (raw, maxcut_cost(raw, edges))
        for raw in format(2 ** n_nodes - 1, f"0{n_nodes}b")
    )
