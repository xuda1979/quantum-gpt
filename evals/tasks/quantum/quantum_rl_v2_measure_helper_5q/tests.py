import importlib.util
import math

import numpy as np


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _StubRng:
    """Injected rng stub returning a fixed uniform() draw."""

    def __init__(self, value):
        self._value = value

    def uniform(self, low=0.0, high=1.0):
        return self._value


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []
    n = 32

    # --- exhaustive basis states: deterministic, no crash on p=0/1 ---
    basis_wrong = 0
    basis_bad_prob = 0
    bit16 = 1 << 4  # qubit 4 is the most significant bit (index 16)
    for i in range(n):
        state = [0.0j] * n
        state[i] = 1.0
        try:
            outcome, collapsed, prob = module.measure_qubit(state, 4)
        except Exception as e:  # noqa: BLE001
            failures.append(f"measure_qubit raised on basis state {i}: {e}")
            basis_wrong += 1
            continue
        expected = 1 if (i & bit16) else 0
        if outcome != expected:
            basis_wrong += 1
        if abs(prob - 1.0) > 1e-9:
            basis_bad_prob += 1
        # collapsed must be the basis state itself (new object)
        if (
            abs(complex(collapsed[i]) - 1.0) > 1e-9
            or sum(abs(complex(a)) for a in collapsed[:i] + collapsed[i + 1 :]) > 1e-9
        ):
            failures.append(f"collapsed_wrong_for_basis={i}, expected e_{i}")
    if basis_wrong:
        failures.append(f"basis_outcome_wrong={basis_wrong}, expected 0")
    if basis_bad_prob:
        failures.append(f"basis_probability_wrong={basis_bad_prob}, expected 0")

    # --- input must never be mutated ---
    state = [0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] + [0.0j] * (n - 8)
    state[16] = 0.8
    norm = math.sqrt(sum(abs(complex(a)) ** 2 for a in state))
    state = [complex(a) / norm for a in state]
    snapshot = list(state)
    try:
        module.measure_qubit(state, 4)
    except Exception as e:  # noqa: BLE001
        failures.append(f"measure_qubit raised on superposition: {e}")
    if state != snapshot:
        failures.append("input_mutated=1, expected 0")

    # --- collapsed branch + returned probability (stub rng forces outcome 1) ---
    try:
        outcome, collapsed, prob = module.measure_qubit(state, 4, rng=_StubRng(0.1))
        if outcome != 1:
            failures.append(f"stub_outcome={outcome}, expected 1")
        if abs(prob - 0.64) > 1e-9:
            failures.append(f"probability={prob:.9f}, expected 0.640000000")
        if abs(complex(collapsed[16]) - 1.0) > 1e-9:
            failures.append(f"collapsed_amp16={complex(collapsed[16])}, expected 1.0")
        stray = sum(abs(complex(a)) ** 2 for a in collapsed[:16] + collapsed[17:])
        if stray > 1e-9:
            failures.append(f"collapsed_stray={stray:.3e}, expected 0.0")
    except Exception as e:  # noqa: BLE001
        failures.append(f"measure_qubit raised with stub rng: {e}")

    # --- forced outcomes: legal ones pass, impossible ones raise ---
    zero_state = [0.0j] * n
    zero_state[0] = 1.0
    try:
        outcome, _, prob = module.measure_qubit(zero_state, 4, forced=0)
        if outcome != 0 or abs(prob - 1.0) > 1e-9:
            failures.append(f"forced0_outcome={outcome} prob={prob}, expected 0 1.0")
    except Exception as e:  # noqa: BLE001
        failures.append(f"forced=0 on |00000> raised: {e}")
    try:
        module.measure_qubit(zero_state, 4, forced=1)
        failures.append("forced=1 on |00000> must raise, got outcome")
    except ValueError:
        pass
    except Exception as e:  # noqa: BLE001
        failures.append(f"forced=1 on |00000> raised wrong type: {type(e).__name__}")
    one_state = [0.0j] * n
    one_state[16] = 1.0
    try:
        outcome, _, prob = module.measure_qubit(one_state, 4, forced=1)
        if outcome != 1 or abs(prob - 1.0) > 1e-9:
            failures.append(f"forced1_outcome={outcome} prob={prob}, expected 1 1.0")
    except Exception as e:  # noqa: BLE001
        failures.append(f"forced=1 on |10000> raised: {e}")

    # --- invalid states / impossible outcomes are rejected ---
    rejected = 0
    try:
        module.measure_qubit([1.0] * 4, 4)
        failures.append("short state must raise ValueError")
    except ValueError:
        rejected += 1
    except Exception as e:  # noqa: BLE001
        failures.append(f"short state raised wrong type: {type(e).__name__}")
    try:
        module.measure_qubit(zero_state, 5)
        failures.append("invalid qubit 5 must raise ValueError")
    except ValueError:
        rejected += 1
    except Exception as e:  # noqa: BLE001
        failures.append(f"invalid qubit raised wrong type: {type(e).__name__}")
    bad_norm = [0.5] * n
    try:
        module.measure_qubit(bad_norm, 4)
        failures.append("non-normalized state must raise ValueError")
    except ValueError:
        rejected += 1
    except Exception as e:  # noqa: BLE001
        failures.append(f"non-normalized raised wrong type: {type(e).__name__}")
    if rejected != 3:
        failures.append(f"rejected_invalid={rejected}, expected 3")

    # --- seeded Born-frequency test with Wilson interval ---
    try:
        ones = 0
        rng = np.random.default_rng(7)
        plus = [1.0 / math.sqrt(n)] * n
        for _ in range(2000):
            if module.measure_qubit(plus, 4, rng=rng)[0] == 1:
                ones += 1
        lo, hi = module.wilson_interval(ones, 2000)
        if not (lo <= 0.5 <= hi):
            failures.append(f"wilson_interval=[{lo:.4f}, {hi:.4f}], must contain 0.5000")
    except Exception as e:  # noqa: BLE001
        failures.append(f"born frequency test raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "5-qubit measurement helper repaired: 32/32 basis states "
            "deterministic (no crash on p=0/1), no input mutation, correct "
            "branch probability and collapsed copy, forced/impossible and "
            "invalid states rejected, Wilson-interval Born test passes",
        ],
    }
