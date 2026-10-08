import itertools


def maxcut_cost(bitstring, edges):
    """
    Calculates the MaxCut cost for a given bitstring configuration.
    The cost is the number of edges (u, v) such that bitstring[u] != bitstring[v].
    """
    cost = 0
    for u, v in edges:
        if bitstring[u] != bitstring[v]:
            cost += 1
    return cost

def brute_force_maxcut(n, edges):
    """
    Finds the maximum cut value and the corresponding bitstring using brute force.
    """
    max_val = -1
    best_bs = ""

    # Iterate through all possible bitstrings of length n
    for bits in itertools.product('01', repeat=n):
        bs = "".join(bits)
        current_cost = maxcut_cost(bs, edges)
        if current_cost > max_val:
            max_val = current_cost
            best_bs = bs

    return best_bs, max_val

def qaoa_cost_landscape(n, edges):
    """
    Returns a list of (bitstring, cost) tuples for all possible configurations,
    sorted by cost in descending order.
    """
    landscape = []
    for bits in itertools.product('01', repeat=n):
        bs = "".join(bits)
        cost = maxcut_cost(bs, edges)
        landscape.append((bs, cost))

    # Sort by cost descending
    landscape.sort(key=lambda x: x[1], reverse=True)
    return landscape
