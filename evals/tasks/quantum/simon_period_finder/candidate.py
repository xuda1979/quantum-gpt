def solve_simon_system(equations: list[tuple[int, int]], n: int) -> int:
    """Solve the linear system (over GF(2)) gathered by Simon's algorithm.

    Each equation is (y, b) where y is an n-bit integer measurement outcome
    and b = (y . s) mod 2 is guaranteed to be 0 for the unknown period string s.

    Find the unique non-zero s in {0,1}^n (returned as an integer) consistent
    with all equations y . s = 0. If only the trivial solution s = 0 is
    consistent, return 0. Raises ValueError if the system is inconsistent.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    # Build augmented rows: bits of y followed by the RHS bit b
    rows = []
    for y, b in equations:
        row = [(y >> i) & 1 for i in range(n)] + [b & 1]
        rows.append(row)

    # Gaussian elimination over GF(2)
    pivot_row = 0
    pivots = []
    for col in range(n):
        # Find a row at or below pivot_row with a 1 in this column
        sel = None
        for r in range(pivot_row, len(rows)):
            if rows[r][col] == 1:
                sel = r
                break
        if sel is None:
            continue
        rows[pivot_row], rows[sel] = rows[sel], rows[pivot_row]
        for r in range(len(rows)):
            if r != pivot_row and rows[r][col] == 1:
                rows[r] = [(a ^ b) for a, b in zip(rows[r], rows[pivot_row], strict=False)]
        pivots.append(col)
        pivot_row += 1
        if pivot_row == len(rows):
            break

    # Check for inconsistency: a row with all-zero coefficients but RHS=1
    for row in rows:
        if all(v == 0 for v in row[:n]) and row[n] == 1:
            raise ValueError("inconsistent system")

    # Determine if the only solution is s = 0 (full rank n)
    if len(pivots) == n:
        return 0

    # Free variable exists; pick the lowest-index free variable = 1
    free_vars = [c for c in range(n) if c not in pivots]
    if not free_vars:
        return 0
    s = [0] * n
    s[free_vars[0]] = 1
    # Back-substitute to determine pivot variables in terms of the free var
    for pr, pc in enumerate(pivots):
        val = rows[pr][n]
        for c in range(n):
            if c != pc and rows[pr][c] == 1 and s[c] == 1:
                val ^= 1
        s[pc] = val
    return sum(bit << i for i, bit in enumerate(s))
