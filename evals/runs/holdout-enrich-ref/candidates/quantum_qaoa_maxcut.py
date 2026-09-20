def maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    """Compute the MaxCut cost for a given bitstring and edge list.

    An edge (u, v) contributes 1 to the cost if bitstring[u] != bitstring[v].
    """
    cost = 0
    for u, v in edges:
        if bitstring[u] != bitstring[v]:
            cost += 1
    return cost


def brute_force_maxcut(n_nodes: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    """Find the optimal MaxCut by exhaustive search over all 2^n bitstrings.

    Returns (best_bitstring, best_cost). Ties broken by lexicographically smallest bitstring.
    """
    best_bs = "0" * n_nodes
    best_cost = 0
    for i in range(1 << n_nodes):
        bs = format(i, f"0{n_nodes}b")
        c = maxcut_cost(bs, edges)
        if c > best_cost:
            best_cost = c
            best_bs = bs
    return (best_bs, best_cost)


def qaoa_cost_landscape(n_nodes: int, edges: list[tuple[int, int]]) -> list[tuple[str, int]]:
    """Return all bitstrings and their MaxCut costs, sorted descending by cost.

    Each entry is (bitstring, cost). Secondary sort: lexicographic ascending on bitstring.
    """
    results = []
    for i in range(1 << n_nodes):
        bs = format(i, f"0{n_nodes}b")
        results.append((bs, maxcut_cost(bs, edges)))
    results.sort(key=lambda x: (-x[1], x[0]))
    return results
