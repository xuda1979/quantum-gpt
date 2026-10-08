import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _vec(value):
    return value if isinstance(value, (list, tuple)) else None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    amp = 1.0 / (2 * math.sqrt(2))  # 1/(2 sqrt(2)) ~ 0.353553

    # --- encode ---
    enc0 = _vec(module.shor_encode(0))
    length0 = len(enc0) if enc0 is not None else 0
    if length0 != 512:
        failures.append(f"shor_encode(0) length={length0}, expected 512")
    if enc0 is not None:
        norm = sum(a**2 for a in enc0)
        if abs(norm - 1.0) > 1e-6:
            failures.append(f"shor_encode(0) norm={norm:.6f}, expected 1.000000")
        if abs(enc0[0] - amp) > 1e-6:
            failures.append(f"shor_encode(0)[0]={enc0[0]:.6f}, expected {amp:.6f}")
        if abs(enc0[511] - amp) > 1e-6:
            failures.append(f"shor_encode(0)[511]={enc0[511]:.6f}, expected {amp:.6f}")

    enc1 = _vec(module.shor_encode(1))
    if enc1 is None:
        failures.append("shor_encode(1) length=0, expected 512")
    elif len(enc1) != 512:
        failures.append(f"shor_encode(1) length={len(enc1)}, expected 512")
    elif abs(enc1[511] - (-amp)) > 1e-6:
        failures.append(f"shor_encode(1)[511]={enc1[511]:.6f}, expected {-amp:.6f}")

    # --- apply_error semantics ---
    simple = [0.0] * 512
    simple[0] = 1.0  # |000000000>
    try:
        flipped = module.apply_error(simple, 0, "X")
    except Exception as e:  # noqa: BLE001
        flipped = None
        failures.append(f"apply_error(X) raised: {e}")
    if _vec(flipped) is not None:
        nonzero = [(i, a) for i, a in enumerate(flipped) if abs(a) > 1e-9]
        if len(nonzero) != 1 or nonzero[0][0] != 256 or abs(nonzero[0][1] - 1.0) > 1e-9:
            n_bad = len(nonzero)
            failures.append(f"x_error_correct_bits={1 if n_bad == 1 else 0}, expected 1")

    all_ones = [0.0] * 512
    all_ones[511] = 1.0  # |111111111>
    try:
        phased = module.apply_error(all_ones, 0, "Z")
    except Exception as e:  # noqa: BLE001
        phased = None
        failures.append(f"apply_error(Z) raised: {e}")
    if _vec(phased) is not None:
        if abs(phased[511] - (-1.0)) > 1e-9:
            failures.append(f"z_error_sign={phased[511]:.6f}, expected -1.000000")

    # --- decode roundtrips and single-qubit error correction ---
    total_cases = 0
    correct_cases = 0
    for logical in (0, 1):
        try:
            enc = module.shor_encode(logical)
        except Exception as e:  # noqa: BLE001
            failures.append(f"shor_encode({logical}) raised: {e}")
            continue
        if not isinstance(enc, (list, tuple)):
            continue
        # identity roundtrip
        total_cases += 1
        try:
            dec = module.shor_decode(list(enc))
        except Exception as e:  # noqa: BLE001
            dec = None
            failures.append(f"shor_decode(encode({logical})) raised: {e}")
        if dec == logical:
            correct_cases += 1
        else:
            failures.append(f"shor_decode(shor_encode({logical})) = {dec} != {logical}")
        # single-qubit errors: X and Z on every qubit, Y on one qubit per block
        for err, qubits in (("X", range(9)), ("Z", range(9)), ("Y", (0, 4, 8))):
            for q in qubits:
                total_cases += 1
                try:
                    corrupted = module.apply_error(list(enc), q, err)
                    dec = module.shor_decode(corrupted)
                except Exception as e:  # noqa: BLE001
                    dec = None
                    failures.append(f"shor_decode({err}{q}) raised: {e}")
                if dec == logical:
                    correct_cases += 1
                else:
                    failures.append(f"shor_decode(L{logical}, {err}{q}) = {dec} != {logical}")
    if correct_cases != total_cases:
        failures.append(f"error_correction_success={correct_cases}, expected {total_cases}")

    return {
        "passed": not failures,
        "details": failures or ["Shor code phase/bit/combined error correction all correct"],
    }
