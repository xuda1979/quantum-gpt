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

    # s = "1011" (MSB-first string for integer 0b1011 = 11)
    # Build queries for each basis vector
    s_int = 0b1011
    n = 4
    queries = {1 << i: module.bv_oracle(1 << i, s_int) for i in range(n)}
    s_recovered = module.recover_hidden_string(queries, n)
    if s_recovered != "1011":
        failures.append(f"expected hidden string '1011', got {s_recovered!r}")

    # s = "0000"
    queries_zero = {1 << i: 0 for i in range(4)}
    if module.recover_hidden_string(queries_zero, 4) != "0000":
        failures.append("all-zero queries should give '0000'")

    # s = "1111"
    queries_one = {1 << i: 1 for i in range(4)}
    if module.recover_hidden_string(queries_one, 4) != "1111":
        failures.append("all-one queries should give '1111'")

    # 8-bit string
    s_int_8 = 0b10010110
    q8 = {1 << i: module.bv_oracle(1 << i, s_int_8) for i in range(8)}
    rec = module.recover_hidden_string(q8, 8)
    if rec != "10010110":
        failures.append(f"8-bit recovery mismatch: got {rec!r}, expected '10010110'")

    # Missing query should raise
    try:
        module.recover_hidden_string({1: 1, 2: 0}, 3)
        failures.append("should raise on missing query")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Bernstein-Vazirani hidden string recovery correct"],
    }
