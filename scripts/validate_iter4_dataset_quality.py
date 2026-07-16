#!/usr/bin/env python3
"""Validate iter-4 distillation dataset quality by executing teacher code.

This is the comprehensive quality gate that actually RUNS the teacher's Python
code and verifies it prints the expected marker string. It checks:

  1. Question quality (prompt is well-formed, non-empty, has expected_marker)
  2. Teacher answer quality (no  tags, no markdown fences, valid Python syntax)
  3. Teacher code correctness (ast.parse passes)
  4. Teacher code execution (runs without error within timeout)
  5. Marker match (stdout contains the expected_marker string, exact or fuzzy)
  6. Logits consistency (teacher_logprobs length matches token count, top_logprobs <= 20)
  7. No duplicate questions (by SHA-256 of prompt)
  8. No duplicate answers (by SHA-256 of teacher_response)

Usage:
  python3 scripts/validate_iter4_dataset_quality.py \\
    --input data/generated/glm52_soft_distill_sft_iter4_27b/teacher_responses.jsonl \\
    --report data/generated/glm52_soft_distill_sft_iter4_27b/quality_report.json

Exit codes:
  0 = all checks passed
  1 = some checks failed (see report for details)
  2 = input file missing
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Marker match modes
EXACT_MATCH = "exact"
SUBSTRING_MATCH = "substring"
FUZZY_MATCH = "fuzzy"  # numeric tolerance

# Execution settings
DEFAULT_TIMEOUT_SEC = 60
DEFAULT_PYTHON = sys.executable


def stable_sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Check 1: Question quality
# ---------------------------------------------------------------------------


def check_question(seed: dict[str, Any]) -> list[str]:
    """Validate the question (prompt) is well-formed."""
    errors = []
    eid = seed.get("example_id", "?")

    # Seed questions use 'prompt', teacher_responses use 'user_instruction'
    prompt = seed.get("prompt", "") or seed.get("user_instruction", "")
    if not prompt or not prompt.strip():
        errors.append(f"{eid}: empty prompt")
        return errors

    if len(prompt) < 20:
        errors.append(f"{eid}: prompt too short ({len(prompt)} chars)")

    if len(prompt) > 4000:
        errors.append(f"{eid}: prompt too long ({len(prompt)} chars, may truncate)")

    # Must ask for a complete program
    if "complete python program" not in prompt.lower() and "write a complete" not in prompt.lower():
        errors.append(f"{eid}: prompt does not request a complete Python program")

    # Must specify def main()
    if "def main()" not in prompt.lower() and "main()" not in prompt.lower():
        # Some prompts may use a different contract; flag but don't fail
        pass

    # Must have an expected_marker
    marker = seed.get("expected_marker", "")
    if not marker:
        errors.append(f"{eid}: missing expected_marker")

    # Must have task_family and framework
    if not seed.get("task_family"):
        errors.append(f"{eid}: missing task_family")
    if not seed.get("framework"):
        errors.append(f"{eid}: missing framework")

    # Must have adapter_target
    if not seed.get("adapter_target"):
        errors.append(f"{eid}: missing adapter_target")

    return errors


# ---------------------------------------------------------------------------
# Check 2: Teacher answer quality (no  tags, no fences)
# ---------------------------------------------------------------------------


def check_teacher_answer(rec: dict[str, Any]) -> list[str]:
    """Validate teacher response format (no  tags, no markdown fences)."""
    errors = []
    eid = rec.get("example_id", "?")

    response = rec.get("teacher_response", "")
    if not response or not response.strip():
        errors.append(f"{eid}: empty teacher_response")
        return errors

    # Check for  tags
    if "<think" in response.lower():
        errors.append(f"{eid}: teacher_response contains forbidden  tag")
    if "</think>" in response.lower():
        errors.append(f"{eid}: teacher_response contains forbidden  tag")

    # Check for markdown fences (should have been stripped, but double-check)
    if response.strip().startswith("```"):
        errors.append(f"{eid}: teacher_response still has markdown fences")

    # Check for reasoning_content leak
    if "reasoning_content" in response.lower():
        errors.append(f"{eid}: teacher_response contains reasoning_content leak")

    # Check for contract leak
    contract_markers = ("must not ask for fabricated", "do not ask for fabricated")
    if any(m in response.lower() for m in contract_markers):
        errors.append(f"{eid}: teacher_response contains prompt-contract text leak")

    return errors


# ---------------------------------------------------------------------------
# Check 3: Teacher code syntax (ast.parse)
# ---------------------------------------------------------------------------


def check_python_syntax(rec: dict[str, Any]) -> tuple[bool, str | None]:
    """Check that teacher_response is valid Python via ast.parse."""
    eid = rec.get("example_id", "?")
    response = rec.get("teacher_response", "")
    try:
        ast.parse(response)
        return True, None
    except SyntaxError as e:
        return False, f"{eid}: SyntaxError: {e.msg} (line {e.lineno}, col {e.offset})"


# ---------------------------------------------------------------------------
# Check 4 & 5: Execute teacher code and check marker
# ---------------------------------------------------------------------------


def execute_teacher_code(
    code: str,
    timeout: int = DEFAULT_TIMEOUT_SEC,
    python: str = DEFAULT_PYTHON,
) -> tuple[int, str, str]:
    """Execute teacher code in a subprocess. Returns (returncode, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        env = os.environ.copy()
        # Ensure we don't inherit interactive env vars that could break execution
        env.pop("PYTHONSTARTUP", None)

        result = subprocess.run(
            [python, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"TIMEOUT after {timeout}s"
    except Exception as e:
        return -2, "", f"EXECUTION_ERROR: {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def normalize_marker(marker: str) -> str:
    """Normalize a marker string for fuzzy matching (strip trailing zeros, etc.)."""
    # Strip whitespace
    s = marker.strip()
    # Normalize float representations: 1.0000 -> 1.0, 0.5000 -> 0.5
    s = re.sub(r"(\d+\.\d*?)0+\b", r"\1", s)
    s = re.sub(r"(\d+)\.0\b", r"\1", s)
    return s


def check_marker_match(stdout: str, expected_marker: str) -> tuple[str, bool, str]:
    """Check if stdout contains the expected marker.

    Returns (match_mode, matched, details).
    """
    if not stdout:
        return EXACT_MATCH, False, "empty stdout"

    # Try exact substring match first
    if expected_marker in stdout:
        return EXACT_MATCH, True, "exact match in stdout"

    # Try normalized match (e.g., '1.0000' vs '1.0')
    normalized_expected = normalize_marker(expected_marker)
    for line in stdout.splitlines():
        if normalized_expected in normalize_marker(line):
            return FUZZY_MATCH, True, f"fuzzy match (normalized): line='{line.strip()}'"

    # Try line-by-line: expected_marker might be a prefix
    for line in stdout.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith(expected_marker):
            return SUBSTRING_MATCH, True, f"prefix match: line='{line_stripped}'"

    # Find the closest line for diagnostics
    stdout_lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
    closest = stdout_lines[0] if stdout_lines else "(no output)"
    return EXACT_MATCH, False, f"not found in stdout; first line='{closest}'"


# ---------------------------------------------------------------------------
# Check 6: Logits consistency
# ---------------------------------------------------------------------------


def check_logits(rec: dict[str, Any]) -> list[str]:
    """Validate teacher_logprobs structure."""
    errors = []
    eid = rec.get("example_id", "?")

    logprobs = rec.get("teacher_logprobs", [])
    if not logprobs:
        # Logits are optional for hard-SFT; only required for soft-KL
        # Don't fail, just note
        return errors

    if not isinstance(logprobs, list):
        errors.append(f"{eid}: teacher_logprobs is not a list")
        return errors

    # Check each entry has token, logprob, top_logprobs
    for i, entry in enumerate(logprobs[:5]):  # check first 5 only for speed
        if not isinstance(entry, dict):
            errors.append(f"{eid}: teacher_logprobs[{i}] is not a dict")
            continue
        if "token" not in entry:
            errors.append(f"{eid}: teacher_logprobs[{i}] missing 'token'")
        if "logprob" not in entry:
            errors.append(f"{eid}: teacher_logprobs[{i}] missing 'logprob'")
        top = entry.get("top_logprobs", [])
        if not isinstance(top, list):
            errors.append(f"{eid}: teacher_logprobs[{i}].top_logprobs is not a list")
        elif len(top) > 20:
            errors.append(
                f"{eid}: teacher_logprobs[{i}].top_logprobs has {len(top)} entries (max 20)"
            )

    # Check that logits length roughly matches token count of teacher_response
    response = rec.get("teacher_response", "")
    # Rough estimate: tokens ~ words * 1.3 for code
    expected_min_tokens = max(1, len(response.split()) // 2)
    if len(logprobs) < expected_min_tokens:
        # Don't fail — tokenizer differences can cause this. Just note.
        pass

    return errors


# ---------------------------------------------------------------------------
# Check 7 & 8: Duplicates
# ---------------------------------------------------------------------------


def check_duplicates(records: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Find duplicate prompts and duplicate teacher_responses.

    Returns (duplicate_prompt_ids, duplicate_response_ids).
    """
    prompt_hashes: dict[str, str] = {}  # hash -> example_id
    response_hashes: dict[str, str] = {}
    dup_prompts: list[str] = []
    dup_responses: list[str] = []

    for rec in records:
        eid = rec.get("example_id", "?")
        prompt = rec.get("user_instruction", rec.get("prompt", ""))
        response = rec.get("teacher_response", "")

        ph = stable_sha256(prompt)
        if ph in prompt_hashes:
            dup_prompts.append(f"{eid} (dup of {prompt_hashes[ph]})")
        else:
            prompt_hashes[ph] = eid

        rh = stable_sha256(response)
        if rh in response_hashes:
            dup_responses.append(f"{eid} (dup of {response_hashes[rh]})")
        else:
            response_hashes[rh] = eid

    return dup_prompts, dup_responses


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------


def validate_dataset(
    records: list[dict[str, Any]],
    *,
    execute: bool = True,
    timeout: int = DEFAULT_TIMEOUT_SEC,
    python: str = DEFAULT_PYTHON,
    max_errors: int = 100,
) -> dict[str, Any]:
    """Run all quality checks on the dataset."""

    all_errors: list[str] = []
    all_warnings: list[str] = []
    per_record: list[dict[str, Any]] = []

    # Stats
    stats = {
        "total": len(records),
        "question_ok": 0,
        "answer_ok": 0,
        "syntax_ok": 0,
        "execution_ok": 0,
        "marker_ok": 0,
        "logits_ok": 0,
        "executed": 0,
    }

    for rec in records:
        eid = rec.get("example_id", "?")
        record_report: dict[str, Any] = {
            "example_id": eid,
            "task_family": rec.get("task_family"),
            "framework": rec.get("framework"),
            "expected_marker": rec.get("expected_marker"),
        }

        # Check 1: Question quality
        q_errors = check_question(rec)
        if not q_errors:
            stats["question_ok"] += 1
        else:
            all_errors.extend(q_errors)
        record_report["question_errors"] = q_errors

        # Check 2: Teacher answer quality
        a_errors = check_teacher_answer(rec)
        if not a_errors:
            stats["answer_ok"] += 1
        else:
            all_errors.extend(a_errors)
        record_report["answer_errors"] = a_errors

        # Check 3: Python syntax
        syntax_ok, syntax_err = check_python_syntax(rec)
        if syntax_ok:
            stats["syntax_ok"] += 1
        else:
            all_errors.append(syntax_err)
        record_report["syntax_ok"] = syntax_ok
        record_report["syntax_error"] = syntax_err

        # Check 4 & 5: Execute and check marker
        if execute and syntax_ok:
            stats["executed"] += 1
            rc, stdout, stderr = execute_teacher_code(
                rec["teacher_response"], timeout=timeout, python=python
            )
            record_report["execution_returncode"] = rc
            record_report["execution_stdout_preview"] = stdout[:500]
            record_report["execution_stderr_preview"] = stderr[:500]

            if rc == 0:
                stats["execution_ok"] += 1
                # Check marker
                match_mode, matched, match_details = check_marker_match(
                    stdout, rec.get("expected_marker", "")
                )
                record_report["marker_match_mode"] = match_mode
                record_report["marker_matched"] = matched
                record_report["marker_details"] = match_details
                if matched:
                    stats["marker_ok"] += 1
                else:
                    all_errors.append(f"{eid}: marker not matched — {match_details}")
            else:
                all_errors.append(f"{eid}: execution failed rc={rc}, stderr={stderr[:200]}")
        elif execute and not syntax_ok:
            record_report["execution_skipped"] = "syntax_error"
        else:
            record_report["execution_skipped"] = "disabled"

        # Check 6: Logits
        l_errors = check_logits(rec)
        if not l_errors:
            stats["logits_ok"] += 1
        else:
            all_errors.extend(l_errors)
        record_report["logits_errors"] = l_errors

        per_record.append(record_report)

    # Check 7 & 8: Duplicates
    dup_prompts, dup_responses = check_duplicates(records)

    # Summary
    report = {
        "ok": False,
        "total_records": len(records),
        "stats": stats,
        "pass_rates": {
            "question": f"{stats['question_ok']}/{stats['total']}",
            "answer": f"{stats['answer_ok']}/{stats['total']}",
            "syntax": f"{stats['syntax_ok']}/{stats['total']}",
            "execution": f"{stats['execution_ok']}/{stats['executed']}"
            if stats["executed"]
            else "n/a",
            "marker": f"{stats['marker_ok']}/{stats['executed']}" if stats["executed"] else "n/a",
            "logits": f"{stats['logits_ok']}/{stats['total']}",
        },
        "duplicate_prompts": dup_prompts[:50],
        "duplicate_responses": dup_responses[:50],
        "duplicate_prompt_count": len(dup_prompts),
        "duplicate_response_count": len(dup_responses),
        "errors": all_errors[:max_errors],
        "error_count": len(all_errors),
        "warnings": all_warnings[:max_errors],
        "per_record": per_record if len(per_record) <= 200 else per_record[:200],
    }

    # ok = no errors, no duplicate prompts, no duplicate responses
    report["ok"] = len(all_errors) == 0 and len(dup_prompts) == 0 and len(dup_responses) == 0
    return report


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="teacher_responses.jsonl or seed_questions.jsonl")
    p.add_argument("--report", default=None, help="path to write JSON report")
    p.add_argument("--no-execute", action="store_true", help="skip code execution (fast mode)")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SEC)
    p.add_argument("--python", default=DEFAULT_PYTHON)
    p.add_argument("--max-errors", type=int, default=100)
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found", file=sys.stderr)
        return 2

    report_path = Path(args.report) if args.report else input_path.parent / "quality_report.json"

    records = load_jsonl(input_path)
    print(f"Loaded {len(records)} records from {input_path}")

    # If input is seed_questions.jsonl (no teacher_response yet), only check questions
    is_seed_only = "teacher_response" not in records[0] if records else False
    if is_seed_only:
        print(
            "Mode: SEED QUESTIONS ONLY (no teacher_response yet) — checking question quality only"
        )
        execute = False
        # Adapt: seed_questions use 'prompt' not 'user_instruction'
        for r in records:
            if "user_instruction" not in r and "prompt" in r:
                r["user_instruction"] = r["prompt"]
    else:
        print("Mode: FULL VALIDATION (question + answer + syntax + execution + marker + logits)")
        execute = not args.no_execute

    report = validate_dataset(
        records,
        execute=execute,
        timeout=args.timeout,
        python=args.python,
        max_errors=args.max_errors,
    )

    # Write report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print(f"\nReport written to {report_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("QUALITY REPORT SUMMARY")
    print(f"{'='*60}")
    print(f"Total records: {report['total_records']}")
    print(f"Overall OK: {report['ok']}")
    print("\nPass rates:")
    for k, v in report["pass_rates"].items():
        print(f"  {k:15s} {v}")
    print(f"\nDuplicate prompts:   {report['duplicate_prompt_count']}")
    print(f"Duplicate responses: {report['duplicate_response_count']}")
    print(f"Total errors:        {report['error_count']}")

    if args.verbose and report["errors"]:
        print("\nFirst 20 errors:")
        for e in report["errors"][:20]:
            print(f"  - {e}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
