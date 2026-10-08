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

    triangle = [(0, 1), (1, 2), (0, 2)]
    if module.maxcut_cost("000", triangle) != 0:
        failures.append("maxcut_cost('000', triangle) should be 0")
    if module.maxcut_cost("010", triangle) != 2:
        failures.append("maxcut_cost('010', triangle) should be 2")

    line = [(0, 1), (1, 2), (2, 3)]
    if module.maxcut_cost("0101", line) != 3:
        failures.append("maxcut_cost('0101', line) should be 3")

    best_bits, best_cost = module.brute_force_maxcut(3, triangle)
    if best_cost != 2:
        failures.append(f"brute_force_maxcut(triangle) -> cost {best_cost}, expected 2")
    if module.maxcut_cost(best_bits, triangle) != best_cost:
        failures.append("brute_force_maxcut returned inconsistent bitstring/cost")

    landscape = module.qaoa_cost_landscape(3, triangle)
    if len(landscape) != 8:
        failures.append(f"landscape length={len(landscape)}, expected 8")
    else:
        costs = [cost for _, cost in landscape]
        if costs != sorted(costs, reverse=True):
            failures.append("qaoa_cost_landscape is not sorted descending by cost")

    try:
        module.maxcut_cost("01a", [(0, 1)])
        failures.append("maxcut_cost accepted an invalid bitstring")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["bitstring MaxCut landscape works without hidden helper names"],
    }
