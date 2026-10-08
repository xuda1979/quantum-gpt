import importlib.util


def _load(path: str):
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_tests(candidate_path: str) -> dict:
    failures: list[str] = []
    try:
        mod = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return {"passed": False, "details": [f"import failed: {e}"]}

    # Circuit construction
    try:
        c = mod.bell_circuit()
        # Braket Circuit has a to_ir method; just check it's not empty
        if not hasattr(c, "measure"):
            failures.append("bell_circuit() did not return a Braket Circuit-like object")
    except Exception as e:  # noqa: BLE001
        failures.append(f"bell_circuit() raised: {e}")

    # parity_check
    p00 = mod.parity_check("00")
    if p00 != 0:
        failures.append(f"parity_check('00') should be 0; parity={p00}, expected 0")
    p11 = mod.parity_check("11")
    if p11 != 0:
        failures.append(f"parity_check('11') should be 0 (even parity); parity={p11}, expected 0")
    p01 = mod.parity_check("01")
    if p01 != 1:
        failures.append(f"parity_check('01') should be 1; parity={p01}, expected 1")
    p10 = mod.parity_check("10")
    if p10 != 1:
        failures.append(f"parity_check('10') should be 1; parity={p10}, expected 1")

    # Sampling: only |00> and |11> should appear (Bell state)
    try:
        counts = mod.sample_bell_state(shots=400)
        if not counts:
            failures.append("sample_bell_state() returned empty counts")
        else:
            for k, v in counts.items():
                if k not in {"00", "01", "10", "11"}:
                    failures.append(f"unexpected bitstring {k!r} in counts")
                if k in {"01", "10"} and v > 0:
                    # Allow a tiny simulation noise tolerance: < 5% of shots
                    if v > 20:
                        failures.append(
                            f"odd-parity outcome {k!r} count={v} too high for a Bell state; "
                            f"need<={20}"
                        )
    except Exception as e:  # noqa: BLE001
        failures.append(f"sample_bell_state() raised: {e}")

    return {
        "passed": not failures,
        "details": failures or ["Braket Bell circuit, sampling, and parity check all correct"],
    }
