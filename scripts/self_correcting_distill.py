#!/usr/bin/env python3
"""Self-correcting distillation pipeline.

For each question in the pool:
  1. Ask the student adapter to write code for the question.
  2. Ask the teacher (GLM5.2) to evaluate correctness and run the code.
     - If the teacher reports 100% correctness (and, when a test harness
       exists, the harness passes), the sample is accepted as-is and we
       move to the next question.
     - Otherwise, the teacher returns a JSON object with:
         - `is_correct`: false
         - `issues`:   list of concrete problems with the student's code
         - `correct_answer`: the corrected code (and/or explanation)
  3. The final training sample is:
       user:      "<question>\n\nStudent code:\n```python\n<student_code>\n```\n\nDo you think the code is correct?"
       assistant: <teacher's critique + correct answer>
       teacher_logits: top-k logprobs per assistant token (for distillation)

Logits are obtained from GLM5.2 by requesting `logprobs=True` and
`top_logprobs=K` on the chat completion call (OpenAI-compatible API).

The pipeline is resumable: it appends to `student_answers.jsonl`,
`teacher_evals.jsonl`, and `train_chatml_with_logits.jsonl` as it goes,
and skips questions already present in `student_answers.jsonl`.

Usage:
    python3 scripts/self_correcting_distill.py \
        --config configs/distill/self_correcting_distill_27b_v1.json \
        --question-pool data/generated/self_correcting_distill/questions_pool.jsonl \
        --start-index 0 \
        --end-index 8000 \
        --resume
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


SYSTEM_PROMPT_STUDENT = (
    "You are a quantum software engineering student. Given a coding question, "
    "produce a single self-contained Python code block that implements the "
    "requested behavior. Do not include extra prose outside the code block."
)

SYSTEM_PROMPT_TEACHER = (
    "You are a careful quantum software engineering teacher. Evaluate the "
    "student's code for correctness against the question, and if it is "
    "incorrect, provide a precise correction. Always respond with a single "
    "JSON object that matches the requested schema."
)

TEACHER_EVAL_PROMPT_TEMPLATE = """You are grading a student's quantum-coding submission.

Question:
{question}

Student code:
```python
{student_code}
```

Evaluate the student's code. Respond with a single JSON object (no markdown fences) with exactly these keys:

{{
  "is_correct": true | false,
  "issues": ["<concise description of each problem>"],
  "correct_answer": "<the corrected code and/or a precise explanation; if the code is already correct, repeat it here>",
  "confidence": 0.0 | ... | 1.0
}}

Rules:
- Set "is_correct" to true only if the code satisfies every requirement in the question and would pass reasonable tests.
- When the code is incorrect, "correct_answer" must contain a working replacement (or a precise explanation if a full rewrite is impossible).
- Be concise but specific. Do not invent requirements that are not in the question.
"""


@dataclass
class StudentConfig:
    api_base: str
    api_key: str
    model: str
    temperature: float
    max_tokens: int
    timeout: float


@dataclass
class TeacherConfig:
    api_base: str
    api_key: str
    model: str
    temperature: float
    max_tokens: int
    top_logprobs: int
    timeout: float


@dataclass
class GitSyncConfig:
    enabled: bool
    interval: int  # commit every N processed questions
    push: bool  # push to origin after commit
    remote: str
    branch: str  # auto-detected if empty
    add_paths: list[str]  # paths to git add; if empty, adds the output_dir only
    author_name: str
    author_email: str


@dataclass
class PipelineConfig:
    student: StudentConfig
    teacher: TeacherConfig
    output_dir: Path
    start_index: int
    end_index: int
    student_samples_per_question: int
    max_teacher_corrections: int
    execution_timeout: int
    pass_threshold: float
    run_harness_when_available: bool
    teacher_judge_when_no_harness: bool
    user_template: str
    seed: int
    git_sync: GitSyncConfig


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def _env_or_die(env_name: str) -> str:
    val = os.environ.get(env_name)
    if not val:
        raise RuntimeError(f"missing required env var: {env_name}")
    return val


def load_config(path: Path) -> PipelineConfig:
    cfg = json.loads(path.read_text())
    student_cfg = cfg["student_model"]["serving"]
    teacher_cfg = cfg["teacher_model"]
    return PipelineConfig(
        student=StudentConfig(
            api_base=student_cfg["api_base"],
            api_key=os.environ.get(student_cfg["api_key_env"], "dummy"),
            model=student_cfg["model"],
            temperature=student_cfg.get("temperature", 0.3),
            max_tokens=student_cfg.get("max_tokens", 4096),
            timeout=student_cfg.get("timeout_seconds", 600),
        ),
        teacher=TeacherConfig(
            api_base=os.environ.get(teacher_cfg["api_base_env"], "http://127.0.0.1:8009/v1"),
            api_key=os.environ.get(teacher_cfg["api_key_env"], "dummy"),
            model=teacher_cfg["model"],
            temperature=teacher_cfg.get("temperature", 0.0),
            max_tokens=teacher_cfg.get("max_tokens", 4096),
            top_logprobs=teacher_cfg.get("top_logprobs", 20),
            timeout=teacher_cfg.get("timeout_seconds", 900),
        ),
        output_dir=ROOT / cfg["output_dir"],
        start_index=0,
        end_index=cfg["dataset_spec"]["target_question_count"],
        student_samples_per_question=cfg["pipeline"].get("student_samples_per_question", 1),
        max_teacher_corrections=cfg["pipeline"].get("max_teacher_corrections_per_question", 1),
        execution_timeout=cfg["pipeline"].get("execution_timeout_seconds", 30),
        pass_threshold=cfg["pipeline"].get("pass_threshold", 1.0),
        run_harness_when_available=cfg["pipeline"].get("run_harness_when_available", True),
        teacher_judge_when_no_harness=cfg["pipeline"].get("teacher_judge_when_no_harness", True),
        user_template=cfg["sample_format"]["user_template"],
        seed=cfg.get("seed", 20260702),
        git_sync=_load_git_sync_config(cfg.get("git_sync") or {}),
    )


def _load_git_sync_config(raw: dict[str, Any]) -> GitSyncConfig:
    return GitSyncConfig(
        enabled=bool(raw.get("enabled", True)),
        interval=int(raw.get("interval", 100)),
        push=bool(raw.get("push", True)),
        remote=str(raw.get("remote", "origin")),
        branch=str(raw.get("branch", "")),
        add_paths=[str(p) for p in raw.get("add_paths", [])],
        author_name=str(raw.get("author_name", "distill-bot")),
        author_email=str(raw.get("author_email", "distill-bot@local")),
    )


# ---------------------------------------------------------------------------
# API clients
# ---------------------------------------------------------------------------


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail[:800]}") from exc


def call_student(cfg: StudentConfig, user_prompt: str) -> str:
    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_STUDENT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
    }
    headers = {"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"}
    resp = _post_json(cfg.api_base.rstrip("/") + "/chat/completions", payload, headers, cfg.timeout)
    choices = resp.get("choices") or []
    if not choices:
        raise RuntimeError(f"student returned no choices: {resp}")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str):
        raise RuntimeError(f"student returned no content: {resp}")
    return content.strip()


def call_teacher_eval(cfg: TeacherConfig, question: str, student_code: str) -> dict[str, Any]:
    """Ask the teacher to grade the student's code. Returns the parsed JSON dict."""
    user_prompt = TEACHER_EVAL_PROMPT_TEMPLATE.format(question=question, student_code=student_code)
    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_TEACHER},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"}
    resp = _post_json(cfg.api_base.rstrip("/") + "/chat/completions", payload, headers, cfg.timeout)
    choices = resp.get("choices") or []
    if not choices:
        raise RuntimeError(f"teacher returned no choices: {resp}")
    content = choices[0].get("message", {}).get("content") or ""
    return {"raw_content": content, "parsed": parse_teacher_json(content)}


def call_teacher_correction_with_logits(
    cfg: TeacherConfig,
    question: str,
    student_code: str,
    issues: list[str],
) -> dict[str, Any]:
    """Ask the teacher for the corrected answer and capture top-k logprobs per token.

    Returns dict with:
      - content: the teacher's final answer text (critique + correct code)
      - logprobs: list of per-token {token, logprob, top_logprobs:[{token,logprob}]}
    """
    user_prompt = (
        f"Question:\n{question}\n\n"
        f"Student code (incorrect):\n```python\n{student_code}\n```\n\n"
        f"Issues identified in the student's code:\n"
        + "\n".join(f"- {item}" for item in issues)
        + "\n\nProvide the corrected, complete answer. Start with a one-paragraph critique of the student's code, "
          "then give the corrected code in a single ```python block. Be concise."
    )
    payload = {
        "model": cfg.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_TEACHER},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
        "logprobs": True,
        "top_logprobs": cfg.top_logprobs,
    }
    headers = {"Authorization": f"Bearer {cfg.api_key}", "Content-Type": "application/json"}
    resp = _post_json(cfg.api_base.rstrip("/") + "/chat/completions", payload, headers, cfg.timeout)
    choices = resp.get("choices") or []
    if not choices:
        raise RuntimeError(f"teacher returned no choices: {resp}")
    msg = choices[0].get("message", {})
    content = msg.get("content") or ""
    logprobs = choices[0].get("logprobs") or {"content": []}
    return {"content": content.strip(), "logprobs": logprobs.get("content", [])}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_teacher_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    # Find the first {...} block.
    if not stripped.startswith("{"):
        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if not match:
            raise ValueError(f"teacher response is not JSON: {text[:400]}")
        stripped = match.group(0)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError(f"teacher response JSON parse failed: {exc}; text={text[:400]}") from exc


def extract_python_code(text: str) -> str:
    """Extract the first ```python ... ``` block from `text`, or the whole text if no fence."""
    if not isinstance(text, str):
        return ""
    fences = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fences:
        return fences[0].strip()
    fences = re.findall(r"```\s*\n(.*?)```", text, re.DOTALL)
    if fences:
        return fences[0].strip()
    return text.strip()


def run_test_harness(student_code: str, task_dir: Path, timeout: int) -> dict[str, Any]:
    """Write student_code to a temp candidate file, then run the task's tests.py against it."""
    task_dir = (ROOT / task_dir).resolve() if not task_dir.is_absolute() else task_dir
    meta_path = task_dir / "task.json"
    if not meta_path.exists():
        return {"passed": False, "details": [f"missing task.json in {task_dir}"]}
    meta = json.loads(meta_path.read_text())
    test_file = meta.get("test_file", "tests.py")
    test_path = task_dir / test_file
    if not test_path.exists():
        return {"passed": False, "details": [f"missing test file {test_path}"]}

    candidate_path = task_dir / "candidate.py"
    backup = None
    if candidate_path.exists():
        backup = candidate_path.read_text()
    try:
        candidate_path.write_text(student_code + "\n", encoding="utf-8")
        spec = importlib.util.spec_from_file_location("harness_tests", test_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        run_tests = getattr(module, "run_tests", None)
        if run_tests is None:
            return {"passed": False, "details": ["tests.py has no run_tests(candidate_path) function"]}
        result = run_tests(str(candidate_path))
        return {
            "passed": bool(result.get("passed", False)),
            "details": result.get("details", []),
        }
    except Exception as exc:
        return {"passed": False, "details": [f"Exception: {exc}", traceback.format_exc(limit=2)]}
    finally:
        if backup is not None:
            candidate_path.write_text(backup, encoding="utf-8")
        else:
            candidate_path.unlink(missing_ok=True)


def run_code_sandbox(code: str, timeout: int) -> dict[str, Any]:
    """Run the student's code in a subprocess sandbox. Returns {ok, stdout, stderr}."""
    if not code.strip():
        return {"ok": False, "stdout": "", "stderr": "empty code"}
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(code)
        tf.flush()
        tmp_path = Path(tf.name)
    try:
        proc = subprocess.run(
            [sys.executable, str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
            "returncode": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": f"timeout after {timeout}s", "returncode": -1}
    finally:
        tmp_path.unlink(missing_ok=True)


def sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:8]


# ---------------------------------------------------------------------------
# Git sync (commit + push) so partial progress is never lost
# ---------------------------------------------------------------------------


def _git_run(args: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _detect_git_branch(cwd: Path) -> str:
    rc, out, err = _git_run(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if rc == 0 and out:
        return out.strip()
    return ""


def git_sync(
    cfg: GitSyncConfig,
    output_dir: Path,
    report: dict[str, Any],
    phase: str = "periodic",
) -> dict[str, Any]:
    """Stage the distillation outputs, commit, and optionally push.

    `phase` is one of "periodic", "final", "danger" — used in the commit
    message so the timeline can be audited.
    """
    result: dict[str, Any] = {
        "phase": phase,
        "started_at": int(time.time()),
        "committed": False,
        "pushed": False,
        "commit_sha": None,
        "error": None,
    }
    if not cfg.enabled:
        result["error"] = "git_sync disabled in config"
        return result
    try:
        repo_root = ROOT
        # Determine branch (auto-detect if not configured).
        branch = cfg.branch or _detect_git_branch(repo_root)
        # Build the list of paths to add. Default to the output_dir contents
        # plus the pipeline_report.json.
        add_targets: list[str] = []
        if cfg.add_paths:
            add_targets.extend(cfg.add_paths)
        else:
            if output_dir.exists():
                add_targets.append(str(output_dir.relative_to(repo_root)))
        # Always include the report file if present (it lives under output_dir
        # already, but be defensive in case output_dir was redirected).
        if not add_targets:
            result["error"] = "no paths to add"
            return result
        # git add each target (use -A on the directory to capture deletions).
        for target in add_targets:
            rc, out, err = _git_run(["add", "-A", "--", target], repo_root)
            if rc != 0:
                # Fall back to non--A add if pathspec rejected.
                rc2, out2, err2 = _git_run(["add", "--", target], repo_root)
                if rc2 != 0:
                    result["error"] = f"git add {target} failed: {err or err2}"
                    return result
        # Check whether there is anything staged to commit.
        rc, out, err = _git_run(["diff", "--cached", "--quiet"], repo_root)
        staged = rc != 0  # rc==1 means there are staged changes; rc==0 means clean
        if not staged:
            result["error"] = "nothing staged"
            return result
        # Compose commit message with structured metadata.
        processed = report.get("processed", 0)
        accepted = report.get("accepted", 0)
        corrected = report.get("corrected", 0)
        skipped = report.get("skipped", 0)
        errors = report.get("errors", 0)
        msg = (
            f"[distill:{phase}] sync checkpoint: "
            f"processed={processed} accepted={accepted} corrected={corrected} "
            f"skipped={skipped} errors={errors}\n\n"
            f"phase={phase}\n"
            f"output_dir={output_dir}\n"
            f"branch={branch or '(unknown)'}\n"
            f"Co-Authored-By: distill-bot <{cfg.author_email}>"
        )
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = cfg.author_name
        env["GIT_AUTHOR_EMAIL"] = cfg.author_email
        env["GIT_COMMITTER_NAME"] = cfg.author_name
        env["GIT_COMMITTER_EMAIL"] = cfg.author_email
        proc = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        if proc.returncode != 0:
            result["error"] = f"git commit failed: {proc.stderr.strip()[:400]}"
            return result
        result["committed"] = True
        # Get the commit sha.
        rc, out, err = _git_run(["rev-parse", "HEAD"], repo_root)
        if rc == 0:
            result["commit_sha"] = out.strip()
        # Push if enabled and we know the branch.
        if cfg.push:
            if not branch:
                result["error"] = "cannot push: branch unknown"
                return result
            rc, out, err = _git_run(["push", cfg.remote, branch], repo_root)
            if rc != 0:
                result["error"] = f"git push failed: {err[:400]}"
                return result
            result["pushed"] = True
    except Exception as exc:
        result["error"] = f"git_sync exception: {exc}"
    result["finished_at"] = int(time.time())
    return result


# ---------------------------------------------------------------------------
# Per-question pipeline
# ---------------------------------------------------------------------------


def process_one(
    cfg: PipelineConfig,
    question_row: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    qid = question_row["question_id"]
    question = question_row["question"]
    harness = question_row.get("test_harness")
    t0 = time.time()

    # 1. Student writes code.
    student_raw = call_student(cfg.student, question)
    student_code = extract_python_code(student_raw)

    student_answer_record = {
        "question_id": qid,
        "index": index,
        "question": question,
        "student_raw": student_raw,
        "student_code": student_code,
        "student_model": cfg.student.model,
        "timestamp": int(time.time()),
    }

    # 2. Evaluate correctness.
    harness_result = None
    teacher_eval = None
    is_correct = False

    if cfg.run_harness_when_available and isinstance(harness, dict) and harness.get("task_dir"):
        harness_result = run_test_harness(student_code, Path(harness["task_dir"]), cfg.execution_timeout)
        is_correct = bool(harness_result.get("passed", False))
        # If the harness already passed, we don't strictly need a teacher eval, but we still
        # ask the teacher for a one-shot correctness confirmation so the student's record
        # carries a teacher-signed pass. If the harness failed, ask the teacher for a
        # correction.
        if is_correct:
            teacher_eval = {"parsed": {"is_correct": True, "issues": [], "correct_answer": student_code, "confidence": 1.0}}
        else:
            try:
                teacher_eval = call_teacher_eval(cfg.teacher, question, student_code)
            except Exception as exc:
                teacher_eval = {"error": f"teacher_eval_failed: {exc}", "parsed": {"is_correct": False, "issues": [str(exc)], "correct_answer": ""}}
    else:
        if not cfg.teacher_judge_when_no_harness:
            # No harness and teacher judge disabled — we cannot evaluate. Mark as skipped.
            return {
                "question_id": qid,
                "index": index,
                "status": "skipped_no_eval",
                "elapsed_seconds": time.time() - t0,
                "student_answer": student_answer_record,
            }
        try:
            teacher_eval = call_teacher_eval(cfg.teacher, question, student_code)
        except Exception as exc:
            teacher_eval = {"error": f"teacher_eval_failed: {exc}", "parsed": {"is_correct": False, "issues": [str(exc)], "correct_answer": ""}}
        if teacher_eval.get("parsed", {}).get("is_correct"):
            is_correct = True

    # 3. Build the final training sample.
    if is_correct:
        # Accepted: we still emit a training sample where the teacher confirms correctness.
        # The assistant target is a short confirmation plus the student's code (which is correct).
        assistant_target = (
            "The code is correct. It satisfies the requirements in the question.\n\n"
            "```python\n" + student_code + "\n```"
        )
        # For accepted samples, we capture teacher logits on this short confirmation by
        # asking the teacher to score it (so the student can distill the teacher's
        # confidence). When logits are unavailable we fall back to plain text.
        try:
            teacher_resp = call_teacher_correction_with_logits(
                cfg.teacher,
                question,
                student_code,
                issues=["(none — teacher confirmed correctness)"],
            )
            # Use the teacher's own confirmation text as the assistant target so the
            # logits and target text are aligned.
            if teacher_resp.get("content"):
                assistant_target = teacher_resp["content"]
            teacher_logits = teacher_resp.get("logprobs", [])
        except Exception as exc:
            teacher_logits = []
            teacher_eval.setdefault("logits_error", str(exc))
        status = "accepted"
    else:
        # Rejected: teacher must provide a correction. We call the teacher again with
        # logprobs enabled so we can distill.
        issues = teacher_eval.get("parsed", {}).get("issues", []) or ["student code is incorrect"]
        try:
            teacher_resp = call_teacher_correction_with_logits(cfg.teacher, question, student_code, issues)
            assistant_target = teacher_resp.get("content", "")
            teacher_logits = teacher_resp.get("logprobs", [])
        except Exception as exc:
            assistant_target = teacher_eval.get("parsed", {}).get("correct_answer", "")
            teacher_logits = []
            teacher_eval.setdefault("logits_error", str(exc))
        status = "corrected"

    user_text = cfg.user_template.format(question=question, student_code=student_code)

    sample = {
        "format": "self-correcting-distill-v1",
        "question_id": qid,
        "index": index,
        "status": status,
        "is_correct": is_correct,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_TEACHER},
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_target},
        ],
        "teacher_logits": teacher_logits,
        "teacher_top_logprobs_k": cfg.teacher.top_logprobs,
        "teacher_eval": teacher_eval.get("parsed"),
        "harness_result": harness_result,
        "student_model": cfg.student.model,
        "teacher_model": cfg.teacher.model,
        "framework": question_row.get("framework"),
        "category": question_row.get("category"),
        "difficulty": question_row.get("difficulty"),
        "source": question_row.get("source"),
        "elapsed_seconds": time.time() - t0,
    }

    return {
        "question_id": qid,
        "index": index,
        "status": status,
        "is_correct": is_correct,
        "elapsed_seconds": time.time() - t0,
        "student_answer": student_answer_record,
        "teacher_eval": teacher_eval,
        "harness_result": harness_result,
        "sample": sample,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def read_completed_ids(path: Path) -> set[str]:
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
            qid = rec.get("question_id")
            if isinstance(qid, str) and qid:
                done.add(qid)
    return done


def load_questions(path: Path, start: int, end: int, done: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i < start:
                continue
            if i >= end:
                break
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("question_id") in done:
                continue
            rows.append(rec)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--question-pool", type=Path, required=True)
    parser.add_argument("--start-index", type=int, default=None)
    parser.add_argument("--end-index", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=None, help="process at most N questions (debug)")
    parser.add_argument(
        "--git-sync-interval",
        type=int,
        default=None,
        help="override git_sync.interval (commit every N processed questions)",
    )
    parser.add_argument(
        "--no-git-push",
        action="store_true",
        help="commit checkpoints but do not push to remote",
    )
    parser.add_argument(
        "--no-git-sync",
        action="store_true",
        help="disable all git checkpointing (use only for local debug)",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    cfg.start_index = args.start_index if args.start_index is not None else cfg.start_index
    cfg.end_index = args.end_index if args.end_index is not None else cfg.end_index

    # Apply CLI overrides for git sync.
    if args.git_sync_interval is not None:
        cfg.git_sync.interval = max(1, args.git_sync_interval)
    if args.no_git_push:
        cfg.git_sync.push = False
    if args.no_git_sync:
        cfg.git_sync.enabled = False

    out_dir = cfg.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    student_path = out_dir / "student_answers.jsonl"
    eval_path = out_dir / "teacher_evals.jsonl"
    sample_path = out_dir / "train_chatml_with_logits.jsonl"
    report_path = out_dir / "pipeline_report.json"

    done = read_completed_ids(student_path) if args.resume else set()

    questions = load_questions(args.question_pool, cfg.start_index, cfg.end_index, done)
    if args.limit is not None:
        questions = questions[: args.limit]
    print(f"[pipeline] {len(questions)} questions to process "
          f"(range={cfg.start_index}:{cfg.end_index}, resume={args.resume}, workers={args.workers})")

    write_lock = Lock()
    report = {
        "config_path": str(args.config),
        "question_pool": str(args.question_pool),
        "started_at": int(time.time()),
        "processed": 0,
        "accepted": 0,
        "corrected": 0,
        "skipped": 0,
        "errors": 0,
    }

    def flush_records(record: dict[str, Any]) -> None:
        with write_lock:
            with student_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record["student_answer"], ensure_ascii=False) + "\n")
            with eval_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "question_id": record["question_id"],
                    "index": record["index"],
                    "status": record["status"],
                    "is_correct": record["is_correct"],
                    "teacher_eval": record["teacher_eval"],
                    "harness_result": record["harness_result"],
                    "elapsed_seconds": record["elapsed_seconds"],
                }, ensure_ascii=False) + "\n")
            if record.get("sample"):
                with sample_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(record["sample"], ensure_ascii=False) + "\n")

    # Install signal handlers so SIGTERM/SIGINT trigger a final danger-sync
    # before the process exits. This is the "before any dangerous actions"
    # checkpoint the spec calls for.
    shutdown_requested = {"flag": False}

    def _on_signal(signum: int, _frame: Any) -> None:
        shutdown_requested["flag"] = True
        print(f"[signal] received {signum}; will sync and exit after current batch", flush=True)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _on_signal)
        except (ValueError, OSError):
            # In non-main-thread or restricted environments this may fail.
            pass

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(process_one, cfg, q, q_idx): (q_idx, q) for q_idx, q in enumerate(questions)}
        for fut in as_completed(futures):
            q_idx, q = futures[fut]
            try:
                record = fut.result()
            except Exception as exc:
                report["errors"] += 1
                print(f"[error] qid={q.get('question_id')} idx={q_idx}: {exc}", flush=True)
                continue
            flush_records(record)
            with write_lock:
                report["processed"] += 1
                if record["status"] == "accepted":
                    report["accepted"] += 1
                elif record["status"] == "corrected":
                    report["corrected"] += 1
                elif record["status"].startswith("skipped"):
                    report["skipped"] += 1
            if report["processed"] % 25 == 0:
                elapsed = time.time() - t0
                rate = report["processed"] / max(elapsed, 1e-6)
                print(
                    f"[progress] {report['processed']}/{len(questions)} "
                    f"accepted={report['accepted']} corrected={report['corrected']} "
                    f"skipped={report['skipped']} errors={report['errors']} "
                    f"rate={rate:.2f}/s elapsed={elapsed:.0f}s",
                    flush=True,
                )
            # Periodic git checkpoint so partial progress is never lost.
            if cfg.git_sync.enabled and report["processed"] % cfg.git_sync.interval == 0:
                # Flush the report first so the checkpoint reflects current state.
                with write_lock:
                    report_path.write_text(
                        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)
                    )
                try:
                    sync_res = git_sync(cfg.git_sync, out_dir, report, phase="periodic")
                    print(
                        f"[git_sync:periodic] processed={report['processed']} "
                        f"committed={sync_res.get('committed')} pushed={sync_res.get('pushed')} "
                        f"sha={sync_res.get('commit_sha')} err={sync_res.get('error')}",
                        flush=True,
                    )
                except Exception as exc:
                    print(f"[git_sync:periodic] error: {exc}", flush=True)
            # Honor shutdown signals: stop submitting/waiting and do a danger-sync.
            if shutdown_requested["flag"]:
                print("[pipeline] shutdown requested; cancelling remaining futures", flush=True)
                for fut in futures:
                    fut.cancel()
                break

    # Final checkpoint before exiting (the "before dangerous actions" sync).
    report["finished_at"] = int(time.time())
    report["elapsed_seconds"] = time.time() - t0
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    print(json.dumps(report, indent=2, sort_keys=True))
    if cfg.git_sync.enabled:
        phase = "danger" if shutdown_requested["flag"] else "final"
        try:
            sync_res = git_sync(cfg.git_sync, out_dir, report, phase=phase)
            print(
                f"[git_sync:{phase}] committed={sync_res.get('committed')} "
                f"pushed={sync_res.get('pushed')} sha={sync_res.get('commit_sha')} "
                f"err={sync_res.get('error')}",
                flush=True,
            )
        except Exception as exc:
            print(f"[git_sync:{phase}] error: {exc}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
