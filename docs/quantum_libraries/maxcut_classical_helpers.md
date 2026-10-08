# MaxCut: classical bitstring evaluation, enumeration, ranking

## Definitions
A cut on graph G = (V, E, w) given a partition (S, V\S) is the set of
edges with one endpoint in each part. The cut weight (cost) is

  cost(x) = sum_{(u,v) in E} w_uv * [x_u != x_v]

where x is a bitstring of length |V| with 0/1 indicating partition.

## Bitstring cost

```python
def cut_cost(bitstring: list[int], edges: list[tuple[int, int, float]]) -> float:
    total = 0.0
    for u, v, w in edges:
        if bitstring[u] != bitstring[v]:
            total += w
    return total
```

## Brute force enumeration

```python
import itertools

def enumerate_cuts(n: int, edges: list[tuple[int, int, float]]) -> list[tuple[list[int], float]]:
    out: list[tuple[list[int], float]] = []
    for bits in itertools.product([0, 1], repeat=n):
        cost = cut_cost(list(bits), edges)
        out.append((list(bits), cost))
    return out


def best_cut(n: int, edges) -> tuple[float, list[int]]:
    best = (-1.0, [0] * n)
    for bits, cost in enumerate_cuts(n, edges):
        if cost > best[0]:
            best = (cost, bits)
    return best
```

## Ranking partitions

```python
def rank_partitions(n: int, edges) -> list[tuple[list[int], float]]:
    return sorted(enumerate_cuts(n, edges), key=lambda kv: -kv[1])
```

The list returned by `rank_partitions` is in non-increasing cost order.
For deterministic tiebreaking, `sorted(..., key=lambda kv: (-kv[1], kv[0]))`
sorts ties lexicographically by bitstring.

## Common pitfalls
- The cut is symmetric under swapping (S, V\S); both x and ~x give the
  same cost. Tests usually accept either, but if not, normalize so x[0]=0.
- Negative weights flip the optimisation direction; make sure the test
  expects max-cost or min-cost.
- For weighted MaxCut, ensure weights are floats (`int + int * float`
  in Python silently widens, but mixed dtypes can break numpy paths).
