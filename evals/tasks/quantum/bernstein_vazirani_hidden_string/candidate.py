def recover_hidden_string(oracle_queries: dict[int, int], n: int) -> str:
    """Recover the hidden string s in {0,1}^n of a linear Boolean function
    f(x) = (s . x) mod 2.

    `oracle_queries` maps query inputs x (integers in [0, 2^n)) to f(x).
    A single query on each basis vector e_i (i.e. x = 1<<i) recovers s_i.
    Returns the bitstring s with s_0 as the least-significant bit, padded to n bits.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    bits = ["0"] * n
    for i in range(n):
        x = 1 << i
        if x not in oracle_queries:
            raise ValueError(f"missing oracle query for basis vector {x}")
        v = oracle_queries[x]
        if v not in (0, 1):
            raise ValueError("oracle output must be 0 or 1")
        bits[i] = str(v)
    # bits[i] is s_i (LSB first), reverse to MSB-first display
    return "".join(reversed(bits))


def bv_oracle(x: int, s: int) -> int:
    """Compute f(x) = (s . x) mod 2 for the Bernstein-Vazirani problem."""
    return bin(x & s).count("1") % 2
