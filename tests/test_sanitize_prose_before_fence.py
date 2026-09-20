"""TDD test for C-9168: candidate_sanitize.py must NOT discard code when
prose precedes a fenced code block.

The old code did: stripped.split(fence, 1)[0].rstrip()
which keeps text BEFORE the first fence and DROPS everything after.
When prose precedes a fence, this keeps the prose and drops the code,
causing SyntaxError at line 1 in 13/15 failing tasks.
"""

from evals.runner.candidate_sanitize import sanitize_candidate_text

FENCE = chr(96) * 3  # three backticks


def test_prose_before_fence_extracts_fenced_code() -> None:
    """Prose before a python fence must yield the fenced code, not the prose."""
    raw = (
        "Here is the solution:\n"
        + FENCE
        + "python\n"
        + "from qiskit import QuantumCircuit\n"
        + "qc = QuantumCircuit(2)\n"
        + "qc.h(0)\n"
        + "qc.cx(0, 1)\n"
        + "print(qc)\n"
        + FENCE
        + "\n"
    )
    result = sanitize_candidate_text(raw)
    assert "QuantumCircuit" in result, f"fenced code was dropped! got: {result!r}"
    assert "Here is the solution" not in result, f"prose was kept instead of code! got: {result!r}"


def test_pure_code_before_fence_is_kept() -> None:
    """Valid Python before a stray fence line must be kept as-is."""
    raw = "def solve(x):\n    return x + 1\n" + FENCE + "\n"
    result = sanitize_candidate_text(raw)
    assert "def solve(x):" in result
    assert "return x + 1" in result


def test_think_block_then_prose_then_fence() -> None:
    """Prose + fence must extract the fenced code."""
    raw = (
        "Let me reason about this.\n\n"
        + "Here is my solution:\n"
        + FENCE
        + "python\n"
        + "x = 42\n"
        + "print(x)\n"
        + FENCE
        + "\n"
    )
    result = sanitize_candidate_text(raw)
    assert "x = 42" in result, f"fenced code was dropped! got: {result!r}"
    assert "Here is my solution" not in result
