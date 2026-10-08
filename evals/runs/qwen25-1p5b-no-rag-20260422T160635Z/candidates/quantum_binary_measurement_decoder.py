from typing import List, Tuple

def bit_register_to_int(bits: List[int]) -> int:
    if not bits:
        raise ValueError("bits must be non-empty")
    value = 0
    for bit in bits:
        if bit not in (0, 1):
            raise ValueError("measurement must be 0 or 1")
        value = (value << 1) | int(bit)
    return value

def measurement_register_to_phase(bits: List[int]) -> float:
    scale = 1 << len(bits)
    return bit_register_to_int(bits) / scale
