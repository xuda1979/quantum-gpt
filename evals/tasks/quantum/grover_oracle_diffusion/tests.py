import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _close_vec(a, b, tol=1e-9):
    if len(a) != len(b):
        return False
    return all(abs(x - y) < tol for x, y in zip(a, b))


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # --- uniform_superposition ---
    # 2 qubits -> 4 amplitudes, each 1/2
    us2 = module.uniform_superposition(2)
    if len(us2) != 4:
        failures.append(f"uniform_superposition(2) length={len(us2)}, expected 4")
    elif not all(math.isclose(a, 0.5, abs_tol=1e-9) for a in us2):
        failures.append(f"uniform_superposition(2) amplitudes wrong: {us2}")

    us3 = module.uniform_superposition(3)
    if len(us3) != 8:
        failures.append(f"uniform_superposition(3) length={len(us3)}, expected 8")
    elif not all(math.isclose(a, 1.0 / math.sqrt(8), abs_tol=1e-9) for a in us3):
        failures.append(f"uniform_superposition(3) amplitudes wrong")

    # --- oracle ---
    # Oracle flips the sign of the marked state.
    # 2-qubit, mark state 3 (|11>): [a, b, c, d] -> [a, b, c, -d]
    state = [0.5, 0.5, 0.5, 0.5]
    after_oracle = module.oracle(state, 3)
    if len(after_oracle) != 4:
        failures.append(f"oracle returned length {len(after_oracle)}")
    else:
        expected = [0.5, 0.5, 0.5, -0.5]
        if not _close_vec(after_oracle, expected):
            failures.append(f"oracle([0.5]*4, 3) -> {after_oracle}, expected {expected}")

    # Oracle on state 0
    state2 = [0.5, 0.5, 0.5, 0.5]
    after_oracle2 = module.oracle(state2, 0)
    expected2 = [-0.5, 0.5, 0.5, 0.5]
    if not _close_vec(after_oracle2, expected2):
        failures.append(f"oracle([0.5]*4, 0) -> {after_oracle2}, expected {expected2}")

    # --- diffusion ---
    # Diffusion operator: 2|s><s| - I where |s> is uniform superposition.
    # On state [0.5, 0.5, 0.5, -0.5]:
    #   mean = (0.5+0.5+0.5-0.5)/4 = 0.25
    #   diffusion: 2*mean - a_i  =>  [0.5-0.5, 0.5-0.5, 0.5-0.5, 0.5+0.5] = [0, 0, 0, 1]
    diff_in = [0.5, 0.5, 0.5, -0.5]
    after_diff = module.diffusion(diff_in)
    expected_diff = [0.0, 0.0, 0.0, 1.0]
    if not _close_vec(after_diff, expected_diff, tol=1e-9):
        failures.append(f"diffusion({diff_in}) -> {after_diff}, expected {expected_diff}")

    # --- grover_search ---
    # 2-qubit Grover with 1 iteration should find marked state deterministically
    # when there is exactly 1 marked state out of 4.
    result_state = module.grover_search(n_qubits=2, marked=3, iterations=1)
    if len(result_state) != 4:
        failures.append(f"grover_search result length={len(result_state)}, expected 4")
    else:
        # After 1 Grover iteration on 2 qubits with 1 marked state,
        # the probability of measuring the marked state should be 1.0
        prob_marked = result_state[3] ** 2
        if not math.isclose(prob_marked, 1.0, abs_tol=1e-6):
            failures.append(
                f"grover_search(2, marked=3, iter=1) P(marked)={prob_marked:.6f}, expected 1.0"
            )

    # 3-qubit Grover: 1 marked out of 8, optimal iterations = floor(pi/4 * sqrt(8)) = 2
    result3 = module.grover_search(n_qubits=3, marked=5, iterations=2)
    if len(result3) != 8:
        failures.append(f"grover_search(3) result length={len(result3)}")
    else:
        prob_marked3 = result3[5] ** 2
        # After 2 iterations, probability should be high (>0.94)
        if prob_marked3 < 0.94:
            failures.append(
                f"grover_search(3, marked=5, iter=2) P(marked)={prob_marked3:.6f}, expected >0.94"
            )

    # Normalization check
    if result3:
        norm = sum(a ** 2 for a in result3)
        if not math.isclose(norm, 1.0, abs_tol=1e-6):
            failures.append(f"grover_search(3) not normalized: sum|a|^2={norm}")

    return {
        "passed": not failures,
        "details": failures or ["Grover oracle and diffusion simulation correct for all test cases"],
    }
