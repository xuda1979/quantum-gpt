from __future__ import annotations


def cut_size(spins: tuple[int, ...] | list[int], edges: list[tuple[int, int]]) -> int:
    normalized = tuple(spins)
    if any(spin not in (-1, 1) for spin in normalized):
        raise ValueError("spins must only contain -1 or 1")

    size = 0
    for left, right in edges:
        if normalized[left] != normalized[right]:
            size += 1
    return size


def rank_ising_assignments(
    n_nodes: int, edges: list[tuple[int, int]]
) -> list[tuple[tuple[int, ...], int]]:
    ranked: list[tuple[tuple[int, ...], int]] = []
    for mask in range(1 << n_nodes):
        spins = tuple(1 if (mask >> index) & 1 else -1 for index in range(n_nodes))
        ranked.append((spins, cut_size(spins, edges)))
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return ranked


def best_ising_assignment(
    n_nodes: int, edges: list[tuple[int, int]]
) -> tuple[tuple[int, ...], int]:
    return rank_ising_assignments(n_nodes, edges)[0]
