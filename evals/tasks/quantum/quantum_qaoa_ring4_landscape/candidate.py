"""QAOA p=1 for the MaxCut of the 4-node ring graph using Cirq.

Ring edges: (0,1), (1,2), (2,3), (3,0). The optimal cut value is 4
(alternating bit assignment 0101 / 1010). The p=1 expected cut is computed
exactly by statevector simulation of the QAOA circuit; the best p=1
expectation on this graph is 3.0 (reached near gamma=pi/8, beta=pi/8).
"""

import cirq
import numpy as np


def maxcut_ring4_edges() -> list[tuple[int, int]]:
    """Return the four edges of the 4-node ring graph."""
    return [(0, 1), (1, 2), (2, 3), (3, 0)]


def best_maxcut_value() -> int:
    """The maximum number of cut edges on the ring (a 4-cycle is bipartite)."""
    return 4


def maxcut_value(bitstring: str) -> int:
    """Number of ring edges cut by the given 4-bit assignment."""
    bits = [int(c) for c in bitstring]
    return sum(1 for u, v in maxcut_ring4_edges() if bits[u] != bits[v])


def qaoa_ring4_circuit(gamma: float, beta: float) -> cirq.Circuit:
    """Build the p=1 QAOA circuit for the 4-node ring MaxCut."""
    qubits = cirq.LineQubit.range(4)
    circuit = cirq.Circuit()

    # Initial superposition
    circuit.append(cirq.H.on_each(*qubits))

    # Cost unitary: exp(-i gamma (I - Z_u Z_v)/2) per edge. Cirq's
    # ZZPowGate(exponent=t) implements exp(+i pi t (I-ZZ)/4), so the negative
    # exponent gives the standard QAOA cost phase.
    for u, v in maxcut_ring4_edges():
        circuit.append(cirq.ZZPowGate(exponent=-2 * gamma / np.pi)(qubits[u], qubits[v]))

    # Mixer unitary: exp(-i beta X) on each qubit
    for q in qubits:
        circuit.append(cirq.XPowGate(exponent=2 * beta / np.pi)(q))

    return circuit


def expected_cut_value(gamma: float, beta: float) -> float:
    """Exact expected MaxCut of the p=1 QAOA output state.

    Uses statevector simulation (qubit 0 is the most significant bit of the
    simulator index): for each edge, the probability that the two endpoints
    differ is 1 - P(agree), and the expectation is the sum over the edges.
    """
    qubits = cirq.LineQubit.range(4)
    circuit = qaoa_ring4_circuit(gamma, beta)
    sim = cirq.Simulator()
    state = np.asarray(sim.simulate(circuit, qubit_order=qubits).final_state_vector)
    expectation = 0.0
    for u, v in maxcut_ring4_edges():
        agree = 0.0
        for i, amp in enumerate(state):
            if ((i >> (3 - u)) & 1) == ((i >> (3 - v)) & 1):
                agree += abs(amp) ** 2
        expectation += 1.0 - agree
    return float(expectation)


def optimize_angles(steps: int = 40, seed: int = 0) -> dict:
    """Deterministic seeded search for the p=1 angles maximizing expected cut.

    Coarse (gamma, beta) grid over [0, pi]^2 followed by local refinement.
    Returns {'cost': best expected cut, 'gamma': float, 'beta': float}.
    """
    np.random.seed(seed)
    best = -1.0
    best_gamma = best_beta = 0.0
    for gamma in np.linspace(0.0, np.pi, 13):
        for beta in np.linspace(0.0, np.pi, 13):
            cost = expected_cut_value(gamma, beta)
            if cost > best:
                best, best_gamma, best_beta = cost, gamma, beta
    # local refinement around the grid winner
    for _ in range(steps):
        dg = np.random.uniform(-0.08, 0.08)
        db = np.random.uniform(-0.08, 0.08)
        candidate_g = max(0.0, min(np.pi, best_gamma + dg))
        candidate_b = max(0.0, min(np.pi, best_beta + db))
        cost = expected_cut_value(candidate_g, candidate_b)
        if cost > best:
            best, best_gamma, best_beta = cost, candidate_g, candidate_b
    return {"cost": float(best), "gamma": float(best_gamma), "beta": float(best_beta)}
