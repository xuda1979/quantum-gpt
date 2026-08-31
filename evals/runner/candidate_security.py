"""Static launch gate for candidate-to-scorer introspection attacks."""

from __future__ import annotations

import ast

FORBIDDEN_IMPORT_ROOTS = frozenset(
    {"builtins", "gc", "importlib", "inspect", "pathlib", "sys", "traceback"}
)
FORBIDDEN_NAMES = frozenset(
    {
        "__import__",
        "breakpoint",
        "compile",
        "dir",
        "eval",
        "exec",
        "getattr",
        "globals",
        "locals",
        "open",
        "vars",
    }
)
FORBIDDEN_ATTRIBUTES = frozenset(
    {
        "__code__",
        "__globals__",
        "__subclasses__",
        "_getframe",
        "currentframe",
        "f_back",
        "f_code",
        "f_globals",
        "f_locals",
        "getouterframes",
        "glob",
        "listdir",
        "read_bytes",
        "read_text",
        "rglob",
        "scandir",
        "tb_frame",
        "walk",
    }
)
FORBIDDEN_FILE_MARKERS = ("tests.py", "task.json")


def candidate_security_violations(source: str) -> list[str]:
    """Return stable reasons a candidate could inspect hidden scorer state."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []  # Syntax failure is handled by the ordinary scorer.

    violations: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    violations.add(f"forbidden introspection import: {root}")
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".", 1)[0]
            if root in FORBIDDEN_IMPORT_ROOTS:
                violations.add(f"forbidden introspection import: {root}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            violations.add(f"forbidden dynamic/file primitive: {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRIBUTES:
            violations.add(f"forbidden introspection attribute: {node.attr}")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            lowered = node.value.lower().replace("\\", "/")
            for marker in FORBIDDEN_FILE_MARKERS:
                if marker in lowered:
                    violations.add(f"forbidden hidden scorer path: {marker}")
    return sorted(violations)


def reject_candidate_source(source: str) -> dict | None:
    """Return a harness-compatible rejection, or ``None`` when allowed."""
    violations = candidate_security_violations(source)
    if not violations:
        return None
    return {
        "passed": False,
        "security_violation": True,
        "details": [f"candidate source policy: {reason}" for reason in violations],
    }
