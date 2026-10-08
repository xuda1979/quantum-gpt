from itertools import product


def maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    bits = str(bitstring)
    if any(bit not in {"0", "1"} for bit in bits):
        raise ValueError("bitstring must contain only 0 and 1")
    cost = 0
    for left, right in edges:
        if bits[left] != bits[right]:
            cost += 1
    return cost


def brute_force_maxcut(n_nodes: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    best = ""
    best_cost = -1
    for bits in product("01", repeat=n_nodes):
        bitstring = "".join(bits)
        cost = maxcut_cost(bitstring, edges)
        if cost > best_cost or (cost == best_cost and bitstring < best):
            best = bitstring
            best_cost = cost
    return best, best_cost


def qaoa_cost_landscape(n_nodes: int, edges: list[tuple[int, int]]) -> list[tuple[str, int]]:
    landscape = []
    for bits in product("01", repeat=n_nodes):
        bitstring = "".join(bits)
        landscape.append((bitstring, maxcut_cost(bitstring, edges)))
    landscape.sort(key=lambda item: (-item[1], item[0]))
    return landscape
