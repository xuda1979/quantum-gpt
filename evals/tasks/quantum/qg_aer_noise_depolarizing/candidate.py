from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

def depolarized_bell_fidelity():
    """Bell survival fraction under p=0.1 depolarizing noise."""
    noise = NoiseModel()
    noise.add_quantum_error(depolarizing_error(0.1, 1), ["h"], [0])
    noise.add_quantum_error(depolarizing_error(0.1, 2), ["cx"], [0, 1])
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    sim = AerSimulator(noise_model=noise, seed_simulator=11)
    counts = sim.run(qc, shots=2048).result().get_counts()
    good = counts.get("00", 0) + counts.get("11", 0)
    return good / 2048
