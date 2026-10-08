"""B-328 RED: graded syntax reward to break all-syntax-error zero-gradient deadlock.

A group where EVERY candidate is SyntaxError-garbage has syntax_reward=0 for all,
total_reward=0 for all, LOO advantages all zero -> no gradient (13/18 tasks stuck).
Fix Lever A: `_graded_syntax_score` returns 1.0 (clean parse), 0.3 (recoverable),
0.1 (contains real Python keywords), 0.0 (utter garbage) so non-identical syntax
health yields intra-group reward dispersion and non-zero advantages.
"""

from __future__ import annotations

import training.grpo_utils as gu


def test_graded_syntax_score_exists():
    assert hasattr(gu, "_graded_syntax_score"), "_graded_syntax_score not implemented"


def _score(code: str) -> float:
    return gu._graded_syntax_score(code)  # noqa: SLF001


def test_clean_compile_returns_1():
    assert _score("def solve():\n    return 42\n") == 1.0


def test_empty_returns_0():
    assert _score("") == 0.0
    assert _score("   \n  ") == 0.0


def test_recoverable_unclosed_paren_returns_partial():
    # valid tokens, one recoverable structural defect (unclosed paren)
    s = _score("def solve():\n    return max(1, 2\n")
    assert 0.0 < s < 1.0, s


def test_keywords_present_returns_floor_partial():
    s = _score("import numpy\ndef broken(:\n")
    assert 0.0 < s < 1.0, s


def test_utter_garbage_returns_0():
    assert _score("\xff\xfe\x00\x01 not python at all {{{") == 0.0


def test_scores_monotone_across_health_levels():
    good = _score("def solve():\n    return 42\n")
    mid = _score("def solve():\n    return max(1, 2\n")
    low = _score("import numpy\ndef broken(:\n")
    bad = _score("\xff\xfe{{{")
    assert good > mid > bad
    assert 0.0 <= low <= 1.0
