import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mat(value):
    """Return value if it looks like a list-of-lists matrix, else None."""
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], (list, tuple)):
        return value
    return None


def _entries_correct(actual, expected, tol=1e-6):
    """Count matching entries between two same-shape matrices (0 if invalid)."""
    actual = _mat(actual)
    if actual is None or len(actual) != len(expected):
        return 0
    count = 0
    for row_a, row_b in zip(actual, expected):
        if not isinstance(row_a, (list, tuple)) or len(row_a) != len(row_b):
            return 0
        for x, y in zip(row_a, row_b):
            if abs(float(x) - y) <= tol:
                count += 1
    return count


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    s2 = 1.0 / math.sqrt(2)

    # --- density_from_state on a single qubit ---
    try:
        rho0 = module.density_from_state([1.0, 0.0])
    except Exception as e:  # noqa: BLE001
        rho0 = None
        failures.append(f"density_from_state raised: {e}")
    if _mat(rho0) is None:
        failures.append("density_from_state(|0>) returned non-matrix, expected 2x2")
    elif abs(float(rho0[0][0]) - 1.0) > 1e-9:
        failures.append(
            f"density_from_state(|0>) row0col0={float(rho0[0][0]):.6f}, expected 1.000000"
        )

    # --- GHZ density matrix ---
    ghz = [s2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, s2]
    try:
        rho_ghz = module.density_from_state(ghz)
    except Exception as e:  # noqa: BLE001
        rho_ghz = None
        failures.append(f"density_from_state(GHZ) raised: {e}")
    if _mat(rho_ghz) is not None:
        trace = sum(float(rho_ghz[i][i]) for i in range(8))
        if abs(trace - 1.0) > 1e-6:
            failures.append(f"ghz_rho trace={trace:.6f}, expected 1.000000")
        if abs(float(rho_ghz[0][7]) - 0.5) > 1e-6:
            failures.append(f"ghz_rho row0col7={float(rho_ghz[0][7]):.6f}, expected 0.500000")

    # --- partial trace over one qubit of GHZ -> maximally mixed pair ---
    expected_red4 = [
        [0.5, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.5],
    ]
    pt_ghz = None
    try:
        pt_ghz = module.partial_trace(rho_ghz, [2, 2, 2], [0])
    except Exception as e:  # noqa: BLE001
        failures.append(f"partial_trace(GHZ, [0]) raised: {e}")
    correct_pt = _entries_correct(pt_ghz, expected_red4)
    if correct_pt != 16:
        failures.append(f"pt_entries_correct={correct_pt}, expected 16")

    # --- entropy of the reduced state = 1 (two-bit Bell-like correlations) ---
    try:
        ent_red = module.von_neumann_entropy(pt_ghz) if _mat(pt_ghz) is not None else None
    except Exception as e:  # noqa: BLE001
        ent_red = None
        failures.append(f"von_neumann_entropy raised: {e}")
    if ent_red is None:
        failures.append("entropy_red=0.000000, expected 1.000000")
    elif abs(ent_red - 1.0) > 1e-6:
        failures.append(f"entropy_red={float(ent_red):.6f}, expected 1.000000")

    # --- tracing out a different subsystem gives the same reduced state ---
    try:
        pt_ghz_b = module.partial_trace(rho_ghz, [2, 2, 2], [1])
    except Exception as e:  # noqa: BLE001
        pt_ghz_b = None
        failures.append(f"partial_trace(GHZ, [1]) raised: {e}")
    correct_pt_b = _entries_correct(pt_ghz_b, expected_red4)
    if correct_pt_b != 16:
        failures.append(f"pt_b_entries_correct={correct_pt_b}, expected 16")

    # --- tracing out two qubits of GHZ -> one maximally mixed qubit ---
    expected_red2 = [[0.5, 0.0], [0.0, 0.5]]
    try:
        pt_ghz_2 = module.partial_trace(rho_ghz, [2, 2, 2], [0, 1])
    except Exception as e:  # noqa: BLE001
        pt_ghz_2 = None
        failures.append(f"partial_trace(GHZ, [0,1]) raised: {e}")
    correct_pt_2 = _entries_correct(pt_ghz_2, expected_red2)
    if correct_pt_2 != 4:
        failures.append(f"pt2_entries_correct={correct_pt_2}, expected 4")
    try:
        ent_red2 = module.von_neumann_entropy(pt_ghz_2) if _mat(pt_ghz_2) is not None else None
    except Exception as e:  # noqa: BLE001
        ent_red2 = None
        failures.append(f"von_neumann_entropy(2x2) raised: {e}")
    if ent_red2 is None:
        failures.append("entropy_red2=0.000000, expected 1.000000")
    elif abs(ent_red2 - 1.0) > 1e-6:
        failures.append(f"entropy_red2={float(ent_red2):.6f}, expected 1.000000")

    # --- W state: 1-qubit reduced entropy = -(2/3)log2(2/3)-(1/3)log2(1/3) ---
    w = [0.0] * 8
    inv_s3 = 1.0 / math.sqrt(3.0)
    w[1] = inv_s3  # |001>
    w[2] = inv_s3  # |010>
    w[4] = inv_s3  # |100>
    expected_w = -(2.0 / 3.0) * math.log2(2.0 / 3.0) - (1.0 / 3.0) * math.log2(1.0 / 3.0)
    try:
        rho_w = module.density_from_state(w)
    except Exception as e:  # noqa: BLE001
        rho_w = None
        failures.append(f"density_from_state(W) raised: {e}")
    try:
        pt_w = module.partial_trace(rho_w, [2, 2, 2], [0, 1]) if _mat(rho_w) is not None else None
    except Exception as e:  # noqa: BLE001
        pt_w = None
        failures.append(f"partial_trace(W, [0,1]) raised: {e}")
    try:
        ent_w = module.von_neumann_entropy(pt_w) if _mat(pt_w) is not None else None
    except Exception as e:  # noqa: BLE001
        ent_w = None
        failures.append(f"von_neumann_entropy(W) raised: {e}")
    if ent_w is None:
        failures.append(f"w_state_entropy=0.000000, expected {expected_w:.6f}")
    elif abs(ent_w - expected_w) > 1e-6:
        failures.append(f"w_state_entropy={float(ent_w):.6f}, expected {expected_w:.6f}")

    # --- product state |010>: reduced entropy must be exactly 0 ---
    try:
        rho_prod = module.density_from_state([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    except Exception as e:  # noqa: BLE001
        rho_prod = None
        failures.append(f"density_from_state(|010>) raised: {e}")
    try:
        pt_prod = (
            module.partial_trace(rho_prod, [2, 2, 2], [1]) if _mat(rho_prod) is not None else None
        )
    except Exception as e:  # noqa: BLE001
        pt_prod = None
        failures.append(f"partial_trace(|010>, [1]) raised: {e}")
    try:
        ent_prod = module.von_neumann_entropy(pt_prod) if _mat(pt_prod) is not None else None
    except Exception as e:  # noqa: BLE001
        ent_prod = None
        failures.append(f"von_neumann_entropy(product) raised: {e}")
    if ent_prod is None:
        failures.append("product_entropy=1.000000, expected 0.000000")
    elif abs(ent_prod) > 1e-6:
        failures.append(f"product_entropy={float(ent_prod):.6f}, expected 0.000000")

    return {
        "passed": not failures,
        "details": failures
        or ["Partial trace and von Neumann entropy correct on GHZ, W, and product states"],
    }
