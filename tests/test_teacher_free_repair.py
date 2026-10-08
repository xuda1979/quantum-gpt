"""Unit tests for the teacher-free (no-reference) self-repair rollout."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.teacher_free_repair import (  # noqa: E402
    build_repair_prompt,
    extract_code,
    teacher_free_self_repair,
)


def test_extract_code_from_python_fence():
    resp = "Here is the fix:\n```python\ndef f(x):\n    return x + 1\n```\n-- done"
    assert extract_code(resp) == "def f(x):\n    return x + 1"


def test_extract_code_plain():
    assert extract_code("def f():\n    pass") == "def f():\n    pass"


def test_build_repair_prompt_contains_failure_and_no_reference(tmp_path):
    prompt = build_repair_prompt(
        "implement add(a,b)",
        "def add(a,b): return a-b",
        ["AssertionError: add(1,2) expected 3 got -1"],
        interface_lines=["def add(a: int, b: int) -> int"],
    )
    assert "FAILING PROGRAM" in prompt
    assert "AssertionError" in prompt
    assert "def add(a: int, b: int) -> int" in prompt
    # Teacher-free: no reference solution is injected.
    assert "reference" not in prompt.lower() or "no reference solution" in prompt.lower()


def test_repair_not_needed_when_already_passes():
    out = teacher_free_self_repair(
        task_prompt="t",
        failing_code="def f(): return 1",
        correctness={"passed": True, "details": []},
        repair=lambda p: "def f(): return 2",
        verify=lambda c: {"passed": True, "details": []},
    )
    assert out["passed"] is True
    assert out["best_round"] == 0
    assert out["attempted"] == []


def test_repair_succeeds_on_second_round():
    """First repair still fails, second repair (fed the new error log) passes."""
    calls = {"n": 0}

    def repair(prompt):
        calls["n"] += 1
        return "def f(): return 2" if calls["n"] == 2 else "def f(): return 1"

    verify_results = iter(
        [
            {"passed": False, "details": ["expected 2 got 1"]},  # round 1 fail
            {"passed": True, "details": []},  # round 2 pass
        ]
    )

    out = teacher_free_self_repair(
        task_prompt="return 2",
        failing_code="def f(): return 1",
        correctness={"passed": False, "details": ["expected 2 got 1"]},
        repair=repair,
        verify=lambda c: next(verify_results),
        max_rounds=2,
    )
    assert out["passed"] is True
    assert out["best_round"] == 2
    assert out["code"] == "def f(): return 2"
    assert calls["n"] == 2


def test_repair_caps_at_max_rounds_and_keeps_original():
    """No repair passes within the cap -> original failing code is retained."""
    out = teacher_free_self_repair(
        task_prompt="t",
        failing_code="def f(): return 0",
        correctness={"passed": False, "details": ["AssertionError"]},
        repair=lambda p: "def f(): return 9",  # never passes
        verify=lambda c: {"passed": False, "details": ["AssertionError"]},
        max_rounds=3,
    )
    assert out["passed"] is False
    assert out["best_round"] == 0
    assert out["code"] == "def f(): return 0"  # original retained for GROPO
    assert len(out["attempted"]) == 3


def test_repair_uses_policy_alone_no_teacher_call():
    calls = []

    def repair(prompt):
        calls.append(prompt)
        return "def f(): return 1"

    out = teacher_free_self_repair(
        task_prompt="return 1",
        failing_code="def f(): return 0",
        correctness={"passed": False, "details": ["expected 1 got 0"]},
        repair=repair,
        verify=lambda c: {"passed": True, "details": []},
        max_rounds=1,
    )
    assert out["passed"] is True
    assert len(calls) == 1
    # The repair prompt is built from task + failing code + errors only.
    assert "return 1" in calls[0]
    assert "expected 1 got 0" in calls[0]
