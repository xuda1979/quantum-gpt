from evals.runner.candidate_sanitize import sanitize_candidate_text


def test_sanitize_drops_trailing_fence_and_prose() -> None:
    raw = """from typing import List

def solve(values: List[int]) -> int:
    return sum(values)
```

This solution sums the values.
"""
    assert sanitize_candidate_text(raw) == (
        "from typing import List\n\n"
        "def solve(values: List[int]) -> int:\n"
        "    return sum(values)\n"
    )


def test_sanitize_extracts_parseable_prefix_from_broken_tail() -> None:
    raw = """def solve(x):
    return x + 1

Explanation:
"""
    assert sanitize_candidate_text(raw) == "def solve(x):\n    return x + 1\n"


def test_sanitize_drops_known_terminal_markers() -> None:
    raw = "OK<|im_end|>\n<|endoftext|>"
    assert sanitize_candidate_text(raw) == "OK\n"
