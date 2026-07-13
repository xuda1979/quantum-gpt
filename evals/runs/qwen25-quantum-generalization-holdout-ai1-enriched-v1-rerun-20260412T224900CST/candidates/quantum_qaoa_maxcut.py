# Reference implementation
def maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    """Return the maximum cut cost of a graph with given edges."""
    cost = 0
    for i, j in edges:
        if bitstring[i - 1] == bitstring[j - 1]:
            cost += 1
    return cost


def brute_force_maxcut(n: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    """Brute force find the max-cut assignment and its cost."""
    from itertools import product

    best_bitstring = ""
    best_cost = float("-inf")
    for bits in product("01", repeat=n):
        cost = maxcut_cost(bits, edges)
        if cost > best_cost:
            best_cost = cost
            best_bitstring = "".join(bits)
    return best_bitstring, best_cost


def qaoa_cost_landscape(depth: int, edges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return the cost landscape for QAOA at depth=depth."""
    from qaoa import qaoa_cost_matrix

    return [
        (i + 1, qaoa_cost_matrix(depth, len(edges), i))
        for i in range(len(edges))
    ]
