import math


def shor_encode(logical_bit: int) -> list[float]:
    """
    Encode a single logical qubit (0 or 1) using the Shor 9-qubit code.

    |0_L> = (|000> + |111>)(|000> + |111>)(|000> + |111>) / (2*sqrt(2))
    |1_L> = (|000> - |111>)(|000> - |111>)(|000> - |111>) / (2*sqrt(2))
    """
    sign = 1 if logical_bit == 0 else -1
    block_states = [0, 7]  # |000>=0, |111>=7 in 3-bit
    block_signs = [1, sign]

    state = [0.0] * 512
    amp = 1.0 / (2 * math.sqrt(2))
    for b1 in range(2):
        for b2 in range(2):
            for b3 in range(2):
                idx = (block_states[b1] << 6) | (block_states[b2] << 3) | block_states[b3]
                state[idx] = amp * block_signs[b1] * block_signs[b2] * block_signs[b3]
    return state


def apply_x_error(state: list[float], qubit: int) -> list[float]:
    """Apply a bit-flip (X) error on the given qubit index (0-8, MSB first)."""
    n = len(state)
    result = [0.0] * n
    bit = 8 - qubit  # convert to bit position from LSB
    for i in range(n):
        j = i ^ (1 << bit)
        result[j] = state[i]
    return result


def shor_decode(state: list[float]) -> int:
    """
    Decode a (possibly single-bit-flip-corrupted) Shor-encoded state.

    Steps:
    1. Bit-flip correction via majority vote within each 3-qubit block.
    2. Phase detection: compare the sign of amplitude at |000 000 000>
       vs |111 000 000> in the corrected state. Same sign → logical 0,
       opposite sign → logical 1.

    Returns the logical bit (0 or 1).
    """
    # Step 1: Correct bit-flips via majority vote per block.
    corrected = [0.0] * 512
    for idx in range(512):
        if abs(state[idx]) < 1e-15:
            continue
        b0 = (idx >> 6) & 7
        b1 = (idx >> 3) & 7
        b2 = idx & 7
        cb0 = 7 if bin(b0).count('1') >= 2 else 0
        cb1 = 7 if bin(b1).count('1') >= 2 else 0
        cb2 = 7 if bin(b2).count('1') >= 2 else 0
        new_idx = (cb0 << 6) | (cb1 << 3) | cb2
        corrected[new_idx] += state[idx]

    # Step 2: Determine logical bit from phase of first block.
    # Compare amplitude at |000 000 000> (index 0) with |111 000 000> (index 448).
    # |0_L>: these have the same sign.
    # |1_L>: these have opposite signs.
    amp_000 = corrected[0]            # |000 000 000>
    amp_111 = corrected[0b111000000]  # |111 000 000>

    if abs(amp_000) < 1e-12 and abs(amp_111) < 1e-12:
        return 0  # fallback for degenerate case
    if amp_000 * amp_111 >= 0:
        return 0
    else:
        return 1
