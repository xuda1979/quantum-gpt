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

    # s = 0b101 (n=3): equations y.s = 0 must include y not orthogonal...
    # We construct equations that are satisfied by s = 0b101
    s = 0b101
    eqs = []
    for y in [0b000, 0b010, 0b101]:
        b = bin(y & s).count("1") % 2
        eqs.append((y, b))
    # Note: y=0b101 gives b=0 because s.s = popcount(s) mod 2 = 2 mod 2 = 0
    rec = module.solve_simon_system(eqs, 3)
    # The system admits both s=0 and s=0b101 (rank-deficient); candidate
    # picks the lowest-index-free-variable solution, which should be 0b101.
    if rec != 0b101:
        failures.append(f"expected s=5, got {rec}")

    # Full-rank system => only solution s = 0
    full = [(0b001, 0), (0b010, 0), (0b100, 0)]
    if module.solve_simon_system(full, 3) != 0:
        failures.append("full-rank zero-RHS system should give s=0")

    # Inconsistent system should raise
    bad = [(0b000, 1)]
    try:
        module.solve_simon_system(bad, 3)
        failures.append("should raise on inconsistent system")
    except ValueError:
        pass

    # n=4 case: s = 0b0110
    s4 = 0b0110
    eqs4 = []
    for y in [0b0000, 0b0001, 0b1001, 0b0110]:
        b = bin(y & s4).count("1") % 2
        eqs4.append((y, b))
    rec4 = module.solve_simon_system(eqs4, 4)
    if rec4 != 0b0110:
        failures.append(f"n=4 expected s=6, got {rec4}")

    return {
        "passed": not failures,
        "details": failures or ["Simon period recovery correct for all test cases"],
    }
