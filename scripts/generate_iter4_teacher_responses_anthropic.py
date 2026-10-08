#!/usr/bin/env python3
"""Generate iter-4 teacher responses from glm5.2 via Anthropic Messages API.

This is the Anthropic-format counterpart to generate_iter4_teacher_responses.py.
The local Huanxin proxy exposing glm5.2 only speaks /v1/messages (Anthropic
format), not /v1/chat/completions (OpenAI format). Logprobs are not supported
by the proxy, so teacher_logprobs is set to an empty list — the downstream
prepare_iter4_distill_sft.py handles this gracefully (teacher_logprobs_preserved=False).

Reads seed questions from data/generated/glm52_soft_distill_sft_iter4_{27b,35b}/seed_questions.jsonl,
calls glm5.2 via the Anthropic Messages endpoint, applies quality gates
(no </think>markdown, no  < think > tags, valid Python AST), and writes teacher_responses.jsonl.

Usage:
  python3 scripts/generate_iter4_teacher_responses_anthropic.py \
    --input data/generated/glm52_soft_distill_sft_iter4_27b/seed_questions.jsonl \
    --output data/generated/glm52_soft_distill_sft_iter4_27b/teacher_responses.jsonl \
    --api-base http://127.0.0.1:58497 \
    --api-key huanxin-local-proxy \
    --model glm5.2 \
    --report data/generated/glm52_soft_distill_sft_iter4_27b/teacher_report.json
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SYSTEM_PROMPT = (
    "You are a careful quantum software engineering assistant. Use the user's "
    "task and any supplied context to produce correct, testable Python or precise "
    "repair guidance. Always produce a complete, runnable Python program with `def main()` "
    "that prints the exact specified marker string. Do not include markdown fences "
    "or surrounding commentary."
)


def anthropic_messages(
    *,
    api_base: str,
    api_key: str,
    model: str,
    user_prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
    max_tokens: int = 8000,
    temperature: float = 0.3,
    timeout: float = 300.0,
    messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Call the Anthropic Messages endpoint (/v1/messages).

    If `messages` is provided, use it directly (for multi-turn). Otherwise build
    a single-turn [user] message list from user_prompt.
    """
    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": messages
        if messages is not None
        else [
            {"role": "user", "content": user_prompt},
        ],
    }
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


def extract_content(raw: dict[str, Any]) -> str:
    """Extract the text content from an Anthropic Messages response.

    The response has content as a list of blocks (thinking, text, etc.).
    We concatenate all text blocks and ignore thinking blocks.
    """
    content_list = raw.get("content", [])
    if not isinstance(content_list, list):
        # Some proxies return a plain string
        return str(content_list).strip()
    parts: list[str] = []
    for block in content_list:
        if not isinstance(block, dict):
            continue
        btype = block.get("type", "")
        if btype == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts).strip()


def extract_thinking(raw: dict[str, Any]) -> str:
    """Extract all thinking-block text from the response (for fallback)."""
    content_list = raw.get("content", [])
    if not isinstance(content_list, list):
        return ""
    parts: list[str] = []
    for block in content_list:
        if not isinstance(block, dict):
            continue
        if block.get("type", "") == "thinking":
            parts.append(block.get("thinking", ""))
    return "\n".join(parts).strip()


def extract_code_from_thinking(thinking: str) -> str | None:
    """Try to extract a complete Python program from a thinking block.

    Models often write the final code inside their thinking. We look for:
    1. A fenced ```python ... ``` block
    2. The last contiguous run of Python-looking lines (starts with import/from/def/class)
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
    # 2. Last contiguous run starting with import/from/def
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


def strip_markdown_fences(text: str) -> str:
    """Strip ```python ... ``` fences if present."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:python)?\s*\n?", "", stripped)
        stripped = re.sub(r"\n?```\s*$", "", stripped)
    return stripped.strip()


def validate_python(code: str) -> tuple[bool, str | None]:
    """Validate that the teacher response is valid Python. Returns (ok, error)."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} (line {e.lineno})"


def check_no_think_tags(text: str) -> bool:
    return "<think" not in text.lower()


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
) -> dict[str, Any]:
    """Generate one teacher response with retries."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
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
            content = extract_content(raw)

            # Strip markdown fences if present
            content = strip_markdown_fences(content)

            # Fallback: if no text block, try extracting code from thinking
            used_thinking_fallback = False
            used_two_turn = False
            if not content:
                thinking = extract_thinking(raw)
                fallback_code = extract_code_from_thinking(thinking)
                if fallback_code:
                    content = strip_markdown_fences(fallback_code)
                    used_thinking_fallback = True
                elif thinking:
                    # Two-turn: send thinking back as assistant context, ask for code
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
                            "content": "Now output ONLY the complete Python program with def main() that prints the exact marker string. No markdown fences, no commentary, just the code.",
                        },
                    ]
                    raw2 = anthropic_messages(
                        api_base=api_base,
                        api_key=api_key,
                        model=model,
                        user_prompt="",
                        system_prompt=seed.get("system_prompt", SYSTEM_PROMPT),
                        max_tokens=max_tokens,
                        temperature=temperature,
                        timeout=timeout,
                        messages=two_turn_messages,
                    )
                    content2 = extract_content(raw2)
                    if content2:
                        content = strip_markdown_fences(content2)
                        used_two_turn = True

            # Quality gate: non-empty
            if not content:
                raise ValueError(
                    "teacher output is empty (no text block, no code in thinking, and two-turn fallback failed)"
                )

            # Quality gate: no <think> tags
            if not check_no_think_tags(content):
                raise ValueError("teacher output contains forbidden <think> tag")

            # Quality gate: valid Python
            ok, err = validate_python(content)
            if not ok:
                raise ValueError(f"teacher output is not valid Python: {err}")

            return {
                "example_id": seed["example_id"],
                "adapter_target": seed["adapter_target"],
                "task_family": seed["task_family"],
                "framework": seed["framework"],
                "difficulty": seed["difficulty"],
                "variant_id": seed["variant_id"],
                "source_gap": seed["source_gap"],
                "user_instruction": seed["prompt"],
                "expected_marker": seed["expected_marker"],
                "teacher_response": content,
                "teacher_logprobs": [],  # Not supported by local proxy
                "teacher_model": model,
                "teacher_temperature": temperature,
                "teacher_max_tokens": max_tokens,
                "teacher_api_format": "anthropic_messages",
                "teacher_thinking_fallback": used_thinking_fallback,
                "teacher_two_turn_fallback": used_two_turn,
                "quality_gates": {
                    "no_think_tags": True,
                    "valid_python": True,
                    "syntax_error": None,
                    "no_markdown_fences": "```" not in content,
                    "non_empty": True,
                    "used_thinking_fallback": used_thinking_fallback,
                    "used_two_turn_fallback": used_two_turn,
                },
            }
        except Exception as exc:
            last_error = exc
            if attempt <= retries:
                # Longer backoff for 500/503 (proxy overloaded)
                exc_str = str(exc)
                if "500" in exc_str or "503" in exc_str or "502" in exc_str:
                    wait = min(10.0 * attempt, 30.0)
                else:
                    wait = min(2.0 * attempt, 8.0)
                print(
                    f"  attempt {attempt}/{retries+1} failed: {exc}; retrying in {wait}s",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(wait)
                continue
            raise
    raise RuntimeError(f"teacher generation failed: {last_error}")


def load_seeds(path: Path) -> list[dict[str, Any]]:
    seeds = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                seeds.append(json.loads(line))
    return seeds


def load_completed(path: Path) -> set[str]:
    """Load example_ids that are already in the output file (for resume)."""
    if not path.exists():
        return set()
    completed = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                completed.add(rec["example_id"])
            except json.JSONDecodeError:
                continue
    return completed


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="seed_questions.jsonl")
    p.add_argument("--output", required=True, help="teacher_responses.jsonl")
    p.add_argument("--api-base", required=True, help="e.g. http://127.0.0.1:58497")
    p.add_argument("--api-key", default=os.environ.get("GLM52_API_KEY", "huanxin-local-proxy"))
    p.add_argument("--model", default="glm5.2")
    p.add_argument("--max-tokens", type=int, default=8000)
    p.add_argument("--temperature", type=float, default=0.3)
    p.add_argument("--timeout", type=float, default=300.0)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--limit", type=int, default=0, help="0 = all")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--report", default=None, help="path to write JSON report")
    p.add_argument(
        "--force",
        action="store_true",
        help="regenerate ALL teacher responses (ignore already-completed)",
    )
    p.add_argument("--delay", type=float, default=5.0, help="seconds to wait between requests")
    args = p.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report) if args.report else output_path.parent / "teacher_report.json"

    seeds = load_seeds(input_path)

    if args.force:
        completed: set[str] = set()
        print("⚠️  --force: regenerating ALL teacher responses")
    else:
        completed = load_completed(output_path)
        if completed:
            print(f"Resuming: {len(completed)} already completed")

    remaining = [s for s in seeds if s["example_id"] not in completed]
    selected = remaining if args.limit == 0 else remaining[: args.limit]

    report: dict[str, Any] = {
        "ok": False,
        "input_jsonl": str(input_path),
        "output_jsonl": str(output_path),
        "seed_rows": len(seeds),
        "already_completed": len(completed),
        "selected": len(selected),
        "generated": 0,
        "errors": [],
        "model": args.model,
        "api_format": "anthropic_messages",
        "force": args.force,
        "logprobs_supported": False,
    }

    if args.dry_run:
        report["ok"] = True
        write_report(report_path, report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if args.force else "a"
    if args.force and output_path.exists():
        print(f"⚠️  Overwriting existing {output_path} (--force mode)")
    with open(output_path, mode, encoding="utf-8") as out_fh:
        for i, seed in enumerate(selected, 1):
            try:
                rec = generate_one(
                    seed=seed,
                    api_base=args.api_base,
                    api_key=args.api_key,
                    model=args.model,
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                    timeout=args.timeout,
                    retries=args.retries,
                )
                out_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out_fh.flush()
                report["generated"] += 1
                print(
                    f"[{i}/{len(selected)}] OK {seed['example_id']} ({seed['task_family']})",
                    flush=True,
                )
            except Exception as exc:
                err_msg = f"{seed['example_id']}: {exc}"
                report["errors"].append(err_msg)
                print(
                    f"[{i}/{len(selected)}] FAIL {seed['example_id']}: {exc}",
                    file=sys.stderr,
                    flush=True,
                )

            # Delay between requests to avoid 503 from proxy
            if args.delay > 0 and i < len(selected):
                time.sleep(args.delay)

    report["ok"] = report["generated"] == len(selected) and not report["errors"]
    write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
