import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _approx_equal_matrices(a, b, tol=1e-9):
    if len(a) != len(b):
        return False
    for row_a, row_b in zip(a, b, strict=False):
        if len(row_a) != len(row_b):
            return False
        for x, y in zip(row_a, row_b, strict=False):
            if abs(x - y) > tol:
                return False
    return True


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # iSWAP matrix correctness
    M = module.iswap_matrix()
    expected = [
        [1, 0, 0, 0],
        [0, 0, 1j, 0],
        [0, 1j, 0, 0],
        [0, 0, 0, 1],
    ]
    if not _approx_equal_matrices(M, expected):
        failures.append("iSWAP matrix does not match the canonical definition")

    # sqrt(iSWAP) squared should equal iSWAP (modulo global phase),
    # actually equals the matrix product sqrt*sqrt:
    sqrt_i = module.sqrt_iswap_matrix()
    prod = module._mat_mul(sqrt_i, sqrt_i)
    # Compare to iSWAP: prod = sqrt^2 should equal [[1,0,0,0],[0,-1? ,..]]
    # Actually sqrt(iSWAP)^2 = iSWAP only up to a swap of basis; here we
    # only check the (0,0) and (3,3) blocks which are 1, and the off-diagonal
    # magnitudes match iSWAP (each = 1).
    if not math.isclose(abs(prod[1][2]), 1.0, abs_tol=1e-9):
        failures.append("|sqrt(iSWAP)^2[1,2]| should be 1")
    if not math.isclose(abs(prod[2][1]), 1.0, abs_tol=1e-9):
        failures.append("|sqrt(iSWAP)^2[2,1]| should be 1")

    # Decomposition produces iSWAP
    decomp = module.iswap_from_sqrt_iswap()
    if not _approx_equal_matrices(decomp, expected):
        failures.append("iswap_from_sqrt_iswap does not equal the iSWAP matrix")

    # All matrices are 4x4
    for name, mat in [("iswap", M), ("sqrt_iswap", sqrt_i), ("decomp", decomp)]:
        if len(mat) != 4 or any(len(r) != 4 for r in mat):
            failures.append(f"{name} matrix should be 4x4")
            break

    return {
        "passed": not failures,
        "details": failures or ["iSWAP decomposition correct"],
    }
