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
        (["H", "H", "X", "Z"], ["X", "Z"]),
        ([" s ", "sdg", "H", "x", "X"], ["H"]),
        (["Z", "S", "SDG", "Z", "H"], ["H"]),
        (["S", "H", "SDG"], ["S", "H", "SDG"]),
        (["sdg", "s", "x", "x", "z"], ["Z"]),
    ]
    for raw, expected in cases:
        actual = module.repair_phase_sequence(raw)
        if actual != expected:
            failures.append(f"repair_phase_sequence({raw!r}) -> {actual!r}, expected {expected!r}")

    for bad in [["T"], ["H", " measure "]]:
        try:
            module.repair_phase_sequence(bad)
        except ValueError:
            continue
        except Exception as exc:
            failures.append(f"repair_phase_sequence({bad!r}) raised {type(exc).__name__}, expected ValueError")
        else:
            failures.append(f"repair_phase_sequence({bad!r}) did not raise ValueError")

    return {
        "passed": not failures,
        "details": failures or ["Circuit phase repair handles normalization, cancellations, and unsupported gates"],
    }
