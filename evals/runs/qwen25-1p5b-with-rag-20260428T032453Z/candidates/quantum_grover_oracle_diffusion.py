import numpy as np

def uniform_superposition(qubits):
    """Return a uniform superposition of qubits."""
    n = 2**len(qubits)
    return np.array([(1/n)**(i//n) for i in range(n)], dtype=np.complex128)

def oracle(state, marked_index):
    """Apply the Grover oracle to the given state."""
    n = len(state)
    if marked_index >= n:
        raise ValueError("Marked index exceeds the size of the system.")
    
    flipped_amplitude = -state[marked_index]
    return np.where(np.arange(n) == marked_index, flipped_amplitude, state)

def diffusion(state):
    """Apply the Grover diffusion operator to the given state."""
    n = len(state)
    mean = sum(state) / n
    return 2 * mean - state

def grover_search(n_qubits, marked_indices, iterations=None):
    """Simulate Grover's search algorithm."""
    state = uniform_superposition(range(n_qubits))
    if iterations is None:
        M = max(len(marked_indices), 1)
        iterations = int(round((math.pi / 4) * math.sqrt(n_qubits / M)))
    
    for _ in range(iterations):
        for marked in marked_indices:
            state[marked] *= -1
        
        mean = state.mean()
        state = 2 * mean - state
    
    return state

# Test function
def test_grover_search():
    from itertools import combinations
    from random import randint
    
    def generate_test_case(n_qubits, marked_count):
        marked_indices = []
        while len(marked_indices) < marked_count:
            index = randint(0, 2**(n_qubits-1)-1)
            if index not in marked_indices:
                marked_indices.append(index)
        
        return n_qubits, marked_indices
    
    results = {}
