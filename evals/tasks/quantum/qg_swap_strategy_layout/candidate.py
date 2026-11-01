from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

def star_to_line_layout():
    """Star CX pattern onto a line: count the 2q-gate inflation."""
    qc = QuantumCircuit(5)
    for leaf in (1, 2, 3, 4):
        qc.cx(0, leaf)
    n_in = sum(1 for i in qc.data if len(i.qubits) == 2)
    cmap = CouplingMap([[0, 1], [1, 0], [1, 2], [2, 1], [2, 3],
                        [3, 2], [3, 4], [4, 3]])
    out = transpile(qc, coupling_map=cmap, optimization_level=3,
                    seed_transpiler=1)
    n_out = sum(1 for i in out.data if len(i.qubits) == 2)
    return n_out - n_in
