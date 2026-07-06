import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    cases = [
        ("x", "X"),
        (" X ", "X"),
        ("Pauli_X", "X"),
        ("h", "H"),
        ("controlled-x", "CX"),
        ("CNOT", "CX"),
    ]
    for raw_gate, expected in cases:
        actual = module.canonical_gate_token(raw_gate)
        if actual != expected:
            failures.append(f"canonical_gate_token({raw_gate!r}) -> {actual!r}, expected {expected!r}")

    for bad_gate in ("swap", "measure", "t"):
        try:
            module.canonical_gate_token(bad_gate)
        except ValueError:
            continue
        except Exception as exc:
            failures.append(f"canonical_gate_token({bad_gate!r}) raised {type(exc).__name__}, expected ValueError")
        else:
            failures.append(f"canonical_gate_token({bad_gate!r}) did not raise ValueError")

    return {
        "passed": not failures,
        "details": failures or ["gate token canonicalizer preserves uppercase X/H/CX outputs"],
    }
