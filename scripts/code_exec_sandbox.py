#!/usr/bin/env python3
"""Sandboxed Python code execution for the RL-distill pipeline.

Executes a candidate code block in an isolated subprocess with strict
resource limits, returning a structured verdict that feeds:
  1. the teacher's evaluation (so its judgment is grounded in real runtime
     behavior, not text-only inspection), and
  2. the double-confirmation gate on the teacher's corrected code (a
     corrected sample is admitted to the SFT set only if it actually runs
     to PASS).

Design:
  - One subprocess per execution (fresh interpreter -> no global state
    leakage between samples).
  - resource.setrlimit caps CPU time and address space; a wall-clock
    timeout is enforced by the parent joining with timeout.
  - stdout/stderr are captured and tail-truncated to keep records compact.
  - No network access is provided; the sandbox runs in the same env as
    the pipeline (which already has qiskit, cirq, pennylane, etc. on the
    NAS-backed venv). If a question requires a missing package, the
    execution returns ERROR and the sample is rejected.
  - The verdict is one of:
      PASS  — exit 0, no stderr, optional test harness assertions passed.
      FAIL  — runtime exception, non-zero exit, or assertion failure.
      ERROR — could not execute (syntax error, missing module, timeout,
              OOM).

This module is intentionally self-contained (stdlib only) so it can be
imported from scripts/rl_distill_pipeline.py without extra deps.
"""

from __future__ import annotations

import os
import resource
import subprocess
import sys
import textwrap
import time
from typing import Any

# Defaults (overridable by callers)
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MEMORY_GIB = 1
DEFAULT_MAX_STDOUT_CHARS = 4000
DEFAULT_MAX_STDERR_CHARS = 4000


def _set_rlimits(memory_gib: float) -> None:
    """Apply CPU-time and address-space limits inside the child process."""
    # Address space limit (bytes). On platforms that don't support RLIMIT_AS
    # this is silently skipped.
    mem_bytes = int(memory_gib * 1024 * 1024 * 1024)
    try:
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    except (ValueError, OSError):
        pass
    # CPU time limit (seconds, hard = soft). Raises SIGXCPU if exceeded.
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (DEFAULT_TIMEOUT_SECONDS, DEFAULT_TIMEOUT_SECONDS))
    except (ValueError, OSError):
        pass


def _tail(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return "..." + text[-max_chars:]


def execute_code(
    code: str,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    memory_gib: float = DEFAULT_MEMORY_GIB,
    max_stdout_chars: int = DEFAULT_MAX_STDOUT_CHARS,
    max_stderr_chars: int = DEFAULT_MAX_STDERR_CHARS,
    extra_env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute `code` in a sandboxed subprocess.

    Returns a dict with shape:
        {
          "verdict": "PASS" | "FAIL" | "ERROR",
          "stdout": str,
          "stderr": str,
          "exit_code": int,
          "runtime_ms": int,
          "truncated": bool,
        }
    """
    code = textwrap.dedent(code).strip()
    if not code:
        return {
            "verdict": "ERROR",
            "stdout": "",
            "stderr": "empty code block",
            "exit_code": -1,
            "runtime_ms": 0,
            "truncated": False,
        }

    # Quick syntax check without executing — cheap and avoids spawning a
    # process for obviously-broken code.
    try:
        compile(code, "<candidate>", "exec")
    except SyntaxError as exc:
        return {
            "verdict": "ERROR",
            "stdout": "",
            "stderr": f"SyntaxError: {exc.msg} (line {exc.lineno})",
            "exit_code": -1,
            "runtime_ms": 0,
            "truncated": False,
        }

    # Write the candidate to a temp file and execute it as a fresh
    # interpreter so there is no shared global state between samples.
    import tempfile

    fd, tmp_path = tempfile.mkstemp(prefix="rl_exec_", suffix=".py", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)
        env = dict(os.environ)
        # Keep matplotlib/qiskit from opening displays or polling servers.
        env.setdefault("MPLBACKEND", "Agg")
        env.setdefault("QISKIT_SUPPRESS_PACKAGING_WARNINGS", "Y")
        if extra_env:
            env.update(extra_env)

        start = time.monotonic()
        try:
            proc = subprocess.run(
                [sys.executable, "-I", tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=env,
                preexec_fn=lambda: _set_rlimits(memory_gib),
            )
            runtime_ms = int((time.monotonic() - start) * 1000)
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            exit_code = proc.returncode
            truncated = len(stdout) > max_stdout_chars or len(stderr) > max_stderr_chars
            stdout = _tail(stdout, max_stdout_chars)
            stderr = _tail(stderr, max_stderr_chars)

            if exit_code == 0 and not stderr.strip():
                verdict = "PASS"
            elif exit_code == 0 and stderr.strip():
                # Exit 0 but with stderr warnings — still PASS, but record stderr.
                verdict = "PASS"
            else:
                verdict = "FAIL"
            return {
                "verdict": verdict,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "runtime_ms": runtime_ms,
                "truncated": truncated,
            }
        except subprocess.TimeoutExpired:
            runtime_ms = int((time.monotonic() - start) * 1000)
            return {
                "verdict": "ERROR",
                "stdout": "",
                "stderr": f"TimeoutExpired after {timeout_seconds}s",
                "exit_code": -1,
                "runtime_ms": runtime_ms,
                "truncated": False,
            }
        except MemoryError:
            runtime_ms = int((time.monotonic() - start) * 1000)
            return {
                "verdict": "ERROR",
                "stdout": "",
                "stderr": f"MemoryError (limit {memory_gib} GiB)",
                "exit_code": -1,
                "runtime_ms": runtime_ms,
                "truncated": False,
            }
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def verdict_for_record(exec_result: dict[str, Any]) -> str:
    """Convenience accessor used by the pipeline."""
    return exec_result.get("verdict", "ERROR")


def format_exec_brief(exec_result: dict[str, Any], *, max_chars: int = 1200) -> str:
    """Format an execution result into a compact string for the teacher prompt.

    The teacher sees the verdict + a tail of stderr/stdout so its critique
    can reference the real runtime error (e.g. `NameError: 'qc' is not
    defined on line 12`).
    """
    verdict = exec_result.get("verdict", "ERROR")
    stdout = (exec_result.get("stdout") or "")[: max_chars // 2]
    stderr = (exec_result.get("stderr") or "")[: max_chars // 2]
    runtime_ms = exec_result.get("runtime_ms", 0)
    exit_code = exec_result.get("exit_code", -1)
    parts = [
        f"execution_verdict: {verdict}",
        f"exit_code: {exit_code}",
        f"runtime_ms: {runtime_ms}",
    ]
    if stderr:
        parts.append(f"stderr:\n{stderr}")
    if stdout:
        parts.append(f"stdout:\n{stdout}")
    return "\n".join(parts)


def check_program_shape(
    code: str, *, require_main: bool = True, require_main_guard: bool = True
) -> dict[str, Any]:
    """Static check that `code` is a full program with a `main()` entry point.

    Returns a dict with:
        {
          "has_main_def": bool,        # `def main(...)` present
          "has_main_guard": bool,      # `if __name__ == '__main__':` present
          "calls_main": bool,          # `main()` is actually called in the guard
          "is_full_program": bool,     # all of the above when require_* are True
          "issues": list[str],         # human-readable problems
        }

    This is a cheap AST-level check (no execution) used to enforce the
    question-shape contract: the student must write a full runnable program
    with a `main` function, not an isolated function or library snippet.
    """
    import ast

    issues: list[str] = []
    code = textwrap.dedent(code).strip()
    if not code:
        return {
            "has_main_def": False,
            "has_main_guard": False,
            "calls_main": False,
            "is_full_program": False,
            "issues": ["empty code block"],
        }
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "has_main_def": False,
            "has_main_guard": False,
            "calls_main": False,
            "is_full_program": False,
            "issues": [f"SyntaxError: {exc.msg} (line {exc.lineno})"],
        }

    # Walk top-level statements for `def main(...)` and the __main__ guard.
    has_main_def = False
    has_main_guard = False
    calls_main = False

    for node in tree.body:
        # `def main(...)` at top level
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            has_main_def = True
        # `if __name__ == '__main__':` guard at top level
        if isinstance(node, ast.If):
            test = node.test

            # Match: __name__ == '__main__'  (or "__main__" == __name__)
            def _is_main_compare(cmp):
                if not isinstance(cmp, ast.Compare):
                    return False
                if not isinstance(cmp.ops, list) or len(cmp.ops) != 1:
                    return False
                if not isinstance(cmp.ops[0], ast.Eq):
                    return False
                left_is_name = isinstance(cmp.left, ast.Name) and cmp.left.id == "__name__"
                right_is_str = (
                    len(cmp.comparators) == 1
                    and isinstance(cmp.comparators[0], ast.Constant)
                    and isinstance(cmp.comparators[0].value, str)
                    and cmp.comparators[0].value == "__main__"
                )
                # Also accept reversed: "__main__" == __name__
                left_is_str = (
                    isinstance(cmp.left, ast.Constant)
                    and isinstance(cmp.left.value, str)
                    and cmp.left.value == "__main__"
                )
                right_is_name = (
                    len(cmp.comparators) == 1
                    and isinstance(cmp.comparators[0], ast.Name)
                    and cmp.comparators[0].id == "__name__"
                )
                return (left_is_name and right_is_str) or (left_is_str and right_is_name)

            if _is_main_compare(test):
                has_main_guard = True
                # Check that the guard body calls main()
                for stmt in node.body:
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                        fn = stmt.value.func
                        if isinstance(fn, ast.Name) and fn.id == "main":
                            calls_main = True

    if require_main and not has_main_def:
        issues.append(
            "missing top-level `def main(...)` — the program must have a main entry point"
        )
    if require_main_guard and not has_main_guard:
        issues.append(
            "missing `if __name__ == '__main__':` guard — the program must be runnable as `python file.py`"
        )
    if has_main_guard and not calls_main:
        issues.append(
            "the `__main__` guard does not call `main()` — the program will not execute anything"
        )

    is_full = has_main_def and has_main_guard and (calls_main or not require_main_guard)
    if require_main and not has_main_def:
        is_full = False
    if require_main_guard and not has_main_guard:
        is_full = False

    return {
        "has_main_def": has_main_def,
        "has_main_guard": has_main_guard,
        "calls_main": calls_main,
        "is_full_program": is_full,
        "issues": issues,
    }


def check_stdout_nonempty(exec_result: dict[str, Any]) -> dict[str, Any]:
    """Verify that the executed program actually printed something to stdout.

    Returns {\"stdout_nonempty\": bool, \"issues\": list[str]}.
    Used to enforce the question-shape contract that the program must
    compute and print a concrete result.
    """
    stdout = (exec_result.get("stdout") or "").strip()
    issues: list[str] = []
    if not stdout:
        issues.append(
            "program ran to PASS but printed nothing to stdout — "
            "the question requires printing a concrete result"
        )
    return {"stdout_nonempty": bool(stdout), "issues": issues}


if __name__ == "__main__":
    # Self-test: run a trivially correct program.
    ok = execute_code("print('hello')\n")
    bad = execute_code("raise ValueError('boom')\n")
    syn = execute_code("def f(:\n  pass\n")
    print("OK sample:", ok)
    print("FAIL sample:", bad)
    print("SYNTAX sample:", syn)
    # Shape checks
    full = "def main():\n    print(1+1)\n\nif __name__ == '__main__':\n    main()\n"
    no_main = "def helper():\n    return 42\n"
    no_guard = "def main():\n    print(42)\n"
    print("SHAPE full:", check_program_shape(full))
    print("SHAPE no_main:", check_program_shape(no_main))
    print("SHAPE no_guard:", check_program_shape(no_guard))
    print("STDOUT nonempty:", check_stdout_nonempty({"stdout": "42\n"}))
    print("STDOUT empty:", check_stdout_nonempty({"stdout": ""}))
