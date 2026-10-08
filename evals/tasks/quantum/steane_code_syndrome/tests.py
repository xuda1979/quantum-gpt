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

    H = module.steane_parity_check_matrix()
    if len(H) != 3 or any(len(row) != 7 for row in H):
        failures.append("H should be 3x7")

    # No error -> syndrome (0,0,0)
    if module.steane_syndrome([0, 0, 0, 0, 0, 0, 0]) != [0, 0, 0]:
        failures.append("zero error pattern should give zero syndrome")

    # Single-bit errors give distinct non-zero syndromes
    syndromes = []
    for i in range(7):
        e = [0] * 7
        e[i] = 1
        s = module.steane_syndrome(e)
        if s == [0, 0, 0]:
            failures.append(f"single error at {i} should give non-zero syndrome")
        syndromes.append(tuple(s))
    if len(set(syndromes)) != 7:
        failures.append("single-bit syndromes should be distinct")

    # Verify against the matrix definition
    e = [1, 0, 0, 0, 1, 0, 0]  # arbitrary weight-2 pattern
    expected = [
        (H[0][j] * e[j] for j in range(7)),
    ]
    s = module.steane_syndrome(e)
    manual = [sum(H[i][j] * e[j] for j in range(7)) % 2 for i in range(3)]
    if s != manual:
        failures.append("syndrome disagrees with manual matrix product")

    # Correctable patterns
    if not module.steane_correctable([0, 0, 0, 0, 0, 0, 0]):
        failures.append("zero error should be correctable")
    if not module.steane_correctable([0, 1, 0, 0, 0, 0, 0]):
        failures.append("single-bit error should be correctable")
    if module.steane_correctable([1, 1, 0, 0, 0, 0, 0]):
        failures.append("weight-2 error should NOT be correctable")

    # Invalid input
    try:
        module.steane_syndrome([0, 1])
        failures.append("should raise on wrong length")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Steane code syndrome computation correct"],
    }
