"""Statevector fidelity check - no-fence exemplar.

Teaches: squared-overlap fidelity, short complete file, no fences."""


def statevector_fidelity(psi, phi):
    psi = numpy.asarray(psi, dtype=complex)
    phi = numpy.asarray(phi, dtype=complex)
    if psi.shape != phi.shape:
        raise ValueError("statevectors must have equal length")
    psi = psi / numpy.linalg.norm(psi)
    phi = phi / numpy.linalg.norm(phi)
    return float(abs(numpy.vdot(psi, phi)) ** 2)


def fidelity_table(pairs):
    return dict((index, statevector_fidelity(psi, phi)) for index, (psi, phi) in enumerate(pairs))


import numpy


def _self_test():
    one = [1.0, 0.0]
    zero = [0.0, 1.0]
    plus = [1.0, 1.0]
    minus = [1.0, -1.0]
    assert abs(statevector_fidelity(one, one) - 1.0) < 1e-12
    assert abs(statevector_fidelity(one, zero)) < 1e-12
    assert abs(statevector_fidelity(plus, minus)) < 1e-12
    table = fidelity_table([(one, one), (plus, minus)])
    assert abs(table[0] - 1.0) < 1e-12
    assert abs(table[1]) < 1e-12
    try:
        statevector_fidelity(one, [1.0, 0.0, 0.0])
    except ValueError:
        pass
    else:
        raise AssertionError("mismatched lengths must raise ValueError")


_self_test()
