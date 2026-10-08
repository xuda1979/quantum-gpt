import math

def ghz_state(n_qubits: int) -> list[float]:
    """
    Construct the n-qubit GHZ state: (|00...0> + |11...1>) / sqrt(2).
    Returns a list of 2^n real amplitudes.
    """
    dim = 2 ** n_qubits
    state = [0.0] * dim
    amp = 1.0 / math.sqrt(2)
    state[0] = amp          # |00...0>
    state[dim - 1] = amp    # |11...1>
    return state

def w_state(n_qubits: int) -> list[float]:
    """
    Construct the n-qubit W state: equal superposition of all single-excitation
    basis states (|00..01> + |00..10> + ... + |10..00>) / sqrt(n).
    """
    dim = 2 ** n_qubits
    state = [0.0] * dim
    amp = 1.0 / math.sqrt(n_qubits)
    for k in range(n_qubits):
        idx = 1 << k
        state[idx] = amp
    return state

def ghz_witness_expectation(state: list[float], n_qubits: int) -> float:
    """
    Compute the expectation value of the GHZ entanglement witness:
    W = I/2 - |GHZ><GHZ|

    <W> = 1/2 - |<GHZ|state>|^2
    Negative value certifies GHZ-type entanglement.
    """
    ghz = ghz_state(n_qubits)
    overlap = sum(g * s for g, s in zip(ghz, state))
    return
