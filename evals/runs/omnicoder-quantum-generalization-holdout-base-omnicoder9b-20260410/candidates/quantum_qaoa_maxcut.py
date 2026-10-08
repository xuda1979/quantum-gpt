def maxcut_cost(bitstring: str, edges: list) -> int:
    """
    Calculate the MaxCut cost for a given bitstring and edge list.
    Cost is the number of edges connecting nodes with different values.
    """
    cost = 0
    for u, v in edges:
        val_u = int(bitstring[u])
        val_v = int(bitstring[v])
        if val_u != val_v:
            cost += 1
    return cost


def brute_force_maxcut(n: int, edges: list) -> tuple:
    """
    Brute force search for the maximum cut cost.
    Returns (bitstring, max_cost).
    """
    max_cost = -1
    best_bitstring = ""

    for i in range(2 ** n):
        # Convert integer to binary string of length n
        current_bitstring = format(i, f'0{n}b')
        current_cost = maxcut_cost(current_bitstring, edges)

        if current_cost > max_cost:
            max_cost = current_cost
            best_bitstring = current_bitstring

    return best_bitstring, max_cost


def qaoa_cost_landscape(n: int, edges: list) -> list:
    """
    Generate a list of (bitstring, cost) pairs sorted by cost descending.
    """
    landscape = []
    for i in range(2 ** n):
        bitstring = format(i, f'0{n}b')
        cost = maxcut_cost(bitstring, edges)
        landscape.append((bitstring, cost))

    # Sort by cost descending
    landscape.sort(key=lambda x: x[1], reverse=True)
    return landscape


# Expose functions for the test module
__all__ = ['maxcut_cost', 'brute_force_maxcut', 'qaoa_cost_landscape']
