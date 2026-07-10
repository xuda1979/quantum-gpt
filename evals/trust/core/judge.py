"""Optional LLM rubric judge.

When a task ships a ``rubric.md`` (or ``rubric.json``) alongside its
``tests.py``, the trust-eval harness can additionally invoke an LLM
judge to score the candidate against the rubric. The LLM judge is
**never** the sole signal: the deterministic program verdict always
takes precedence for pass/fail accounting. The LLM verdict is recorded
alongside and disagreements are surfaced.

To keep the harness hermetic and deterministic, the LLM judge is
invoked via a pluggable adapter (e.g. an OpenAI-compatible client). The
adapter must return a structured result with ``passed`` (bool) and
``details`` (list[str]). If no adapter is configured, the LLM judge is
skipped and only the deterministic verdict is recorded.

The judge configuration (model name, temperature, rubric hash, prompt
template hash) is itself hashed and recorded in the ledger as
``judge_meta_hash``, so any drift in judge configuration is detectable.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

from . import hashing


class JudgeAdapter(Protocol):
    """Pluggable LLM judge adapter."""
    def judge(
        self, *, prompt: str, rubric: str, candidate_code: str
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class LLMVerdict:
    passed: bool
    details: list[str]
    judge_meta_hash: str
    raw_response: str | None = None


def find_rubric(task_dir: Path) -> Path | None:
    for name in ("rubric.json", "rubric.md"):
        p = task_dir / name
        if p.is_file():
            return p
    return None


def build_judge_prompt(
    *, task_name: str, task_id: str, rubric: str, candidate_code: str
) -> str:
    return (
        f"You are a rigorous code reviewer for the task: {task_name} (id={task_id}).\n"
        "You are given a rubric and a candidate Python implementation.\n"
        "Decide whether the candidate satisfies every rubric item.\n"
        "Return STRICT JSON: {\"passed\": bool, \"details\": [string, ...]}.\n"
        "Do not output anything except the JSON object.\n\n"
        f"## Rubric\n{rubric}\n\n"
        f"## Candidate code\n```python\n{candidate_code}\n```\n"
    )


def judge_meta_hash(
    *, judge_model: str, judge_temperature: float, rubric_hash: str, prompt_template_hash: str
) -> str:
    return hashing.hash_json({
        "judge_model": judge_model,
        "judge_temperature": judge_temperature,
        "rubric_hash": rubric_hash,
        "prompt_template_hash": prompt_template_hash,
    })


def parse_judge_response(raw: str) -> dict[str, Any]:
    """Parse a JSON object from an LLM response, tolerating code fences."""
    text = raw.strip()
    if text.startswith("```"):
        # strip ```json ... ``` fences
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise ValueError("judge response is not a JSON object")
    return {
        "passed": bool(obj.get("passed", False)),
        "details": [str(d) for d in obj.get("details", [])],
    }


def run_llm_judge(
    *,
    adapter: JudgeAdapter,
    task_dir: Path,
    task_id: str,
    task_name: str,
    candidate_code: str,
    judge_model: str,
    judge_temperature: float,
    prompt_template_hash: str,
) -> LLMVerdict | None:
    rubric_path = find_rubric(task_dir)
    if rubric_path is None:
        return None
    rubric = rubric_path.read_text(encoding="utf-8")
    rubric_hash = hashing.hash_file(rubric_path)
    prompt = build_judge_prompt(
        task_name=task_name, task_id=task_id,
        rubric=rubric, candidate_code=candidate_code,
    )
    raw = adapter.judge(prompt=prompt, rubric=rubric, candidate_code=candidate_code)
    if isinstance(raw, dict) and "passed" in raw:
        parsed = raw
    else:
        parsed = parse_judge_response(str(raw))
    mh = judge_meta_hash(
        judge_model=judge_model,
        judge_temperature=judge_temperature,
        rubric_hash=rubric_hash,
        prompt_template_hash=prompt_template_hash,
    )
    return LLMVerdict(
        passed=parsed["passed"],
        details=parsed["details"],
        judge_meta_hash=mh,
        raw_response=str(raw),
    )
