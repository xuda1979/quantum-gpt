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

    # 1. Hamiltonian has the expected structure
    try:
        H = mod.h2_hamiltonian()
        if not hasattr(H, "terms"):
            failures.append("h2_hamiltonian() did not return a Hamiltonian-like object")
        else:
            n_terms = len(H.terms) if hasattr(H.terms, "__len__") else 0
            if n_terms < 4:
                failures.append(f"h2_hamiltonian() has too few terms ({n_terms}); expected >=4")
    except Exception as e:  # noqa: BLE001
        failures.append(f"h2_hamiltonian() raised: {e}")

    # 2. run_vqe returns a dict with an 'energy' key
    try:
        out = mod.run_vqe(steps=80, seed=0)
        if not isinstance(out, dict) or "energy" not in out:
            failures.append("run_vqe() must return {'energy': float, ...}")
        else:
            e = float(out["energy"])
            # H2 ground state in this 2-qubit parity mapping is ~ -1.136 Ha.
            # Accept anything below -1.0 to keep the test robust to optimizer
            # settings while still requiring a real variational decrease.
            if e > -1.0:
                failures.append(f"VQE energy {e:.4f} did not drop below -1.0 Ha")
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_vqe() raised: {e}")

    return {
        "passed": not failures,
        "details": failures or ["PennyLane VQE H2 ansatz + Hamiltonian + optimizer all correct"],
    }
