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
        (["H", "cx", "x"], ["H", "CX", "X"]),
        ([" hadamard ", "CNOT", "Pauli_X"], ["H", "CX", "X"]),
        (["x", "z", "controlled-x"], ["X", "Z", "CX"]),
    ]
    for raw, expected in cases:
        actual = module.normalize_gate_sequence(raw)
        if actual != expected:
            failures.append(f"normalize_gate_sequence({raw!r}) -> {actual!r}, expected {expected!r}")

    for bad in (["swap"], ["H", "measure"], ["H", "T"]):
        try:
            module.normalize_gate_sequence(bad)
        except ValueError:
            continue
        except Exception as exc:
            failures.append(f"normalize_gate_sequence({bad!r}) raised {type(exc).__name__}, expected ValueError")
        else:
            failures.append(f"normalize_gate_sequence({bad!r}) did not raise ValueError")

    return {
        "passed": not failures,
        "details": failures or ["gate alias casefold barrier normalizes x/X and rejects invalid aliases"],
    }
