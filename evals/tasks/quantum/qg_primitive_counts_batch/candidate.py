from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

def sampler_bell_batch():
    """Two Bell pubs in one sampler call with seed 5."""
    def bell():
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        return qc
    sampler = StatevectorSampler(seed=5)
    job = sampler.run([bell(), bell()], shots=256)
    res = job.result()
    out = []
    for pub in res:
        out.append(dict(pub.data.c.get_counts()))
    return out
