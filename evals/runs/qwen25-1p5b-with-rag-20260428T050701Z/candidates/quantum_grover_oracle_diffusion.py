import math

def uniform_superposition(n_qubits: int) -> list[float]:
    n_states = 2 ** n_qubits
    return [1.0 / math.sqrt(n_states)] * n_states

def oracle(state: list[float], index: int) -> list[float]:
    """Flips the sign of the marked state."""
    marked_bit = state[index]
    state[index] *= -1
    return state

def diffusion(state: list[float]) -> list[float]:
    """Reflects the state about the uniform superposition."""
    mean = sum(state) / len(state)
    new_state = [2 * mean - val for val in state]
    return new_state

def grover_search(n_qubits: int, marked: int, iterations: int) -> list[float]:
    """Simulates Grover's algorithm using the given parameters."""
    state = uniform_superposition(n_qubits)
    for _ in range(iterations):
        for i in range(n_qubits):
            state[i] = oracle(state, i)
        state = diffusion(state)
    return state

# Test function to verify correctness
def test_grover_search():
    results = [
        {"n_qubits": 2, "marked": 3, "iterations": 1},
        {"n_qubits": 3, "marked": 5, "iterations": 2}
    ]
    
    for res in results:
        state = grover_search(res["n_qubits"], res["marked"], res["iterations"])
        print(f"Result for n_qubits={res['n_qubits']}, marked={res['marked']}, iterations={res['iterations']}:\n{state}\n")

test_grover_search()
