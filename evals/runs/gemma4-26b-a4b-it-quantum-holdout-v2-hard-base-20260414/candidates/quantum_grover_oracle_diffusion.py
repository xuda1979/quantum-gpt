import math


def uniform_superposition(n_qubits):
    """Returns the state vector for a uniform superposition of n qubits."""
    n = 2**n_qubits
    amplitude = 1.0 / math.sqrt(n)
    return [amplitude] * n

def oracle(state, marked_index):
    """Flips the sign of the amplitude at the marked_index."""
    new_state = list(state)
    new_state[marked_index] = -new_state[marked_index]
    return new_state

def diffusion(state):
    """Applies the Grover diffusion operator: 2|s><s| - I."""
    n = len(state)
    mean = sum(state) / n
    # The operator 2|s><s| - I applied to a state |psi> results in:
    # 2 * <s|psi> |s> - |psi>
    # Since |s> is the uniform superposition [1/sqrt(n), ..., 1/sqrt(n)],
    # <s|psi> = sum(state) / sqrt(n)
    # The i-th component is: 2 * (sum(state)/sqrt(n)) * (1/sqrt(n)) - state[i]
    # = 2 * sum(state)/n - state[i]
    return [2 * mean - x for x in state]

def grover_search(n_qubits, marked, iterations):
    """Performs the Grover search algorithm."""
    state = uniform_superposition(n_qubits)
    for _ in range(iterations):
        state = oracle(state, marked)
        state = diffusion(state)
    return state
