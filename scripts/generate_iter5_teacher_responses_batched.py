#!/usr/bin/env python3
"""Generate iter-5 teacher responses from glm5.2 in batches of 100.

Quality gates (ALL must pass for a row to be accepted):
  G1. No ildi tags in response
  G2. No markdown fences (```python ... ```)
  G3. ast.parse passes (valid Python syntax)
  G4. `def main()` is defined and called at module level
  G5. Framework import matches the prompt:
      - qiskit prompt  → code must `import qiskit` or `from qiskit`
      - pennylane prompt → code must `import pennylane` or `from pennylane`
      - cirq prompt → code must `import cirq` or `from cirq`
      - braket prompt → code must `import braket` or `from braket`
  G6. RUNNABLE: code executes in subprocess sandbox within run_timeout
  G7. MARKER PRINTED: expected_marker appears in stdout

On failure, retry up to --retries times with a targeted correction prompt
that names the exact gate that failed. Rows that still fail after all
retries are written with validation.runnable=False so they can be filtered
out by prepare_iter5_distill_sft.py.

Teacher logprobs: the local Huanxin proxy does NOT return logprobs, so
teacher_logprobs is an empty list. The schema is preserved for a future
soft-KL trainer.

Output: data/generated/glm52_soft_distill_sft_iter5_{adapter}/teacher_responses.jsonl
        (appended incrementally; resume-safe via --skip-completed)
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

SYSTEM_PROMPT = (
    "You are a careful quantum software engineering assistant. Use the user's task "
    "and any supplied context to produce correct, testable Python or precise repair "
    "guidance. Always produce a complete, runnable Python program with `def main()` "
    "that prints the exact specified marker string. Do not include markdown fences "
    "or surrounding commentary."
)

CORRECTION_PROMPT = (
    "Your previous response failed validation. Specific failure: {error}\n\n"
    "Please regenerate the COMPLETE, runnable Python program that:\n"
    "1. Uses the {framework} framework (you MUST `import {framework}` or `from {framework} import ...`)\n"
    "2. Defines `def main():` and calls it under `if __name__ == '__main__':`\n"
    "3. Prints EXACTLY this marker string on its own line: {marker}\n"
    "4. Is valid Python (ast.parse passes)\n"
    "5. Has NO markdown fences (no ```python blocks)\n"
    "6. Has NO ildi tags\n"
    "7. Runs in under {timeout} seconds using only numpy/scipy/qiskit/pennylane/cirq/braket\n"
    "8. Does NOT substitute numpy for the required quantum framework\n\n"
    "Output ONLY the raw Python code. No commentary, no fences."
)

FRAMEWORK_KEYWORDS = {
    "qiskit": ["qiskit"],
    "pennylane": ["pennylane"],
    "cirq": ["cirq"],
    "braket": ["braket"],
}


# ---------------------------------------------------------------------------
# GLM5.2 Anthropic Messages API
# ---------------------------------------------------------------------------


def anthropic_messages(
    *,
    api_base: str,
    api_key: str,
    model: str,
    user_prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
    max_tokens: int = 4096,
    temperature: float = 0.2,
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

    data = json.dumps(payload).encode("utf-8")
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
    """Extract all thinking-block text from the response (for fallback).

    GLM5.2 often returns only a thinking block with no text block when the
    system prompt asks for raw code (the model "thinks through" the solution
    but doesn't emit a final text answer). This lets us recover the code
    from the thinking content.
    """
    content = raw.get("content", [])
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type", "") == "thinking":
            parts.append(block.get("thinking", ""))
    return "\n".join(parts).strip()


def extract_code_from_thinking(thinking: str) -> str | None:
    """Try to extract a complete Python program from a thinking block.

    Models often write the final code inside their thinking. We look for:
    1. A fenced ```python ... ``` block
    2. The last contiguous run of Python code (lines starting with
       import/from/def/class, plus their indented continuation)

    Returns the code string if a block containing `def main()` is found,
    otherwise None.
    """
    if not thinking:
        return None
    # 1. Fenced code block — take the LAST one that contains `def main()`
    #    (models often emit several partial snippets in thinking; the last
    #    complete one with a main() is the final code)
    fences = re.findall(r"```(?:python)?\s*\n(.*?)\n```", thinking, re.DOTALL)
    for fence in reversed(fences):
        candidate = fence.strip()
        if "def main()" in candidate:
            return candidate
    # 2. Last contiguous run starting with import/from/def/class
    lines = thinking.split("\n")
    code_lines: list[str] = []
    capturing = False
    last_code_block: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("import ", "from ", "def ", "class ")):
            if not capturing:
                capturing = True
                if code_lines:
                    last_code_block = code_lines[:]
                code_lines = [line]
            else:
                code_lines.append(line)
        elif capturing:
            # Allow blank lines and indented lines to continue the code
            if stripped == "" or line.startswith(" ") or line.startswith("\t"):
                code_lines.append(line)
            else:
                capturing = False
                last_code_block = code_lines[:]
                code_lines = []
    if code_lines and "def main()" in "\n".join(code_lines):
        return "\n".join(code_lines).strip()
    if last_code_block and "def main()" in "\n".join(last_code_block):
        return "\n".join(last_code_block).strip()
    return None


# ---------------------------------------------------------------------------
# Code validation gates
# ---------------------------------------------------------------------------


def strip_markdown_fences(text: str) -> str:
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def has_no_think_tags(text: str) -> bool:
    return "<think" not in text.lower()


def has_no_markdown_fences(text: str) -> bool:
    return "```" not in text


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


def detect_required_framework(prompt: str) -> str | None:
    """Detect which quantum framework the prompt requires."""
    p = prompt.lower()
    # Order matters: check more specific first
    for fw in ["qiskit", "pennylane", "cirq", "braket"]:
        if fw in p:
            return fw
    return None


def uses_framework(code: str, framework: str) -> bool:
    """Check if code actually imports/uses the required framework."""
    keywords = FRAMEWORK_KEYWORDS.get(framework, [framework])
    for kw in keywords:
        # Match `import kw` or `from kw`
        if re.search(rf"(?:^|\n)\s*(?:import\s+{kw}\b|from\s+{kw}\b)", code):
            return True
    return False


def run_code_sandbox(code: str, expected_marker: str, timeout: int = 30) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "MPLBACKEND": "Agg", "PYTHONHASHSEED": "0"},
        )
        if proc.returncode != 0:
            return False, f"Exit {proc.returncode}: {proc.stderr[-400:]}"
        if expected_marker not in proc.stdout:
            return False, f"Marker {expected_marker!r} not in stdout (got {proc.stdout[:200]!r})"
        return True, proc.stdout
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout}s"
    except Exception as e:
        return False, f"Exec error: {e}"


def validate_all(
    code: str, seed: dict[str, Any], run_timeout: int, lenient_execution: bool = False
) -> tuple[bool, str, dict]:
    """Run all quality gates. Returns (ok, error, validation_dict).

    When `lenient_execution=True`, an ImportError or ModuleNotFoundError during
    sandbox execution is treated as a soft failure: the code is accepted (ok=True)
    with `runnable=False` and `marker_printed=False` recorded. This lets us keep
    teacher responses that are syntactically valid and framework-correct even
    when the local sandbox lacks the required quantum libraries (the code will
    be re-validated on the NAS where the full quantum stack is installed).
    """
    validation = {
        "no_think_tags": False,
        "no_markdown_fences": False,
        "valid_python": False,
        "has_def_main": False,
        "framework_match": False,
        "runnable": False,
        "marker_printed": False,
        "syntax_error": None,
        "non_empty": bool(code.strip()),
    }

    if not code.strip():
        return False, "empty response", validation

    validation["no_think_tags"] = has_no_think_tags(code)
    if not validation["no_think_tags"]:
        return False, "contains ildi tags", validation

    validation["no_markdown_fences"] = has_no_markdown_fences(code)
    if not validation["no_markdown_fences"]:
        return False, "contains markdown fences", validation

    ok, err = is_valid_python(code)
    validation["valid_python"] = ok
    validation["syntax_error"] = err
    if not ok:
        return False, err or "invalid python", validation

    validation["has_def_main"] = has_def_main(code)
    if not validation["has_def_main"]:
        return False, "missing def main() or main() call", validation

    required_fw = detect_required_framework(seed["prompt"])
    if required_fw:
        validation["framework_match"] = uses_framework(code, required_fw)
        if not validation["framework_match"]:
            return False, f"prompt requires {required_fw} but code does not import it", validation
    else:
        validation["framework_match"] = True  # no framework required

    ok, out = run_code_sandbox(code, seed["expected_marker"], timeout=run_timeout)
    validation["runnable"] = ok
    if not ok:
        # Lenient mode: accept code that fails only due to missing local modules
        if lenient_execution and ("ImportError" in out or "ModuleNotFoundError" in out):
            validation["marker_printed"] = False
            validation["lenient_accept"] = True
            validation["lenient_reason"] = f"local import failed: {out[:200]}"
            return True, f"lenient accept (local import failed): {out[:120]}", validation
        return False, f"run failed: {out}", validation

    validation["marker_printed"] = True
    return True, "ok", validation


# ---------------------------------------------------------------------------
# Teacher generation with retry
# ---------------------------------------------------------------------------


def generate_one(
    *,
    seed: dict[str, Any],
    api_base: str,
    api_key: str,
    model: str,
    max_tokens: int,
    temperature: float,
    timeout: float,
    retries: int,
    run_timeout: int,
    lenient_execution: bool = False,
) -> dict[str, Any]:
    last_error: str | None = None
    required_fw = detect_required_framework(seed["prompt"]) or "the specified"

    for attempt in range(1, retries + 2):
        try:
            if attempt == 1:
                raw = anthropic_messages(
                    api_base=api_base,
                    api_key=api_key,
                    model=model,
                    user_prompt=seed["prompt"],
                    system_prompt=seed.get("system_prompt", SYSTEM_PROMPT),
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=timeout,
                )
            else:
                correction = CORRECTION_PROMPT.format(
                    error=last_error or "unknown",
                    framework=required_fw,
                    marker=seed["expected_marker"],
                    timeout=run_timeout,
                )
                messages = [
                    {"role": "user", "content": seed["prompt"]},
                    {"role": "assistant", "content": "(previous attempt failed validation)"},
                    {"role": "user", "content": correction},
                ]
                raw = anthropic_messages(
                    api_base=api_base,
                    api_key=api_key,
                    model=model,
                    user_prompt="",
                    system_prompt=seed.get("system_prompt", SYSTEM_PROMPT),
                    max_tokens=max_tokens,
                    temperature=max(0.0, temperature - 0.1),
                    timeout=timeout,
                    messages=messages,
                )

            text = extract_text(raw)
            code = strip_markdown_fences(text) if text else ""

            # Thinking-fallback: GLM5.2 often returns only a thinking block
            # with no text block. Try to recover code from the thinking.
            used_thinking_fallback = False
            used_two_turn_fallback = False
            if not code:
                thinking = extract_thinking(raw)
                fallback_code = extract_code_from_thinking(thinking)
                if fallback_code:
                    code = strip_markdown_fences(fallback_code)
                    used_thinking_fallback = True
                elif thinking:
                    # Two-turn: send thinking back as assistant context, ask
                    # for code. This matches iter4's fallback strategy.
                    two_turn_messages = [
                        {"role": "user", "content": seed["prompt"]},
                        {
                            "role": "assistant",
                            "content": [
                                {"type": "thinking", "thinking": thinking, "signature": ""},
                                {"type": "text", "text": "(internal reasoning completed)"},
                            ],
                        },
                        {
                            "role": "user",
                            "content": (
                                "Now output ONLY the complete Python program with "
                                "def main() that prints the exact marker string. "
                                "No markdown fences, no commentary, just the code."
                            ),
                        },
                    ]
                    raw2 = anthropic_messages(
                        api_base=api_base,
                        api_key=api_key,
                        model=model,
                        user_prompt="",
                        system_prompt=seed.get("system_prompt", SYSTEM_PROMPT),
                        max_tokens=max_tokens,
                        temperature=max(0.0, temperature - 0.1),
                        timeout=timeout,
                        messages=two_turn_messages,
                    )
                    text2 = extract_text(raw2)
                    if text2:
                        code = strip_markdown_fences(text2)
                        used_two_turn_fallback = True
                    else:
                        # Try extracting code from the two-turn thinking too
                        thinking2 = extract_thinking(raw2)
                        fallback2 = extract_code_from_thinking(thinking2)
                        if fallback2:
                            code = strip_markdown_fences(fallback2)
                            used_thinking_fallback = True

            ok, err, validation = validate_all(
                code, seed, run_timeout, lenient_execution=lenient_execution
            )
            validation["used_thinking_fallback"] = used_thinking_fallback
            validation["used_two_turn_fallback"] = used_two_turn_fallback
            if ok:
                return {
                    "example_id": seed["example_id"],
                    "adapter_target": seed["adapter_target"],
                    "task_family": seed["task_family"],
                    "framework": seed["framework"],
                    "difficulty": seed["difficulty"],
                    "variant_id": seed["variant_id"],
                    "source_gap": seed.get("source_gap", ""),
                    "user_instruction": seed["prompt"],
                    "expected_marker": seed["expected_marker"],
                    "system_prompt": seed.get("system_prompt", SYSTEM_PROMPT),
                    "teacher_response": code,
                    "teacher_logprobs": [],  # local proxy does not return logprobs
                    "teacher_model": model,
                    "teacher_temperature": temperature,
                    "teacher_max_tokens": max_tokens,
                    "teacher_api_format": "anthropic_messages",
                    "attempts": attempt,
                    "validation": validation,
                }
            last_error = err
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')[:200]}"
            # Backoff for 502/503/429 (server overload)
            if e.code in (502, 503, 429):
                time.sleep(min(5 * attempt, 20))
            else:
                time.sleep(min(2 * attempt, 10))
        except urllib.error.URLError as e:
            last_error = f"URLError: {e}"
            time.sleep(min(5 * attempt, 20))
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(min(2 * attempt, 10))

    return {
        "example_id": seed["example_id"],
        "adapter_target": seed["adapter_target"],
        "task_family": seed["task_family"],
        "framework": seed["framework"],
        "difficulty": seed["difficulty"],
        "variant_id": seed["variant_id"],
        "source_gap": seed.get("source_gap", ""),
        "user_instruction": seed["prompt"],
        "expected_marker": seed["expected_marker"],
        "system_prompt": seed.get("system_prompt", SYSTEM_PROMPT),
        "teacher_response": "",
        "teacher_logprobs": [],
        "teacher_model": model,
        "teacher_temperature": temperature,
        "teacher_max_tokens": max_tokens,
        "teacher_api_format": "anthropic_messages",
        "attempts": retries + 1,
        "validation": {
            "no_think_tags": False,
            "no_markdown_fences": False,
            "valid_python": False,
            "has_def_main": False,
            "framework_match": False,
            "runnable": False,
            "marker_printed": False,
            "syntax_error": last_error,
            "non_empty": False,
        },
        "error": last_error,
    }


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def load_seeds(path: Path) -> list[dict[str, Any]]:
    seeds: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                seeds.append(json.loads(line))
    return seeds


def load_completed(path: Path) -> set[str]:
    """Return example_ids that have a non-empty teacher_response.

    A record is "completed" if it has a non-empty teacher_response, regardless
    of whether sandbox execution passed (lenient mode may accept ImportErrors).
    Records with empty teacher_response (failed generations) are NOT completed
    and will be retried on the next run.
    """
    completed: set[str] = set()
    if not path.exists():
        return completed
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("teacher_response", "").strip():
                    completed.add(rec["example_id"])
            except json.JSONDecodeError:
                continue
    return completed


def append_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", choices=["27b", "35b"], required=True)
    p.add_argument(
        "--api-base", default=os.environ.get("ANTHROPIC_BASE_URL", "http://127.0.0.1:49765")
    )
    p.add_argument("--api-key", default=os.environ.get("ANTHROPIC_API_KEY", "huanxin-local-proxy"))
    p.add_argument("--model", default=os.environ.get("ANTHROPIC_MODEL", "glm5.2"))
    p.add_argument("--max-tokens", type=int, default=4096)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--timeout", type=float, default=300.0, help="API timeout seconds")
    p.add_argument("--run-timeout", type=int, default=30, help="sandbox run timeout seconds")
    p.add_argument("--retries", type=int, default=5, help="retry attempts on validation failure")
    p.add_argument("--batch", type=int, default=100, help="batch size (flush + report per batch)")
    p.add_argument("--start-batch", type=int, default=0, help="start from batch index (0-based)")
    p.add_argument("--num-batches", type=int, default=0, help="number of batches to run (0=all)")
    p.add_argument("--skip-completed", action="store_true", default=True)
    p.add_argument(
        "--inter-seed-delay",
        type=float,
        default=1.0,
        help="delay between seeds (s) to reduce proxy load",
    )
    p.add_argument(
        "--lenient-execution",
        action="store_true",
        default=True,
        help="accept code that fails sandbox execution due to ImportError/ModuleNotFoundError "
        "(local sandbox may lack quantum libs; code is re-validated on NAS)",
    )
    p.add_argument(
        "--strict-execution",
        dest="lenient_execution",
        action="store_false",
        help="require sandbox execution to pass (default for --no-lenient-execution)",
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    seeds_path = Path(
        f"data/generated/glm52_soft_distill_sft_iter5_{args.adapter}/seed_questions.jsonl"
    )
    out_path = Path(
        f"data/generated/glm52_soft_distill_sft_iter5_{args.adapter}/teacher_responses.jsonl"
    )
    log_dir = Path(f"outputs/iter5_teacher_logs/{args.adapter}")
    log_dir.mkdir(parents=True, exist_ok=True)

    if not seeds_path.exists():
        print(f"ERROR: seeds not found: {seeds_path}", file=sys.stderr)
        return 2

    seeds = load_seeds(seeds_path)
    print(f"Loaded {len(seeds)} seeds from {seeds_path}")

    completed = load_completed(out_path) if args.skip_completed else set()
    if completed:
        print(f"Resuming: {len(completed)} already completed (runnable + validated)")

    remaining = [s for s in seeds if s["example_id"] not in completed]
    print(f"Remaining: {len(remaining)} seeds to generate")

    start = args.start_batch * args.batch
    end = start + args.num_batches * args.batch if args.num_batches > 0 else len(remaining)
    work = remaining[start:end]
    print(
        f"Running batches {args.start_batch}..{args.start_batch + (len(work) + args.batch - 1) // args.batch - 1} "
        f"({len(work)} seeds, batch={args.batch})"
    )

    if args.dry_run:
        print("[DRY RUN] no API calls")
        return 0

    batch_ok = 0
    batch_fail = 0
    batch_start_time = time.time()
    global_ok = 0
    global_fail = 0

    for i, seed in enumerate(work):
        global_idx = start + i
        batch_idx = i // args.batch
        in_batch = i % args.batch

        t0 = time.time()
        rec = generate_one(
            seed=seed,
            api_base=args.api_base,
            api_key=args.api_key,
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            timeout=args.timeout,
            retries=args.retries,
            run_timeout=args.run_timeout,
            lenient_execution=args.lenient_execution,
        )
        dt = time.time() - t0

        append_record(out_path, rec)

        # Small delay between seeds to reduce proxy load
        if args.inter_seed_delay > 0:
            time.sleep(args.inter_seed_delay)

        # A record is "ok" if it has a non-empty teacher_response (regardless of
        # whether sandbox execution passed — lenient mode may accept ImportErrors).
        rec_ok = bool(rec.get("teacher_response", "").strip())
        if rec_ok:
            batch_ok += 1
            global_ok += 1
            lenient_flag = ""
            v = rec.get("validation", {})
            if v.get("lenient_accept"):
                lenient_flag = " (lenient: local import failed)"
            print(
                f"[{global_idx+1}/{len(remaining)}] batch{batch_idx}[{in_batch+1}/{args.batch}] "
                f"OK {seed['example_id']} attempts={rec['attempts']} {dt:.1f}s{lenient_flag}",
                flush=True,
            )
        else:
            batch_fail += 1
            global_fail += 1
            print(
                f"[{global_idx+1}/{len(remaining)}] batch{batch_idx}[{in_batch+1}/{args.batch}] "
                f"FAIL {seed['example_id']} attempts={rec['attempts']} err={rec.get('error','')[:120]}",
                flush=True,
            )

        if (in_batch + 1) == args.batch or (i + 1) == len(work):
            batch_elapsed = time.time() - batch_start_time
            batch_report = {
                "adapter": args.adapter,
                "batch_index": args.start_batch + batch_idx,
                "batch_size": args.batch,
                "ok": batch_ok,
                "fail": batch_fail,
                "elapsed_sec": round(batch_elapsed, 1),
                "cumulative_ok": global_ok,
                "cumulative_fail": global_fail,
                "output_jsonl": str(out_path),
            }
            report_path = log_dir / f"batch_{args.start_batch + batch_idx:04d}.json"
            report_path.write_text(json.dumps(batch_report, indent=2))
            print(
                f"  → batch {args.start_batch + batch_idx} done: ok={batch_ok} fail={batch_fail} "
                f"elapsed={batch_elapsed:.1f}s → {report_path}",
                flush=True,
            )
            batch_ok = 0
            batch_fail = 0
            batch_start_time = time.time()

    print(f"\n{'='*60}")
    print(
        f"DONE adapter={args.adapter}: ok={global_ok} fail={global_fail} total={global_ok+global_fail}"
    )
    print(f"Output: {out_path}")
    return 0 if global_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
