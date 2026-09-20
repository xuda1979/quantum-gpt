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

    # --- codewords ---
    cw0 = _vec(module.shor_codeword(0))
    cw1 = _vec(module.shor_codeword(1))
    if cw0 is None or cw1 is None:
        failures.append("shor_codeword returned None, expected 512 amplitudes")
        failures.append("codeword_length=0, expected 512")
    else:
        if len(cw0) != 512 or len(cw1) != 512:
            failures.append(f"codeword_length={len(cw0) if cw0 is not None else 0}, expected 512")
        else:
            amp = 1.0 / (2 * math.sqrt(2))
            if abs(cw0[0] - amp) > 1e-6 or abs(cw0[511] - amp) > 1e-6:
                failures.append(f"cw0_amp0={abs(cw0[0]):.6f}, expected {amp:.6f}")
            if abs(cw1[511] + amp) > 1e-6:
                failures.append(f"cw1_amp511={cw1[511]:.6f}, expected {-amp:.6f}")
            overlap = abs(sum(a * b for a, b in zip(cw0, cw1))) ** 2
            if overlap > 1e-9:
                failures.append(f"codeword_overlap={overlap:.6f}, expected 0.000000")

    # --- generators: 8 valid Pauli strings ---
    try:
        gens = module.shor_stabilizer_generators()
    except Exception as e:  # noqa: BLE001
        gens = []
        failures.append(f"shor_stabilizer_generators raised: {e}")
    if not isinstance(gens, (list, tuple)):
        failures.append("shor_stabilizer_generators returned non-list, expected 8 strings")
        failures.append("gen_count=0, expected 8")
        gens = []
    else:
        valid = 0
        for g in gens:
            if isinstance(g, str) and len(g) == 9 and all(ch in "IXYZ" for ch in g):
                valid += 1
        if len(gens) != 8:
            failures.append(f"gen_count={len(gens)}, expected 8")
        elif valid != 8:
            failures.append(f"gen_valid={valid}, expected 8")

    # --- pairwise commutation: 28 pairs ---
    comm_ok = 0
    try:
        for i in range(len(gens)):
            for j in range(i + 1, len(gens)):
                if module.pauli_commute(gens[i], gens[j]):
                    comm_ok += 1
    except Exception as e:  # noqa: BLE001
        failures.append(f"pauli_commute raised: {e}")
    if comm_ok != 28:
        failures.append(f"commuting_pairs={comm_ok}, expected 28")

    # --- every generator has eigenvalue +1 on both codewords: 16 checks ---
    eig_ok = 0
    try:
        for logical, cw in ((0, cw0), (1, cw1)):
            for gi, g in enumerate(gens):
                ev = module.pauli_eigenvalue(g, cw)
                if abs(abs(complex(ev)) - 1.0) < 1e-6 and complex(ev).real > 0.99:
                    eig_ok += 1
                else:
                    failures.append(
                        f"eigenvalue(g{gi}, |{logical}>) = {complex(ev).real:.4f}, expected 1.0000"
                    )
    except Exception as e:  # noqa: BLE001
        failures.append(f"pauli_eigenvalue raised: {e}")
    if eig_ok != 16:
        failures.append(f"eigenvalue_checks_correct={eig_ok}, expected 16")

    return {
        "passed": not failures,
        "details": failures or ["Shor code generators commute and stabilize both codewords"],
    }
