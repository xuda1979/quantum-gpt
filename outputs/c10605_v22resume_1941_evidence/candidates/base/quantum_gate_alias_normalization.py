def normalize_gates(gates):
    """
    Normalize a sequence of quantum gate names while preserving order.

    Args:
        gates: A list of gate name strings.

    Returns:
        A list of canonical uppercase gate names.

    Raises:
        ValueError: If any gate name is unknown.
    """
    if not gates:
        return []

    mapping = {
        "h": "H",
        "hadamard": "H",
        "x": "X",
        "pauli_x": "X",
        "cx": "CX",
        "cnot": "CX",
    }

    result = []
    for gate in gates:
        stripped = gate.strip().lower()
        if stripped in mapping:
            result.append(mapping[stripped])
        else:
            raise ValueError(f"Unknown gate name: {gate}")

    return result
