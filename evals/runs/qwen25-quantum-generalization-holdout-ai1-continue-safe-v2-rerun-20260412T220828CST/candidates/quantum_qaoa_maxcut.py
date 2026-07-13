# Reference implementation


def maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    """Compute the maximum cut cost for a given bipartition."""
    cost = 0
    for i, j in edges:
        if (bitstring[i - 1] + bitstring[j - 1]) % 2 == 0:
            cost += 1
    return cost


class QAOACostLandscape:
    def __init__(self, num_nodes: int, edges: list[tuple[int, int]]):
        self.num_nodes = num_nodes
        self.edges = edges
        self.costs = {}

    def add(self, bitstring: str):
        key = tuple(int(b) for b in bitstring.strip())
        self.costs[key] = maxcut_cost(key, self.edges)

    def sort_by_cost_descending(self):
        return [
            (key, value)
            for key, value in self.costs.items()
            if key in self.costs
        ]

    @property
    def size(self):
        return len(self.costs)


def qaoa_cost_landscape(num_qubits: int, edges: list[tuple[int, int]]) -> QAOACostLandscape:
    """Return the QAOA cost landscape for a problem instance."""
    return QAOACostLandscape(num_qubits, edges)


def brute_force_maxcut(n: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    """Brute force search for the maximum cut assignment."""
    best_bitstring = ""
    best_cost = float("-inf")
    for bits in itertools.product([0, 1], repeat=n):
        cost = maxcut_cost(bits, edges)
        if cost > best_cost:
            best_cost = cost
            best_bitstring = "".join(map(str, bits))
    return best_bitstring, best_cost
