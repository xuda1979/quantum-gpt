"""Single home for the loop's py3.9-safe pairing idioms (architect lane #26).

Why this module exists — the recurring bug class (2026-08-26):

- The canonical training venv is Python 3.9.6, where ``zip`` has NO ``strict``
  kwarg: ``zip(a, b, strict=True)`` is a TypeError at runtime on the box, but
  works silently on py3.10+ dev hosts — a split-brain failure mode.
- Plain ``zip`` on mismatched lengths silently truncates: a partial pairing
  that looks complete (e.g. a truncated scorecard leg producing a partial
  cross-arm comparison, or a strict-length caller bug pairing the wrong
  records). Caller bugs must fail loud, never silently pair.

The fix is structural: ONE helper (``strict_zip``), one behavior test suite
(``tests/test_compat.py``), imported everywhere; the source guard in that
suite fails on any new ``zip(..., strict=`` in training/ + scripts/ +
evals/runner/ and on any local re-implementation of the helper.

The frozen holdout task contracts under evals/tasks/ are intentionally out of
the guard's scope (their ``strict=False`` pairings are frozen contract text).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any


def strict_zip(*iterables: Iterable[Any]) -> Iterator[tuple[Any, ...]]:
    """py3.9-safe ``zip(..., strict=True)`` (semantics identical to py3.10).

    Yields tuples until any iterable is exhausted, then raises ValueError if
    the others still have items (a caller bug must fail loudly, never
    silently pair). Works on any iterable, including generators; supports one
    or more iterables. Raises on the pull that detects the mismatch, after
    yielding the common prefix — exactly py3.10's strict-zip contract.
    """
    iterators = [iter(it) for it in iterables]
    sentinel = object()
    while True:
        values = [next(it, sentinel) for it in iterators]
        if any(value is sentinel for value in values):
            if all(value is sentinel for value in values):
                return
            raise ValueError("zip() argument lengths differ (strict mode)")
        yield tuple(values)
