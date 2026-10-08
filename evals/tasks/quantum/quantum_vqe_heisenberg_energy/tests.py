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

    # 1. Hamiltonian has the expected structure: three XX/YY/ZZ terms.
    try:
        H = module.heisenberg_hamiltonian(1.0)
    except Exception as e:  # noqa: BLE001
        H = None
        failures.append(f"heisenberg_hamiltonian raised: {e}")
    if H is None or not hasattr(H, "terms"):
        failures.append("heisenberg_hamiltonian() did not return a Hamiltonian-like object")
    else:
        try:
            terms = H.terms() if callable(H.terms) else H.terms
            n_terms = len(terms[0]) if isinstance(terms, tuple) else len(terms)
        except Exception as e:  # noqa: BLE001
            n_terms = 0
            failures.append(f"heisenberg_hamiltonian terms() raised: {e}")
        if n_terms < 3:
            failures.append(f"heisenberg_hamiltonian() has too few terms ({n_terms}); expected 3")

    # 2. run_vqe returns a dict with an 'energy' key.
    try:
        out = module.run_vqe(steps=80, seed=0)
    except Exception as e:  # noqa: BLE001
        out = None
        failures.append(f"run_vqe() raised: {e}")
    if out is None or not isinstance(out, dict) or "energy" not in out:
        failures.append("run_vqe() must return {'energy': float, 'params': [...]}")
        failures.append("energy=0.000000 need<=-2.600000")
    else:
        e = float(out["energy"])
        # The 2-qubit XXX Heisenberg chain (J=1) has ground-state energy
        # -3.0 (the singlet). Require a genuine variational decrease below
        # -2.6 Ha while staying robust to optimizer settings.
        if e > -2.6:
            failures.append(f"VQE energy {e:.4f} need<=-2.6000")
        if e < -3.2:
            failures.append(f"VQE energy {e:.4f} below the physical ground state -3.0000")
        params = out.get("params")
        if not isinstance(params, (list, tuple)) or len(params) != 4:
            failures.append(
                f"run_vqe() params length={len(params) if params is not None else 0}, expected 4"
            )

    return {
        "passed": not failures,
        "details": failures
        or ["PennyLane Heisenberg VQE ansatz + Hamiltonian + optimizer all correct"],
    }
