from qiskit.circuit.library import QFT

def qft_no_final_swaps():
    """Inverse QFT on 4 qubits without swaps."""
    return QFT(4, do_swaps=False, inverse=True)
