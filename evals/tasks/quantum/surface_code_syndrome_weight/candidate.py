def manhattan_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Manhattan distance between two defect coordinates on the surface code
    syndrome lattice."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def pair_defects_min_weight(defects: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Pair an even number of defects to minimize total Manhattan distance.

    Returns a list of (i, j) index pairs into `defects` such that each defect
    appears in exactly one pair. Uses a brute-force search over all perfect
    matchings (suitable for small numbers of defects, n <= 10).
    """
    n = len(defects)
    if n == 0:
        return []
    if n % 2 != 0:
        raise ValueError("number of defects must be even")

    best_pairs = None
    best_cost = None

    def recurse(remaining: list[int], pairs: list[tuple[int, int]], cost: int):
        nonlocal best_pairs, best_cost
        if not remaining:
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_pairs = list(pairs)
            return
        first = remaining[0]
        for k in range(1, len(remaining)):
            other = remaining[k]
            d = manhattan_distance(defects[first], defects[other])
            new_remaining = [remaining[i] for i in range(len(remaining)) if i not in (0, k)]
            pairs.append((first, other))
            recurse(new_remaining, pairs, cost + d)
            pairs.pop()

    recurse(list(range(n)), [], 0)
    return best_pairs or []


def total_pairing_weight(defects: list[tuple[int, int]], pairs: list[tuple[int, int]]) -> int:
    """Compute total Manhattan weight of a defect pairing."""
    total = 0
    for i, j in pairs:
        total += manhattan_distance(defects[i], defects[j])
    return total
