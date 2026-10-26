import numpy as np
from scipy.linalg import expm


def trotterize_hamiltonian(hamiltonian_terms, dt, num_steps, num_trotter_steps):
    """
    Trotterized Hamiltonian time evolution.

    Parameters:
    -----------
    hamiltonian_terms : list of (operator, coefficient) tuples
        Each operator is a 2D numpy array (unitary or Hermitian), and coefficient is a scalar.
        The Hamiltonian is H = sum_i coefficient_i * operator_i
    dt : float
        Total time step for evolution
    num_steps : int
        Number of time steps
    num_trotter_steps : int
        Number of Trotter steps per time step

    Returns:
    --------
    list of 2D numpy arrays
        The state after each time step (or the evolution operator)
    """
    dim = hamiltonian_terms[0][0].shape[0]
    identity = np.eye(dim, dtype=complex)

    # Total time per Trotter step
    dt_trotter = dt / num_trotter_steps

    # Build the Trotterized evolution operator for one time step
    # U_trotter = prod_i exp(-i * dt_trotter * coefficient_i * operator_i)
    trotter_operator = np.eye(dim, dtype=complex)

    for op, coeff in hamiltonian_terms:
        # Compute exp(-i * dt_trotter * coeff * op)
        exponent = -1j * dt_trotter * coeff * op
        term = expm(exponent)
        trotter_operator = term @ trotter_operator

    # Apply num_trotter_steps times to get one full time step evolution
    full_step_operator = np.linalg.matrix_power(trotter_operator, num_trotter_steps)

    # Return the evolution operator for one time step
    # If we need to apply to a state, we can do so externally
    return full_step_operator


def trotterize_hamiltonian_evolution(
    hamiltonian_terms, initial_state, dt, num_steps, num_trotter_steps
):
    """
    Trotterized Hamiltonian time evolution applied to an initial state.

    Parameters:
    -----------
    hamiltonian_terms : list of (operator, coefficient) tuples
        Each operator is a 2D numpy array, and coefficient is a scalar.
        The Hamiltonian is H = sum_i coefficient_i * operator_i
    initial_state : 1D numpy array
        Initial quantum state
    dt : float
        Total time step for evolution
    num_steps : int
        Number of time steps
    num_trotter_steps : int
        Number of Trotter steps per time step

    Returns:
    --------
    list of 1D numpy arrays
        The state after each time step
    """
    dim = hamiltonian_terms[0][0].shape[0]

    # Total time per Trotter step
    dt_trotter = dt / num_trotter_steps

    state = initial_state.copy()
    states = [state.copy()]

    for step in range(num_steps):
        # Apply num_trotter_steps of Trotterized evolution
        for _ in range(num_trotter_steps):
            for op, coeff in hamiltonian_terms:
                exponent = -1j * dt_trotter * coeff * op
                term = expm(exponent)
                state = term @ state

        states.append(state.copy())

    return states


def trotterize_hamiltonian(hamiltonian_terms, dt, num_steps, num_trotter_steps):
    """
    Trotterized Hamiltonian time evolution.

    Parameters:
    -----------
    hamiltonian_terms : list of (operator, coefficient) tuples
        Each operator is a 2D numpy array, and coefficient is a scalar.
        The Hamiltonian is H = sum_i coefficient_i * operator_i
    dt : float
        Total time step for evolution
    num_steps : int
        Number of time steps
    num_trotter_steps : int
        Number of Trotter steps per time step

    Returns:
    --------
    2D numpy array
        The evolution operator for the full time evolution
    """
    dim = hamiltonian_terms[0][0].shape[0]

    # Total time per Trotter step
    dt_trotter = dt / num_trotter_steps

    # Build the Trotterized evolution operator for one Trotter step
    trotter_operator = np.eye(dim, dtype=complex)

    for op, coeff in hamiltonian_terms:
        exponent = -1j * dt_trotter * coeff * op
        term = expm(exponent)
        trotter_operator = term @ trotter_operator

    # Apply num_trotter_steps times to get one full time step evolution
    full_step_operator = np.linalg.matrix_power(trotter_operator, num_trotter_steps)

    # Apply num_steps times for total evolution
    total_evolution = np.linalg.matrix_power(full_step_operator, num_steps)

    return total_evolution
