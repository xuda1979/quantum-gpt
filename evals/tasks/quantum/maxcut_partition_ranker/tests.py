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

    square_edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    if module.cut_size((-1, 1, -1, 1), square_edges) != 4:
        failures.append("cut_size should return 4 for the alternating square assignment")
    if module.cut_size((-1, -1, 1, 1), square_edges) != 2:
        failures.append("cut_size should return 2 when only two square edges cross the cut")

    path_edges = [(0, 1), (1, 2), (2, 3)]
    if module.cut_size((1, -1, 1, -1), path_edges) != 3:
        failures.append("cut_size should return 3 for the alternating path assignment")

    ranked = module.rank_ising_assignments(4, square_edges)
    if len(ranked) != 16:
        failures.append(f"rank_ising_assignments returned {len(ranked)} assignments, expected 16")
    elif ranked[0] != ((-1, 1, -1, 1), 4):
        failures.append(f"top-ranked square assignment was {ranked[0]!r}, expected ((-1, 1, -1, 1), 4)")

    best_assignment, best_score = module.best_ising_assignment(3, [(0, 1), (1, 2), (0, 2)])
    if best_score != 2:
        failures.append(f"best_ising_assignment on the triangle returned score {best_score}, expected 2")
    if module.cut_size(best_assignment, [(0, 1), (1, 2), (0, 2)]) != best_score:
        failures.append("best_ising_assignment returned an assignment/score pair that does not match cut_size")

    try:
        module.cut_size((1, 0, -1), [(0, 1)])
    except ValueError:
        pass
    except Exception as exc:
        failures.append(f"cut_size raised {type(exc).__name__} for invalid spins, expected ValueError")
    else:
        failures.append("cut_size accepted a spin assignment containing values outside {-1, 1}")

    return {
        "passed": not failures,
        "details": failures or ["MaxCut partition ranking works for deterministic Ising-style assignments"],
    }
