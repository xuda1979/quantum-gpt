"""Build model-visible task specifications without leaking scorer artifacts."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
    return f"{prefix} {node.name}({ast.unparse(node.args)}){returns}"


def extract_public_api(source: str) -> str:
    """Return only public signatures and docstrings from Python source.

    Function/class bodies, constant values, imports, and executable statements
    are intentionally excluded because candidate.py is a reference solution,
    not model input.  The resulting interface is enough to make legacy task
    bundles (which lack a task_prompt field) solvable without leaking answers.
    """

    tree = ast.parse(source)
    lines: list[str] = []
    module_doc = ast.get_docstring(tree, clean=True)
    if module_doc:
        lines.extend(["Module contract:", module_doc, ""])

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith(
            "_"
        ):
            lines.append(_signature(node))
            doc = ast.get_docstring(node, clean=True)
            if doc:
                lines.append(f'    """{doc}"""')
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            bases = f"({', '.join(ast.unparse(base) for base in node.bases)})" if node.bases else ""
            lines.append(f"class {node.name}{bases}")
            doc = ast.get_docstring(node, clean=True)
            if doc:
                lines.append(f'    """{doc}"""')
            for child in node.body:
                if isinstance(
                    child, (ast.FunctionDef, ast.AsyncFunctionDef)
                ) and not child.name.startswith("_"):
                    lines.append(f"    {_signature(child)}")
                    child_doc = ast.get_docstring(child, clean=True)
                    if child_doc:
                        lines.append(f'        """{child_doc}"""')
    return "\n".join(lines).strip()


def build_public_task_spec(task_dir: Path, metadata: dict[str, Any]) -> str:
    explicit = str(metadata.get("task_prompt") or metadata.get("description") or "").strip()
    candidate_name = str(metadata.get("candidate_file") or "candidate.py")
    candidate_path = task_dir / candidate_name
    public_api = ""
    if candidate_path.is_file():
        try:
            public_api = extract_public_api(candidate_path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            public_api = ""

    sections = [
        f"Task: {metadata.get('name') or metadata.get('id')}",
        f"Domain: {metadata.get('domain', 'unknown')}",
        f"Category: {metadata.get('category', 'unknown')}",
        f"Output file: {candidate_name}",
    ]
    if explicit:
        sections.extend(["", "Public task specification:", explicit])
    if public_api:
        sections.extend(["", "Required public API (signatures and docstrings only):", public_api])
    sections.extend(
        [
            "",
            "Implement the requested file. Hidden tests will verify behavior.",
            "Return only the complete Python source, without markdown fences or explanation.",
        ]
    )
    return "\n".join(sections)
