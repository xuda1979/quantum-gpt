#!/usr/bin/env python3
"""Reinforcement-learning + soft-distillation pipeline for quantum coding.

For each iteration:
  1. (RL explore) Ask the student model to PROPOSE a new quantum-coding
     question given a sampled (framework, topic, difficulty) contract.
  2. (Teacher gate) Ask GLM5.2 to validate the proposed question is
     well-formed, answerable, and non-trivial. Reject and re-sample if not.
  3. (RL roll-out) Ask the student to answer its own question with code.
  4. (Teacher correction) Ask GLM5.2 to grade + correct the student's
     answer. The teacher's `correct_answer` becomes the target.
  5. (Teacher logits) Re-score the corrected answer with GLM5.2 with
     `logprobs=True, top_logprobs=20` so we have a soft target
     distribution for KL distillation.
  6. (Buffer) Append the (question, corrected_answer, teacher_logits)
     tuple to a rolling JSONL buffer along with acceptance metadata.

A separate trainer process consumes the buffer periodically and runs
soft-KL SFT on the accumulated batches (see training/qwen_sft_peft_kl.py).

The script is intentionally I/O-bound against two OpenAI-compatible
endpoints (student server + GLM5.2 teacher) and ships no GPU code; it is
safe to run on the login node while the student server owns the NPUs.

Usage:
    python3 scripts/rl_distill_pipeline.py \
        --config configs/distill/rl_distill_27b_v1.json \
        --buffer-dir data/generated/rl_distill_27b_v1 \
        --target-buffer-size 256
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import signal
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.code_exec_sandbox import (  # noqa: E402
    check_program_shape,
    check_stdout_nonempty,
    execute_code,
    format_exec_brief,
)
from training.artifact_scoring import score_artifact  # noqa: E402

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_STUDENT_QGEN = (
    "You are a quantum software engineering student. You will be asked to "
    "propose a NEW, self-contained quantum-coding question that a peer could "
    "answer in a single Python file. The question must be specific, "
    "answerable, and require writing real code against a real quantum SDK. "
    "Do not ask for literature summaries or opinion answers. "
    "CRITICAL: the question must ask the answerer to write a FULL, runnable "
    "Python program that contains a `main()` function and computes a concrete "
    "numeric or structured result that gets printed to stdout. The program "
    "must be runnable as `python file.py` and print its result. Do NOT ask "
    "for an isolated function or a library snippet — ask for a complete "
    "program with a `main` function that calculates something specific "
    "(e.g. a probability, an expectation value, a statevector, a circuit "
    "metric, a measurement histogram). Return ONLY the question text, no preamble."
)

SYSTEM_PROMPT_TEACHER_QGATE = (
    "You are a senior quantum software engineer reviewing a proposed "
    "quantum-coding question. Decide whether the question is well-formed, "
    "answerable with a single self-contained Python file, and non-trivial "
    "(i.e. not a one-liner copy from documentation). "
    "REQUIRE: the question must ask for a FULL runnable program with a "
    "`main()` function that computes and prints a concrete result — not an "
    "isolated function or library snippet. Reject questions that only ask "
    "for a function definition without a runnable main. "
    "Respond as strict JSON."
)

SYSTEM_PROMPT_STUDENT = (
    "You are a quantum software engineering student. Given a coding question, "
    "produce a single self-contained Python program that implements the "
    "requested behavior. The program MUST define a `main()` function that "
    "computes the concrete result asked for and prints it to stdout, and MUST "
    "include the standard `if __name__ == '__main__': main()` guard so it is "
    "runnable as `python file.py`. Do NOT write an isolated function without a "
    "main entry point. Output ONLY the code block, no prose."
)

SYSTEM_PROMPT_TEACHER = (
    "You are a careful quantum software engineering teacher. You will be "
    "given a coding question and a student's code answer. Grade the answer "
    "strictly and, when incorrect, provide a corrected version."
)

TEACHER_QGATE_PROMPT_TEMPLATE = """Proposed quantum-coding question:

\"\"\"
{question}
\"\"\"

Framework hint: {framework}
Difficulty hint: {difficulty}
Topic hint: {topic}

Respond as JSON with this schema:
{{
  "is_valid": true | false,
  "is_answerable": true | false,
  "is_non_trivial": true | false,
  "requires_full_program": true | false,
  "issues": ["<concise description of each problem>"],
  "confidence": 0.0 | ... | 1.0,
  "improved_question": "<if the question is mostly good but slightly ambiguous, return an improved version; otherwise return empty string>"
}}

`requires_full_program` is true only if the question asks the answerer to
write a COMPLETE runnable Python program structured around a `def main():`
entry point (called under `if __name__ == "__main__":`) that computes and
prints a concrete numeric/symbolic result. It is false if the question only
asks for an isolated function, a snippet, a class, or a fill-in-the-blank.

A question is valid only if all four of is_valid, is_answerable,
is_non_trivial, requires_full_program are true."""

TEACHER_EVAL_PROMPT_TEMPLATE = """You are grading a student's quantum-coding submission.

Question:
{question}

Student code:
```python
{student_code}
```

Real execution result (ground truth from running the student's code in a sandboxed interpreter):
{exec_brief}

Respond as JSON with this schema:
{{
  "is_correct": true | false,
  "issues": ["<concise description of each problem, referencing the execution error when present>"],
  "correct_answer": "<the corrected code and/or a precise explanation; if the code is already correct, repeat it here>",
  "confidence": 0.0 | ... | 1.0
}}

Rules:
- Treat the execution result as ground truth. If `execution_verdict` is `PASS`, the student's code ran successfully — you may still flag logical issues, but do not claim it raises an exception. If `execution_verdict` is `FAIL` or `ERROR`, the code does NOT work and `is_correct` must be `false`.
- When the code is incorrect, `correct_answer` must contain a working replacement (or a precise explanation if a full rewrite is impossible). Your corrected code MUST actually run to `PASS` — it will be executed in the same sandbox as a double-confirmation gate before being admitted to the training set.
- Be concise but specific. Do not invent requirements that are not in the question. Reference the real stderr/stdout lines when diagnosing the failure.
"""

TEACHER_CORRECTION_LOGPROBS_PROMPT_TEMPLATE = """You previously graded a student's quantum-coding submission. Below is the question and the corrected answer you produced. Re-emit the corrected answer verbatim so we can capture per-token logprobs for soft distillation.

Question:
{question}

Corrected answer:
{correct_answer}

Return ONLY the corrected answer text (the contents of `correct_answer`), no preamble, no code fences, no commentary."""


# ---------------------------------------------------------------------------
# Science-domain prompts (task_domain == "science"). Parallel to the coding
# prompts above. Used for quantum-computing SCIENCE QA (concept explanation,
# math derivation, algorithm walk-through, limitation analysis, cross-paper
# comparison) — NOT for code-writing tasks. No sandbox execution is involved.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_STUDENT_QGEN_SCIENCE = (
    "You are a quantum-computing science student. You will be asked to "
    "propose a NEW, self-contained quantum-science question that a peer "
    "could answer in prose plus inline LaTeX math, WITHOUT writing any code. "
    "The question must be specific, scientifically answerable, and require "
    "real understanding of quantum computing (not a literature recall one-"
    "liner). Do not ask the answerer to write, run, or repair code. Return "
    "ONLY the question text, no preamble."
)

SYSTEM_PROMPT_TEACHER_QGATE_SCIENCE = (
    "You are a senior quantum-computing scientist reviewing a proposed "
    "science question. Decide whether the question is well-formed, "
    "scientifically answerable in prose + math (no code required), and "
    "non-trivial (i.e. not a definitional one-liner). Reject any question "
    "that requires writing or running code. Respond as strict JSON."
)

SYSTEM_PROMPT_STUDENT_SCIENCE = (
    "You are a quantum-computing science student. Given a science question, "
    "produce a rigorous answer in prose with inline LaTeX math where helpful. "
    "You may use numbered derivation steps. Do NOT write or attach code. "
    "Output ONLY the answer, no preamble."
)

SYSTEM_PROMPT_TEACHER_SCIENCE = (
    "You are a careful quantum-computing science teacher. You will be given "
    "a science question and a student's prose+math answer. Grade the answer "
    "strictly on scientific correctness, mathematical rigor, and grounding. "
    "When incorrect, provide a corrected answer in prose+math (no code)."
)

TEACHER_QGATE_PROMPT_TEMPLATE_SCIENCE = """Proposed quantum-science question:

\"\"\"
{question}
\"\"\"

Science level hint: {framework}
Field hint: {topic}
Difficulty hint: {difficulty}

Respond as JSON with this schema:
{{
  "is_valid": true | false,
  "is_answerable": true | false,
  "is_non_trivial": true | false,
  "requires_code": true | false,
  "issues": ["<concise description of each problem>"],
  "improved_question": "<optional rewritten question, or empty string>"
}}

Reject (set is_valid=false) if the question requires writing or running code, asks for a literature recall one-liner, or is not scientifically answerable.
"""

TEACHER_EVAL_PROMPT_TEMPLATE_SCIENCE = """You are grading a student's quantum-computing science submission.

Question:
{question}

Student answer:
{student_code}

Note: this is a science question. There is no code execution. Grade the answer on scientific correctness, mathematical rigor, and citation grounding only.

Respond as JSON with this schema:
{{
  "is_correct": true | false,
  "issues": ["<concise description of each scientific or mathematical problem>"],
  "correct_answer": "<the corrected prose+math answer; if the student's answer is already correct, repeat it here>",
  "confidence": 0.0 | ... | 1.0,
  "citation_grounding": 0.0 | ... | 1.0,
  "fabricated_claim": true | false
}}

Guidance:
- `is_correct` is true ONLY if the answer is scientifically correct, mathematically rigorous, and free of unsupported claims.
- `citation_grounding` is 1.0 if every non-trivial claim is either self-evidently derivable or explicitly attributed to a known result; 0.0 if the answer invents results, misattributes, or fabricates citations.
- `fabricated_claim` is true if you suspect any claim, equation, or result is invented rather than established.
- When the answer is incorrect, `correct_answer` must contain a rigorous corrected prose+math answer (no code). Do not write code unless the question explicitly asks for it (it should not).
- Be concise but specific. Reference the exact step or equation that is wrong.
"""

TEACHER_CORRECTION_LOGPROBS_PROMPT_TEMPLATE_SCIENCE = """You previously graded a student's quantum-computing science submission. Below is the question and the corrected answer you produced. Re-emit the corrected answer verbatim so we can capture per-token logprobs for soft distillation.

Question:
{question}

Corrected answer:
{correct_answer}

Return ONLY the corrected answer text (the contents of `correct_answer`), no preamble, no code fences, no commentary."""


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


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
class QuestionGenConfig:
    frameworks: list[str]
    topics: list[str]
    difficulties: list[str]
    framework_distribution: dict[str, float]
    difficulty_distribution: dict[str, float]
    topic_distribution: dict[str, float]
    max_resamples_per_question: int
    rejection_buffer_size: int


@dataclass
class GuardrailConfig:
    """Hard stops that protect against teacher drift and buffer poisoning.

    These are checked after each sample is appended; if any threshold is
    breached the pipeline writes a manifest entry with `guardrail_trip: true`
    and exits cleanly so the orchestrator can run the trainer + eval burst
    early instead of wasting wall-clock on a degenerate round.
    """

    max_consecutive_teacher_rejections: int = 12
    max_teacher_qgate_rejection_rate: float = 0.85  # over the last `window` samples
    min_teacher_confidence: float = 0.30
    min_corrected_answer_chars: int = 40
    rolling_window: int = 32
    # Science-mode guardrails (only consulted when task_domain == "science").
    # Trip if >20% of recent samples have fabricated_claim == true, or if the
    # rolling mean citation_grounding drops below 0.4.
    max_fabricated_claim_rate: float = 0.20
    min_citation_grounding: float = 0.40


@dataclass
class EvalGateConfig:
    """Eval-regression gate. Pauses the RL loop when a fresh held-out eval
    shows the current adapter regressed beyond tolerance.

    The pipeline does NOT run evals itself. An external orchestrator runs
    `evals/subsystem/harness.py` + `analyzer.py` between training rounds and
    writes a small JSON verdict the pipeline polls. This keeps the eval
    harness decoupled and reuses the canonical scoring path.

    Verdict file format (minimal):
      {
        "schema_version": 1,
        "adapter_eval_pass_at_1": 0.42,
        "baseline_eval_pass_at_1": 0.55,
        "r_runnable": 0.88,
        "baseline_r_runnable": 0.97,
        "n_tasks": 44,
        "consecutive_regressions": 2,
        "verdict": "regression" | "ok" | "inconclusive"
      }
    """

    enabled: bool = False
    verdict_path: str = ""  # path to the verdict JSON written by the orchestrator
    poll_every_seconds: int = 300  # how often to re-check the verdict file
    tolerance_pass_at_1: float = 0.03  # absolute drop allowed before it counts as a regression
    tolerance_r_runnable: float = 0.20  # r_runnable collapse threshold (absolute)
    required_consecutive: int = 2  # consecutive regressions needed for a hard stop


@dataclass
class SandboxConfig:
    """Sandboxed code-execution settings for the execution-gated reward.

    When `enabled` is true, the pipeline executes the student's code in a
    sandboxed subprocess before asking the teacher to grade, and executes
    the teacher's corrected code as a double-confirmation gate before
    admitting the sample to the SFT buffer.
    """

    enabled: bool = True
    timeout_seconds: int = 30
    memory_gib: float = 1.0
    # Drop samples whose teacher-corrected code also fails to run.
    reject_on_teacher_exec_fail: bool = True
    # When True, a sample is only marked `is_correct` if execution was PASS.
    exec_is_ground_truth: bool = True


@dataclass
class PipelineConfig:
    student: StudentConfig
    teacher: TeacherConfig
    question_gen: QuestionGenConfig
    pipeline: dict[str, Any]
    output_dir: Path
    seed: int
    concurrency: int = 4
    guardrail: GuardrailConfig = field(default_factory=GuardrailConfig)
    eval_gate: EvalGateConfig = field(default_factory=EvalGateConfig)
    reward_weighting: dict[str, float] = field(default_factory=dict)
    dedup: dict[str, Any] = field(default_factory=dict)
    per_artifact_scoring: dict[str, Any] = field(default_factory=dict)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    # Weakness-aware question generation: when non-empty, the pipeline
    # reads `weakness_report_path` between batches and biases the
    # (framework, topic, difficulty) sampler toward the student's
    # diagnosed weak cells. See WeaknessReport.
    weakness_aware: dict[str, Any] = field(default_factory=dict)
    # Task domain: "coding" (default, sandbox-executed quantum code) or
    # "science" (prose+math quantum-science QA, no sandbox). Selected from
    # raw["pipeline"]["task_domain"]. When "science", the pipeline uses the
    # SCIENCE_* prompts, forces sandbox.enabled=False, and uses science
    # reward weighting (drops exec terms, adds w_citation_grounding).
    task_domain: str = "coding"


# ---------------------------------------------------------------------------
# Distribution samplers
# ---------------------------------------------------------------------------


def _sample_from_distribution(dist: dict[str, float], rng: random.Random) -> str:
    items = list(dist.items())
    keys = [k for k, _ in items]
    weights = [w for _, w in items]
    total = sum(weights)
    if total <= 0:
        return rng.choice(keys)
    weights = [w / total for w in weights]
    return rng.choices(keys, weights=weights, k=1)[0]


def _normalize_dist(dist: dict[str, float] | None, fallback_keys: list[str]) -> dict[str, float]:
    if not dist:
        return {k: 1.0 / max(len(fallback_keys), 1) for k in fallback_keys}
    total = sum(dist.values())
    if total <= 0:
        return {k: 1.0 / max(len(fallback_keys), 1) for k in fallback_keys}
    return {k: v / total for k, v in dist.items()}


# ---------------------------------------------------------------------------
# Rejection-aware distribution + dedup helpers
# ---------------------------------------------------------------------------


class RejectionTracker:
    """Tracks per-(framework, topic, difficulty) rejection rates and produces
    adjusted sampling weights.

    A low-pass update blends the prior distribution with the inverse-rejection
    distribution so the student is gently nudged toward contracts where its
    proposals survive the teacher gate, while never fully abandoning hard
    contracts.
    """

    def __init__(self, prior: dict[str, dict[str, float]]) -> None:
        # prior is {"framework": {...}, "topic": {...}, "difficulty": {...}}
        self.prior = {k: dict(v) for k, v in prior.items()}
        self.attempts: dict[str, dict[str, int]] = {
            k: {kk: 0 for kk in v} for k, v in prior.items()
        }
        self.rejections: dict[str, dict[str, int]] = {
            k: {kk: 0 for kk in v} for k, v in prior.items()
        }
        self._lock = threading.Lock()

    def record(self, dim: str, key: str, rejected: bool) -> None:
        with self._lock:
            self.attempts.setdefault(dim, {})
            self.rejections.setdefault(dim, {})
            self.attempts[dim][key] = self.attempts[dim].get(key, 0) + 1
            if rejected:
                self.rejections[dim][key] = self.rejections[dim].get(key, 0) + 1

    def adjusted_distribution(
        self, dim: str, *, smoothing: float = 4.0, low_pass: float = 0.25
    ) -> dict[str, float]:
        """Return a rejection-aware distribution for `dim`.

        smoothing: pseudo-count added to both attempts and rejections so a
            handful of early samples don't dominate the prior.
        low_pass: blend factor — 0.0 = pure prior, 1.0 = pure inverse-rejection.
        """
        with self._lock:
            prior = self.prior.get(dim, {})
            attempts = self.attempts.get(dim, {})
            rejections = self.rejections.get(dim, {})
        if not prior:
            return {}
        weights = {}
        for k, p in prior.items():
            a = attempts.get(k, 0) + smoothing
            r = rejections.get(k, 0)
            # acceptance rate with smoothing; never zero
            accept = max(1e-3, (a - r) / a)
            weights[k] = (1.0 - low_pass) * p + low_pass * accept
        total = sum(weights.values())
        if total <= 0:
            return {k: 1.0 / max(len(prior), 1) for k in prior}
        return {k: v / total for k, v in weights.items()}


class WeaknessReport:
    """Weakness-aware question-generation bias.

    Reads a JSON report produced by the orchestrator (or by
    `scripts/analyze_batch_weakness.py`) summarising the student's failure
    distribution over (framework, topic, difficulty) cells from the last
    batch, and exposes a blended distribution that up-weights weak cells.

    Report shape (minimal):
      {
        "schema_version": 1,
        "batch_id": "round-7",
        "n_samples": 100,
        "cells": [
          {"framework": "qiskit", "topic": "algorithms",
           "difficulty": "hard", "pass_rate": 0.12, "n": 8},
          ...
        ]
      }

    The blend is: `blended = (1 - alpha) * prior + alpha * weakness_weight`,
    where `weakness_weight` is proportional to `1 - pass_rate` (clipped to
    [0.05, 1.0] so a fully-passed cell still gets some mass). `alpha`
    defaults to 0.4 — gentle enough to preserve coverage, strong enough
    to push the student toward its weak spots.
    """

    def __init__(
        self, prior: dict[str, dict[str, float]], alpha: float = 0.4, min_weight: float = 0.05
    ) -> None:
        self.prior = prior
        self.alpha = float(alpha)
        self.min_weight = float(min_weight)
        self._lock = threading.Lock()
        self._cells: dict[tuple[str, str, str], float] = {}
        self._marginal: dict[str, dict[str, float]] = {
            "framework": {},
            "topic": {},
            "difficulty": {},
        }
        self._loaded_at: float = 0.0
        self._path: Path | None = None

    def load(self, path: str | Path) -> bool:
        """(Re)load the weakness report from `path`. Returns True on success."""
        p = Path(path)
        if not p.is_file():
            return False
        try:
            raw = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            return False
        cells = raw.get("cells", []) if isinstance(raw, dict) else []
        new_cells: dict[tuple[str, str, str], float] = {}
        marg_fw: dict[str, float] = {}
        marg_tp: dict[str, float] = {}
        marg_df: dict[str, float] = {}
        for cell in cells:
            fw = str(cell.get("framework", ""))
            tp = str(cell.get("topic", ""))
            df = str(cell.get("difficulty", ""))
            n = float(cell.get("n", 0))
            pass_rate = float(cell.get("pass_rate", 0.0))
            # weakness weight = (1 - pass_rate), weighted by sample count
            # so a cell with 8 failures matters more than one with 1.
            w = max(self.min_weight, 1.0 - pass_rate) * max(1.0, n)
            new_cells[(fw, tp, df)] = w
            marg_fw[fw] = marg_fw.get(fw, 0.0) + w
            marg_tp[tp] = marg_tp.get(tp, 0.0) + w
            marg_df[df] = marg_df.get(df, 0.0) + w
        with self._lock:
            self._cells = new_cells
            self._marginal = {"framework": marg_fw, "topic": marg_tp, "difficulty": marg_df}
            self._loaded_at = time.time()
            self._path = p
        return True

    def blended_distribution(self, dim: str) -> dict[str, float]:
        """Return a blended distribution for `dim` in {framework, topic, difficulty}."""
        with self._lock:
            prior = dict(self.prior.get(dim, {}))
            weakness = dict(self._marginal.get(dim, {}))
        if not weakness:
            return prior
        # Normalize weakness to a distribution.
        total = sum(weakness.values())
        if total <= 0:
            return prior
        weakness = {k: v / total for k, v in weakness.items()}
        # Ensure all prior keys appear in weakness (assign min_weight share).
        for k in prior:
            weakness.setdefault(k, self.min_weight / max(len(prior), 1))
        wtot = sum(weakness.values())
        weakness = {k: v / wtot for k, v in weakness.items()}
        # Blend.
        blended: dict[str, float] = {}
        for k in prior:
            blended[k] = (1.0 - self.alpha) * prior[k] + self.alpha * weakness.get(k, 0.0)
        btotal = sum(blended.values())
        if btotal <= 0:
            return prior
        return {k: v / btotal for k, v in blended.items()}

    @property
    def loaded_at(self) -> float:
        return self._loaded_at


class DedupIndex:
    """Bloom-filter-like dedup over question normalized text + answer sha.

    Uses a bounded LRU set of sha1 hashes; cheap and thread-safe.
    """

    def __init__(self, max_entries: int = 20000) -> None:
        self.max_entries = max_entries
        self._seen: set[str] = set()
        self._order: list[str] = []
        self._lock = threading.Lock()

    @staticmethod
    def _hash(question: str, answer: str) -> str:
        norm_q = re.sub(r"\s+", " ", question or "").strip().lower()[:512]
        norm_a = re.sub(r"\s+", " ", answer or "").strip().lower()[:256]
        return hashlib.sha1(f"{norm_q}||{norm_a}".encode()).hexdigest()

    def is_duplicate(self, question: str, answer: str) -> bool:
        h = self._hash(question, answer)
        with self._lock:
            if h in self._seen:
                return True
            self._seen.add(h)
            self._order.append(h)
            if len(self._order) > self.max_entries:
                old = self._order.pop(0)
                self._seen.discard(old)
            return False


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def _post_json(
    url: str, payload: dict[str, Any], headers: dict[str, str], timeout: float
) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    if not body:
        raise RuntimeError(f"empty response from {url}")
    return json.loads(body)


def _chat(
    api_base: str,
    api_key: str,
    model: str,
    system: str,
    user: str,
    *,
    temperature: float,
    max_tokens: int,
    timeout: float,
    logprobs: bool = False,
    top_logprobs: int = 0,
    response_format: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if logprobs:
        payload["logprobs"] = True
        payload["top_logprobs"] = top_logprobs
    if response_format is not None:
        payload["response_format"] = response_format
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return _post_json(api_base.rstrip("/") + "/chat/completions", payload, headers, timeout)


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------


def student_propose_question(
    cfg: StudentConfig,
    *,
    framework: str,
    topic: str,
    difficulty: str,
    rng: random.Random,
    task_domain: str = "coding",
) -> str:
    """Ask the student to propose a new question (coding or science)."""
    seed_hint = rng.randint(10_000, 99_999)
    if task_domain == "science":
        system_prompt = SYSTEM_PROMPT_STUDENT_QGEN_SCIENCE
        user_prompt = (
            f"Propose ONE new, original quantum-science question with these constraints:\n"
            f"- Science level: {framework}\n"
            f"- Field: {topic}\n"
            f"- Difficulty: {difficulty}\n"
            f"- The answer must be prose + inline LaTeX math, NO code\n"
            f"- Avoid definitional one-liners; the task must require real reasoning\n"
            f"- Do not ask the answerer to write, run, or repair code\n"
            f"- Seed hint (do not echo): {seed_hint}\n\n"
            f"Return ONLY the question text. No code, no preamble, no markdown headers."
        )
    else:
        system_prompt = SYSTEM_PROMPT_STUDENT_QGEN
        user_prompt = (
            f"Propose ONE new, original quantum-coding question with these constraints:\n"
            f"- Framework: {framework}\n"
            f"- Topic: {topic}\n"
            f"- Difficulty: {difficulty}\n"
            f"- The answer must be a single self-contained Python file\n"
            f"- The question must ask the answerer to write FULL runnable code that\n"
            f"  computes and prints a concrete numeric/symbolic result, structured\n"
            f"  around a `def main():` entry point (plus any helper functions needed).\n"
            f"  Do NOT ask for an isolated function or a snippet; ask for a complete\n"
            f'  program where `main()` is called under `if __name__ == "__main__":`\n'
            f"  and actually performs a calculation (e.g. an expectation value, a\n"
            f"  probability, a statevector overlap, a gate count, a noise metric).\n"
            f"- Avoid copying documentation verbatim; the task must require writing code\n"
            f"- Seed hint (do not echo): {seed_hint}\n\n"
            f"Return ONLY the question text. No code, no preamble, no markdown headers."
        )
    resp = _chat(
        cfg.api_base,
        cfg.api_key,
        cfg.model,
        system_prompt,
        user_prompt,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        timeout=cfg.timeout,
    )
    content = (resp.get("choices") or [{}])[0].get("message", {}).get("content", "")
    return content.strip()


def teacher_validate_question(
    cfg: TeacherConfig,
    question: str,
    *,
    framework: str,
    topic: str,
    difficulty: str,
    task_domain: str = "coding",
) -> dict[str, Any]:
    if task_domain == "science":
        system_prompt = SYSTEM_PROMPT_TEACHER_QGATE_SCIENCE
        template = TEACHER_QGATE_PROMPT_TEMPLATE_SCIENCE
    else:
        system_prompt = SYSTEM_PROMPT_TEACHER_QGATE
        template = TEACHER_QGATE_PROMPT_TEMPLATE
    user_prompt = template.format(
        question=question,
        framework=framework,
        difficulty=difficulty,
        topic=topic,
    )
    resp = _chat(
        cfg.api_base,
        cfg.api_key,
        cfg.model,
        system_prompt,
        user_prompt,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        timeout=cfg.timeout,
        response_format={"type": "json_object"},
    )
    content = (resp.get("choices") or [{}])[0].get("message", {}).get("content", "{}")
    return parse_teacher_json(content)


def student_attempt(cfg: StudentConfig, question: str, task_domain: str = "coding") -> str:
    if task_domain == "science":
        system_prompt = SYSTEM_PROMPT_STUDENT_SCIENCE
        user_prompt = (
            f"Answer the following quantum-computing science question with "
            f"rigorous prose and inline LaTeX math where helpful. Do NOT "
            f"write code.\n\nQuestion:\n{question}\n\n"
            f"Output ONLY the answer, no preamble."
        )
    else:
        system_prompt = SYSTEM_PROMPT_STUDENT
        user_prompt = (
            f"Answer the following quantum-coding question with a FULL, "
            f"runnable Python program. The program must define a `main()` "
            f"function that computes the concrete result and prints it to "
            f"stdout, and must include `if __name__ == '__main__': main()` "
            f"so it can be run as `python file.py`.\n\nQuestion:\n{question}\n\n"
            f"Output ONLY the ```python ... ``` code block."
        )
    resp = _chat(
        cfg.api_base,
        cfg.api_key,
        cfg.model,
        system_prompt,
        user_prompt,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        timeout=cfg.timeout,
    )
    content = (resp.get("choices") or [{}])[0].get("message", {}).get("content", "")
    return content.strip()


def teacher_eval(
    cfg: TeacherConfig,
    question: str,
    student_code: str,
    exec_brief: str = "",
    task_domain: str = "coding",
) -> dict[str, Any]:
    if task_domain == "science":
        system_prompt = SYSTEM_PROMPT_TEACHER_SCIENCE
        template = TEACHER_EVAL_PROMPT_TEMPLATE_SCIENCE
        user_prompt = template.format(
            question=question,
            student_code=student_code,
        )
    else:
        system_prompt = SYSTEM_PROMPT_TEACHER
        template = TEACHER_EVAL_PROMPT_TEMPLATE
        user_prompt = template.format(
            question=question,
            student_code=student_code,
            exec_brief=exec_brief or "(no execution evidence available)",
        )
    resp = _chat(
        cfg.api_base,
        cfg.api_key,
        cfg.model,
        system_prompt,
        user_prompt,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        timeout=cfg.timeout,
        response_format={"type": "json_object"},
    )
    content = (resp.get("choices") or [{}])[0].get("message", {}).get("content", "{}")
    return parse_teacher_json(content)


def teacher_correction_with_logits(
    cfg: TeacherConfig, question: str, correct_answer: str, task_domain: str = "coding"
) -> dict[str, Any]:
    """Re-emit the corrected answer with per-token top-k logprobs."""
    if task_domain == "science":
        system_prompt = SYSTEM_PROMPT_TEACHER_SCIENCE
        template = TEACHER_CORRECTION_LOGPROBS_PROMPT_TEMPLATE_SCIENCE
    else:
        system_prompt = SYSTEM_PROMPT_TEACHER
        template = TEACHER_CORRECTION_LOGPROBS_PROMPT_TEMPLATE
    user_prompt = template.format(
        question=question,
        correct_answer=correct_answer,
    )
    resp = _chat(
        cfg.api_base,
        cfg.api_key,
        cfg.model,
        system_prompt,
        user_prompt,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        timeout=cfg.timeout,
        logprobs=True,
        top_logprobs=cfg.top_logprobs,
    )
    choices = resp.get("choices") or [{}]
    content = choices[0].get("message", {}).get("content", "")
    logprobs = choices[0].get("logprobs") or {"content": []}
    return {
        "content": content.strip() if isinstance(content, str) else "",
        "logprobs": logprobs.get("content", []) if isinstance(logprobs, dict) else [],
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse_teacher_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    if not stripped.startswith("{"):
        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if match:
            stripped = match.group(0)
    try:
        return json.loads(stripped)
    except Exception:
        return {"_parse_error": True, "_raw": text[:2000]}


def sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:8]


def extract_code_block(text: str) -> str:
    """Extract the first ```python ... ``` block, or the whole text if no fence."""
    if "```" not in text:
        return text.strip()
    match = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------


def load_config(path: Path) -> PipelineConfig:
    raw = json.loads(path.read_text())
    student_cfg = raw["student_model"]["serving"]
    teacher_cfg = raw["teacher_model"]
    qgen_cfg = raw["question_generation"]
    frameworks = qgen_cfg.get("frameworks", ["qiskit", "pennylane", "cirq"])
    topics = qgen_cfg.get("topics", ["circuits", "algorithms", "noise", "ml"])
    difficulties = qgen_cfg.get("difficulties", ["easy", "medium", "hard"])
    framework_distribution = _normalize_dist(qgen_cfg.get("framework_distribution"), frameworks)
    difficulty_distribution = _normalize_dist(qgen_cfg.get("difficulty_distribution"), difficulties)
    topic_distribution = _normalize_dist(qgen_cfg.get("topic_distribution"), topics)
    cfg = PipelineConfig(
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
        question_gen=QuestionGenConfig(
            frameworks=frameworks,
            topics=topics,
            difficulties=difficulties,
            framework_distribution=framework_distribution,
            difficulty_distribution=difficulty_distribution,
            topic_distribution=topic_distribution,
            max_resamples_per_question=qgen_cfg.get("max_resamples_per_question", 3),
            rejection_buffer_size=qgen_cfg.get("rejection_buffer_size", 64),
        ),
        pipeline=raw.get("pipeline", {}),
        output_dir=Path(raw.get("output_dir", "data/generated/rl_distill_default")),
        seed=raw.get("seed", 20260706),
        concurrency=int(raw.get("concurrency", raw.get("pipeline", {}).get("concurrency", 4))),
        guardrail=_load_guardrail(raw.get("guardrail", {})),
        eval_gate=_load_eval_gate(raw.get("eval_gate", {})),
        reward_weighting=raw.get("reward_weighting", {}),
        dedup=raw.get("dedup", {}),
        per_artifact_scoring=raw.get("per_artifact_scoring", {}),
        sandbox=_load_sandbox(raw.get("sandbox", {})),
        weakness_aware=raw.get("weakness_aware", {}),
        task_domain=str(raw.get("pipeline", {}).get("task_domain", "coding") or "coding"),
    )
    # Science mode: force sandbox off and inject science distributions into
    # QuestionGenConfig if the config supplies them. The science loop never
    # executes code; the teacher is the sole ground truth.
    if cfg.task_domain == "science":
        cfg.sandbox.enabled = False
        cfg.sandbox.exec_is_ground_truth = False
        qgen_sci = raw.get("question_generation", {})
        sci_levels = qgen_sci.get("science_levels") or []
        sci_fields = qgen_sci.get("science_fields") or []
        if sci_levels:
            # Reuse the frameworks/topics slots to carry science level/field
            # so the existing sampler code path works unchanged. The
            # student_propose_question and teacher_validate_question functions
            # read cfg.task_domain and select the science prompts, which
            # frame the hint as "Science level" and "Field" respectively.
            cfg.question_gen.frameworks = list(sci_levels)
            cfg.question_gen.framework_distribution = _normalize_dist(
                qgen_sci.get("science_level_distribution"),
                sci_levels,
            )
        if sci_fields:
            cfg.question_gen.topics = list(sci_fields)
            cfg.question_gen.topic_distribution = _normalize_dist(
                qgen_sci.get("science_field_distribution"),
                sci_fields,
            )
    return cfg


def _load_guardrail(raw: dict[str, Any]) -> GuardrailConfig:
    g = GuardrailConfig()
    g.max_consecutive_teacher_rejections = int(
        raw.get("max_consecutive_teacher_rejections", g.max_consecutive_teacher_rejections)
    )
    g.max_teacher_qgate_rejection_rate = float(
        raw.get("max_teacher_qgate_rejection_rate", g.max_teacher_qgate_rejection_rate)
    )
    g.min_teacher_confidence = float(raw.get("min_teacher_confidence", g.min_teacher_confidence))
    g.min_corrected_answer_chars = int(
        raw.get("min_corrected_answer_chars", g.min_corrected_answer_chars)
    )
    g.rolling_window = int(raw.get("rolling_window", g.rolling_window))
    g.max_fabricated_claim_rate = float(
        raw.get("max_fabricated_claim_rate", g.max_fabricated_claim_rate)
    )
    g.min_citation_grounding = float(raw.get("min_citation_grounding", g.min_citation_grounding))
    return g


def _load_eval_gate(raw: dict[str, Any]) -> EvalGateConfig:
    g = EvalGateConfig()
    g.enabled = bool(raw.get("enabled", g.enabled))
    g.verdict_path = str(raw.get("verdict_path", g.verdict_path))
    g.poll_every_seconds = int(raw.get("poll_every_seconds", g.poll_every_seconds))
    g.tolerance_pass_at_1 = float(raw.get("tolerance_pass_at_1", g.tolerance_pass_at_1))
    g.tolerance_r_runnable = float(raw.get("tolerance_r_runnable", g.tolerance_r_runnable))
    g.required_consecutive = int(raw.get("required_consecutive", g.required_consecutive))
    return g


def _load_sandbox(raw: dict[str, Any]) -> SandboxConfig:
    s = SandboxConfig()
    s.enabled = bool(raw.get("enabled", s.enabled))
    s.timeout_seconds = int(raw.get("timeout_seconds", s.timeout_seconds))
    s.memory_gib = float(raw.get("memory_gib", s.memory_gib))
    s.reject_on_teacher_exec_fail = bool(
        raw.get("reject_on_teacher_exec_fail", s.reject_on_teacher_exec_fail)
    )
    s.exec_is_ground_truth = bool(raw.get("exec_is_ground_truth", s.exec_is_ground_truth))
    return s


def _read_eval_verdict(path: str) -> dict[str, Any] | None:
    """Read the external eval-verdict JSON. Returns None if missing/unreadable.

    The verdict file is written by the orchestrator after
    evals/subsystem/harness.py + analyzer.py run between training rounds.
    Missing file means "no eval yet" — not a regression, just no signal.
    """
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _eval_gate_tripped(gate: EvalGateConfig, verdict: dict[str, Any] | None) -> str | None:
    """Return a reason string if the eval gate is tripped, else None.

    Trip rules (mirrors skills/quantum-eval-verifier):
      - r_runnable collapse (>= tolerance_r_runnable absolute drop) -> hard stop now.
      - pass@1 drop >= tolerance_pass_at_1 for `required_consecutive` evals -> hard stop.
      - verdict explicitly says "regression" with required_consecutive met -> hard stop.
    A single dip is NOT a hard stop; it just gets logged by the caller.
    """
    if not gate.enabled or verdict is None:
        return None
    # r_runnable collapse is an immediate hard stop — runnable code is foundational.
    r_run = verdict.get("r_runnable")
    base_r_run = verdict.get("baseline_r_runnable")
    if isinstance(r_run, (int, float)) and isinstance(base_r_run, (int, float)):
        if (base_r_run - r_run) >= gate.tolerance_r_runnable:
            return (
                f"r_runnable collapse: {r_run:.3f} vs baseline {base_r_run:.3f} "
                f"(drop {(base_r_run - r_run):.3f} >= {gate.tolerance_r_runnable})"
            )
    # pass@1 regression requires consecutive confirmations to avoid noise.
    pass1 = verdict.get("adapter_eval_pass_at_1")
    base_pass1 = verdict.get("baseline_eval_pass_at_1")
    consec = verdict.get("consecutive_regressions", 0)
    if isinstance(pass1, (int, float)) and isinstance(base_pass1, (int, float)):
        if (base_pass1 - pass1) >= gate.tolerance_pass_at_1:
            if consec >= gate.required_consecutive:
                return (
                    f"eval_regression: pass@1 {pass1:.3f} vs baseline {base_pass1:.3f} "
                    f"(drop {(base_pass1 - pass1):.3f} >= {gate.tolerance_pass_at_1}, "
                    f"consecutive={consec} >= {gate.required_consecutive})"
                )
    return None


# ---------------------------------------------------------------------------
# Buffer writer (thread-safe append-only JSONL)
# ---------------------------------------------------------------------------


class BufferWriter:
    """Append-only JSONL buffer with periodic manifest updates."""

    def __init__(self, buffer_dir: Path, name: str):
        self.buffer_dir = buffer_dir
        self.buffer_dir.mkdir(parents=True, exist_ok=True)
        self.buffer_path = buffer_dir / f"{name}_samples.jsonl"
        self.manifest_path = buffer_dir / f"{name}_manifest.json"
        self.rejected_path = buffer_dir / f"{name}_rejected.jsonl"
        self._lock = threading.Lock()
        self._count = 0
        self._rejected = 0
        self._accepted = 0
        if self.buffer_path.exists():
            with self.buffer_path.open("r", encoding="utf-8") as fh:
                self._count = sum(1 for _ in fh)
                self._accepted = self._count
        if self.rejected_path.exists():
            with self.rejected_path.open("r", encoding="utf-8") as fh:
                self._rejected = sum(1 for _ in fh)

    def append_sample(self, sample: dict[str, Any]) -> None:
        with self._lock:
            with self.buffer_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(sample, ensure_ascii=False) + "\n")
            self._count += 1
            self._accepted = self._count

    def append_rejection(self, record: dict[str, Any]) -> None:
        with self._lock:
            with self.rejected_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._rejected += 1

    def write_manifest(self, extra: dict[str, Any] | None = None) -> None:
        with self._lock:
            manifest = {
                "buffer_path": str(self.buffer_path),
                "buffer_count": self._count,
                "accepted_total": self._accepted,
                "rejected_total": self._rejected,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            if extra:
                manifest.update(extra)
            tmp = self.manifest_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
            tmp.replace(self.manifest_path)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------


shutdown_requested = {"flag": False}
_STATS_LOCK = threading.Lock()


def _incr(stats: dict[str, int], key: str, by: int = 1) -> None:
    """Thread-safe stat increment (stats dict is shared across worker threads)."""
    with _STATS_LOCK:
        stats[key] = stats.get(key, 0) + by


def _install_signal_handlers() -> None:
    def handler(signum, _frame):
        print(f"[rl_distill] received signal {signum}; setting shutdown flag", flush=True)
        shutdown_requested["flag"] = True

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


def _compute_reward(
    *,
    cfg: PipelineConfig,
    teacher_eval_result: dict[str, Any],
    qgate: dict[str, Any],
    correct_answer: str,
    resample_attempts: int,
    student_exec: dict[str, Any] | None = None,
    teacher_exec: dict[str, Any] | None = None,
    program_shape: dict[str, Any] | None = None,
) -> float:
    """Compute a scalar reward in [0, 1] for this sample.

    The reward up-weights samples where:
      - the student's original attempt was already correct (teacher didn't
        have to rewrite it),
      - the teacher's confidence is high,
      - the question passed the gate on the first try (less resampling),
      - the corrected answer is substantial (not a one-liner cop-out).

    The trainer can use `metadata.reward` to do reward-weighted regression
    (samples with reward < `reward_floor` are dropped entirely).
    """
    rw = cfg.reward_weighting or {}
    sandbox_on = bool(cfg.sandbox.enabled)
    science_on = cfg.task_domain == "science"
    w_exec_pass = float(rw.get("w_student_exec_pass", 0.45 if sandbox_on else 0.0))
    w_teacher_exec_pass = float(rw.get("w_teacher_exec_pass", 0.20 if sandbox_on else 0.0))
    w_correct = float(
        rw.get("w_teacher_already_correct", 0.15 if sandbox_on else (0.35 if science_on else 0.40))
    )
    w_conf = float(
        rw.get("w_teacher_confidence", 0.10 if sandbox_on else (0.20 if science_on else 0.25))
    )
    w_first_pass = float(
        rw.get("w_first_pass_qgate", 0.05 if sandbox_on else (0.15 if science_on else 0.20))
    )
    w_substance = float(
        rw.get("w_answer_substance", 0.05 if sandbox_on else (0.10 if science_on else 0.15))
    )
    # Science-only term: citation grounding. Zero in coding mode so it
    # contributes nothing to the normalised reward there.
    w_grounding = float(rw.get("w_citation_grounding", 0.20 if science_on else 0.0))
    # Normalise in case the config supplies unbalanced weights.
    total_w = max(
        1e-6,
        w_exec_pass
        + w_teacher_exec_pass
        + w_correct
        + w_conf
        + w_first_pass
        + w_substance
        + w_grounding,
    )

    student_pass = 1.0 if (student_exec or {}).get("verdict") == "PASS" else 0.0
    teacher_pass = 1.0 if (teacher_exec or {}).get("verdict") == "PASS" else 0.0
    already_correct = 1.0 if teacher_eval_result.get("is_correct") else 0.0
    confidence = float(teacher_eval_result.get("confidence", 0.5) or 0.5)
    confidence = max(0.0, min(1.0, confidence))
    first_pass = 1.0 if resample_attempts <= 1 else (0.5 if resample_attempts == 2 else 0.0)
    substance = min(1.0, len(correct_answer) / 800.0)
    # Citation grounding in [0,1]; default 0.5 when the teacher omits it.
    grounding = float(teacher_eval_result.get("citation_grounding", 0.5) or 0.5)
    grounding = max(0.0, min(1.0, grounding))
    # Penalise fabricated claims hard: drop grounding to 0 if the teacher
    # flagged a fabricated claim.
    if teacher_eval_result.get("fabricated_claim"):
        grounding = 0.0

    reward = (
        w_exec_pass * student_pass
        + w_teacher_exec_pass * teacher_pass
        + w_correct * already_correct
        + w_conf * confidence
        + w_first_pass * first_pass
        + w_substance * substance
        + w_grounding * grounding
    ) / total_w
    # Program-shape penalty (coding mode only): if the student's code is not
    # a full program with a main() entry point + __main__ guard, scale the
    # reward down. This enforces the question-shape contract at the reward
    # level, not just the prompt level.
    if program_shape is not None and cfg.task_domain == "coding":
        if not program_shape.get("is_full_program", True):
            reward *= 0.5
        elif program_shape.get("stdout_nonempty") is False:
            # Ran to PASS but printed nothing — half penalty.
            reward *= 0.75
    return max(0.0, min(1.0, reward))


def _build_sample(
    *,
    cfg: PipelineConfig,
    question: str,
    framework: str,
    topic: str,
    difficulty: str,
    student_code: str,
    teacher_eval_result: dict[str, Any],
    teacher_correction: dict[str, Any],
    qgate: dict[str, Any],
    student_qgen_meta: dict[str, Any],
    student_exec: dict[str, Any] | None = None,
    teacher_exec: dict[str, Any] | None = None,
    program_shape: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the SFT sample that the trainer will consume."""
    correct_answer = teacher_eval_result.get("correct_answer", "") or teacher_correction.get(
        "content", ""
    )
    if cfg.task_domain == "science":
        _sys_prompt = SYSTEM_PROMPT_TEACHER_SCIENCE
        _user_prompt = f"Question:\n{question}\n\nProduce a correct, rigorous prose+math answer. Do NOT write code."
    else:
        _sys_prompt = SYSTEM_PROMPT_TEACHER
        _user_prompt = (
            f"Question:\n{question}\n\nProduce a correct, self-contained Python solution."
        )
    messages = [
        {"role": "system", "content": _sys_prompt},
        {"role": "user", "content": _user_prompt},
        {"role": "assistant", "content": correct_answer},
    ]
    sample_id = f"rl_distill_{sha8(question)}_{sha8(correct_answer)}"
    reward = _compute_reward(
        cfg=cfg,
        teacher_eval_result=teacher_eval_result,
        qgate=qgate,
        correct_answer=correct_answer,
        resample_attempts=int(student_qgen_meta.get("resample_attempts", 1)),
        student_exec=student_exec,
        teacher_exec=teacher_exec,
        program_shape=program_shape,
    )
    metadata: dict[str, Any] = {
        "pipeline": "rl_distill_v1",
        "framework": framework,
        "topic": topic,
        "difficulty": difficulty,
        "student_model": cfg.student.model,
        "teacher_model": cfg.teacher.model,
        "teacher_is_correct": teacher_eval_result.get("is_correct"),
        "teacher_confidence": teacher_eval_result.get("confidence"),
        "teacher_issues": teacher_eval_result.get("issues", []),
        "citation_grounding": teacher_eval_result.get("citation_grounding"),
        "fabricated_claim": teacher_eval_result.get("fabricated_claim"),
        "task_domain": cfg.task_domain,
        "qgate_is_valid": qgate.get("is_valid"),
        "qgate_is_answerable": qgate.get("is_answerable"),
        "qgate_is_non_trivial": qgate.get("is_non_trivial"),
        "qgate_requires_full_program": qgate.get("requires_full_program"),
        "qgate_improved_question": qgate.get("improved_question", ""),
        "student_qgen_temperature": student_qgen_meta.get("temperature"),
        "resample_attempts": student_qgen_meta.get("resample_attempts", 1),
        "reward": reward,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "student_exec": student_exec or {},
        "teacher_exec": teacher_exec or {},
        "program_shape": program_shape or {},
    }
    # Per-artifact score vector (reward decomposition). Gated by config so
    # the legacy single-reward path is preserved when disabled. The trainer
    # ignores this field unless its --reward-weighted-nll / --per-artifact-kl-gate
    # / --partial-credit-upweight flags are set.
    pas_cfg = cfg.per_artifact_scoring or {}
    if pas_cfg.get("enabled", False):
        classifier = pas_cfg.get("issue_classifier", "rule_v1")
        metadata["artifact_scores"] = score_artifact(
            teacher_eval_result=teacher_eval_result,
            correct_answer=correct_answer,
            resample_attempts=int(student_qgen_meta.get("resample_attempts", 1)),
            issue_classifier=classifier,
        )
    return {
        "example_id": sample_id,
        "format": "chat-sft-v1",
        "messages": messages,
        "metadata": metadata,
        "teacher_logits": {
            "content": teacher_correction.get("content", ""),
            "logprobs": teacher_correction.get("logprobs", []),
            "top_logprobs": cfg.teacher.top_logprobs,
        },
        "student_attempt": student_code,
        "source_schema": "rl-distill-v1",
    }


def process_one(
    cfg: PipelineConfig,
    rng: random.Random,
    buffer: BufferWriter,
    stats: dict[str, int],
    *,
    rejection_tracker: RejectionTracker | None = None,
    dedup_index: DedupIndex | None = None,
    weakness_report: WeaknessReport | None = None,
) -> str:
    """Run one full RL+distill iteration.

    Returns a status string:
      - "appended" — a sample was appended to the buffer
      - "rejected_qgate" — teacher rejected the question
      - "rejected_eval" — teacher rejected the student's code
      - "duplicate" — sample was a near-duplicate of an existing one
      - "error" — unexpected error / empty response
    """
    # Rejection-aware contract sampling: if a tracker is provided, blend the
    # prior with the inverse-rejection distribution so the student is nudged
    # toward contracts where its proposals survive the teacher gate.
    if rejection_tracker is not None:
        fw_dist = rejection_tracker.adjusted_distribution("framework")
        tp_dist = rejection_tracker.adjusted_distribution("topic")
        df_dist = rejection_tracker.adjusted_distribution("difficulty")
        framework = _sample_from_distribution(
            fw_dist or cfg.question_gen.framework_distribution, rng
        )
        topic = _sample_from_distribution(tp_dist or cfg.question_gen.topic_distribution, rng)
        difficulty = _sample_from_distribution(
            df_dist or cfg.question_gen.difficulty_distribution, rng
        )
    elif weakness_report is not None and weakness_report.loaded_at > 0:
        # Weakness-aware sampling: bias toward (framework, topic, difficulty)
        # cells where the student failed most in the last batch.
        fw_dist = weakness_report.blended_distribution("framework")
        tp_dist = weakness_report.blended_distribution("topic")
        df_dist = weakness_report.blended_distribution("difficulty")
        framework = _sample_from_distribution(
            fw_dist or cfg.question_gen.framework_distribution, rng
        )
        topic = _sample_from_distribution(tp_dist or cfg.question_gen.topic_distribution, rng)
        difficulty = _sample_from_distribution(
            df_dist or cfg.question_gen.difficulty_distribution, rng
        )
    else:
        framework = _sample_from_distribution(cfg.question_gen.framework_distribution, rng)
        topic = _sample_from_distribution(cfg.question_gen.topic_distribution, rng)
        difficulty = _sample_from_distribution(cfg.question_gen.difficulty_distribution, rng)

    # Stage 1: student proposes a question (with up to N resamples on rejection)
    resample_attempts = 0
    question = ""
    qgate: dict[str, Any] = {}
    while resample_attempts < cfg.question_gen.max_resamples_per_question:
        resample_attempts += 1
        try:
            question = student_propose_question(
                cfg.student,
                framework=framework,
                topic=topic,
                difficulty=difficulty,
                rng=rng,
                task_domain=cfg.task_domain,
            )
        except Exception as exc:
            _incr(stats, "student_qgen_errors")
            print(f"[rl_distill] student_qgen error: {exc}", flush=True)
            return "error"
        if not question or len(question) < 40:
            _incr(stats, "student_qgen_empty")
            continue
        try:
            qgate = teacher_validate_question(
                cfg.teacher,
                question,
                framework=framework,
                topic=topic,
                difficulty=difficulty,
                task_domain=cfg.task_domain,
            )
        except Exception as exc:
            _incr(stats, "teacher_qgate_errors")
            print(f"[rl_distill] teacher_qgate error: {exc}", flush=True)
            return "error"
        if qgate.get("_parse_error"):
            _incr(stats, "teacher_qgate_parse_errors")
            continue
        improved = qgate.get("improved_question", "") or ""
        if improved and len(improved) > 40 and qgate.get("is_valid") is not False:
            question = improved
        if qgate.get("is_valid") and qgate.get("is_answerable") and qgate.get("is_non_trivial"):
            # Science mode: also reject questions the teacher says require code.
            if cfg.task_domain == "science" and qgate.get("requires_code"):
                _incr(stats, "qgate_science_requires_code")
            # Coding mode: reject questions that don't require a full program
            # with a main() entry point (the question-generation contract).
            elif cfg.task_domain == "coding" and not qgate.get("requires_full_program"):
                _incr(stats, "qgate_coding_not_full_program")
            else:
                break
        # rejected — record and resample
        buffer.append_rejection(
            {
                "framework": framework,
                "topic": topic,
                "difficulty": difficulty,
                "question": question,
                "qgate": qgate,
                "attempt": resample_attempts,
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        )
        _incr(stats, "qgate_rejected")
        if rejection_tracker is not None:
            rejection_tracker.record("framework", framework, True)
            rejection_tracker.record("topic", topic, True)
            rejection_tracker.record("difficulty", difficulty, True)
    else:
        _incr(stats, "qgate_exhausted")
        if rejection_tracker is not None:
            rejection_tracker.record("framework", framework, True)
            rejection_tracker.record("topic", topic, True)
            rejection_tracker.record("difficulty", difficulty, True)
        return "rejected_qgate"

    # Stage 2: student attempts the validated question
    try:
        student_code = student_attempt(cfg.student, question, task_domain=cfg.task_domain)
    except Exception as exc:
        _incr(stats, "student_attempt_errors")
        print(f"[rl_distill] student_attempt error: {exc}", flush=True)
        return "error"
    if not student_code:
        _incr(stats, "student_attempt_empty")
        return "error"
    code_only = extract_code_block(student_code)
    # In science mode the student writes prose+math, not code. Use the raw
    # student answer as the thing the teacher grades. code_only stays None
    # and is only used in metadata/coding-mode downstream paths.
    if cfg.task_domain == "science":
        student_answer_for_eval = student_code
    else:
        student_answer_for_eval = code_only

    # Stage 2.5: execute the student's code in a sandbox (real runtime evidence)
    student_exec: dict[str, Any] = {
        "verdict": "ERROR",
        "stdout": "",
        "stderr": "(sandbox disabled)",
        "exit_code": -1,
        "runtime_ms": 0,
        "truncated": False,
    }
    if cfg.sandbox.enabled:
        try:
            student_exec = execute_code(
                code_only,
                timeout_seconds=cfg.sandbox.timeout_seconds,
                memory_gib=cfg.sandbox.memory_gib,
            )
        except Exception as exc:
            _incr(stats, "student_exec_errors")
            print(f"[rl_distill] student_exec error: {exc}", flush=True)
            student_exec = {
                "verdict": "ERROR",
                "stdout": "",
                "stderr": f"sandbox error: {exc}",
                "exit_code": -1,
                "runtime_ms": 0,
                "truncated": False,
            }
        _incr(stats, f"student_exec_{student_exec.get('verdict', 'ERROR').lower()}")
    exec_brief = format_exec_brief(student_exec)

    # Stage 2.6: program-shape enforcement (coding mode only).
    # Static AST check that the student wrote a full program with a main()
    # entry point + __main__ guard, and runtime check that it printed a
    # concrete result. This hardens the question-shape contract that is
    # otherwise only prompt-enforced.
    program_shape: dict[str, Any] = {
        "has_main_def": None,
        "has_main_guard": None,
        "calls_main": None,
        "is_full_program": None,
        "stdout_nonempty": None,
        "issues": [],
    }
    if cfg.task_domain == "coding":
        shape = check_program_shape(code_only)
        program_shape.update(shape)
        if student_exec.get("verdict") == "PASS":
            stdout_check = check_stdout_nonempty(student_exec)
            program_shape["stdout_nonempty"] = stdout_check["stdout_nonempty"]
            program_shape["issues"].extend(stdout_check["issues"])
        if not shape["is_full_program"]:
            _incr(stats, "student_shape_rejected")
        elif student_exec.get("verdict") == "PASS" and not program_shape["stdout_nonempty"]:
            _incr(stats, "student_shape_empty_stdout")

    # Stage 3: teacher grades + corrects (grounded in the execution result)
    try:
        eval_result = teacher_eval(
            cfg.teacher,
            question,
            student_answer_for_eval,
            exec_brief=exec_brief,
            task_domain=cfg.task_domain,
        )
    except Exception as exc:
        _incr(stats, "teacher_eval_errors")
        print(f"[rl_distill] teacher_eval error: {exc}", flush=True)
        return "error"
    if eval_result.get("_parse_error"):
        _incr(stats, "teacher_eval_parse_errors")
        return "rejected_eval"
    correct_answer = eval_result.get("correct_answer", "") or ""
    if not correct_answer or len(correct_answer) < cfg.guardrail.min_corrected_answer_chars:
        _incr(stats, "teacher_correction_empty")
        if rejection_tracker is not None:
            rejection_tracker.record("framework", framework, True)
            rejection_tracker.record("topic", topic, True)
            rejection_tracker.record("difficulty", difficulty, True)
        return "rejected_eval"
    # Teacher-confidence guardrail: drop low-confidence corrections.
    confidence = float(eval_result.get("confidence", 1.0) or 1.0)
    if confidence < cfg.guardrail.min_teacher_confidence:
        _incr(stats, "teacher_low_confidence")
        if rejection_tracker is not None:
            rejection_tracker.record("framework", framework, True)
            rejection_tracker.record("topic", topic, True)
            rejection_tracker.record("difficulty", difficulty, True)
        return "rejected_eval"

    # Stage 4: teacher re-emits the corrected answer with per-token top-k logprobs
    try:
        correction = teacher_correction_with_logits(
            cfg.teacher, question, correct_answer, task_domain=cfg.task_domain
        )
    except Exception as exc:
        _incr(stats, "teacher_logprobs_errors")
        print(f"[rl_distill] teacher_logprobs error: {exc}", flush=True)
        return "error"
    if not correction.get("content") or not correction.get("logprobs"):
        _incr(stats, "teacher_logprobs_empty")
        return "error"

    # Stage 4.5: dedup against the rolling index
    if dedup_index is not None and dedup_index.is_duplicate(question, correct_answer):
        _incr(stats, "duplicates_dropped")
        return "duplicate"

    # Stage 4.6: double-confirmation gate — execute the teacher's corrected code.
    # A corrected sample is admitted to the SFT set ONLY if the teacher's
    # corrected code actually runs to PASS. This is the "correct code in
    # teacher's evaluation (double confirm)" requirement.
    teacher_exec: dict[str, Any] = {
        "verdict": "ERROR",
        "stdout": "",
        "stderr": "(sandbox disabled)",
        "exit_code": -1,
        "runtime_ms": 0,
        "truncated": False,
    }
    teacher_correct_code = extract_code_block(correct_answer) or correct_answer
    if cfg.sandbox.enabled:
        try:
            teacher_exec = execute_code(
                teacher_correct_code,
                timeout_seconds=cfg.sandbox.timeout_seconds,
                memory_gib=cfg.sandbox.memory_gib,
            )
        except Exception as exc:
            _incr(stats, "teacher_exec_errors")
            print(f"[rl_distill] teacher_exec error: {exc}", flush=True)
            teacher_exec = {
                "verdict": "ERROR",
                "stdout": "",
                "stderr": f"sandbox error: {exc}",
                "exit_code": -1,
                "runtime_ms": 0,
                "truncated": False,
            }
        _incr(stats, f"teacher_exec_{teacher_exec.get('verdict', 'ERROR').lower()}")
        if cfg.sandbox.reject_on_teacher_exec_fail and teacher_exec.get("verdict") != "PASS":
            _incr(stats, "teacher_exec_rejected")
            buffer.append_rejection(
                {
                    "framework": framework,
                    "topic": topic,
                    "difficulty": difficulty,
                    "question": question,
                    "student_code": code_only,
                    "student_exec": student_exec,
                    "teacher_correct_answer": correct_answer,
                    "teacher_exec": teacher_exec,
                    "teacher_eval": eval_result,
                    "reason": "teacher_corrected_code_failed_execution",
                    "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )
            if rejection_tracker is not None:
                rejection_tracker.record("framework", framework, True)
                rejection_tracker.record("topic", topic, True)
                rejection_tracker.record("difficulty", difficulty, True)
            return "rejected_teacher_exec"

    # Stage 4.7: override teacher's is_correct with execution ground truth.
    # If exec_is_ground_truth, a sample is only "correct" if the student's
    # code actually ran to PASS. This prevents the teacher from green-
    # lighting code that looks right but doesn't run.
    if cfg.sandbox.enabled and cfg.sandbox.exec_is_ground_truth:
        if student_exec.get("verdict") == "PASS":
            eval_result["is_correct"] = True
        else:
            eval_result["is_correct"] = False

    # Stage 5: build and append the SFT sample
    sample = _build_sample(
        cfg=cfg,
        question=question,
        framework=framework,
        topic=topic,
        difficulty=difficulty,
        student_code=student_answer_for_eval,
        teacher_eval_result=eval_result,
        teacher_correction=correction,
        qgate=qgate,
        student_qgen_meta={
            "temperature": cfg.student.temperature,
            "resample_attempts": resample_attempts,
        },
        student_exec=student_exec,
        teacher_exec=teacher_exec,
        program_shape=program_shape,
    )
    buffer.append_sample(sample)
    _incr(stats, "samples_appended")
    # Science-mode guardrail accounting: track fabricated-claim rate and
    # mean citation grounding over accepted samples.
    if cfg.task_domain == "science":
        if eval_result.get("fabricated_claim"):
            _incr(stats, "fabricated_claim_count")
        g_val = eval_result.get("citation_grounding")
        try:
            g_float = float(g_val) if g_val is not None else 0.5
        except (TypeError, ValueError):
            g_float = 0.5
        g_float = max(0.0, min(1.0, g_float))
        with stats_lock:
            stats["grounding_sum"] = stats.get("grounding_sum", 0.0) + g_float
    # Record acceptance so the rejection tracker's acceptance rate goes up.
    if rejection_tracker is not None:
        rejection_tracker.record("framework", framework, False)
        rejection_tracker.record("topic", topic, False)
        rejection_tracker.record("difficulty", difficulty, False)
    return "appended"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument(
        "--buffer-dir", type=Path, default=None, help="Override output_dir from config"
    )
    parser.add_argument(
        "--target-buffer-size",
        type=int,
        default=256,
        help="Stop once the buffer reaches this many samples (0 = run forever)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Stop after this many iterations (0 = unlimited)",
    )
    parser.add_argument(
        "--manifest-every",
        type=int,
        default=8,
        help="Write the buffer manifest every N appended samples",
    )
    parser.add_argument("--seed", type=int, default=None, help="Override the seed from config")
    parser.add_argument(
        "--max-wallclock-seconds",
        type=int,
        default=0,
        help="Stop after this many seconds of wall-clock time (0 = unlimited)",
    )
    parser.add_argument(
        "--pass-rate-stop",
        type=float,
        default=0.0,
        help="Stop when the student's execution pass-rate over the "
        "last --pass-rate-window samples reaches this fraction "
        "(e.g. 0.99). 0 = disabled.",
    )
    parser.add_argument(
        "--pass-rate-window",
        type=int,
        default=100,
        help="Minimum number of recent samples to consider for " "--pass-rate-stop (default 100).",
    )
    parser.add_argument(
        "--weakness-report",
        type=str,
        default="",
        help="Path to a weakness report JSON to bias question "
        "generation toward the student's weak cells. "
        "Overrides weakness_aware.report_path in config.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=0,
        help="Number of in-flight RL+distill iterations (0 = use config value). "
        "Each iteration is 5 sequential LLM calls, so this is I/O-bound "
        "and safe to set to 4-8 on a single vLLM student + remote teacher.",
    )
    parser.add_argument(
        "--guardrail-max-consecutive-rejections",
        type=int,
        default=0,
        help="Override guardrail.max_consecutive_teacher_rejections (0 = use config).",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.buffer_dir is not None:
        cfg.output_dir = args.buffer_dir
    if args.seed is not None:
        cfg.seed = args.seed
    rng = random.Random(cfg.seed)

    buffer = BufferWriter(cfg.output_dir, name="rl_distill")
    _install_signal_handlers()

    # Apply CLI overrides for guardrails / concurrency.
    if args.guardrail_max_consecutive_rejections > 0:
        cfg.guardrail.max_consecutive_teacher_rejections = args.guardrail_max_consecutive_rejections
    if args.concurrency > 0:
        cfg.concurrency = args.concurrency

    # Rejection-aware distribution tracker (built from the config priors).
    rejection_tracker = RejectionTracker(
        {
            "framework": cfg.question_gen.framework_distribution,
            "topic": cfg.question_gen.topic_distribution,
            "difficulty": cfg.question_gen.difficulty_distribution,
        }
    )
    # Dedup index sized from config.
    dedup_index = (
        DedupIndex(max_entries=int(cfg.dedup.get("max_entries", 20000)))
        if cfg.dedup.get("enabled", True)
        else None
    )

    # Weakness-aware question-generation report. When the config supplies
    # a `weakness_report_path`, the pipeline (re)loads it between batches
    # so the next batch's (framework, topic, difficulty) sampler biases
    # toward the student's diagnosed weak cells from the last batch.
    weakness_report: WeaknessReport | None = None
    wa_cfg = cfg.weakness_aware or {}
    if wa_cfg.get("enabled", False):
        weakness_report = WeaknessReport(
            prior={
                "framework": cfg.question_gen.framework_distribution,
                "topic": cfg.question_gen.topic_distribution,
                "difficulty": cfg.question_gen.difficulty_distribution,
            },
            alpha=float(wa_cfg.get("alpha", 0.4)),
            min_weight=float(wa_cfg.get("min_weight", 0.05)),
        )
        wr_path = wa_cfg.get("report_path", "")
        if args.weakness_report:
            wr_path = args.weakness_report
        if wr_path and weakness_report.load(wr_path):
            print(
                json.dumps(
                    {
                        "stage": "weakness_report_loaded",
                        "path": wr_path,
                        "loaded_at": weakness_report.loaded_at,
                    }
                ),
                flush=True,
            )

    stats = {
        "iterations": 0,
        "samples_appended": 0,
        "qgate_rejected": 0,
        "qgate_exhausted": 0,
        "student_qgen_errors": 0,
        "student_qgen_empty": 0,
        "teacher_qgate_errors": 0,
        "teacher_qgate_parse_errors": 0,
        "student_attempt_errors": 0,
        "student_attempt_empty": 0,
        "teacher_eval_errors": 0,
        "teacher_eval_parse_errors": 0,
        "teacher_correction_empty": 0,
        "teacher_low_confidence": 0,
        "teacher_logprobs_errors": 0,
        "teacher_logprobs_empty": 0,
        "duplicates_dropped": 0,
        "rejected_eval": 0,
        "rejected_teacher_exec": 0,
        "concurrent_in_flight": 0,
        "guardrail_trips": 0,
        "eval_gate_trips": 0,
        "student_exec_pass": 0,
        "student_exec_fail": 0,
        "student_exec_error": 0,
        "teacher_exec_pass": 0,
        "teacher_exec_fail": 0,
        "teacher_exec_error": 0,
        "student_exec_errors": 0,
        "teacher_exec_errors": 0,
        "student_shape_rejected": 0,
        "student_shape_empty_stdout": 0,
        # Science-mode guardrail counters (cumulative since pipeline start).
        "fabricated_claim_count": 0,
        "grounding_sum": 0.0,
        "qgate_science_requires_code": 0,
    }
    stats_lock = threading.Lock()
    # Rolling window of recent accept/reject outcomes for guardrail checks.
    recent_outcomes: list[bool] = []  # True = accepted, False = rejected
    outcomes_lock = threading.Lock()
    consecutive_rejections = 0
    # Science-mode rolling window of (fabricated, grounding) for the last N
    # accepted samples. Used by the science guardrails.
    recent_science: list[tuple[bool, float]] = []
    science_lock = threading.Lock()

    print(
        json.dumps(
            {
                "stage": "rl_distill_start",
                "config": str(args.config),
                "buffer_dir": str(cfg.output_dir),
                "student_api_base": cfg.student.api_base,
                "teacher_api_base": cfg.teacher.api_base,
                "teacher_model": cfg.teacher.model,
                "target_buffer_size": args.target_buffer_size,
                "max_iterations": args.max_iterations,
                "concurrency": int(cfg.concurrency),
                "guardrail": {
                    "max_consecutive_teacher_rejections": cfg.guardrail.max_consecutive_teacher_rejections,
                    "max_teacher_qgate_rejection_rate": cfg.guardrail.max_teacher_qgate_rejection_rate,
                    "min_teacher_confidence": cfg.guardrail.min_teacher_confidence,
                    "min_corrected_answer_chars": cfg.guardrail.min_corrected_answer_chars,
                    "rolling_window": cfg.guardrail.rolling_window,
                    "max_fabricated_claim_rate": cfg.guardrail.max_fabricated_claim_rate,
                    "min_citation_grounding": cfg.guardrail.min_citation_grounding,
                },
                "task_domain": cfg.task_domain,
                "dedup_enabled": dedup_index is not None,
                "reward_weighting": cfg.reward_weighting,
                "per_artifact_scoring": cfg.per_artifact_scoring,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    start_time = time.time()
    last_manifest_count = 0
    last_eval_gate_check = 0.0  # forces an immediate first poll if gate is enabled
    last_weakness_reload = 0  # samples_appended count at last weakness-report reload
    workers = max(1, int(cfg.concurrency))

    def _tick_stats(status: str) -> None:
        """Update stats and guardrail state from a process_one return value."""
        nonlocal consecutive_rejections
        with stats_lock:
            if status == "rejected_eval":
                _incr(stats, "rejected_eval")
            elif status == "duplicate":
                pass  # already counted in process_one
            elif status == "appended":
                pass  # already counted in process_one
            # "error" / "rejected_qgate" already counted in process_one
        with outcomes_lock:
            accepted = status == "appended"
            recent_outcomes.append(accepted)
            if len(recent_outcomes) > cfg.guardrail.rolling_window:
                recent_outcomes.pop(0)
            if accepted:
                consecutive_rejections = 0
            else:
                consecutive_rejections += 1

    def _guardrail_tripped() -> str | None:
        """Return a reason string if a guardrail is tripped, else None."""
        if consecutive_rejections >= cfg.guardrail.max_consecutive_teacher_rejections:
            return (
                f"max_consecutive_teacher_rejections={consecutive_rejections} "
                f">= {cfg.guardrail.max_consecutive_teacher_rejections}"
            )
        with outcomes_lock:
            n = len(recent_outcomes)
            if n >= cfg.guardrail.rolling_window:
                accepted = sum(1 for x in recent_outcomes if x)
                rej_rate = 1.0 - (accepted / max(n, 1))
                if rej_rate >= cfg.guardrail.max_teacher_qgate_rejection_rate:
                    return (
                        f"qgate_rejection_rate={rej_rate:.2f} over last {n} samples "
                        f">= {cfg.guardrail.max_teacher_qgate_rejection_rate}"
                    )
        # Science-mode guardrails (only checked when task_domain == "science").
        # Use cumulative rates over accepted samples once we have at least
        # rolling_window of them.
        if cfg.task_domain == "science":
            with stats_lock:
                n_appended = stats["samples_appended"]
                n_fab = stats["fabricated_claim_count"]
                g_sum = stats["grounding_sum"]
            if n_appended >= cfg.guardrail.rolling_window:
                fab_rate = n_fab / max(n_appended, 1)
                if fab_rate >= cfg.guardrail.max_fabricated_claim_rate:
                    return (
                        f"fabricated_claim_rate={fab_rate:.2f} over {n_appended} samples "
                        f">= {cfg.guardrail.max_fabricated_claim_rate}"
                    )
                mean_grounding = g_sum / max(n_appended, 1)
                if mean_grounding < cfg.guardrail.min_citation_grounding:
                    return (
                        f"mean_citation_grounding={mean_grounding:.2f} over {n_appended} samples "
                        f"< {cfg.guardrail.min_citation_grounding}"
                    )
        return None

    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            in_flight: set = set()
            while not shutdown_requested["flag"]:
                # Stop conditions
                if args.max_iterations and stats["iterations"] >= args.max_iterations:
                    print("[rl_distill] reached max_iterations; stopping", flush=True)
                    break
                if args.target_buffer_size and stats["samples_appended"] >= args.target_buffer_size:
                    print(
                        f"[rl_distill] reached target_buffer_size={args.target_buffer_size}; stopping",
                        flush=True,
                    )
                    break
                if (
                    args.max_wallclock_seconds
                    and (time.time() - start_time) >= args.max_wallclock_seconds
                ):
                    print("[rl_distill] reached max_wallclock_seconds; stopping", flush=True)
                    break
                # 99% pass-rate stop condition: if the student's code passes
                # execution on >= 99% of the most recent `pass_rate_window`
                # samples, the student has effectively converged on this
                # batch's topic mix and we stop collecting.
                if args.pass_rate_stop > 0:
                    window = max(20, int(args.pass_rate_window))
                    with stats_lock:
                        n_pass = stats["student_exec_pass"]
                        n_fail = stats["student_exec_fail"] + stats["student_exec_error"]
                    n_total = n_pass + n_fail
                    if n_total >= window:
                        rate = n_pass / max(n_total, 1)
                        if rate >= float(args.pass_rate_stop):
                            print(
                                json.dumps(
                                    {
                                        "stage": "rl_distill_pass_rate_stop",
                                        "pass_rate": rate,
                                        "n_total": n_total,
                                        "threshold": args.pass_rate_stop,
                                    },
                                    ensure_ascii=False,
                                ),
                                flush=True,
                            )
                            break
                # Guardrail check
                reason = _guardrail_tripped()
                if reason is not None:
                    _incr(stats, "guardrail_trips")
                    print(
                        json.dumps(
                            {
                                "stage": "rl_distill_guardrail_trip",
                                "reason": reason,
                                "stats": stats,
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
                    break

                # Eval-regression gate: poll external verdict file.
                # The orchestrator runs evals/subsystem/harness.py between rounds
                # and writes a verdict JSON; we just read it and decide.
                if (
                    cfg.eval_gate.enabled
                    and (time.time() - last_eval_gate_check) >= cfg.eval_gate.poll_every_seconds
                ):
                    last_eval_gate_check = time.time()
                    verdict = _read_eval_verdict(cfg.eval_gate.verdict_path)
                    if verdict is not None:
                        gate_reason = _eval_gate_tripped(cfg.eval_gate, verdict)
                        if gate_reason is not None:
                            _incr(stats, "eval_gate_trips")
                            print(
                                json.dumps(
                                    {
                                        "stage": "rl_distill_eval_gate_trip",
                                        "reason": gate_reason,
                                        "verdict": verdict,
                                        "stats": stats,
                                    },
                                    ensure_ascii=False,
                                ),
                                flush=True,
                            )
                            break
                        else:
                            # Log a heartbeat so the orchestrator knows the gate is active.
                            print(
                                json.dumps(
                                    {
                                        "stage": "rl_distill_eval_gate_ok",
                                        "pass_at_1": verdict.get("adapter_eval_pass_at_1"),
                                        "baseline_pass_at_1": verdict.get(
                                            "baseline_eval_pass_at_1"
                                        ),
                                    },
                                    ensure_ascii=False,
                                ),
                                flush=True,
                            )

                # Top up the in-flight pool
                while len(in_flight) < workers and not shutdown_requested["flag"]:
                    fut = pool.submit(
                        process_one,
                        cfg,
                        rng,
                        buffer,
                        stats,
                        rejection_tracker=rejection_tracker,
                        dedup_index=dedup_index,
                        weakness_report=weakness_report,
                    )
                    in_flight.add(fut)
                    with stats_lock:
                        _incr(stats, "iterations")
                        stats["concurrent_in_flight"] = len(in_flight)
                # Wait for at least one to complete
                if not in_flight:
                    continue
                done_now = set()
                for fut in as_completed(in_flight, timeout=None):
                    done_now.add(fut)
                    try:
                        status = fut.result()
                    except Exception as exc:  # noqa: BLE001
                        _incr(stats, "unexpected_errors")
                        print(f"[rl_distill] iteration error: {exc}", flush=True)
                        traceback.print_exc()
                        status = "error"
                    _tick_stats(status)
                    break  # re-check stop conditions + top up
                in_flight -= done_now
                with stats_lock:
                    stats["concurrent_in_flight"] = len(in_flight)

                # Periodic manifest write
                if stats["samples_appended"] - last_manifest_count >= args.manifest_every:
                    buffer.write_manifest(extra={"stats": stats, "config": str(args.config)})
                    last_manifest_count = stats["samples_appended"]
                    print(
                        json.dumps(
                            {"stage": "rl_distill_progress", "stats": stats}, ensure_ascii=False
                        ),
                        flush=True,
                    )
                # Periodic weakness-report reload (so a freshly written
                # report from the orchestrator's batch analyzer is picked
                # up without restarting the pipeline).
                if weakness_report is not None:
                    wa_cfg = cfg.weakness_aware or {}
                    reload_every = int(wa_cfg.get("reload_every_samples", 100))
                    wr_path = wa_cfg.get("report_path", "") or args.weakness_report
                    if (
                        wr_path
                        and reload_every > 0
                        and stats["samples_appended"] - last_weakness_reload >= reload_every
                    ):
                        if weakness_report.load(wr_path):
                            last_weakness_reload = stats["samples_appended"]
                            print(
                                json.dumps(
                                    {
                                        "stage": "weakness_report_reloaded",
                                        "path": wr_path,
                                        "loaded_at": weakness_report.loaded_at,
                                        "samples_appended": stats["samples_appended"],
                                    },
                                    ensure_ascii=False,
                                ),
                                flush=True,
                            )
            # Drain remaining in-flight tasks on shutdown
            for fut in in_flight:
                try:
                    fut.result(timeout=60)
                except Exception:  # noqa: BLE001
                    pass
    finally:
        buffer.write_manifest(
            extra={
                "stats": stats,
                "config": str(args.config),
                "shutdown": shutdown_requested["flag"],
            }
        )
        print(
            json.dumps({"stage": "rl_distill_exit", "stats": stats}, ensure_ascii=False), flush=True
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
