import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _close(a, b, tol=1e-9):
    return abs(a - b) < tol


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # --- ghz_state ---
    # 2-qubit GHZ = Bell state: (|00> + |11>)/sqrt(2)
    ghz2 = module.ghz_state(2)
    if len(ghz2) != 4:
        failures.append(f"ghz_state(2) length={len(ghz2)}, expected 4")
    else:
        s2 = 1.0 / math.sqrt(2)
        if not _close(ghz2[0], s2) or not _close(ghz2[3], s2):
            failures.append(f"ghz_state(2)[0]={ghz2[0]}, [3]={ghz2[3]}, expected {s2}")
        if not _close(ghz2[1], 0) or not _close(ghz2[2], 0):
            failures.append(f"ghz_state(2) middle amplitudes nonzero: {ghz2}")

    # 3-qubit GHZ: (|000> + |111>)/sqrt(2)
    ghz3 = module.ghz_state(3)
    if len(ghz3) != 8:
        failures.append(f"ghz_state(3) length={len(ghz3)}, expected 8")
    else:
        s2 = 1.0 / math.sqrt(2)
        if not _close(ghz3[0], s2) or not _close(ghz3[7], s2):
            failures.append(f"ghz_state(3) endpoints wrong: [0]={ghz3[0]}, [7]={ghz3[7]}")
        for i in range(1, 7):
            if not _close(ghz3[i], 0):
                failures.append(f"ghz_state(3)[{i}]={ghz3[i]}, expected 0")
                break

    # 4-qubit GHZ
    ghz4 = module.ghz_state(4)
    if len(ghz4) != 16:
        failures.append(f"ghz_state(4) length={len(ghz4)}, expected 16")
    else:
        s2 = 1.0 / math.sqrt(2)
        if not _close(ghz4[0], s2) or not _close(ghz4[15], s2):
            failures.append(f"ghz_state(4) endpoints wrong")

    # Normalization
    for n, state in [(2, ghz2), (3, ghz3), (4, ghz4)]:
        norm = sum(a ** 2 for a in state)
        if not _close(norm, 1.0, tol=1e-6):
            failures.append(f"ghz_state({n}) not normalized: {norm}")

    # --- w_state ---
    # 3-qubit W state: (|001> + |010> + |100>)/sqrt(3)
    w3 = module.w_state(3)
    if len(w3) != 8:
        failures.append(f"w_state(3) length={len(w3)}, expected 8")
    else:
        s3 = 1.0 / math.sqrt(3)
        expected_nonzero = {1, 2, 4}  # |001>, |010>, |100>
        for i in range(8):
            if i in expected_nonzero:
                if not _close(w3[i], s3):
                    failures.append(f"w_state(3)[{i}]={w3[i]}, expected {s3}")
            else:
                if not _close(w3[i], 0):
                    failures.append(f"w_state(3)[{i}]={w3[i]}, expected 0")

    # --- ghz_witness_expectation ---
    # The GHZ witness W = I/2 - |GHZ><GHZ|
    # For the GHZ state: <W> = 1/2 - 1 = -1/2 (negative = entangled)
    # For a separable state: <W> >= 0

    witness_ghz = module.ghz_witness_expectation(ghz3, 3)
    if not _close(witness_ghz, -0.5, tol=1e-6):
        failures.append(f"ghz_witness(GHZ_3) = {witness_ghz}, expected -0.5")

    # Separable state |000>: <W> = 1/2 - |<000|GHZ>|^2 = 1/2 - 1/2 = 0
    sep = [0.0] * 8
    sep[0] = 1.0
    witness_sep = module.ghz_witness_expectation(sep, 3)
    if not _close(witness_sep, 0.0, tol=1e-6):
        failures.append(f"ghz_witness(|000>) = {witness_sep}, expected 0.0")

    # W state: <W> = 1/2 - |<W|GHZ>|^2 = 1/2 - 0 = 0.5
    witness_w = module.ghz_witness_expectation(w3, 3)
    if not _close(witness_w, 0.5, tol=1e-6):
        failures.append(f"ghz_witness(W_3) = {witness_w}, expected 0.5")

    # --- concurrence_2qubit ---
    # Bell state concurrence = 1
    c_bell = module.concurrence_2qubit(ghz2)
    if not _close(c_bell, 1.0, tol=1e-6):
        failures.append(f"concurrence(Bell) = {c_bell}, expected 1.0")

    # Product state |00> concurrence = 0
    prod = [1.0, 0.0, 0.0, 0.0]
    c_prod = module.concurrence_2qubit(prod)
    if not _close(c_prod, 0.0, tol=1e-6):
        failures.append(f"concurrence(|00>) = {c_prod}, expected 0.0")

    # Partially entangled: cos(pi/8)|00> + sin(pi/8)|11>
    a = math.cos(math.pi / 8)
    b = math.sin(math.pi / 8)
    partial = [a, 0.0, 0.0, b]
    c_partial = module.concurrence_2qubit(partial)
    expected_c = 2 * a * b  # = sin(pi/4) = 1/sqrt(2)
    if not _close(c_partial, expected_c, tol=1e-6):
        failures.append(f"concurrence(partial) = {c_partial}, expected {expected_c}")

    return {
        "passed": not failures,
        "details": failures or ["GHZ/W state construction and entanglement witness correct for all test cases"],
    }
