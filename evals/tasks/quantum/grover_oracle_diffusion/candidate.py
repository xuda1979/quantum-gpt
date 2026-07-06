import math


def uniform_superposition(n_qubits: int) -> list[float]:
    """Return the uniform superposition state for n qubits."""
    n = 2 ** n_qubits
    amp = 1.0 / math.sqrt(n)
    return [amp] * n


def oracle(state: list[float], marked: int) -> list[float]:
    """Apply the Grover oracle: flip the sign of the marked basis state."""
    result = list(state)
    result[marked] = -result[marked]
    return result


def diffusion(state: list[float]) -> list[float]:
    """Apply the Grover diffusion operator: 2|s><s| - I."""
    n = len(state)
    mean = sum(state) / n
    return [2 * mean - a for a in state]


def grover_search(n_qubits: int, marked: int, iterations: int) -> list[float]:
    """Run Grover's search algorithm for a given number of iterations."""
    state = uniform_superposition(n_qubits)
    for _ in range(iterations):
        state = oracle(state, marked)
        state = diffusion(state)
    return state
