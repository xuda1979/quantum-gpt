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

    # Constant zero / constant one
    if module.classify_oracle([0, 0, 0, 0]) != "constant":
        failures.append("all-zero table should be constant")
    if module.classify_oracle([1, 1, 1, 1]) != "constant":
        failures.append("all-one table should be constant")

    # Balanced
    if module.classify_oracle([0, 0, 1, 1]) != "balanced":
        failures.append("[0,0,1,1] should be balanced")
    if module.classify_oracle([0, 1, 0, 1]) != "balanced":
        failures.append("[0,1,0,1] should be balanced")

    # Neither
    if module.classify_oracle([0, 0, 0, 1]) != "neither":
        failures.append("[0,0,0,1] should be neither")

    # 8-entry table: balanced XOR(2)
    tt = [bin(i).count("1") % 2 for i in range(8)]
    if module.classify_oracle(tt) != "balanced":
        failures.append("XOR truth table over 3 bits should be balanced")

    # Query counts
    if module.deutsch_jozsa_query_count(2) != 2:
        failures.append("query count for n=2 should be 2")
    if module.deutsch_jozsa_query_count(4) != 3:
        failures.append("query count for n=4 should be 3")
    if module.deutsch_jozsa_query_count(8) != 5:
        failures.append("query count for n=8 should be 5")

    # Length not power of two should raise
    try:
        module.classify_oracle([0, 0, 1])
        failures.append("classify_oracle should raise on non-power-of-2 length")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Deutsch-Jozsa classification correct for all test cases"],
    }
