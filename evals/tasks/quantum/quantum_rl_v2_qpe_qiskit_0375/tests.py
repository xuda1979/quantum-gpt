import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    grid = 1.0 / 8.0

    # --- decode convention: MSB-first bitstring decoding ---
    decode_cases = {
        "000": 0.0,
        "001": 0.125,
        "010": 0.25,
        "011": 0.375,
        "100": 0.5,
        "101": 0.625,
        "110": 0.75,
        "111": 0.875,
    }
    bad = 0
    first_bad = None
    try:
        for bits, expected in sorted(decode_cases.items()):
            got = float(module.decode_phase(bits))
            if abs(got - expected) > 1e-12:
                bad += 1
                if first_bad is None:
                    first_bad = (bits, got, expected)
    except Exception as e:  # noqa: BLE001
        failures.append(f"decode_phase raised: {e}")
        bad = 1
    if bad:
        bits, got, expected = first_bad
        failures.append(f"decode_{bits}={got:.6f}, expected {expected:.6f}")

    # --- phase value ---
    try:
        phase = float(module.phase_value())
        if abs(phase - 0.375) > 1e-12:
            failures.append(f"phase_value={phase:.9f}, expected 0.375000000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"phase_value raised: {e}")

    # --- circuit structure: 4 qubits, 3 counting, 3 clbits ---
    circuit = None
    try:
        circuit = module.qpe_circuit()
        if len(circuit.qubits) != 4:
            failures.append(f"circuit_qubits={len(circuit.qubits)}, expected 4")
        if len(circuit.clbits) != 3:
            failures.append(f"circuit_clbits={len(circuit.clbits)}, expected 3")
    except Exception as e:  # noqa: BLE001
        failures.append(f"qpe_circuit raised: {e}")

    # --- end-to-end QPE: dominant estimate = 0.375 within 1/8, exact ---
    result = None
    try:
        result = module.run_qpe()
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_qpe raised: {e}")
    if result is None:
        failures.append(f"dominant_phase=0.000, expected 0.375 within {grid:.3f}")
    else:
        est = result.get("top_phase")
        if est is None:
            failures.append(f"dominant_phase=0.000, expected 0.375 within {grid:.3f}")
        else:
            if abs(float(est) - 0.375) > grid:
                failures.append(
                    f"dominant_phase={float(est):.6f}, expected 0.375000 within {grid:.6f}"
                )
            if abs(float(est) - 0.375) > 1e-9:
                failures.append(
                    f"exact_phase_error={abs(float(est) - 0.375):.9f}, " "expected 0.000000000"
                )
        top_bits = result.get("top_bits")
        if top_bits != "011":
            failures.append(f"top_bits={top_bits}, expected 011")
        share = result.get("top_share")
        if share is None or float(share) < 0.99:
            failures.append(f"top_share={share}, expected >= 0.990000")

    return {
        "passed": not failures,
        "details": failures
        or [
            "QPE (qiskit, 3 counting qubits) on P(2*pi*0.375)|1>: MSB-first "
            "decode verified on all 8 bitstrings, dominant estimate 0.375 "
            "exact with 2048 seeded shots",
        ],
    }
