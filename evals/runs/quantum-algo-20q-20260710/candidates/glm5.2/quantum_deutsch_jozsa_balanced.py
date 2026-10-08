from qiskit.primitives import StatevectorSampler

sampler = StatevectorSampler()
job = sampler.run([circuit], shots=1000)
result = job.result()
counts = result[0].data.meas.get_counts()
