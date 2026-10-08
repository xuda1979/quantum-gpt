from itertools import product


def enumerate_bitstrings(n_nodes: int) -> list[str]:
    if n_nodes <= 0:
        raise ValueError("n_nodes must be positive")
    return ["".join(bits) for bits in product("01", repeat=n_nodes)]


def cut_value(bitstring: str, edges: list[tuple[int, int]]) -> int:
    if any(bit not in {"0", "1"} for bit in bitstring):
        raise ValueError("bitstring must contain only 0/1")
    total = 0
    for left, right in edges:
        if bitstring[left] != bitstring[right]:
            total += 1
    return total


def best_cut_assignment(n_nodes: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    best_bits = ""
    best_cost = -1
    for bitstring in enumerate_bitstrings(n_nodes):
        cost = cut_value(bitstring, edges)
        if cost > best_cost or (cost == best_cost and (not best_bits or bitstring < best_bits)):
            best_bits = bitstring
            best_cost = cost
    return best_bits, best_cost
