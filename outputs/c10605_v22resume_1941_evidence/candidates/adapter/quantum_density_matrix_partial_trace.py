import math


def density_from_state(state: list[float]) -> list[list[float]]:
    """Compute the density matrix rho = |psi><psi| from a state vector."""
    n = len(state)
    return [[state[i] * state[j] for j in range(n)] for i in range(n)]


def tensor_product(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Compute the Kronecker (tensor) product of two square matrices."""
    da = len(a)
    db = len(b)
    size = da * db
    result = [[0.0] * size for _ in range(size)]
    for i in range(da):
        for j in range(da):
            for k in range(db):
                for l in range(db):
                    result[i * db + k][j * db + l] = a[i][j] * b[k][l]
    return result


def partial_trace(
    rho: list[list[float]], dim_a: int, dim_b: int, trace_out: str
) -> list[list[float]]:
    """
    Compute the partial trace of a bipartite density matrix.

    rho: (dim_a * dim_b) x (dim_a * dim_b) density matrix
    trace_out: 'A' to trace out subsystem A, 'B' to trace out subsystem B
    """
    if trace_out == "B":
        # Trace out B -> result is dim_a x dim_a
        result = [[0.0] * dim_a for _ in range(dim_a)]
        for i in range(dim_a):
            for j in range(dim_a):
                for k in range(dim_b):
                    result[i][j] += rho[i * dim_b + k][j * dim_b + k]
        return result
    else:
        # Trace out A -> result is dim_b x dim_b
        result = [[0.0] * dim_b for _ in range(dim_b)]
        for k in range(dim_b):
            for l in range(dim_b):
                for i in range(dim_a):
                    result[k][l] += rho[i * dim_b + k][i * dim_b + l]
        return result


def purity(rho: list[list[float]]) -> float:
    """Compute Tr(rho^2), the purity of a density matrix."""
    n = len(rho)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += rho[i][j] * rho[j][i]
    return total


def entropy_from_eigenvalues(eigs: list[float]) -> float:
    """Compute von Neumann entropy S = -sum lambda log2(lambda)."""
    s = 0.0
    for l in eigs:
        if l > 1e-15:
            s -= l * math.log2(l)
    return s


def _mat_mul(a, b):
    """Multiply two square matrices."""
    n = len(a)
    m = len(b[0])
    p = len(b)
    result = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            for k in range(p):
                result[i][j] += a[i][k] * b[k][j]
    return result


def _mat_add(a, b):
    n = len(a)
    m = len(a[0])
    return [[a[i][j] + b[i][j] for j in range(m)] for i in range(n)]


def _mat_scale(s, a):
    n = len(a)
    m = len(a[0])
    return [[s * a[i][j] for j in range(m)] for i in range(n)]


def _char_poly_coeffs(m):
    """Return coefficients c0..cn of the characteristic polynomial det(xI - M) = x^n + c1 x^(n-1) + ... + cn."""
    n = len(m)
    if n == 1:
        return [1.0, -m[0][0]]
    if n == 2:
        tr = m[0][0] + m[1][1]
        det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
        return [1.0, -tr, det]
    if n == 3:
        tr = m[0][0] + m[1][1] + m[2][2]
        s2 = (
            m[0][0] * m[1][1]
            - m[0][1] * m[1][0]
            + m[0][0] * m[2][2]
            - m[0][2] * m[2][0]
            + m[1][1] * m[2][2]
            - m[1][2] * m[2][1]
        )
        det = (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )
        return [1.0, -tr, s2, -det]
    raise ValueError(f"Unsupported matrix size {n} for characteristic polynomial")


def _newton_eigenvalues(coeffs, tol=1e-12, max_iter=200):
    """Find all real roots of a polynomial using Newton's method with deflation."""
    n = len(coeffs) - 1
    # Start with several initial guesses
    guesses = [0.0, 1.0, -1.0, 0.5, -0.5, 2.0, -2.0]
    found = []

    def poly_val(x, c):
        return sum(c[i] * x**i for i in range(len(c)))

    def poly_deriv(x, c):
        return sum(c[i] * i * x ** (i - 1) for i in range(1, len(c)))

    for x0 in guesses:
        x = x0
        for _ in range(max_iter):
            f = poly_val(x, coeffs)
            if abs(f) < tol:
                break
            df = poly_deriv(x, coeffs)
            if abs(df) < 1e-15:
                x += 1e-6
                continue
            x -= f / df
        else:
            continue
        if abs(poly_val(x, coeffs)) > 1e-8:
            continue
        # Check if already found
        is_new = True
        for fr in found:
            if abs(fr - x) < 1e-6:
                is_new = False
                break
        if is_new:
            found.append(x)

    # If we didn't find enough, try more guesses
    if len(found) < n:
        for x0 in [0.1, -0.1, 0.3, -0.3, 0.7, -0.7, 1.5, -1.5, 3.0, -3.0]:
            x = x0
            for _ in range(max_iter):
                f = poly_val(x, coeffs)
                if abs(f) < tol:
                    break
                df = poly_deriv(x, coeffs)
                if abs(df) < 1e-15:
                    x += 1e-6
                    continue
                x -= f / df
            else:
                continue
            if abs(poly_val(x, coeffs)) > 1e-8:
                continue
            is_new = True
            for fr in found:
                if abs(fr - x) < 1e-6:
                    is_new = False
                    break
            if is_new:
                found.append(x)

    found.sort(reverse=True)
    return found[:n]


def eigenvalues_hermitian(m: list[list[float]]) -> list[float]:
    """
    Compute eigenvalues of a small Hermitian (real symmetric) matrix
    using the characteristic polynomial + Newton's method.
    Supports n = 1, 2, 3.
    """
    n = len(m)
    if n == 1:
        return [m[0][0]]
    coeffs = _char_poly_coeffs(m)
    eigs = _newton_eigenvalues(coeffs)
    # Clamp small negatives from numerical error
    eigs = [max(0.0, e) for e in eigs]
    return eigs
