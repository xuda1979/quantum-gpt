# encoding.py
class QuantumMessageEncoder:
    def encode_message(self, bits: str) -> str:
        """Encode classical bits into quantum operations."""
        raise NotImplementedError()

    def decode_message(self, operation: str) -> str:
        """Decode quantum operation back to classical bits."""
        raise NotImplementedError()
