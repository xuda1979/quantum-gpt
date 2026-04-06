from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_run_hf_pass1_eval_uses_canonical_sanitizer() -> None:
    text = _read("scripts/run_hf_pass1_eval.py")
    assert "from evals.runner.candidate_sanitize import sanitize_candidate_text" in text
    assert "def sanitize_candidate_text(" not in text


def test_serve_openai_chat_adapter_uses_canonical_sanitizer() -> None:
    text = _read("scripts/serve_openai_chat_adapter.py")
    assert "from evals.runner.candidate_sanitize import sanitize_candidate_text" in text
    assert "def sanitize_candidate_text(" not in text
    assert "def _strip_think_block(" not in text
    assert "def _extract_leading_fenced_block(" not in text
    assert "def _remove_standalone_fence_lines(" not in text
    assert "def _longest_parseable_python_prefix(" not in text
