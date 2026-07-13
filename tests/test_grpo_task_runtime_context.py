from __future__ import annotations

import textwrap
from pathlib import Path

from training.grpo_trainer import build_prompt, build_task_runtime_context


def _write_task(
    tmp_path: Path,
    *,
    meta: dict,
    candidate_source: str = "def solve(x):\n    return x\n",
    tests_source: str = """
        # Preserve declared behavior
        def run_tests(candidate_path: str) -> dict:
            failures = []
            failures.append("must keep stable ordering")
            return {"passed": not failures, "details": failures}
    """,
) -> dict:
    task_dir = tmp_path / meta.get("id", "task")
    task_dir.mkdir()
    (task_dir / "tests.py").write_text(textwrap.dedent(tests_source), encoding="utf-8")
    if meta.get("candidate_file"):
        (task_dir / meta["candidate_file"]).write_text(candidate_source, encoding="utf-8")
    return {
        "meta": meta,
        "task_dir": task_dir,
        "tests_py": task_dir / "tests.py",
    }


def test_build_task_runtime_context_marks_single_file_tasks_and_reads_interface(
    tmp_path: Path,
) -> None:
    task = _write_task(
        tmp_path,
        meta={
            "id": "quantum_gate_alias_registry_cleanup",
            "candidate_file": "candidate.py",
        },
        candidate_source="def canonicalize_gate(name):\n    return name.upper()\n",
    )

    context = build_task_runtime_context(task, detail_budget_cap=8)

    assert context["task_id"] == "quantum_gate_alias_registry_cleanup"
    assert context["single_file_expected"] is True
    assert context["allowed_import_roots"] == []
    assert "canonicalize_gate(name)" in context["required_interface"]
    assert "must keep stable ordering" in context["behavior_hints"]
    assert context["detail_budget"] >= 1


def test_build_task_runtime_context_marks_multifile_tasks_and_filters_import_allowlist(
    tmp_path: Path,
) -> None:
    task = _write_task(
        tmp_path,
        meta={
            "id": "workspace_runner_smoke",
            "candidate_files": ["runner.py", "helpers.py"],
            "allowed_import_roots": ["numpy", " pandas ", "", 123],
        },
    )

    context = build_task_runtime_context(task, detail_budget_cap=6)

    assert context["single_file_expected"] is False
    assert context["allowed_import_roots"] == ["numpy", "pandas"]
    assert context["required_interface"] == []
    assert context["detail_budget"] >= 1


def test_build_prompt_adds_single_file_guardrails(tmp_path: Path) -> None:
    task = _write_task(
        tmp_path,
        meta={
            "id": "quantum_qaoa_maxcut",
            "domain": "quantum",
            "category": "optimization",
            "candidate_file": "candidate.py",
            "task_prompt": "Implement the requested helpers.",
        },
        candidate_source="def solve():\n    return 1\n",
    )
    task.update(build_task_runtime_context(task, detail_budget_cap=8))

    prompt = build_prompt(task)

    assert "Keep the answer self-contained in one Python file." in prompt
    assert "Do not depend on repository-local helpers or invent non-standard modules." in prompt
    assert "Return only the final Python code." in prompt
