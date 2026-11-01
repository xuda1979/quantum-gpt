from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error

def amplitude_damping_survival():
    """|1> survival after two damped id layers, gamma=0.25."""
    err = amplitude_damping_error(0.25)
    noise = NoiseModel()
    noise.add_quantum_error(err, ["id"], [0])
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.id(0)
    qc.id(0)
    qc.measure(0, 0)
    sim = AerSimulator(noise_model=noise, seed_simulator=2)
    counts = sim.run(qc, shots=512).result().get_counts()
    return counts.get("1", 0) / 512
