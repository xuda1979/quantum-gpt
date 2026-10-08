def optimize_circuit(gates: list[tuple[str, list[int]]]) -> list[list[tuple[str, list[int]]]]:
    """Schedule gates into layers (time steps) to minimize circuit depth.

    Each gate is (name, qubits) where qubits is a list of qubit indices.
    Two gates can be in the same layer if they act on disjoint qubits.
    Returns a list of layers, each layer a list of gates, preserving
    the relative order of gates that share qubits.

    Greedy ASAP scheduling: place each gate in the earliest layer where
    none of its qubits are already occupied.
    """
    layers: list[list[tuple[str, list[int]]]] = []
    # Track the earliest available layer for each qubit
    qubit_ready: dict[int, int] = {}

    for name, qubits in gates:
        # This gate can start at the max of all its qubits' ready times
        earliest = 0
        for q in qubits:
            earliest = max(earliest, qubit_ready.get(q, 0))

        # Extend layers list if needed
        while len(layers) <= earliest:
            layers.append([])

        layers[earliest].append((name, qubits))

        # Update ready times
        for q in qubits:
            qubit_ready[q] = earliest + 1

    return layers


def circuit_depth(gates: list[tuple[str, list[int]]]) -> int:
    """Return the minimum depth of the circuit."""
    return len(optimize_circuit(gates))
