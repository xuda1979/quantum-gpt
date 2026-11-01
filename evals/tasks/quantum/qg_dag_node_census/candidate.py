from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag

def dag_gate_census():
    """Count DAG op nodes by gate name for a small circuit."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.x(1)
    dag = circuit_to_dag(qc)
    census = {}
    for node in dag.op_nodes():
        census[node.name] = census.get(node.name, 0) + 1
    return census
