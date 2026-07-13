def classify_oracle(truth_table: list[int]) -> str:
    """Classify a Boolean function f: {0,1}^n -> {0,1} given its full truth table.

    The Deutsch-Jozsa problem: f is either
      * "constant"  - all outputs are 0 or all outputs are 1, or
      * "balanced"  - exactly half the outputs are 0 and half are 1.

    Return "constant", "balanced", or "neither" otherwise.
    """
    if not truth_table:
        raise ValueError("truth table must be non-empty")
    n = len(truth_table)
    if n & (n - 1) != 0:
        raise ValueError("truth table length must be a power of 2")
    count_ones = sum(1 for v in truth_table if v == 1)
    count_zeros = n - count_ones
    if count_ones == 0 or count_zeros == 0:
        return "constant"
    if count_ones == count_zeros:
        return "balanced"
    return "neither"


def deutsch_jozsa_query_count(n: int) -> int:
    """Return the number of classical queries required to deterministically
    distinguish constant from balanced in the worst case (n/2 + 1)."""
    if n <= 1:
        raise ValueError("n must be at least 2 and a power of 2")
    if n & (n - 1) != 0:
        raise ValueError("n must be a power of 2")
    return n // 2 + 1
