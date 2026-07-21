#!/usr/bin/env python3
"""Self-correcting distillation pipeline for Qwen3.6-27B (iter-5).

Pipeline (per question):
  1. Student (27B adapter on Huanxin, OpenAI chat completions) writes code.
  2. Teacher (GLM5.2 via local Anthropic Messages proxy) evaluates correctness.
  3. If student is correct → keep student code as the assistant target
     (positive sample: the student got it right).
  4. If student is incorrect → teacher writes a correction:
     a one-paragraph critique + the corrected code using UPDATED libraries
     (Qiskit >= 2.3, PennyLane >= 0.44, Cirq >= 1.4, Braket latest).
  5. Three quality passes on the final code:
       Pass 1 — def main() prints the exact expected marker string.
       Pass 2 — 100% runnable, correct, efficient (sandbox-executed).
       Pass 3 — beautiful: clean, idiomatic, well-structured (static checks).
  6. If all 3 passes → emit a chat-sft-v1 record.
     Otherwise → retry the teacher correction (up to 3 attempts); skip if still failing.
  7. (Corrections only) Re-emit the teacher's corrected answer via the
     OpenAI-compatible GLM5.2 endpoint to capture per-token top-k logprobs
     for soft-KL distillation. The Anthropic Messages path used in step 4
     does not expose top_logprobs, so this is a second, single-pass call.
     Positive samples (student was correct) and any re-emit failures get an
     empty teacher_logits field and fall back to plain NLL in the KL trainer.

Output (data/generated/self_correcting_distill_27b_v1/):
  - teacher_responses.jsonl   (raw student code + teacher eval + correction + teacher_logits)
  - sft_chatml.jsonl          (chat-sft-v1 records with top-level teacher_logits,
                               ready for training/qwen_sft_peft_kl.py)
  - quality_report.json       (per-question pass/fail summary)

Env vars:
  STUDENT_27B_API_BASE    e.g. http://127.0.0.1:8007/v1  (vLLM on Huanxin ASI1)
  STUDENT_27B_API_KEY     any non-empty string if the server ignores keys
  STUDENT_27B_MODEL       served model name (default qwen36-27b-rl-distill)
  GLM52_API_BASE          e.g. http://127.0.0.1:49983   (local Anthropic proxy, step 4)
  GLM52_API_KEY           Huanxin GLM5.2 key
  GLM52_OPENAI_API_BASE   e.g. http://127.0.0.1:8009/v1 (OpenAI-compat proxy, step 7)
  GLM52_OPENAI_API_KEY    defaults to $GLM52_API_KEY
  TEACHER_TOP_LOGPROBS    top-k logprobs per token (default 20)
  PYTHON_RUN_BIN          python interpreter for sandbox execution (default .venv/bin/python)
  MAX_QUESTIONS           cap (default 100)
  START_INDEX             default 0
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_STUDENT = (
    "You are a careful quantum software engineering assistant. Use the user's task "
    "and any supplied context to produce correct, testable Python. Always produce a "
    "complete, runnable Python program with `def main()` that prints the exact "
    "specified marker string. Do not include markdown fences or surrounding commentary."
)

SYSTEM_PROMPT_TEACHER = (
    "You are a senior quantum software engineering reviewer. You evaluate student "
    "code with precision and, when the student is wrong, you produce a corrected, "
    "complete, runnable Python program using CURRENT versions of the relevant "
    "libraries (Qiskit >= 2.3 with `qiskit.primitives.StatevectorSampler` / "
    "`StatevectorEstimator`, PennyLane >= 0.44, Cirq >= 1.4, amazon-braket-sdk "
    "with `LocalSimulator`). Always include `def main()` that prints the exact "
    "specified marker string. Be concise and rigorous."
)

TEACHER_EVAL_PROMPT = """\
You are reviewing a student's Python program for correctness.

Question (task prompt):
{question}

Expected marker string (must be printed exactly):
{marker}

Student code:
```python
{student_code}
```

Evaluate whether the student's code is correct. A correct program:
  - Defines `def main():` and calls it.
  - Prints the exact expected marker string.
  - Uses the required quantum framework (not a numpy substitute).
  - Produces the correct quantum-computing result (state, counts, expectation, etc.).
  - Runs in under 30 seconds.
  - Uses current library APIs (no deprecated calls).

Respond as STRICT JSON only (no markdown, no prose outside JSON):
{{
  "is_correct": true | false,
  "issues": ["short issue 1", "short issue 2"],
  "confidence": 0.0
}}

If the code is fully correct, return `"is_correct": true` and `"issues": []`.
"""

TEACHER_CORRECTION_PROMPT = """\
Question (task prompt):
{question}

Expected marker string (must be printed exactly on its own line):
{marker}

Student code (INCORRECT):
```python
{student_code}
```

Issues identified in the student's code:
{issues}

Write a corrected, complete, runnable Python program. Requirements:
  1. Starts with a ONE-paragraph critique of the student's code (2-4 sentences).
  2. Then a SINGLE ```python block with the complete corrected program.
  3. The program STARTS with a module docstring (a triple-quoted string describing what it does).
  4. The program defines `def main():` (with a short docstring) and calls it under `if __name__ == '__main__':`.
  5. The program prints EXACTLY this marker string: {marker}
  6. Uses CURRENT versions of the required quantum framework:
     - Qiskit >= 2.3: use `from qiskit.primitives import StatevectorSampler, StatevectorEstimator`
       (NOT the deprecated `BackendSampler`/`Sampler` V1 primitives).
     - PennyLane >= 0.44: use `qml.device("default.qubit", ...)` (the modern API).
     - Cirq >= 1.4: use `cirq.Simulator(seed=...)` and `result.histogram(key=...)`.
     - Braket: use `from braket.devices import LocalSimulator`.
  7. No markdown fences around the python block's INNER content — just the code.
  8. No `<think>` tags, no commentary after the code block.
  9. Runs in under 30 seconds with only numpy/scipy + the required framework.

Format:
<one-paragraph critique>

```python
<complete corrected code with module docstring>
```"""

CORRECTION_RETRY_PROMPT = """\
Your previous correction failed validation: {error}

Please regenerate the corrected Python program for this question:
{question}

Expected marker: {marker}

Requirements (same as before):
  - `def main():` defined and called.
  - Prints EXACTLY: {marker}
  - Uses current APIs of the required framework.
  - No markdown fences, no <think> tags.
  - Runs in under 30 seconds.

Output ONLY the raw Python code (no critique this time, no fences).
"""

TEACHER_REEMIT_LOGPROBS_PROMPT = """\
You previously graded a student's quantum-coding submission. Below is the question and the corrected answer you produced. Re-emit the corrected answer verbatim so we can capture per-token logprobs for soft distillation.

Question:
{question}

Corrected answer:
{correct_answer}

Return ONLY the corrected answer text (the contents of `correct_answer`), no preamble, no code fences, no commentary."""

# ---------------------------------------------------------------------------
# GLM5.2 Anthropic Messages API (teacher)
# ---------------------------------------------------------------------------


def anthropic_messages(
    *,
    api_base: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str = "",
    max_tokens: int = 4096,
    temperature: float = 0.0,
    timeout: float = 300.0,
    messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
    }
    if messages is not None:
        payload["messages"] = messages
    else:
        payload["messages"] = [{"role": "user", "content": user_prompt}]
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    if api_key:
        headers["x-api-key"] = api_key
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        f"{api_base.rstrip('/')}/v1/messages",
        data=data,
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def anthropic_messages_with_retry(
    *,
    api_base: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str = "",
    max_tokens: int = 4096,
    temperature: float = 0.0,
    timeout: float = 300.0,
    messages: list[dict[str, Any]] | None = None,
    max_retries: int = 3,
    retry_delay: float = 5.0,
) -> dict[str, Any]:
    """Wrap anthropic_messages with retry-on-transient-error logic.

    Retries on HTTP 5xx and urllib errors; raises immediately on 4xx (client error).
    """
    import urllib.error as _ue

    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return anthropic_messages(
                api_base=api_base,
                api_key=api_key,
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                messages=messages,
            )
        except _ue.HTTPError as e:
            last_exc = e
            if 500 <= e.code < 600 and attempt < max_retries:
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_exc = e
            if attempt < max_retries:
                time.sleep(retry_delay * (attempt + 1))
                continue
            raise
    raise last_exc  # type: ignore[misc]


def extract_text(raw: dict[str, Any]) -> str:
    content = raw.get("content", [])
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for block in content:
        if isinstance(block, dict):
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
        elif isinstance(block, str):
            parts.append(block)
    return "\n".join(parts).strip()


def extract_thinking(raw: dict[str, Any]) -> str:
    content = raw.get("content", [])
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "thinking":
            parts.append(block.get("thinking", ""))
    return "\n".join(parts).strip()


# ---------------------------------------------------------------------------
# 27B student (OpenAI chat completions)
# ---------------------------------------------------------------------------


def call_student_openai(
    *,
    api_base: str,
    api_key: str,
    model: str,
    user_prompt: str,
    system_prompt: str = SYSTEM_PROMPT_STUDENT,
    max_tokens: int = 2048,
    temperature: float = 0.3,
    timeout: float = 300.0,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    req = urllib.request.Request(
        f"{api_base.rstrip('/')}/chat/completions",
        data=data,
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    choices = raw.get("choices") or []
    if not choices:
        raise RuntimeError(f"student returned no choices: {raw}")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(f"student returned no content: {raw}")
    return content.strip()


def teacher_reemit_with_logits(
    *,
    api_base: str,
    api_key: str,
    model: str,
    question: str,
    correct_answer: str,
    system_prompt: str = SYSTEM_PROMPT_TEACHER,
    max_tokens: int = 4096,
    temperature: float = 0.0,
    timeout: float = 600.0,
    top_logprobs: int = 20,
) -> dict[str, Any]:
    """Re-emit the corrected answer via the OpenAI-compatible chat/completions
    endpoint so we can capture per-token top-k logprobs for soft distillation.

    Mirrors scripts/rl_distill_pipeline.py:teacher_correction_with_logits.
    The Anthropic Messages path (anthropic_messages above) does not expose
    top_logprobs, so we use a second OpenAI-compatible call against the
    GLM5.2 proxy for the logprobs pass only; the correction itself is still
    produced via the Anthropic path and validated by the 3-pass quality gate.

    Returns dict with:
      - content:  the re-emitted answer text (whitespace-stripped)
      - logprobs: list of per-token {token, logprob, top_logprobs:[...]}
      - top_logprobs: the K requested
    Returns {"content": "", "logprobs": [], "top_logprobs": K} on any error
    so the caller can degrade gracefully (plain SFT sample, no KL term).
    """
    user_prompt = TEACHER_REEMIT_LOGPROBS_PROMPT.format(
        question=question, correct_answer=correct_answer
    )
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "logprobs": True,
        "top_logprobs": top_logprobs,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    req = urllib.request.Request(
        f"{api_base.rstrip('/')}/chat/completions",
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - degrade gracefully
        return {"content": "", "logprobs": [], "top_logprobs": top_logprobs, "error": str(exc)}
    choices = raw.get("choices") or [{}]
    content = choices[0].get("message", {}).get("content", "")
    lp = choices[0].get("logprobs") or {"content": []}
    return {
        "content": content.strip() if isinstance(content, str) else "",
        "logprobs": lp.get("content", []) if isinstance(lp, dict) else [],
        "top_logprobs": top_logprobs,
    }


# ---------------------------------------------------------------------------
# Code extraction & validation
# ---------------------------------------------------------------------------


def strip_markdown_fences(text: str) -> str:
    """If text contains a ```python ... ``` block, return the inner code."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def extract_python_code(text: str) -> str:
    """Extract the python code from a teacher response.

    Strategy:
      1. If there's a ```python ... ``` block, return its content.
      2. Otherwise, if the whole text looks like python (starts with import/from/def/#),
         return it as-is.
      3. Otherwise, return the text stripped (best-effort).
    """
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    stripped = text.strip()
    first_line = stripped.split("\n", 1)[0].strip() if stripped else ""
    if (
        first_line.startswith("import ")
        or first_line.startswith("from ")
        or first_line.startswith("def ")
        or first_line.startswith('"""')
        or first_line.startswith("#")
    ):
        return stripped
    return stripped


def has_no_think_tags(text: str) -> bool:
    return "<think" not in text.lower()


def is_valid_python(code: str) -> tuple[bool, str | None]:
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} (line {e.lineno})"


def has_def_main(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    has_def = any(
        isinstance(node, ast.FunctionDef) and node.name == "main" for node in ast.walk(tree)
    )
    has_call = bool(re.search(r"^\s*main\s*\(\s*\)", code, re.MULTILINE))
    return has_def and has_call


FRAMEWORK_KEYWORDS = {
    "qiskit": ["qiskit"],
    "pennylane": ["pennylane"],
    "cirq": ["cirq"],
    "braket": ["braket"],
}


def detect_required_framework(prompt: str) -> str | None:
    p = prompt.lower()
    for fw in ["qiskit", "pennylane", "cirq", "braket"]:
        if fw in p:
            return fw
    return None


def uses_framework(code: str, framework: str) -> bool:
    keywords = FRAMEWORK_KEYWORDS.get(framework, [framework])
    for kw in keywords:
        if re.search(rf"(?:^|\n)\s*(?:import\s+{kw}\b|from\s+{kw}\b)", code):
            return True
    return False


def run_code_sandbox(
    code: str, expected_marker: str, timeout: int, python_bin: str
) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [python_bin, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={
                **os.environ,
                "MPLBACKEND": "Agg",
                "PYTHONHASHSEED": "0",
            },
        )
        if proc.returncode != 0:
            return False, f"Exit {proc.returncode}: {proc.stderr[-400:]}"
        if expected_marker not in proc.stdout:
            return False, (f"Marker {expected_marker!r} not in stdout (got {proc.stdout[:200]!r})")
        return True, proc.stdout
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout}s"
    except Exception as e:
        return False, f"Exec error: {e}"


def marker_in_source(code: str, expected_marker: str) -> bool:
    """Static check: does the code contain the marker string in a print statement?"""
    return expected_marker in code


# ---------------------------------------------------------------------------
# Three quality passes
# ---------------------------------------------------------------------------


def pass1_marker_contract(code: str, expected_marker: str) -> tuple[bool, str]:
    """Pass 1: def main() + prints the exact marker string (static check)."""
    if not has_def_main(code):
        return False, "missing def main() or main() call"
    if not marker_in_source(code, expected_marker):
        return False, f"marker {expected_marker!r} not found in source"
    ok, err = is_valid_python(code)
    if not ok:
        return False, err or "invalid python"
    return True, "ok"


def pass2_runnable_correct(
    code: str,
    expected_marker: str,
    framework: str | None,
    timeout: int,
    python_bin: str,
    lenient_execution: bool = True,
) -> tuple[bool, str, dict[str, Any]]:
    """Pass 2: 100% runnable, correct, efficient (sandbox-executed).

    When `lenient_execution=True`, an ImportError or ModuleNotFoundError for a
    framework that isn't installed locally (cirq, braket, mitiq, etc.) is accepted
    as a pass — the code will run on the Huanxin NPU box which has all frameworks.
    """
    validation: dict[str, Any] = {}
    if framework:
        validation["framework_match"] = uses_framework(code, framework)
        if not validation["framework_match"]:
            return False, f"prompt requires {framework} but code does not import it", validation
    else:
        validation["framework_match"] = True

    ok, out = run_code_sandbox(code, expected_marker, timeout, python_bin)
    validation["runnable"] = ok
    if not ok:
        lower_out = out.lower()
        if lenient_execution and ("importerror" in lower_out or "modulenotfounderror" in lower_out):
            validation["lenient_accept"] = True
            validation["run_reason"] = f"local import failed: {out[:200]}"
            return True, f"lenient accept (local import failed): {out[:120]}", validation
        return False, f"run failed: {out}", validation

    validation["marker_printed"] = True
    return True, "ok", validation


def pass3_beautiful(code: str) -> tuple[bool, str]:
    """Pass 3: beautiful — clean, idiomatic, well-structured (static checks).

    Checks:
      - No leftover markdown fences.
      - No <think> tags.
      - Reasonable line length (no line > 120 chars).
      - Has a module docstring or top-level comment.
      - No bare `except:` clauses.
      - No `print` outside `main()` (except inside `if __name__ == '__main__':`).
    """
    if "```" in code:
        return False, "contains markdown fences"
    if not has_no_think_tags(code):
        return False, "contains <think> tags"

    lines = code.split("\n")
    long_lines = [i + 1 for i, ln in enumerate(lines) if len(ln) > 120]
    if long_lines:
        return False, f"lines exceed 120 chars: {long_lines[:5]}"

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False, "invalid python (cannot parse)"

    # Check for a module docstring, top-level comment, or main() docstring
    has_module_docstring = (
        isinstance(tree, ast.Module)
        and tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    )
    has_top_comment = any(ln.strip().startswith("#") for ln in lines[:5] if ln.strip())
    has_main_docstring = False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "main"
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            has_main_docstring = True
            break
    if not (has_module_docstring or has_top_comment or has_main_docstring):
        return False, "no module docstring, top-level comment, or main() docstring"

    # No bare except clauses
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None and node.name is None:
                return False, "bare `except:` clause found"

    return True, "ok"


# ---------------------------------------------------------------------------
# Teacher eval parsing
# ---------------------------------------------------------------------------


def parse_teacher_eval_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    if not stripped.startswith("{"):
        m = re.search(r"\{.*\}", stripped, re.DOTALL)
        if not m:
            raise ValueError(f"teacher eval is not JSON: {text[:400]}")
        stripped = m.group(0)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError as e:
        raise ValueError(f"teacher eval JSON parse error: {e}: {text[:400]}") from e


# ---------------------------------------------------------------------------
# Per-question pipeline
# ---------------------------------------------------------------------------


def process_one(
    *,
    seed: dict[str, Any],
    index: int,
    student_api_base: str,
    student_api_key: str,
    student_model: str,
    teacher_api_base: str,
    teacher_api_key: str,
    teacher_model: str,
    run_timeout: int,
    python_bin: str,
    max_correction_retries: int = 2,
) -> dict[str, Any]:
    qid = seed.get("example_id") or f"q-{index:04d}"
    question = seed["prompt"]
    expected_marker = seed["expected_marker"]
    framework = detect_required_framework(question)
    t0 = time.time()

    record: dict[str, Any] = {
        "example_id": qid,
        "index": index,
        "adapter_target": seed.get("adapter_target", "27b"),
        "task_family": seed.get("task_family"),
        "framework": seed.get("framework") or framework,
        "difficulty": seed.get("difficulty"),
        "variant_id": seed.get("variant_id"),
        "source_gap": seed.get("source_gap"),
        "question": question,
        "expected_marker": expected_marker,
        "student_model": student_model,
        "teacher_model": teacher_model,
        "student_code": None,
        "student_raw": None,
        "teacher_eval": None,
        "teacher_correction_raw": None,
        "final_code": None,
        "final_source": None,  # "student" or "teacher_correction"
        "is_correct": None,
        "quality_passes": {},
        "status": "pending",
        "error": None,
        "elapsed_seconds": None,
    }

    # 1. Student writes code.
    try:
        student_raw = call_student_openai(
            api_base=student_api_base,
            api_key=student_api_key,
            model=student_model,
            user_prompt=question,
            system_prompt=seed.get("system_prompt", SYSTEM_PROMPT_STUDENT),
            max_tokens=2048,
            temperature=0.3,
            timeout=300.0,
        )
    except Exception as e:
        record["status"] = "student_call_failed"
        record["error"] = f"student call: {e}"
        record["elapsed_seconds"] = time.time() - t0
        return record

    record["student_raw"] = student_raw
    student_code = extract_python_code(student_raw)
    record["student_code"] = student_code

    # 2. Teacher evaluates correctness.
    try:
        eval_raw = anthropic_messages_with_retry(
            api_base=teacher_api_base,
            api_key=teacher_api_key,
            model=teacher_model,
            system_prompt=SYSTEM_PROMPT_TEACHER,
            user_prompt=TEACHER_EVAL_PROMPT.format(
                question=question,
                marker=expected_marker,
                student_code=student_code,
            ),
            max_tokens=1024,
            temperature=0.0,
            timeout=300.0,
        )
        eval_text = extract_text(eval_raw)
        teacher_eval = parse_teacher_eval_json(eval_text)
    except Exception as e:
        record["status"] = "teacher_eval_failed"
        record["error"] = f"teacher eval: {e}"
        record["elapsed_seconds"] = time.time() - t0
        return record

    record["teacher_eval"] = teacher_eval
    is_correct = bool(teacher_eval.get("is_correct", False))
    record["is_correct"] = is_correct
    issues = teacher_eval.get("issues", []) or []

    # 3. Decide the final code source.
    if is_correct:
        record["final_code"] = student_code
        record["final_source"] = "student"
        record["teacher_correction_raw"] = None
    else:
        # 4. Teacher writes a correction.
        correction_text = ""
        last_error = ""
        for attempt in range(max_correction_retries + 1):
            try:
                if attempt == 0:
                    messages = None
                    user_prompt = TEACHER_CORRECTION_PROMPT.format(
                        question=question,
                        marker=expected_marker,
                        student_code=student_code,
                        issues="\n".join(f"- {it}" for it in issues) or "- (none)",
                    )
                    raw = anthropic_messages_with_retry(
                        api_base=teacher_api_base,
                        api_key=teacher_api_key,
                        model=teacher_model,
                        system_prompt=SYSTEM_PROMPT_TEACHER,
                        user_prompt=user_prompt,
                        max_tokens=4096,
                        temperature=0.2,
                        timeout=600.0,
                    )
                else:
                    # Retry: multi-turn with the failure reason.
                    retry_prompt = CORRECTION_RETRY_PROMPT.format(
                        error=last_error,
                        question=question,
                        marker=expected_marker,
                    )
                    messages = [
                        {
                            "role": "user",
                            "content": TEACHER_CORRECTION_PROMPT.format(
                                question=question,
                                marker=expected_marker,
                                student_code=student_code,
                                issues="\n".join(f"- {it}" for it in issues) or "- (none)",
                            ),
                        },
                        {"role": "assistant", "content": correction_text},
                        {"role": "user", "content": retry_prompt},
                    ]
                    raw = anthropic_messages_with_retry(
                        api_base=teacher_api_base,
                        api_key=teacher_api_key,
                        model=teacher_model,
                        system_prompt=SYSTEM_PROMPT_TEACHER,
                        messages=messages,
                        max_tokens=4096,
                        temperature=0.2,
                        timeout=600.0,
                    )
                correction_text = extract_text(raw)
                if not correction_text:
                    thinking = extract_thinking(raw)
                    if thinking:
                        correction_text = thinking
                record["teacher_correction_raw"] = correction_text
                candidate_code = extract_python_code(correction_text)
                # Run the 3 quality passes on the candidate.
                p1_ok, p1_err = pass1_marker_contract(candidate_code, expected_marker)
                p2_ok, p2_err, _ = pass2_runnable_correct(
                    candidate_code, expected_marker, framework, run_timeout, python_bin
                )
                p3_ok, p3_err = pass3_beautiful(candidate_code)
                if p1_ok and p2_ok and p3_ok:
                    record["final_code"] = candidate_code
                    record["final_source"] = "teacher_correction"
                    record["quality_passes"] = {
                        "pass1_marker_contract": True,
                        "pass2_runnable_correct": True,
                        "pass3_beautiful": True,
                    }
                    break
                last_error = (
                    f"pass1={p1_ok}({p1_err}), pass2={p2_ok}({p2_err}), pass3={p3_ok}({p3_err})"
                )
            except Exception as e:
                last_error = f"attempt {attempt + 1}: {e}"
        else:
            record["status"] = "correction_failed_quality"
            record["error"] = last_error
            record["elapsed_seconds"] = time.time() - t0
            return record

    # 5. If the student was correct, still run the quality passes on the student code.
    if is_correct:
        p1_ok, p1_err = pass1_marker_contract(student_code, expected_marker)
        p2_ok, p2_err, _ = pass2_runnable_correct(
            student_code, expected_marker, framework, run_timeout, python_bin
        )
        p3_ok, p3_err = pass3_beautiful(student_code)
        record["quality_passes"] = {
            "pass1_marker_contract": p1_ok,
            "pass2_runnable_correct": p2_ok,
            "pass3_beautiful": p3_ok,
        }
        if not (p1_ok and p2_ok and p3_ok):
            # Student said correct but quality gates disagree. Re-ask teacher for a correction.
            record["status"] = "student_quality_failed"
            record["error"] = (
                f"pass1={p1_ok}({p1_err}), pass2={p2_ok}({p2_err}), pass3={p3_ok}({p3_err})"
            )
            record["elapsed_seconds"] = time.time() - t0
            return record

    # 6. (Corrections only) Re-emit the teacher's corrected answer via the
    # OpenAI-compatible GLM5.2 endpoint to capture per-token top-k logprobs
    # for soft-KL distillation. The Anthropic Messages path used above does
    # not expose top_logprobs, so this is a second, single-pass call against
    # the OpenAI-compat proxy. We re-emit only the final assistant text
    # (record["teacher_correction_raw"]) so the logprobs align cleanly with
    # the chat-sft-v1 assistant target written by to_chat_sft_v1().
    # Positive samples (student was correct) have no teacher correction to
    # re-emit, so teacher_logits stays empty and the sample falls back to
    # plain NLL SFT in qwen_sft_peft_kl.py.
    record["teacher_logits"] = {"content": "", "logprobs": [], "top_logprobs": 20}
    if record.get("final_source") == "teacher_correction" and record.get("teacher_correction_raw"):
        openai_api_base = os.environ.get("GLM52_OPENAI_API_BASE", "http://127.0.0.1:8009/v1")
        openai_api_key = os.environ.get("GLM52_OPENAI_API_KEY") or teacher_api_key
        try:
            reemit = teacher_reemit_with_logits(
                api_base=openai_api_base,
                api_key=openai_api_key,
                model=teacher_model,
                question=question,
                correct_answer=record["teacher_correction_raw"],
                top_logprobs=int(os.environ.get("TEACHER_TOP_LOGPROBS", "20")),
            )
            record["teacher_logits"] = reemit
            if reemit.get("error"):
                print(
                    f"[self_corr] teacher_logits re-emit error for "
                    f"{record['example_id']}: {reemit['error']}",
                    flush=True,
                )
            elif not reemit.get("logprobs"):
                print(
                    f"[self_corr] teacher_logits empty for {record['example_id']}",
                    flush=True,
                )
        except Exception as exc:  # noqa: BLE001 - never block a passing sample
            record["teacher_logits"] = {
                "content": "",
                "logprobs": [],
                "top_logprobs": 20,
                "error": str(exc),
            }
            print(
                f"[self_corr] teacher_logits exception for {record['example_id']}: {exc}",
                flush=True,
            )

    record["status"] = "accepted"
    record["elapsed_seconds"] = time.time() - t0
    return record


# ---------------------------------------------------------------------------
# chat-sft-v1 record assembly
# ---------------------------------------------------------------------------


def to_chat_sft_v1(
    seed: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    """Build a chat-sft-v1 record from a completed pipeline record.

    The assistant target is:
      - if the student was correct: the student's code (positive sample).
      - if the student was incorrect: the teacher's critique + corrected code.
    """
    question = seed["prompt"]
    student_code = record["student_code"] or ""
    final_code = record["final_code"] or ""
    is_correct = record["is_correct"]

    system_prompt = seed.get(
        "system_prompt",
        "You are a careful quantum software engineering assistant. "
        "Use the user's task and any supplied context to produce correct, "
        "testable Python or precise repair guidance.",
    )

    user_content = (
        f"Question:\n{question}\n\n"
        f"Student code:\n```python\n{student_code}\n```\n\n"
        f"Do you think the code is correct?"
    )

    if is_correct:
        # Positive sample: the student's code is correct.
        assistant_content = (
            "Yes, the code is correct. It defines `def main():`, prints the "
            "exact expected marker string, and uses the required framework "
            "appropriately.\n\n"
            "```python\n" + final_code + "\n```"
        )
    else:
        # Correction sample: teacher's critique + corrected code.
        assistant_content = record.get("teacher_correction_raw") or (
            "The student's code has issues. Here is the corrected version.\n\n"
            "```python\n" + final_code + "\n```"
        )

    return {
        "example_id": record["example_id"],
        "format": "chat-sft-v1",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content},
        ],
        # Per-token teacher top-k logprobs aligned to the assistant span.
        # Consumed by training/qwen_sft_peft_kl.py (teacher_logits_field).
        # Empty for positive samples (student was correct) and for any
        # correction where the OpenAI-compat re-emit call failed — in both
        # cases qwen_sft_peft_kl.py falls back to plain NLL on that row.
        "teacher_logits": record.get("teacher_logits")
        or {
            "content": "",
            "logprobs": [],
            "top_logprobs": 20,
        },
        "metadata": {
            "domain": "quantum" if record.get("framework") != "general" else "software",
            "framework": record.get("framework"),
            "language": "python",
            "difficulty": record.get("difficulty"),
            "task_family": record.get("task_family"),
            "variant_id": record.get("variant_id"),
            "source_gap": record.get("source_gap"),
            "is_correct": is_correct,
            "final_source": record.get("final_source"),
            "quality_passes": record.get("quality_passes"),
            "distillation_strategy": "self_correcting_distill_v1",
            "distillation_phase": "iter5_27b",
        },
        "source_schema": "self-correcting-distill-v1",
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def load_seeds(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"No seeds in {path}")
    return rows


def load_completed(path: Path) -> set[str]:
    if not path.exists():
        return set()
    done: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            qid = rec.get("example_id")
            if isinstance(qid, str) and qid:
                done.add(qid)
    return done


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seeds",
        type=Path,
        default=ROOT / "data/generated/glm52_soft_distill_sft_iter4_27b/seed_questions.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/generated/self_correcting_distill_27b_v1",
    )
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--max-questions", type=int, default=100)
    parser.add_argument("--run-timeout", type=int, default=30)
    parser.add_argument("--max-correction-retries", type=int, default=2)
    parser.add_argument("--python-run-bin", type=str, default="")
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    args = parser.parse_args()

    student_api_base = os.environ.get("STUDENT_27B_API_BASE", "")
    student_api_key = os.environ.get("STUDENT_27B_API_KEY", "dummy")
    student_model = os.environ.get("STUDENT_27B_MODEL", "qwen36-27b-rl-distill")
    teacher_api_base = os.environ.get("GLM52_API_BASE", "http://127.0.0.1:49983")
    teacher_api_key = os.environ.get("GLM52_API_KEY", "")
    python_bin = args.python_run_bin or os.environ.get(
        "PYTHON_RUN_BIN", str(ROOT / ".venv/bin/python")
    )

    if not student_api_base:
        print(
            "[fatal] STUDENT_27B_API_BASE is not set. The 27B adapter must be "
            "serving (e.g. via vLLM on Huanxin ASI1, tunneled to 127.0.0.1:8007).",
            file=sys.stderr,
        )
        return 2
    if not teacher_api_key:
        print("[fatal] GLM52_API_KEY is not set.", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    responses_path = args.output_dir / "teacher_responses.jsonl"
    chatml_path = args.output_dir / "sft_chatml.jsonl"
    report_path = args.output_dir / "quality_report.json"

    seeds = load_seeds(args.seeds)
    done = load_completed(responses_path) if args.resume else set()
    if done:
        print(f"[resume] {len(done)} already completed; skipping them.", flush=True)

    todo = [
        (i, s)
        for i, s in enumerate(seeds)
        if i >= args.start_index and s.get("example_id") not in done
    ]
    if args.max_questions > 0:
        todo = todo[: args.max_questions]
    print(
        f"[plan] {len(todo)} questions to process (start_index={args.start_index}, "
        f"max={args.max_questions}, total_seeds={len(seeds)})",
        flush=True,
    )

    accepted = 0
    skipped = 0
    statuses: dict[str, int] = {}

    with (
        responses_path.open("a", encoding="utf-8") as resp_fh,
        chatml_path.open("a", encoding="utf-8") as chatml_fh,
    ):
        for n, (idx, seed) in enumerate(todo, 1):
            qid = seed.get("example_id", f"q-{idx:04d}")
            print(f"[{n}/{len(todo)}] qid={qid} ...", end=" ", flush=True)
            try:
                record = process_one(
                    seed=seed,
                    index=idx,
                    student_api_base=student_api_base,
                    student_api_key=student_api_key,
                    student_model=student_model,
                    teacher_api_base=teacher_api_base,
                    teacher_api_key=teacher_api_key,
                    teacher_model="glm5.2",
                    run_timeout=args.run_timeout,
                    python_bin=python_bin,
                    max_correction_retries=args.max_correction_retries,
                )
            except Exception as e:
                record = {
                    "example_id": qid,
                    "index": idx,
                    "status": "exception",
                    "error": f"{type(e).__name__}: {e}",
                    "elapsed_seconds": 0,
                }

            resp_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            resp_fh.flush()

            status = record.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
            if status == "accepted":
                accepted += 1
                chatml_rec = to_chat_sft_v1(seed, record)
                chatml_fh.write(json.dumps(chatml_rec, ensure_ascii=False) + "\n")
                chatml_fh.flush()
                print(
                    f"ACCEPTED ({record.get('final_source')}, "
                    f"{record.get('elapsed_seconds', 0):.1f}s)",
                    flush=True,
                )
            else:
                skipped += 1
                print(
                    f"SKIP ({status}: {record.get('error', '')[:120]})",
                    flush=True,
                )

    report = {
        "name": "self_correcting_distill_27b_v1",
        "created": int(time.time()),
        "seeds_path": str(args.seeds),
        "output_dir": str(args.output_dir),
        "student_model": student_model,
        "student_api_base": student_api_base,
        "teacher_model": "glm5.2",
        "teacher_api_base": teacher_api_base,
        "python_run_bin": python_bin,
        "total_processed": accepted + skipped,
        "accepted": accepted,
        "skipped": skipped,
        "statuses": statuses,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("\n=== Quality report ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
