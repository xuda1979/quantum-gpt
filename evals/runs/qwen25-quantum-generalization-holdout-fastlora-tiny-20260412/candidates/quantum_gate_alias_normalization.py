
class QuantumGateNormalizer:
    @staticmethod
    def normalize_gate_sequence(gate_sequence: list[str]) -> list[str]:
        # Simple case-insensitive replacement of gate names
        normalized_sequence = [gate.replace(' ', '') for gate in gate_sequence]
        return normalized_sequence

# Test function to verify correctness
def test_normalize_gate_sequence():
    cases = [
        (["H", "cx", "x"], ["H", "CX", "X"]),
        (["hadamard ", "CNOT", "Pauli_X"], ["H", "CX", "X"]),
        (["h", "h", "cx"], ["H", "H", "CX"]),
    ]

    for raw, expected in cases:
        actual = QuantumGateNormalizer.normalize_gate_sequence(raw)
        assert actual == expected, f"Expected {expected} but got {actual}"

test_normalize_gate_sequence()
