"""Repaired computational-basis measurement helper for 5-qubit
statevectors measuring qubit 4. The old code raised whenever p(1) was
exactly zero or one, renormalized with the wrong branch probability, and
mutated its input. This implementation handles deterministic outcomes
(p=0 / p=1) without raising, returns the Born probability of the actual
outcome, never mutates its input, accepts an injected
numpy.random.Generator, and rejects only invalid states or impossible
forced outcomes. Bit convention: the 5-qubit statevector is indexed
|q4 q3 q2 q1 q0> with q4 the most significant bit (bit 16)."""

import math

import numpy as np

N_QUBITS = 5
STATE_SIZE = 1 << N_QUBITS


def qubit_bit(qubit):
    """Bit position of `qubit` in the statevector index (qiskit
    convention |q4 q3 q2 q1 q0> with q4 = bit 16 the most significant,
    q0 = bit 1 the least significant)."""
    if not 0 <= qubit < N_QUBITS:
        raise ValueError(f"invalid qubit index: {qubit} (expected 0..4)")
    return 1 << qubit


def _validate(state, qubit):
    if state is None or len(state) != STATE_SIZE:
        raise ValueError(
            f"invalid state length: {len(state) if state is not None else None}, "
            f"expected {STATE_SIZE}"
        )
    norm_sq = sum(abs(complex(a)) ** 2 for a in state)
    if abs(norm_sq - 1.0) > 1e-9:
        raise ValueError(f"state not normalized: norm^2 = {norm_sq:.12f}")


def measurement_probabilities(state, qubit=4):
    """(p0, p1) Born probabilities for the computational-basis measurement
    of `qubit` (p1 = probability of outcome 1)."""
    _validate(state, qubit)
    bit = qubit_bit(qubit)
    p1 = sum(abs(complex(a)) ** 2 for i, a in enumerate(state) if i & bit)
    return 1.0 - p1, p1


def measure_qubit(state, qubit=4, rng=None, forced=None):
    """Measure `qubit` of a 5-qubit statevector in the computational basis.

    Returns (outcome, collapsed, probability):
      outcome    - 0 or 1 (deterministic when p(1) is 0 or 1)
      collapsed  - a NEW list with the collapsed (renormalized) branch
                   amplitudes; the input state is never mutated
      probability- the Born probability of the actual outcome

    `rng` is an injected numpy.random.Generator (or any object with a
    .uniform() method); `forced` pins the outcome and raises ValueError
    for an impossible forced outcome.
    """
    _validate(state, qubit)
    p0, p1 = measurement_probabilities(state, qubit)
    bit = qubit_bit(qubit)

    if forced is not None:
        if forced not in (0, 1):
            raise ValueError(f"invalid forced outcome: {forced}")
        if forced == 0 and p1 > 1e-12:
            raise ValueError(f"impossible forced outcome 0: p(1) = {p1:.12f} > 0")
        if forced == 1 and p0 > 1e-12:
            raise ValueError(f"impossible forced outcome 1: p(0) = {p0:.12f} > 0")
        outcome = forced
    elif p1 <= 1e-12:
        outcome = 0  # deterministic, must not raise
    elif p0 <= 1e-12:
        outcome = 1  # deterministic, must not raise
    else:
        if rng is None:
            rng = np.random.default_rng()
        outcome = 1 if float(rng.uniform()) < p1 else 0

    branch_prob = p1 if outcome == 1 else p0
    collapsed = [0.0j] * STATE_SIZE
    if branch_prob > 0.0:
        scale = 1.0 / math.sqrt(branch_prob)
        for i, a in enumerate(state):
            if (i & bit) == (bit if outcome == 1 else 0):
                collapsed[i] = complex(a) * scale
    return outcome, collapsed, float(branch_prob)


def wilson_interval(k, n, z=1.96):
    """Wilson score interval (lower, upper) for k successes in n trials."""
    if n <= 0:
        raise ValueError("n must be positive")
    p = k / float(n)
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return center - half, center + half


def run_helper_tests(n_freq=2000, seed=42):
    """Exhaustive basis-state tests and seeded Born-frequency tests."""
    # basis states |i> for i in 0..31: deterministic, no crash on p=0/1
    basis_ok = 0
    for i in range(STATE_SIZE):
        state = [0.0j] * STATE_SIZE
        state[i] = 1.0 + 0.0j
        expected = 1 if (i & qubit_bit(4)) else 0
        outcome, collapsed, prob = measure_qubit(state, 4, forced=None)
        if outcome != expected:
            raise AssertionError(f"basis state {i}: outcome {outcome} != {expected}")
        if abs(prob - 1.0) > 1e-12:
            raise AssertionError(
                f"basis state {i}: deterministic outcome must have probability 1.0, " f"got {prob}"
            )
        if any(abs(a) > 1e-12 for a in collapsed[:i]) or abs(collapsed[i] - 1.0) > 1e-12:
            raise AssertionError(f"basis state {i}: collapsed vector wrong")
        basis_ok += 1
    # stochastic frequency test: equal superposition -> p1 = 0.5
    state = [1.0 / math.sqrt(STATE_SIZE)] * STATE_SIZE
    rng = np.random.default_rng(seed)
    ones = sum(1 for _ in range(n_freq) if measure_qubit(state, 4, rng=rng)[0] == 1)
    lo, hi = wilson_interval(ones, n_freq)
    if not (lo <= 0.5 <= hi):
        raise AssertionError(
            f"Born frequency {ones}/{n_freq} outside Wilson interval " f"[{lo:.4f}, {hi:.4f}]"
        )
    # forced outcomes
    zero_state = [0.0j] * STATE_SIZE
    zero_state[0] = 1.0
    outcome, collapsed, prob = measure_qubit(zero_state, 4, forced=0)
    assert outcome == 0 and abs(prob - 1.0) < 1e-12
    try:
        measure_qubit(zero_state, 4, forced=1)
        raise AssertionError("forced=1 on |00000> must raise")
    except ValueError:
        pass
    # invalid states are rejected
    try:
        measure_qubit([1.0] * 4, 4)
        raise AssertionError("short state must raise")
    except ValueError:
        pass
    try:
        measure_qubit(zero_state, 5)
        raise AssertionError("invalid qubit must raise")
    except ValueError:
        pass
    return {
        "basis_states": basis_ok,
        "born_ones": ones,
        "born_total": n_freq,
        "wilson_interval": [lo, hi],
    }


def main():
    result = run_helper_tests()
    print("basis states verified:", result["basis_states"])
    print("born ones:", result["born_ones"], "/", result["born_total"])
    print("wilson interval:", result["wilson_interval"])
    # input non-mutation check
    state = [0.6j * 0.0 + 0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] + [0.0j] * 24
    state[16] = 0.8 + 0.0j
    norm = math.sqrt(sum(abs(a) ** 2 for a in state))
    state = [a / norm for a in state]
    snapshot = list(state)
    outcome, collapsed, prob = measure_qubit(state, 4)
    assert state == snapshot, "measure_qubit mutated its input"
    print("non-mutation verified; sample outcome:", outcome, "prob:", prob)


if __name__ == "__main__":
    main()
