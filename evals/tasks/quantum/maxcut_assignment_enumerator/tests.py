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

    if module.enumerate_bitstrings(2) != ["00", "01", "10", "11"]:
        failures.append("enumerate_bitstrings(2) should enumerate all assignments in lexical order")

    triangle = [(0, 1), (1, 2), (0, 2)]
    if module.cut_value("010", triangle) != 2:
        failures.append("cut_value('010', triangle) should be 2")

    best_bits, best_cost = module.best_cut_assignment(3, triangle)
    if best_cost != 2:
        failures.append(f"best_cut_assignment(triangle) -> cost {best_cost}, expected 2")
    if module.cut_value(best_bits, triangle) != best_cost:
        failures.append("best_cut_assignment returned inconsistent assignment/cost")

    try:
        module.enumerate_bitstrings(0)
        failures.append("enumerate_bitstrings(0) did not raise ValueError")
    except ValueError:
        pass

    try:
        module.cut_value("01a", [(0, 1)])
        failures.append("cut_value accepted invalid bitstring")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["maxcut assignment enumerator imports itertools and returns stable best cuts"],
    }
