#!/usr/bin/env python3
"""Build clean runnable SFT dataset v5 from archived teacher responses.

- Source: _flash_archive_20260606 high_quality file (intact indentation).
- Extract the largest Python code block from each response.
- Strip all comments and docstrings (AST round-trip via ast.unparse).
- Execute every sample in a subprocess; only emit samples that run cleanly.
"""

import ast
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (
    ROOT
    / "data/generated/_flash_archive_20260606/quantum_distillation_teacher_responses_asi2_v1_high_quality.jsonl"
)
OUT_DIR = (
    ROOT
    / "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_clean_runnable_v5"
)
PYTHON = ROOT / ".venv/bin/python"

SYSTEM_PROMPT = (
    "You are a careful quantum software engineering assistant. Use the user's "
    "task and any supplied context to produce correct, testable Python or "
    "precise repair guidance."
)


def extract_code_blocks(text: str):
    blocks = []
    parts = text.split("```")
    for i in range(1, len(parts), 2):
        block = parts[i]
        if block.startswith("python"):
            block = block[len("python") :]
        elif block.startswith("py\n"):
            block = block[2:]
        blocks.append(block.strip("\n"))
    return blocks


class DocstringStripper(ast.NodeTransformer):
    def _strip(self, node):
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            node.body = node.body[1:]
            if not node.body:
                node.body = [ast.Pass()]
        return node

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        return self._strip(node)

    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)
        return self._strip(node)

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        return self._strip(node)

    def visit_Module(self, node):
        self.generic_visit(node)
        return self._strip(node)


def strip_comments(code: str) -> str:
    tree = ast.parse(code)
    tree = DocstringStripper().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def ensure_test_invocation(code: str) -> str:
    """If code defines test functions but never calls them, append a main guard."""
    tree = ast.parse(code)
    defined_tests = [
        n.name for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
    ]
    if not defined_tests:
        return code
    has_main = any(
        isinstance(n, ast.If)
        and isinstance(n.test, ast.Compare)
        and getattr(getattr(n.test.left, "id", None), "__str__", lambda: "")() == "__name__"
        for n in tree.body
    )
    top_calls = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            top_calls.add(n.func.id)
    uncalled = [t for t in defined_tests if t not in top_calls]
    if uncalled and not has_main:
        code += "\n\nif __name__ == '__main__':\n"
        for t in uncalled:
            code += f"    {t}()\n"
    return code


def run_sample(code: str, timeout: int = 60):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        proc = subprocess.run([str(PYTHON), path], capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    finally:
        Path(path).unlink(missing_ok=True)


def main():
    rows = [json.loads(l) for l in open(SRC) if l.strip()]
    kept, rejected = [], []
    for idx, r in enumerate(rows):
        eid = r["example_id"]
        blocks = extract_code_blocks(r["response"])
        py_blocks = []
        for b in blocks:
            try:
                ast.parse(b)
                py_blocks.append(b)
            except SyntaxError:
                pass
        if not py_blocks:
            rejected.append({"example_id": eid, "reason": "no_parseable_code"})
            print(f"[{idx}] {eid}: REJECT no parseable code")
            continue
        code = "\n\n".join(py_blocks) if len(py_blocks) > 1 else py_blocks[0]
        try:
            ast.parse(code)
        except SyntaxError:
            code = max(py_blocks, key=len)
        try:
            clean = strip_comments(code)
            clean = ensure_test_invocation(clean)
            clean = strip_comments(clean)
        except Exception as e:
            rejected.append({"example_id": eid, "reason": f"strip_failed: {e}"})
            print(f"[{idx}] {eid}: REJECT strip failed {e}")
            continue
        rc, out, err = run_sample(clean)
        if rc != 0:
            rejected.append(
                {"example_id": eid, "reason": "runtime_error", "stderr_tail": err[-2000:]}
            )
            print(
                f"[{idx}] {eid}: RUNTIME FAIL rc={rc} | {err.strip().splitlines()[-1] if err.strip() else 'no stderr'}"
            )
            continue
        kept.append(
            {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": r["instruction"]},
                    {"role": "assistant", "content": f"```python\n{clean}\n```"},
                ],
                "example_id": eid,
            }
        )
        print(f"[{idx}] {eid}: OK")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "all_chatml.jsonl", "w") as f:
        for k in kept:
            f.write(json.dumps({"messages": k["messages"]}, ensure_ascii=False) + "\n")
    with open(OUT_DIR / "rejected.jsonl", "w") as f:
        for rj in rejected:
            f.write(json.dumps(rj, ensure_ascii=False) + "\n")
    manifest = {
        "source": str(SRC.relative_to(ROOT)),
        "total_source_rows": len(rows),
        "kept": len(kept),
        "rejected": len(rejected),
        "policy": {
            "code_extraction": "all parseable python blocks merged",
            "comments": "stripped via ast.unparse (no comments, no docstrings)",
            "validation": "executed in subprocess, exit code 0 required",
            "test_invocation": "auto main-guard appended for uncalled test_ functions",
        },
    }
    with open(OUT_DIR / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nDONE kept={len(kept)} rejected={len(rejected)} -> {OUT_DIR}")


if __name__ == "__main__":
    main()
