import math


def iswap_matrix() -> list[list[complex]]:
    """Return the 4x4 unitary matrix of the iSWAP gate.

    iSWAP acts on two qubits as:
        |00> -> |00>
        |01> -> i|10>
        |10> -> i|01>
        |11> -> |11>
    """
    return [
        [1.0 + 0j, 0.0 + 0j, 0.0 + 0j, 0.0 + 0j],
        [0.0 + 0j, 0.0 + 0j, 0.0 + 1j, 0.0 + 0j],
        [0.0 + 0j, 0.0 + 1j, 0.0 + 0j, 0.0 + 0j],
        [0.0 + 0j, 0.0 + 0j, 0.0 + 0j, 1.0 + 0j],
    ]


def sqrt_iswap_matrix() -> list[list[complex]]:
    """Return the 4x4 unitary matrix of the sqrt(iSWAP) gate.

    sqrt(iSWAP) is the principal square root of the iSWAP gate. On the
    {|01>, |10>} subspace it acts as exp(i * (pi/4) * X) = (1/sqrt(2))(I + iX):

        |00> -> |00>
        |01> -> (1/sqrt(2)) * (|01> + i|10>)
        |10> -> (1/sqrt(2)) * (i|01> + |10>)
        |11> -> |11>

    so that sqrt(iSWAP)^2 = iSWAP exactly.
    """
    s = 1.0 / math.sqrt(2.0)
    return [
        [1.0 + 0j, 0.0 + 0j, 0.0 + 0j, 0.0 + 0j],
        [0.0 + 0j, s + 0j, 0.0 + s * 1j, 0.0 + 0j],
        [0.0 + 0j, 0.0 + s * 1j, s + 0j, 0.0 + 0j],
        [0.0 + 0j, 0.0 + 0j, 0.0 + 0j, 1.0 + 0j],
    ]


def _mat_mul(a: list[list[complex]], b: list[list[complex]]) -> list[list[complex]]:
    n = len(a)
    m = len(b[0])
    p = len(b)
    out = [[0j] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            acc = 0j
            for k in range(p):
                acc += a[i][k] * b[k][j]
            out[i][j] = acc
    return out


def iswap_from_sqrt_iswap() -> list[list[complex]]:
    """Construct iSWAP by squaring sqrt(iSWAP).

    With the principal branch convention sqrt(iSWAP) = exp(i * (pi/4) * X)
    restricted to the {|01>, |10>} subspace, the matrix product
    sqrt(iSWAP) . sqrt(iSWAP) equals iSWAP exactly.
    """
    sqrt_i = sqrt_iswap_matrix()
    return _mat_mul(sqrt_i, sqrt_i)
