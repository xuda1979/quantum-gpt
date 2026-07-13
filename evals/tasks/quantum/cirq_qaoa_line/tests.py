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

    edges = mod.maxcut_line_edges()
    if edges != [(0, 1), (1, 2), (2, 3)]:
        failures.append(f"maxcut_line_edges() = {edges}, expected [(0,1),(1,2),(2,3)]")

    # Optimal MaxCut value of a 4-node line is 3.
    opt = mod.best_maxcut_value(edges, 4)
    if opt != 3:
        failures.append(f"best_maxcut_value() = {opt}, expected 3")

    # maxcut_value correctness on known bitstrings
    if mod.maxcut_value("0101", edges) != 3:
        failures.append("maxcut_value('0101') should be 3")
    if mod.maxcut_value("0000", edges) != 0:
        failures.append("maxcut_value('0000') should be 0")
    if mod.maxcut_value("0011", edges) != 1:
        failures.append("maxcut_value('0011') should be 1 (only edge 1-2 is cut)")

    # Circuit construction: must be a Cirq Circuit with measurements available
    try:
        circ = mod.qaoa_line_circuit(gamma=0.3, beta=0.2)
        if not hasattr(circ, "moments"):
            failures.append("qaoa_line_circuit() did not return a Circuit-like object")
    except Exception as e:  # noqa: BLE001
        failures.append(f"qaoa_line_circuit() raised: {e}")

    # Sampling: must return a histogram dict with bitstring keys
    try:
        hist = mod.measure_bitstrings(gamma=0.4, beta=0.2, repetitions=200, seed=1)
        if not isinstance(hist, dict) or not hist:
            failures.append("measure_bitstrings() must return a non-empty dict")
        else:
            for k in hist:
                if len(k) != 4 or any(c not in "01" for c in k):
                    failures.append(f"histogram key {k!r} is not a 4-char bitstring")
                    break
    except Exception as e:  # noqa: BLE001
        failures.append(f"measure_bitstrings() raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or ["Cirq QAOA line graph circuit, sampling, and MaxCut value all correct"],
    }
