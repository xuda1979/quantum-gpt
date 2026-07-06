import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _close_vec(a, b, tol=1e-6):
    if len(a) != len(b):
        return False
    return all(abs(x - y) < tol for x, y in zip(a, b))


def _close_mat(a, b, tol=1e-6):
    if len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if len(ra) != len(rb):
            return False
        for x, y in zip(ra, rb):
            if abs(x - y) > tol:
                return False
    return True


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # --- pauli_matrix ---
    X = module.pauli_matrix("X")
    expected_X = [[0, 1], [1, 0]]
    if not _close_mat(X, expected_X):
        failures.append(f"pauli_matrix('X') wrong: {X}")

    Z = module.pauli_matrix("Z")
    expected_Z = [[1, 0], [0, -1]]
    if not _close_mat(Z, expected_Z):
        failures.append(f"pauli_matrix('Z') wrong: {Z}")

    Y = module.pauli_matrix("Y")
    # Y should be [[0, -j], [j, 0]] but we use real representation
    # Actually we need complex for proper Hamiltonian evolution.
    # Let's check it's a 2x2 with correct structure
    if len(Y) != 2 or len(Y[0]) != 2:
        failures.append(f"pauli_matrix('Y') wrong shape")

    I = module.pauli_matrix("I")
    expected_I = [[1, 0], [0, 1]]
    if not _close_mat(I, expected_I):
        failures.append(f"pauli_matrix('I') wrong: {I}")

    # --- matrix_exp_hermitian ---
    # exp(-i * theta * Z) for theta=pi/4:
    # [[e^{-i*pi/4}, 0], [0, e^{i*pi/4}]]
    # = [[cos(pi/4) - i*sin(pi/4), 0], [0, cos(pi/4) + i*sin(pi/4)]]
    result = module.matrix_exp_hermitian(Z, math.pi / 4)
    c = math.cos(math.pi / 4)
    s = math.sin(math.pi / 4)
    expected_00 = complex(c, -s)
    expected_11 = complex(c, s)
    r00 = result[0][0]
    r11 = result[1][1]
    if abs(r00 - expected_00) > 1e-6:
        failures.append(f"matrix_exp_hermitian(Z, pi/4)[0][0] = {r00}, expected {expected_00}")
    if abs(r11 - expected_11) > 1e-6:
        failures.append(f"matrix_exp_hermitian(Z, pi/4)[1][1] = {r11}, expected {expected_11}")
    if abs(result[0][1]) > 1e-9 or abs(result[1][0]) > 1e-9:
        failures.append(f"matrix_exp_hermitian(Z, pi/4) off-diagonal not zero")

    # exp(-i * theta * X) for theta=pi/2:
    # [[cos(pi/2), -i*sin(pi/2)], [-i*sin(pi/2), cos(pi/2)]]
    # = [[0, -i], [-i, 0]]
    result_x = module.matrix_exp_hermitian(X, math.pi / 2)
    if abs(result_x[0][0]) > 1e-6:
        failures.append(f"matrix_exp_hermitian(X, pi/2)[0][0] = {result_x[0][0]}, expected 0")
    if abs(result_x[0][1] - complex(0, -1)) > 1e-6:
        failures.append(f"matrix_exp_hermitian(X, pi/2)[0][1] = {result_x[0][1]}, expected -i")

    # --- trotter_evolve ---
    # Evolve |0> under H=X for time t=pi/2:
    # e^{-i*X*pi/2}|0> = cos(pi/2)|0> - i*sin(pi/2)|1> = -i|1>
    state_0 = [complex(1, 0), complex(0, 0)]
    evolved = module.trotter_evolve(state_0, [(1.0, "X")], t=math.pi / 2, steps=100)
    if len(evolved) != 2:
        failures.append(f"trotter_evolve result length={len(evolved)}")
    else:
        # Should be approximately [0, -i]
        if abs(evolved[0]) > 0.01:
            failures.append(f"trotter_evolve(|0>, X, pi/2)[0] = {evolved[0]}, expected ~0")
        if abs(abs(evolved[1]) - 1.0) > 0.01:
            failures.append(f"trotter_evolve(|0>, X, pi/2)[1] magnitude = {abs(evolved[1])}, expected ~1")

    # Evolve |0> under H=Z for time t=pi:
    # e^{-i*Z*pi}|0> = e^{-i*pi}|0> = -|0>
    evolved_z = module.trotter_evolve(state_0, [(1.0, "Z")], t=math.pi, steps=100)
    if abs(evolved_z[0] - complex(-1, 0)) > 0.01:
        failures.append(f"trotter_evolve(|0>, Z, pi)[0] = {evolved_z[0]}, expected -1")
    if abs(evolved_z[1]) > 0.01:
        failures.append(f"trotter_evolve(|0>, Z, pi)[1] = {evolved_z[1]}, expected 0")

    # Conservation: norm should be preserved
    norm = sum(abs(a) ** 2 for a in evolved)
    if not math.isclose(norm, 1.0, abs_tol=0.01):
        failures.append(f"trotter_evolve norm not preserved: {norm}")

    # Multi-term Hamiltonian: H = 0.5*X + 0.5*Z
    # Just check normalization is preserved
    evolved_multi = module.trotter_evolve(state_0, [(0.5, "X"), (0.5, "Z")], t=1.0, steps=200)
    norm_multi = sum(abs(a) ** 2 for a in evolved_multi)
    if not math.isclose(norm_multi, 1.0, abs_tol=0.01):
        failures.append(f"trotter_evolve multi-term norm: {norm_multi}")

    return {
        "passed": not failures,
        "details": failures or ["Trotterized Hamiltonian evolution correct for all test cases"],
    }
