from qiskit.quantum_info import hellinger_fidelity

def hellinger_orthogonal():
    """Hellinger fidelity of disjoint distributions is 0."""
    p = {"00": 1}
    q = {"11": 1}
    return float(hellinger_fidelity(p, q))
