"""Circuit construct-and-measure drill - no-fence exemplar.

Teaches: uniform single-qubit gates by permutation, short complete file."""


def apply_fixed_gates_and_measure(amplitudes, gate_names):
    amplitudes = numpy.asarray(amplitudes, dtype=complex)
    if amplitudes.ndim != 1:
        raise ValueError("statevector must be one-dimensional")
    n = amplitudes.shape[0]
    if n == 0 or (n & (n - 1)) != 0:
        raise ValueError("statevector length must be a power of two")
    state = amplitudes / numpy.linalg.norm(amplitudes)
    sqrt_half = numpy.sqrt(0.5)
    for name in gate_names:
        gate = str(name).strip().upper()
        if gate == "H":
            plus = (state[0::2] + state[1::2]) * sqrt_half
            minus = (state[0::2] - state[1::2]) * sqrt_half
            state = numpy.empty(n, dtype=complex)
            state[0::2] = plus
            state[1::2] = minus
        elif gate == "X":
            state = state.reshape(-1, 2)[:, ::-1].reshape(-1)
        elif gate == "Z":
            signs = numpy.tile(numpy.array([1.0, -1.0]), n // 2)
            state = state * signs
        else:
            raise ValueError("unsupported gate: %s" % name)
    probabilities = numpy.abs(state) ** 2
    total = probabilities.sum()
    return probabilities / total


import numpy


def _self_test():
    import math

    assert numpy.allclose(apply_fixed_gates_and_measure([1.0, 0.0], ["H"]), [0.5, 0.5])
    assert numpy.allclose(apply_fixed_gates_and_measure([1.0, 0.0], ["X"]), [0.0, 1.0])
    plus = [1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0)]
    assert numpy.allclose(apply_fixed_gates_and_measure(plus, ["Z"]), [0.5, 0.5])
    try:
        apply_fixed_gates_and_measure([1.0, 0.0], ["SWAP"])
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported gate must raise ValueError")


_self_test()
