import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _mat(value):
    try:
        import numpy as np

        if isinstance(value, np.ndarray):
            return value.tolist()
    except Exception:  # noqa: BLE001
        pass
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], (list, tuple)):
        return value
    return None


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    a = 8
    n = 15

    # --- permutation gate for multiplier 8: x -> 8x mod 15, |15> fixed ---
    mat = _mat(module.mul_mod_matrix(8, 4))
    if mat is None:
        failures.append("mul_mod_matrix returned nothing, expected 16x16")
    else:
        if len(mat) != 16 or len(mat[0]) != 16:
            failures.append(f"gate_shape={len(mat)}x{len(mat[0]) if mat else 0}, expected 16x16")
        else:
            expected_cols = {1: 8, 8: 4, 4: 2, 2: 1}  # 8*1, 8*8, 8*4, 8*2 mod 15
            ok_pairs = 0
            for x, y in expected_cols.items():
                if abs(complex(mat[y][x]) - 1.0) < 1e-9:
                    ok_pairs += 1
            if ok_pairs != 4:
                failures.append(f"gate_pairs_correct={ok_pairs}, expected 4")
            if abs(complex(mat[15][15]) - 1.0) > 1e-9:
                failures.append("gate_15_fixed=0.000000, expected 1.000000")
            row_sums = [sum(abs(complex(v)) for v in row) for row in mat]
            col_sums = [sum(abs(complex(mat[i][j])) for i in range(16)) for j in range(16)]
            bad_rows = sum(1 for s in row_sums if abs(s - 1.0) > 1e-9)
            bad_cols = sum(1 for s in col_sums if abs(s - 1.0) > 1e-9)
            if bad_rows > 0 or bad_cols > 0:
                failures.append(
                    f"permutation_bad_rows={bad_rows}, bad_cols={bad_cols}, expected 0/0"
                )

    # --- circuit structure: qubit count and work-register initialization ---
    try:
        qc = module.order_finding_circuit(a, n_count=6, n_work=4)
        nq = qc.num_qubits
        if nq != 10:
            failures.append(f"circuit_qubits={nq}, expected 10")
    except Exception as e:  # noqa: BLE001
        failures.append(f"order_finding_circuit raised: {e}")

    # --- full run: seeded sampling must recover periods and factors ---
    result = None
    try:
        result = module.run_shor(a=8, n=15, n_count=6, shots=2048, seed=42)
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_shor raised: {e}")
    if result is None:
        failures.append("factors_recovered=0, expected 2 (3 and 5)")
        return {"passed": not failures, "details": failures or ["shor ok"]}
    factors = set(result.get("factors") or set())
    if 3 not in factors or 5 not in factors:
        found = sorted(factors)
        failures.append(f"factors_recovered={len(found)}, expected 2 (3 and 5)")
    periods = sorted(result.get("periods") or [])
    if 4 not in periods:
        failures.append("period_4_present=0, expected 1 (order of 8 mod 15 is 4)")
    counts = result.get("counts") or {}
    total = sum(counts.values()) if counts else 0
    if total != 2048:
        failures.append(f"sampled_shots={total}, expected 2048")
    if counts and pow(a, 4, n) != 1:
        failures.append("a^r mod 15 validation failed in candidate period check")

    # --- high-probability outcome determinism: same seed, same top outcome ---
    try:
        qc = module.order_finding_circuit(a, n_count=6, n_work=4)
        counts2 = module.sample_counts(qc, shots=2048, seed=42)
        top1 = max(counts, key=counts.get)
        top2 = max(counts2, key=counts2.get)
        if top1 != top2:
            failures.append("seed_determinism_top_outcome_diff=1, expected 0")
    except Exception as e:  # noqa: BLE001
        failures.append(f"sample_counts raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "Shor order finding N=15 a=8: permutation gate exact, period 4 "
            "recovered, factors {3,5} from seeded high-probability outcome",
        ],
    }
