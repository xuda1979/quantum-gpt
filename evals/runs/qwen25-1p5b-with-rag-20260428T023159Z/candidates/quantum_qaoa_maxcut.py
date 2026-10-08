from typing import List, Tuple, Union

# Define the MaxCut cost function
def maxcut_cost(bitstring: str, edges: List[Tuple[int, int]]) -> Union[float, int]:
    """
    Calculate the MaxCut cost based on the given bitstring and edges.
    
    :param bitstring: A string representation of the node labels.
    :param edges: A list of tuples representing the edges in the graph.
    :return: The calculated cost.
    """
    total_cost = 0.0
    for edge in edges:
        u, v, w = _edge_weight(edge)
        if int(bitstring[u]) != int(bitstring[v]):
            total_cost += w
    return int(total_cost) if float(total_cost).is_integer() else total_cost

# Helper function to convert an edge into its corresponding weight
def _edge_weight(edge: Tuple[int, int]) -> Tuple[int, int, float]:
    if len(edge) == 2:
        u, v = edge
        return u, v, 1.0
    if len(edge) == 3:
        u, v, w = edge
        return u, v, float(w)
    raise ValueError("MaxCut edges must be (u, v) or (u, v, weight)")

# Brute force method to find the maximum cut
def brute_force_maxcut(n: int, edges: List[Tuple[int, int]]) -> Tuple[str, int]:
    best_bitstring = ""
    best_cost = float('-inf')
    for perm in itertools.permutations(range(n)):
        current_cost = maxcut_cost("".join(map(str, perm)), edges)
