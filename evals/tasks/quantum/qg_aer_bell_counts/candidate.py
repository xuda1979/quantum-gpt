from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def bell_shot_counts():
    """Deterministic-ish Bell counts with seed 3, 512 shots."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    sim = AerSimulator(seed_simulator=3)
    return dict(sim.run(qc, shots=512).result().get_counts())
