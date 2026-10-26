from typing import Optional

import numpy as np


def grover_oracle(n: int, target: int) -> np.ndarray:
    """
    Create a Grover oracle operator for n qubits that marks the target state.

    Args:
        n: Number of qubits
        target: Target state index (0 to 2^n - 1)

    Returns:
        Oracle operator as a 2^n x 2^n matrix
    """
    dim = 2**n
    oracle = np.eye(dim, dtype=complex)
    oracle[target, target] = -1
    return oracle


def grover_diffusion(n: int) -> np.ndarray:
    """
    Create the Grover diffusion operator for n qubits.

    The diffusion operator is: 2|s><s| - I, where |s> is the uniform superposition state.

    Args:
        n: Number of qubits

    Returns:
        Diffusion operator as a 2^n x 2^n matrix
    """
    dim = 2**n
    # Uniform superposition state
    s = np.ones(dim, dtype=complex) / np.sqrt(dim)
    # 2|s><s| - I
    diffusion = 2 * np.outer(s, s.conj()) - np.eye(dim, dtype=complex)
    return diffusion


def grover_iteration(n: int, target: int) -> np.ndarray:
    """
    Create a single Grover iteration operator (diffusion * oracle).

    Args:
        n: Number of qubits
        target: Target state index

    Returns:
        Grover iteration operator as a 2^n x 2^n matrix
    """
    oracle = grover_oracle(n, target)
    diffusion = grover_diffusion(n)
    return diffusion @ oracle


def grover_search(n: int, target: int, num_iterations: Optional[int] = None) -> np.ndarray:
    """
    Simulate Grover's search algorithm.

    Args:
        n: Number of qubits
        target: Target state index
        num_iterations: Number of Grover iterations. If None, uses optimal number.

    Returns:
        Final state vector after Grover iterations
    """
    dim = 2**n
    if num_iterations is None:
        # Optimal number of iterations: pi/4 * sqrt(N)
        num_iterations = int(np.round(np.pi / 4 * np.sqrt(dim)))

    # Initial state: uniform superposition
    state = np.ones(dim, dtype=complex) / np.sqrt(dim)

    oracle = grover_oracle(n, target)
    diffusion = grover_diffusion(n)

    for _ in range(num_iterations):
        state = oracle @ state
        state = diffusion @ state

    return state


def grover_search_probability(n: int, target: int, num_iterations: Optional[int] = None) -> float:
    """
    Simulate Grover's search and return the probability of measuring the target state.

    Args:
        n: Number of qubits
        target: Target state index
        num_iterations: Number of Grover iterations. If None, uses optimal number.

    Returns:
        Probability of measuring the target state
    """
    state = grover_search(n, target, num_iterations)
    return float(np.abs(state[target]) ** 2)


def grover_search_all_probabilities(
    n: int, target: int, num_iterations: Optional[int] = None
) -> np.ndarray:
    """
    Simulate Grover's search and return the probability distribution over all states.

    Args:
        n: Number of qubits
        target: Target state index
        num_iterations: Number of Grover iterations. If None, uses optimal number.

    Returns:
        Array of probabilities for each state
    """
    state = grover_search(n, target, num_iterations)
    return np.abs(state) ** 2


def grover_search_multiple_targets(n: int, targets: list[int]) -> np.ndarray:
    """
    Create a Grover oracle for multiple target states.

    Args:
        n: Number of qubits
        targets: List of target state indices

    Returns:
        Oracle operator as a 2^n x 2^n matrix
    """
    dim = 2**n
    oracle = np.eye(dim, dtype=complex)
    for target in targets:
        oracle[target, target] = -1
    return oracle


def grover_search_multiple(
    n: int, targets: list[int], num_iterations: Optional[int] = None
) -> np.ndarray:
    """
    Simulate Grover's search with multiple target states.

    Args:
        n: Number of qubits
        targets: List of target state indices
        num_iterations: Number of Grover iterations. If None, uses optimal number.

    Returns:
        Final state vector after Grover iterations
    """
    dim = 2**n
    if num_iterations is None:
        # Optimal number of iterations for multiple targets
        num_targets = len(targets)
        num_iterations = int(np.round(np.pi / 4 * np.sqrt(dim / num_targets)))

    # Initial state: uniform superposition
    state = np.ones(dim, dtype=complex) / np.sqrt(dim)

    oracle = grover_search_multiple_targets(n, targets)
    diffusion = grover_diffusion(n)

    for _ in range(num_iterations):
        state = oracle @ state
        state = diffusion @ state

    return state


def grover_search_multiple_probability(
    n: int, targets: list[int], num_iterations: Optional[int] = None
) -> float:
    """
    Simulate Grover's search with multiple targets and return the total probability of measuring any target.

    Args:
        n: Number of qubits
        targets: List of target state indices
        num_iterations: Number of Grover iterations. If None, uses optimal number.

    Returns:
        Total probability of measuring any target state
    """
    state = grover_search_multiple(n, targets, num_iterations)
    total_prob = 0.0
    for target in targets:
        total_prob += float(np.abs(state[target]) ** 2)
    return total_prob
