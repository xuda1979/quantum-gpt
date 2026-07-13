# Reference implementation
def maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    """Return the cost of cutting an edge based on the input bitstring."""
    cost = 0
    for i, j in edges:
        if bitstring[i - 1] == bitstring[j - 1]:
            cost += 1
    return cost


def maxcut_cost_optimized(bitstring: str, edges: list[tuple[int, int]]) -> int:
    """Optimize the maxcut cost calculation using symmetry breaking."""
    cost = sum(
        int(bitstring[i - 1] == bitstring[j - 1]) * (-1) ** (i + j)
        for i, j in edges
    )
    return cost


def brute_force_maxcut(n: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    """Find the max-cut assignment with no symmetry breaks."""
    best_bitstring = ""
    best_cost = float("-inf")
    for bits in itertools.product("01", repeat=n):
        current_cost = maxcut_cost(bits, edges)
        if current_cost > best_cost:
            best_bitstring = bits
            best_cost = current_cost
    return best_bitstring, best_cost


def qaoa_cost_landscape(n: int, edges: list[tuple[int, int]], depth: int = 5) -> list[tuple[int, int]]:
    """Compute the QAOA cost landscape over depth."""
    landscape = []
    for depth in range(depth):
        cost = 0
        for i in range(n):
            for j in range(i + 1, n):
                cost += (-1) ** (depth + i + j) * bool(edges[i][j])
        landscape.append((depth, cost))
    return landscape
