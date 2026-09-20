import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _vec(value):
    return value if isinstance(value, (list, tuple)) else None


def _inner(a, b):
    return sum(complex(x) * complex(y).conjugate() for x, y in zip(a, b))


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    s2 = 1.0 / math.sqrt(2)

    # --- Bell statevectors ---
    expected = [
        [s2, 0.0, 0.0, s2],
        [s2, 0.0, 0.0, -s2],
        [0.0, s2, s2, 0.0],
        [0.0, s2, -s2, 0.0],
    ]
    bells: list = []
    try:
        bells = [module.bell_statevector(k) for k in range(4)]
    except Exception as e:  # noqa: BLE001
        failures.append(f"bell_statevector raised: {e}")
    entries_correct = 0
    for k, state in enumerate(bells):
        if _vec(state) is None:
            failures.append(f"bell_statevector({k}) returned None, expected 4 entries")
            failures.append("bell_entries_correct=0, expected 16")
            continue
        if len(state) != 4:
            failures.append(f"bell_statevector({k}) length={len(state)}, expected 4")
            continue
        for j in range(4):
            if abs(complex(state[j]) - expected[k][j]) <= 1e-9:
                entries_correct += 1
    if entries_correct != 16:
        failures.append(f"bell_entries_correct={entries_correct}, expected 16")

    # --- Bell basis is orthonormal and unitary ---
    try:
        U = module.bell_basis_unitary()
    except Exception as e:  # noqa: BLE001
        U = None
        failures.append(f"bell_basis_unitary raised: {e}")
    ortho_correct = 0
    if U is None or not isinstance(U, (list, tuple)) or len(U) != 4:
        failures.append("bell_basis_unitary returned non-matrix, expected 4x4")
        failures.append("orthogonality_correct=0, expected 10")
    else:
        pairs = 0
        for i in range(4):
            for j in range(i, 4):
                pairs += 1
                ip = _inner([row[i] for row in U], [row[j] for row in U])
                want = 1.0 if i == j else 0.0
                if abs(ip - want) < 1e-9:
                    ortho_correct += 1
        if ortho_correct != pairs:
            failures.append(f"orthogonality_correct={ortho_correct}, expected {pairs}")

    # --- discrimination: each Bell state maps to its own index ---
    disc_correct = 0
    try:
        for k in range(4):
            idx = module.classify_bell(bells[k])
            if idx == k:
                disc_correct += 1
            else:
                failures.append(f"classify_bell(bell_{k}) = {idx}, expected {k}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"classify_bell raised: {e}")
    if disc_correct != 4:
        failures.append(f"discrimination_correct={disc_correct}, expected 4")

    # --- concurrence: Bell = 1, product = 0, separable superposition = 0 ---
    try:
        c_bell = module.entanglement_concurrence(bells[0])
        c_prod = module.entanglement_concurrence([1.0, 0.0, 0.0, 0.0])
        c_sep = module.entanglement_concurrence([s2, s2, 0.0, 0.0])
    except Exception as e:  # noqa: BLE001
        c_bell = c_prod = c_sep = None
        failures.append(f"entanglement_concurrence raised: {e}")
    if c_bell is None:
        failures.append("concurrence=0.000000 need>=0.990000")
    else:
        if abs(c_bell - 1.0) > 1e-9:
            failures.append(f"concurrence={float(c_bell):.6f} need>=0.990000")
        if abs(c_prod) > 1e-9:
            failures.append(f"concurrence_prod={float(c_prod):.6f}, expected 0.000000")
        if abs(c_sep) > 1e-9:
            failures.append(f"concurrence_sep={float(c_sep):.6f}, expected 0.000000")

    return {
        "passed": not failures,
        "details": failures
        or ["Bell basis states, unitary, discrimination, and concurrence all correct"],
    }
