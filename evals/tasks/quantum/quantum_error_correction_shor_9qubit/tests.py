import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _close(a, b, tol=1e-9):
    return abs(a - b) < tol


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # --- encode ---
    # Shor code encodes 1 logical qubit into 9 physical qubits.
    # |0_L> = (|000>+|111>)(|000>+|111>)(|000>+|111>) / 2*sqrt(2)
    # |1_L> = (|000>-|111>)(|000>-|111>)(|000>-|111>) / 2*sqrt(2)
    encoded_0 = module.shor_encode(0)
    if len(encoded_0) != 512:  # 2^9
        failures.append(f"shor_encode(0) length={len(encoded_0)}, expected 512")
    else:
        norm = sum(a ** 2 for a in encoded_0)
        if not _close(norm, 1.0, tol=1e-6):
            failures.append(f"shor_encode(0) not normalized: {norm}")
        # Check key amplitudes: |000000000>=|0> should have amp 1/(2*sqrt(2))
        amp = 1.0 / (2 * math.sqrt(2))
        # |000000000> = index 0
        if not _close(encoded_0[0], amp, tol=1e-6):
            failures.append(
                f"shor_encode(0)[0]={encoded_0[0]}, expected {amp}"
            )
        # |111000000> is not a valid codeword component for the first block
        # |111111111> = index 511 should have amp 1/(2*sqrt(2))
        if not _close(encoded_0[511], amp, tol=1e-6):
            failures.append(
                f"shor_encode(0)[511]={encoded_0[511]}, expected {amp}"
            )

    encoded_1 = module.shor_encode(1)
    if len(encoded_1) != 512:
        failures.append(f"shor_encode(1) length={len(encoded_1)}, expected 512")
    else:
        norm1 = sum(a ** 2 for a in encoded_1)
        if not _close(norm1, 1.0, tol=1e-6):
            failures.append(f"shor_encode(1) not normalized: {norm1}")
        amp = 1.0 / (2 * math.sqrt(2))
        # |0_L>: |000000000> has +amp; |1_L>: |000000000> has +amp
        # |1_L> = (|000>-|111>)^3 / (2sqrt2)
        # index 0 = |000 000 000> -> (+1)(+1)(+1) -> +amp
        if not _close(encoded_1[0], amp, tol=1e-6):
            failures.append(
                f"shor_encode(1)[0]={encoded_1[0]}, expected {amp}"
            )
        # index 511 = |111 111 111> -> (-1)(-1)(-1) = -1 -> -amp
        if not _close(encoded_1[511], -amp, tol=1e-6):
            failures.append(
                f"shor_encode(1)[511]={encoded_1[511]}, expected {-amp}"
            )

    # --- apply_x_error ---
    # Flip qubit i: swap amplitudes between states differing in bit i
    simple_state = [0.0] * 512
    simple_state[0] = 1.0  # |000000000>
    flipped = module.apply_x_error(simple_state, 0)
    # Flipping qubit 0 (MSB in our convention or LSB) — we need to check convention
    # We'll verify: the state should now be all-zero except one entry = 1
    nonzero = [(i, a) for i, a in enumerate(flipped) if abs(a) > 1e-12]
    if len(nonzero) != 1:
        failures.append(f"apply_x_error: expected exactly 1 nonzero amplitude, got {len(nonzero)}")
    elif abs(nonzero[0][1] - 1.0) > 1e-9:
        failures.append(f"apply_x_error: amplitude={nonzero[0][1]}, expected 1.0")

    # --- decode ---
    # Encoding then decoding without errors should recover the original qubit
    for logical_bit in [0, 1]:
        enc = module.shor_encode(logical_bit)
        dec = module.shor_decode(enc)
        if dec != logical_bit:
            failures.append(f"shor_decode(shor_encode({logical_bit})) = {dec}, expected {logical_bit}")

    # --- single X error correction ---
    for logical_bit in [0, 1]:
        for error_qubit in [0, 4, 8]:  # test one qubit per block
            enc = module.shor_encode(logical_bit)
            corrupted = module.apply_x_error(enc, error_qubit)
            dec = module.shor_decode(corrupted)
            if dec != logical_bit:
                failures.append(
                    f"Single X error on qubit {error_qubit}, logical={logical_bit}: "
                    f"decoded={dec}, expected {logical_bit}"
                )

    return {
        "passed": not failures,
        "details": failures or ["Shor 9-qubit error correction code correct for all test cases"],
    }
