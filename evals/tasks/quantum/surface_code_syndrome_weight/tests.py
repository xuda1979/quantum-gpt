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

    # Manhattan distance
    if module.manhattan_distance((0, 0), (3, 4)) != 7:
        failures.append("Manhattan((0,0),(3,4)) should be 7")
    if module.manhattan_distance((1, 1), (1, 1)) != 0:
        failures.append("Manhattan to self should be 0")

    # Empty pairing
    if module.pair_defects_min_weight([]) != []:
        failures.append("empty defect list should give empty pairing")

    # Two defects: trivial
    p = module.pair_defects_min_weight([(0, 0), (1, 2)])
    if p != [(0, 1)]:
        failures.append(f"two defects should pair as [(0,1)], got {p}")

    # Four defects: choose minimum total weight
    defects = [(0, 0), (0, 2), (3, 0), (3, 2)]
    p = module.pair_defects_min_weight(defects)
    cost = module.total_pairing_weight(defects, p)
    # Optimal: pair (0,1) and (2,3) gives 2 + 2 = 4
    if cost != 4:
        failures.append(f"4-defect optimum cost should be 4, got {cost}")
    # Verify each defect appears exactly once
    flat = sorted([i for pair in p for i in pair])
    if flat != [0, 1, 2, 3]:
        failures.append("each defect should appear exactly once in pairing")

    # Odd number of defects should raise
    try:
        module.pair_defects_min_weight([(0, 0), (1, 1), (2, 2)])
        failures.append("should raise on odd number of defects")
    except ValueError:
        pass

    # Total pairing weight helper
    if module.total_pairing_weight([(0, 0), (1, 1)], [(0, 1)]) != 2:
        failures.append("total_pairing_weight helper mismatch")

    return {
        "passed": not failures,
        "details": failures or ["Surface code syndrome pairing weight correct"],
    }
