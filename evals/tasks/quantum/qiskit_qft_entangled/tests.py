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

    # 4. After QFT on (|000>+|111>)/sqrt(2), all 8 amplitudes should be non-zero
    #    and equal in magnitude (1/sqrt(8) up to phase). This is the key property:
    #    QFT spreads the GHZ state uniformly across the computational basis.
    try:
        hist = mod.amplitude_histogram(n, tol=1e-9)
        if len(hist) != 8:
            failures.append(f"expected 8 non-zero amplitudes after QFT on GHZ, got {len(hist)}")
        else:
            mags = [abs(a) for a in hist.values()]
            if max(mags) - min(mags) > 1e-6:
                failures.append(
                    f"amplitude magnitudes not uniform: max={max(mags):.6f} min={min(mags):.6f}"
                )
    except Exception as e:  # noqa: BLE001
        failures.append(f"amplitude_histogram() raised: {e}")

    return {
        "passed": not failures,
        "details": failures or ["Qiskit GHZ + QFT circuit and uniform-amplitude property correct"],
    }
