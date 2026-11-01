from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit import transpile

def ring_depth_2():
    """Depth after level-3 transpile of the CX ring on a line coupling."""
    qc = QuantumCircuit(3)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.cx(2, 0)
    cmap = CouplingMap([[0, 1], [1, 0], [1, 2], [2, 1]])
    out = transpile(qc, coupling_map=cmap, optimization_level=3,
                    seed_transpiler=42)
    return out.depth()
