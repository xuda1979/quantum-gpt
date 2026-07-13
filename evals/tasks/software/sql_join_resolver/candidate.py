"""A miniature SQL engine that resolves:

    SELECT <cols> FROM <t1> JOIN <t2> ON <t1>.<k> = <t2>.<k> [WHERE <col> <op> <val>]

over in-memory Python dicts. Supports inner joins only, equality predicates,
and the comparison operators =, !=, <, >, <=, >=. Returns a list of row dicts
with the requested columns. Column references may be qualified (`t.col`) or
unqualified (`col`); unqualified columns must be unambiguous.
"""

from typing import Any


def _resolve_col(row: dict, col: str, tables: list[str]) -> Any:
    if "." in col:
        t, c = col.split(".", 1)
        key = f"{t}.{c}"
        if key not in row:
            raise KeyError(f"column {col!r} not found")
        return row[key]
    # Unqualified: search all tables, must be unambiguous.
    matches = []
    for t in tables:
        key = f"{t}.{col}"
        if key in row:
            matches.append(row[key])
    if not matches:
        raise KeyError(f"column {col!r} not found")
    if len(matches) > 1:
        raise KeyError(f"column {col!r} is ambiguous")
    return matches[0]


def inner_join(left: list[dict], right: list[dict], left_key: str, right_key: str) -> list[dict]:
    """Inner join on equality of left_key and right_key. Row keys are prefixed
    with their table name."""
    out: list[dict] = []
    # Build a hash index on the right side
    right_idx: dict[Any, list[dict]] = {}
    for r in right:
        k = r.get(right_key)
        right_idx.setdefault(k, []).append(r)
    for l in left:
        k = l.get(left_key)
        for r in right_idx.get(k, []):
            merged = {**l, **r}
            out.append(merged)
    return out


def _apply_predicate(row: dict, where: tuple, tables: list[str]) -> bool:
    col, op, val = where
    actual = _resolve_col(row, col, tables)
    if op == "=":
        return actual == val
    if op == "!=":
        return actual != val
    if op == "<":
        return actual < val
    if op == ">":
        return actual > val
    if op == "<=":
        return actual <= val
    if op == ">=":
        return actual >= val
    raise ValueError(f"unsupported operator {op!r}")


def select(
    rows: list[dict],
    columns: list[str],
    tables: list[str],
    where: tuple | None = None,
) -> list[dict]:
    """Project columns out of joined rows, optionally filtering by a single
    predicate `where = (col, op, val)`."""
    out: list[dict] = []
    for r in rows:
        if where is not None and not _apply_predicate(r, where, tables):
            continue
        out_row = {}
        for c in columns:
            out_row[c] = _resolve_col(r, c, tables)
        out.append(out_row)
    return out


def run_query(
    left_table: list[dict],
    right_table: list[dict],
    left_name: str,
    right_name: str,
    left_key: str,
    right_key: str,
    columns: list[str],
    where: tuple | None = None,
) -> list[dict]:
    """Convenience wrapper: prefix row keys with table names, join, project."""
    L = [{f"{left_name}.{k}": v for k, v in r.items()} for r in left_table]
    R = [{f"{right_name}.{k}": v for k, v in r.items()} for r in right_table]
    joined = inner_join(L, R, f"{left_name}.{left_key}", f"{right_name}.{right_key}")
    return select(joined, columns, [left_name, right_name], where=where)
