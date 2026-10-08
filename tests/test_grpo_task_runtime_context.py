# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate (precedent: training/grpo_trainer.py)
from __future__ import annotations

import textwrap
from pathlib import Path
from types import SimpleNamespace

import torch

from training.grpo_trainer import (
    SYSTEM_PROMPT,
    StopAfterClosedCodeFence,
    _run_harness_subprocess,
    adaptive_generation_token_budget,
    build_generation_diagnostics,
    build_prompt,
    build_task_runtime_context,
    evaluate_candidate,
    has_closed_code_fence,
    load_reference_code_char_counts,
)


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


def test_rollout_prompt_requires_concise_code_and_an_immediate_stop(tmp_path: Path) -> None:
    task = _write_task(
        tmp_path,
        meta={
            "id": "concise_quantum_solution",
            "candidate_file": "candidate.py",
            "task_prompt": "Implement solve().",
        },
    )
    task.update(build_task_runtime_context(task, detail_budget_cap=8))

    prompt = build_prompt(task)

    assert "Do not include Markdown fences" in SYSTEM_PROMPT
    assert "Stop immediately after the final required Python statement." in prompt
    assert "Do not add explanations, tests, examples, or demo code." in prompt


def test_generation_diagnostics_exposes_eos_and_extraction_overhead() -> None:
    diagnostics = build_generation_diagnostics(
        raw_responses=["```python\nprint(1)\n```\nextra", "print(2)"],
        codes=["print(1)", "print(2)"],
        completion_token_ids=[torch.tensor([10, 11, 99]), torch.tensor([12, 13, 14, 15])],
        max_new_tokens=4,
        eos_token_ids={99},
    )

    assert diagnostics["completion_token_lengths"] == [3, 4]
    # 2026-08-31 stop-identity fix (training/generation.py): the three stop
    # reasons partition completions exactly once. A fence-closed completion
    # is labeled by its fence class only — the r10 synthetic fence-stop
    # marker leaves an EOS id at the end, so counting it as eos_terminated
    # double-counted every fence-stopped completion (eos+fence+truncated
    # == 2) and hid "the model never samples EOS" (run-6 diagnostic).
    # Response 0 closes a code fence -> fence_terminated, NOT eos_terminated,
    # even though its last token id (99) is in eos_token_ids.
    assert diagnostics["eos_terminated"] == [False, False]
    assert diagnostics["fence_terminated"] == [True, False]
    assert diagnostics["eos_termination_rate"] == 0.0
    assert diagnostics["fence_termination_rate"] == 0.5
    assert diagnostics["truncation_rate"] == 0.5
    assert diagnostics["raw_response_chars"] == [28, 8]
    assert diagnostics["extracted_code_chars"] == [8, 8]


def test_generation_diagnostics_eos_at_cap_is_not_truncation() -> None:
    """A completion that ends exactly at the hard cap WITH EOS is a natural
    end, not a truncation. The old rule counted every ``length >= cap``
    completion as truncated regardless of the final token (2026-08-24
    data-efficiency finding 3), overstating truncation_rate and pushing
    healthy groups toward skip/repair routing.
    """
    diagnostics = build_generation_diagnostics(
        raw_responses=["code one", "code two"],
        codes=["code one", "code two"],
        completion_token_ids=[
            torch.tensor([10, 11, 12, 99]),  # exactly at cap, EOS-terminated
            torch.tensor([20, 21, 22, 23]),  # exactly at cap, no EOS -> cut
        ],
        max_new_tokens=4,
        eos_token_ids={99},
    )

    assert diagnostics["completion_token_lengths"] == [4, 4]
    assert diagnostics["eos_terminated"] == [True, False]
    assert diagnostics["truncation_rate"] == 0.5
    assert diagnostics["eos_termination_rate"] == 0.5


def test_closed_code_fence_requires_an_opening_and_a_closing_fence() -> None:
    assert not has_closed_code_fence("print('unfenced')")
    assert not has_closed_code_fence("```python\nprint(1)")
    assert has_closed_code_fence("```python\nprint(1)\n```")
    assert has_closed_code_fence("prose\n```\ndef solve():\n    return 1\n```\nmore")


def test_closed_code_fence_stopping_criterion_ignores_prompt_tokens() -> None:
    class _Tokenizer:
        @staticmethod
        def decode(token_ids: torch.Tensor, *, skip_special_tokens: bool) -> str:
            assert skip_special_tokens
            return "".join(chr(int(token_id)) for token_id in token_ids)

    criterion = StopAfterClosedCodeFence(_Tokenizer(), prompt_length=2)
    prompt = [1, 2]
    open_only = [ord(char) for char in "```python\nprint(1)"]
    closed = [ord(char) for char in "```python\nprint(1)\n```"]

    assert not criterion(torch.tensor([prompt + open_only]), None).item()
    assert criterion(torch.tensor([prompt + closed]), None).item()


def test_reference_code_lengths_are_loaded_from_manifest_lineage(tmp_path: Path) -> None:
    source = tmp_path / "questions_and_code.jsonl"
    source.write_text(
        '{"question":"short","code":"print(1)"}\n{"question":"long","code":"abcdefghij"}\n',
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.txt"
    manifest.write_text(
        "# source=questions_and_code.jsonl sha256=unused-by-runtime-loader\nqc-0001\nqc-0002\n",
        encoding="utf-8",
    )

    lengths = load_reference_code_char_counts(manifest)

    assert lengths == {"qc-0001": 8, "qc-0002": 10}


def test_non_jsonl_manifest_lineage_uses_fixed_generation_budget(tmp_path: Path) -> None:
    source = tmp_path / "targeted_ids.txt"
    source.write_text("quantum_task_one\nquantum_task_two\n", encoding="utf-8")
    manifest = tmp_path / "manifest.txt"
    manifest.write_text(
        "# source=targeted_ids.txt sha256=unused-by-runtime-loader\n"
        "quantum_task_one\nquantum_task_two\n",
        encoding="utf-8",
    )

    assert load_reference_code_char_counts(manifest) == {}


def test_training_subprocess_rejects_candidate_scorer_frame_introspection() -> None:
    root = Path(__file__).resolve().parents[1]
    task_dir = root / "evals/tasks/quantum/superdense_pauli_router"
    exploit = """
import inspect
def encode_message(bits):
    frame = inspect.currentframe().f_back
    while frame:
        if 'expected' in frame.f_locals:
            return frame.f_locals['expected'][bits]
        frame = frame.f_back
def decode_message(opcode):
    return '00'
"""

    result, typed_score, typed_info = _run_harness_subprocess(
        exploit,
        {
            "tests_py": task_dir / "tests.py",
            "task_dir": task_dir,
            "meta": {"id": "quantum_superdense_pauli_router"},
        },
        SimpleNamespace(harness_timeout_seconds=10),
    )

    assert result["passed"] is False
    assert result["security_violation"] is True
    assert any("candidate source policy" in detail for detail in result["details"])
    assert typed_score == 0.0
    assert typed_info is None


def test_training_gives_security_violation_no_shaped_reward() -> None:
    root = Path(__file__).resolve().parents[1]
    task_dir = root / "evals/tasks/quantum/superdense_pauli_router"
    task = {
        "tests_py": task_dir / "tests.py",
        "task_dir": task_dir,
        "meta": {"id": "quantum_superdense_pauli_router"},
        "required_interface": ["encode_message(bits)", "decode_message(opcode)"],
        "detail_budget": 1,
        "single_file_expected": True,
        "allowed_import_roots": [],
    }
    args = SimpleNamespace(
        harness_timeout_seconds=10,
        reward_pass_weight=1.0,
        reward_syntax_weight=1.0,
        reward_interface_weight=1.0,
        reward_verifier_weight=1.0,
        reward_brevity_weight=1.0,
        brevity_target_lines=60,
        reward_import_hygiene_weight=1.0,
        self_evaluation_enabled=False,
        model_judge_enabled=False,
    )
    exploit = "import inspect\ndef encode_message(bits): return bits\n"

    reward = evaluate_candidate(exploit, None, task, args)

    assert reward["security_violation"] is True
    assert reward["total_reward"] == 0.0
    assert all(
        value == 0.0
        for name, value in reward.items()
        if name.endswith("_reward") and isinstance(value, (int, float))
    )


def test_adaptive_generation_budget_is_bounded_and_quantized() -> None:
    assert adaptive_generation_token_budget(None, base_tokens=512, max_tokens=1024) == 512
    assert adaptive_generation_token_budget(1000, base_tokens=512, max_tokens=1024) == 512
    assert adaptive_generation_token_budget(1901, base_tokens=512, max_tokens=1024) == 768
    assert adaptive_generation_token_budget(2052, base_tokens=512, max_tokens=1024) == 896
    assert adaptive_generation_token_budget(2738, base_tokens=512, max_tokens=1024) == 1024
    assert adaptive_generation_token_budget(9999, base_tokens=512, max_tokens=1024) == 1024


def test_distill_prompt_does_not_expose_generated_checker_hints(tmp_path: Path) -> None:
    task = _write_task(
        tmp_path,
        meta={
            "id": "qc-0001",
            "domain": "quantum",
            "category": "distill_v3",
            "candidate_file": "solution.py",
            "task_prompt": "Write a complete quantum program.",
        },
        candidate_source='"""stub"""\n',
        tests_source="""
            EXPECTED = "secret stdout"
            def run_tests(candidate_path):
                return {"passed": False, "details": ["expected: secret stdout"]}
        """,
    )
    task.update(build_task_runtime_context(task, detail_budget_cap=8))

    prompt = build_prompt(task)

    assert task["behavior_hints"] == []
    assert "qiskit" in task["allowed_import_roots"]
    assert "cirq" in task["allowed_import_roots"]
    assert "secret stdout" not in prompt
    assert "Write a complete quantum program" in prompt
