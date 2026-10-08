import importlib.util
import math


def _load(path: str):
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_tests(candidate_path: str) -> dict:
    failures: list[str] = []
    try:
        mod = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return {"passed": False, "details": [f"import failed: {e}"]}

    n = 3

    # 1. ghz_circuit has the right structure
    try:
        g = mod.ghz_circuit(n)
        if g.num_qubits != n:
            failures.append(f"ghz_circuit num_qubits = {g.num_qubits}, expected {n}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"ghz_circuit() raised: {e}")

    # 2. qft_circuit has the right structure
    try:
        q = mod.qft_circuit(n)
        if q.num_qubits != n:
            failures.append(f"qft_circuit num_qubits = {q.num_qubits}, expected {n}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"qft_circuit() raised: {e}")

    # 3. Statevector has the right norm
    try:
        sv = mod.ghz_then_qft_statevector(n)
        norm = math.sqrt(sum(abs(a) ** 2 for a in sv))
        if abs(norm - 1.0) > 1e-6:
            failures.append(f"|statevector| = {norm:.6f}, expected 1.0")
    except Exception as e:  # noqa: BLE001
        failures.append(f"ghz_then_qft_statevector() raised: {e}")

    # 4. After QFT on (|000>+|111>)/sqrt(2), the interference pattern has
    #    exactly ONE null amplitude — bitstring 100 for this no-final-swap QFT
    #    convention — i.e. 7 non-zero amplitudes with magnitudes
    #    {0.5, sqrt(2+sqrt(2))/4, sqrt(2)/4, sqrt(2-sqrt(2))/4} ≈
    #    {0.5, 0.4619, 0.3536, 0.1913}. This is NOT uniform (2026-08-25: the
    #    old all-8-uniform expectation was mathematically wrong for this
    #    convention and failed the task's own reference on qiskit 1.4.x AND
    #    2.x — poisoned baseline). Simulator float noise may leave the null
    #    marginally above tol on some versions, hence 7-8 accepted.
    try:
        hist = mod.amplitude_histogram(n, tol=1e-9)
        n_terms = len(hist)
        if not (7 <= n_terms <= 8):
            failures.append(f"expected 7-8 non-zero amplitudes after QFT on GHZ, got {n_terms}")
        else:
            mags = sorted(abs(a) for a in hist.values())
            mx, mn = mags[-1], mags[0]
            if mx > 0.5 + 1e-9:
                failures.append(f"amplitude exceeds QFT-of-GHZ max 0.5: max={mx:.6f}")
            if mn < 0.1913 - 1e-6:
                failures.append(f"unexpected near-zero amplitude: min={mn:.6f}")
            if mx - mn < 0.25:
                failures.append(
                    f"amplitudes too uniform for QFT-of-GHZ interference: "
                    f"max={mx:.6f} min={mn:.6f}"
                )
    except Exception as e:  # noqa: BLE001
        failures.append(f"amplitude_histogram() raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or ["Qiskit GHZ + QFT circuit and interference-pattern property correct"],
    }
