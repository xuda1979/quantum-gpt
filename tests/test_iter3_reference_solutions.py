"""Tests for scripts/iter3_reference_solutions.py.

Verifies:
- All 7 universal-gap solutions (B1-B5, C1-C2) are present
- Each solution is valid Python (parseable)
- Each solution has a def main() function
- Each solution has a if __name__ == "__main__" guard
- Solutions are non-trivial (minimum line count)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.iter3_reference_solutions import SOLUTIONS, get_solution


def test_all_7_solutions_present():
    """All 7 universal-gap solutions should be in the registry."""
    expected = {"B1", "B2", "B3", "B4", "B5", "C1", "C2"}
    assert set(SOLUTIONS.keys()) == expected, f"Expected {expected}, got {set(SOLUTIONS.keys())}"


def test_solutions_are_valid_python():
    """Each solution should parse as valid Python."""
    for row_id, code in SOLUTIONS.items():
        try:
            ast.parse(code)
        except SyntaxError as e:
            assert False, f"Solution {row_id} has syntax error: {e}"


def test_solutions_have_main_function():
    """Each solution should define a main() function."""
    for row_id, code in SOLUTIONS.items():
        tree = ast.parse(code)
        func_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        assert (
            "main" in func_names
        ), f"Solution {row_id} missing main() function. Found: {func_names}"


def test_solutions_have_name_guard():
    """Each solution should have if __name__ == '__main__' guard."""
    for row_id, code in SOLUTIONS.items():
        assert (
            "__name__" in code and "__main__" in code
        ), f"Solution {row_id} missing __name__ guard"


def test_solutions_are_nontrivial():
    """Each solution should be at least 15 lines (non-trivial)."""
    for row_id, code in SOLUTIONS.items():
        line_count = code.count("\n") + 1
        assert line_count >= 15, f"Solution {row_id} is too short: {line_count} lines"


def test_solutions_have_print_statements():
    """Each solution should print output (for eval verification)."""
    for row_id, code in SOLUTIONS.items():
        tree = ast.parse(code)
        has_print = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
            for node in ast.walk(tree)
        )
        assert has_print, f"Solution {row_id} has no print() calls"


def test_get_solution_returns_none_for_unknown():
    """get_solution should return None for unknown row IDs."""
    assert get_solution("UNKNOWN") is None
    assert get_solution("A1") is None  # A-series not implemented yet


def test_get_solution_returns_code_for_known():
    """get_solution should return the code string for known row IDs."""
    code = get_solution("B1")
    assert code is not None
    assert "braket" in code.lower()
    assert "def main" in code


def test_b1_braket_solution_structure():
    """B1 (braket Bell state) should use braket imports and Bell state circuit."""
    code = get_solution("B1")
    assert "from braket" in code
    assert "Circuit" in code
    assert "h(0)" in code
    assert "cnot" in code.lower()


def test_c1_log_parser_structure():
    """C1 (log parser) should parse log lines and aggregate by level."""
    code = get_solution("C1")
    assert "Counter" in code or "collections" in code
    assert "parse" in code.lower()
    assert "level" in code.lower()


def test_c2_sql_join_structure():
    """C2 (SQL join) should join two tables and project columns."""
    code = get_solution("C2")
    assert "join" in code.lower()
    assert "user" in code.lower()
    assert "order" in code.lower()
