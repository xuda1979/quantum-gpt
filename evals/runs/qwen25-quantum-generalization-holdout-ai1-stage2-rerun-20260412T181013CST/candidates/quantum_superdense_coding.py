# reference implementation
class QuantumSuperdenseCoding:
    def encode_message(self, bits: str) -> str:
        """Encode classical bits into qubits."""
        raise NotImplementedError()

    def decode_message(self, encoded: str) -> str:
        """Decode qubits back to classical bits."""
        raise NotImplementedError()
