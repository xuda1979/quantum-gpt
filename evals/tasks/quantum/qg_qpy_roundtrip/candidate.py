import io
from qiskit import QuantumCircuit
from qiskit import qpy

def qpy_roundtrip_depth():
    """QPY serialize + deserialize preserves structure."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    buf = io.BytesIO()
    qpy.dump(qc, buf)
    buf.seek(0)
    loaded = qpy.load(buf)
    return loaded[0].depth()
