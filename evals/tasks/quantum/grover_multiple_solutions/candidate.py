import math


def optimal_grover_iterations(n_items: int, n_marked: int) -> int:
    """Return the optimal integer number of Grover iterations for a search
    space of `n_items` with `n_marked` solutions.

    The optimal continuous rotation count is
        theta = arcsin(sqrt(n_marked / n_items))
        R*   = (pi / 4) / theta - 1/2

    Return the nearest integer (round half to even via Python's round).
    """
    if n_items <= 0:
        raise ValueError("n_items must be positive")
    if n_marked <= 0 or n_marked > n_items:
        raise ValueError("n_marked must be in 1..n_items")
    ratio = n_marked / n_items
    if ratio >= 1.0:
        return 0
    theta = math.asin(math.sqrt(ratio))
    r_star = math.pi / (4 * theta) - 0.5
    return int(round(r_star))


def grover_success_probability(n_items: int, n_marked: int, iterations: int) -> float:
    """Compute the success probability after `iterations` Grover steps.

    P = sin^2((2*iterations + 1) * theta), with sin(theta) = sqrt(M/N).
    """
    if n_items <= 0:
        raise ValueError("n_items must be positive")
    if n_marked <= 0 or n_marked > n_items:
        raise ValueError("n_marked must be in 1..n_items")
    theta = math.asin(math.sqrt(n_marked / n_items))
    return math.sin((2 * iterations + 1) * theta) ** 2
