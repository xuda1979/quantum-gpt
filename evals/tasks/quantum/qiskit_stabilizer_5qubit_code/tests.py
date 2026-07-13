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

    # 1. Four stabilizer generators of length 5
    gens = mod.stabilizer_generators()
    if len(gens) != 4:
        failures.append(f"expected 4 generators, got {len(gens)}")
    else:
        for i, g in enumerate(gens):
            if len(g) != 5 or any(c not in "IXYZ" for c in g):
                failures.append(f"generator {i} = {g!r} is not a length-5 Pauli string")

    # 2. Stabilizer matrix is 4x10 binary
    try:
        S = mod.stabilizer_matrix()
        if S.shape != (4, 10):
            failures.append(f"stabilizer_matrix shape = {S.shape}, expected (4, 10)")
        elif not ((S == 0) | (S == 1)).all():
            failures.append("stabilizer_matrix must be binary")
    except Exception as e:  # noqa: BLE001
        failures.append(f"stabilizer_matrix() raised: {e}")

    # 3. No-error syndrome is 0000
    try:
        if mod.syndrome_of("IIIII") != "0000":
            failures.append("syndrome_of('IIIII') must be '0000'")
    except Exception as e:  # noqa: BLE001
        failures.append(f"syndrome_of() raised: {e}")

    # 4. The 15 single-qubit errors must produce 15 distinct non-zero syndromes.
    #    This is the defining property of the [[5,1,3]] perfect code.
    try:
        table = mod.single_qubit_error_table()
        if table.get("I") != "0000":
            failures.append(
                f"single_qubit_error_table()['I'] = {table.get('I')!r}, expected '0000'"
            )
        errs = {k: v for k, v in table.items() if k != "I"}
        if len(errs) != 15:
            failures.append(f"expected 15 single-qubit errors, got {len(errs)}")
        else:
            nonzero_ok = all(v != "0000" for v in errs.values())
            unique_ok = len(set(errs.values())) == 15
            if not nonzero_ok:
                failures.append("some single-qubit error has zero syndrome (should not happen)")
            if not unique_ok:
                failures.append("single-qubit error syndromes are not all distinct")
    except Exception as e:  # noqa: BLE001
        failures.append(f"single_qubit_error_table() raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or ["[[5,1,3]] stabilizers, symplectic matrix, and 15-distinct-syndrome property correct"],
    }
