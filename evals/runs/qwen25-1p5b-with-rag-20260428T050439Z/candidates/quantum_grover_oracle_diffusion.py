import math

def uniform_superposition(n_qubits: int) -> list[float]:
    n_states = 2 ** n_qubits
    return [1.0 / math.sqrt(n_states)] * n_states

def oracle(state: list[float], index: int) -> list[float]:
    """Flips the sign of the marked state."""
    if index >= len(state):
        raise ValueError("Index out of bounds.")
    state[index] *= -1
    return state

def diffusion(state: list[float]) -> list[float]:
    """Reflects the state about the uniform superposition."""
    mean = sum(state) / len(state)
    return [2 * mean - s for s in state]

def grover_search(n_qubits: int, marked: list[int], iters: int | None = None) -> list[float]:
    state = uniform_superposition(n_qubits)
    if iters is None:
        M = max(len(marked), 1)
        iters = max(1, int(round((math.pi / 4) * math.sqrt(n_qubits / M))))
    for _ in range(iters):
        for m in marked:
            state[m] *= -1
        mean = sum(state) / len(state)
        state = [2 * mean - s for s in state]
    return state
