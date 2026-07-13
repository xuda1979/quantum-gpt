import cmath
import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # QFT^dagger . QFT = I
    for N in [2, 4, 8]:
        state = [complex(i + 1, 0) for i in range(N)]
        norm = math.sqrt(sum(abs(a) ** 2 for a in state))
        state = [a / norm for a in state]
        fwd = module.qft_amplitudes(state)
        rec = module.inverse_qft_amplitudes(fwd)
        if not all(
            math.isclose(abs(a - b), 0.0, abs_tol=1e-9) for a, b in zip(state, rec, strict=False)
        ):
            failures.append(f"QFT^dagger . QFT != I for N={N}")
            break

    # Inverse QFT of |j> should equal QFT row j conjugated
    # Specifically: iQFT|0> = uniform superposition
    N = 4
    zero = [0j] * N
    zero[0] = 1.0 + 0j
    iqft0 = module.inverse_qft_amplitudes(zero)
    expected = [complex(0.5, 0)] * N
    if not all(math.isclose(abs(iqft0[i] - expected[i]), 0.0, abs_tol=1e-9) for i in range(N)):
        failures.append("iQFT|0> should be uniform over N=4")

    # iQFT on |1> produces phases exp(-2*pi*i*k/N) / sqrt(N)
    one = [0j] * N
    one[1] = 1.0 + 0j
    iqft1 = module.inverse_qft_amplitudes(one)
    for k in range(N):
        exp_val = cmath.exp(-2j * cmath.pi * k / N) / math.sqrt(N)
        if not math.isclose(abs(iqft1[k] - exp_val), 0.0, abs_tol=1e-9):
            failures.append(f"iQFT|1>[{k}] phase mismatch")
            break

    # Non-power-of-2 should raise
    try:
        module.inverse_qft_amplitudes([1, 0, 1])
        failures.append("should raise on non-power-of-2 length")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["Inverse QFT recovery correct for all test cases"],
    }
