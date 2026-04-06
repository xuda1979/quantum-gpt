from __future__ import annotations

from training.grpo_utils import extract_behavior_hints_from_test_source


def test_extract_behavior_hints_captures_literal_append_messages() -> None:
    source = """
def run_tests(candidate_path: str) -> dict:
    failures = []
    failures.append("mapping for '10' was incorrect")
    return {"passed": not failures, "details": failures}
"""
    hints = extract_behavior_hints_from_test_source(source, cap=6)
    assert "mapping for '10' was incorrect" in hints


def test_extract_behavior_hints_captures_fstring_templates() -> None:
    source = """
def run_tests(candidate_path: str) -> dict:
    failures = []
    depth = 3
    failures.append(f"mixed circuit depth={depth}, expected 2")
    return {"passed": not failures, "details": failures}
"""
    hints = extract_behavior_hints_from_test_source(source, cap=6)
    assert "mixed circuit depth={value}, expected 2" in hints


def test_extract_behavior_hints_uses_test_comments_and_caps_output() -> None:
    source = """
# Test preserves ordering
def run_tests(candidate_path: str) -> dict:
    failures = []
    failures.append("first message")
    failures.append("second message")
    failures.append("third message")
    return {"passed": not failures, "details": failures}
"""
    hints = extract_behavior_hints_from_test_source(source, cap=2)
    assert hints == [
        "Test preserves ordering",
        "first message",
    ]
