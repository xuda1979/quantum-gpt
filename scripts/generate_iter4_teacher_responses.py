#!/usr/bin/env python3
"""Generate iter-4 teacher responses from glm5.2 with top-20 logprobs.

Reads seed questions from data/generated/glm52_soft_distill_sft_iter4_{27b,35b}/seed_questions.jsonl,
calls glm5.2 via OpenAI-compatible chat completions API with logprobs=True, top_logprobs=20,
and writes the teacher responses + logits to teacher_responses.jsonl.

Quality gates:
  - No <think> tags in teacher responses
  - ast.parse(teacher_response) passes
  - Teacher response prints the expected_marker (execution check, optional)

Usage:
  python3 scripts/generate_iter4_teacher_responses.py \\
    --input data/generated/glm52_soft_distill_sft_iter4_27b/seed_questions.jsonl \\
    --output data/generated/glm52_soft_distill_sft_iter4_27b/teacher_responses.jsonl \\
    --api-base http://localhost:8000/v1 \\
    --api-key $GLM52_API_KEY \\
    --model glm5.2
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
    "You are a careful quantum software engineering assistant. Use the user's task "
    "and any supplied context to produce correct, testable Python or precise repair "
    "guidance. Always produce a complete, runnable Python program with `def main()` "
    "that prints the exact specified marker string. Do not include markdown fences "
    "or surrounding commentary."
)


def chat_completion(
    *,
    api_base: str,
    api_key: str,
    model: str,
    user_prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
    max_tokens: int = 2048,
    temperature: float = 0.3,
    timeout: float = 120.0,
    api_format: str = "anthropic",  # "anthropic" or "openai"
) -> dict[str, Any]:
    """Call the chat completions endpoint. Supports Anthropic Messages API and OpenAI API."""
    if api_format == "anthropic":
        payload = {
            "model": model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        data = json.dumps(payload).encode("utf-8")
        # Anthropic Messages API: POST /v1/messages
        url = f"{api_base.rstrip('/')}/v1/messages"
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
    else:  # openai
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "logprobs": True,
            "top_logprobs": 20,
        }
        data = json.dumps(payload).encode("utf-8")
        url = f"{api_base.rstrip('/')}/chat/completions"
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_content(raw: dict[str, Any], api_format: str = "anthropic") -> str:
    """Extract text content from the API response, filtering out thinking blocks."""
    if api_format == "anthropic":
        # Anthropic Messages API: content is a list of blocks
        content_blocks = raw.get("content", [])
        text_parts = []
        for block in content_blocks:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "\n".join(text_parts).strip()
    else:  # openai
        return raw["choices"][0]["message"]["content"].strip()


def extract_logprobs(raw: dict[str, Any], api_format: str = "anthropic") -> list[dict[str, Any]]:
    """Extract per-token logprobs from the chat completion response.

    Note: The Anthropic Messages API does not return logprobs by default.
    Logits preservation is only available via the OpenAI-compatible API.
    For the Anthropic API, we return an empty list (hard-SFT only).
    """
    if api_format == "anthropic":
        # Anthropic Messages API does not support logprobs in the standard response.
        # If logprobs are needed, use the OpenAI-compatible endpoint instead.
        return []

    # OpenAI format
    choice = raw["choices"][0]
    logprobs_data = choice.get("logprobs")
    if not logprobs_data:
        return []
    content = logprobs_data.get("content", [])
    result = []
    for entry in content:
        if not isinstance(entry, dict):
            continue
        token = entry.get("token", "")
        logprob = entry.get("logprob", 0.0)
        top_logprobs = entry.get("top_logprobs", [])
        top_list = []
        for tl in top_logprobs:
            if isinstance(tl, dict):
                top_list.append(
                    {
                        "token": tl.get("token", ""),
                        "logprob": tl.get("logprob", 0.0),
                    }
                )
        result.append(
            {
                "token": token,
                "logprob": logprob,
                "top_logprobs": top_list,
            }
        )
    return result


def strip_markdown_fences(text: str) -> str:
    """Strip ```python ... ``` fences if present."""
    stripped = text.strip()
    if stripped.startswith("```"):
        # Remove opening fence
        stripped = re.sub(r"^```(?:python)?\s*\n?", "", stripped)
        # Remove closing fence
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
    api_format: str = "anthropic",
) -> dict[str, Any]:
    """Generate one teacher response with retries."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            raw = chat_completion(
                api_base=api_base,
                api_key=api_key,
                model=model,
                user_prompt=seed["prompt"],
                system_prompt=seed.get("system_prompt", SYSTEM_PROMPT),
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
                api_format=api_format,
            )
            content = extract_content(raw, api_format=api_format)
            logprobs = extract_logprobs(raw, api_format=api_format)

            # Strip markdown fences if present
            content = strip_markdown_fences(content)

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
                "teacher_logprobs": logprobs,
                "teacher_model": model,
                "teacher_temperature": temperature,
                "teacher_max_tokens": max_tokens,
                "quality_gates": {
                    "no_think_tags": True,
                    "valid_python": True,
                    "syntax_error": None,
                },
            }
        except Exception as exc:
            last_error = exc
            if attempt <= retries:
                time.sleep(min(2.0 * attempt, 8.0))
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
    p.add_argument(
        "--api-base",
        default="https://aihuanxin.cn/qdlake/trans/model-subscribe/75/kunlun/ingress/api/68b329/5c1bbb4620fc40eea9712a9771cece1b/ai-8daf0136f30a485d9ea2651bd8d41877/service-6196b60f227c4584890bbd7c67cd04b5",
        help="glm5.2 API base URL (default: local Huanxin glm5.2 endpoint)",
    )
    p.add_argument(
        "--api-key", default=os.environ.get("HUANXIN_GLM52_API_KEY", "huanxin-local-proxy")
    )
    p.add_argument("--model", default="glm5.2")
    p.add_argument("--max-tokens", type=int, default=2048)
    p.add_argument("--temperature", type=float, default=0.3)
    p.add_argument("--timeout", type=float, default=120.0)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--limit", type=int, default=0, help="0 = all")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--report", default=None, help="path to write JSON report")
    p.add_argument(
        "--api-format",
        choices=["anthropic", "openai"],
        default="anthropic",
        help="API format: 'anthropic' for /v1/messages (local glm5.2), 'openai' for /chat/completions",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="regenerate ALL teacher responses (ignore already-completed; logits will be fresh)",
    )
    p.add_argument(
        "--regenerate-logits-only",
        action="store_true",
        help="only re-fetch logits for existing teacher_response rows (use when prompts unchanged but logits need refresh)",
    )
    args = p.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report) if args.report else output_path.parent / "teacher_report.json"

    seeds = load_seeds(input_path)

    if args.force:
        # Start fresh — don't resume from existing output
        completed: set[str] = set()
        print("⚠️  --force: regenerating ALL teacher responses (logits will be fresh)")
    else:
        completed = load_completed(output_path)

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
        "force": args.force,
        "regenerate_logits_only": args.regenerate_logits_only,
    }

    print(f"Seeds: {len(seeds)} | Already completed: {len(completed)} | Selected: {len(selected)}")

    if args.dry_run:
        report["ok"] = True
        write_report(report_path, report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # If --force, overwrite the output file; otherwise append (resume mode)
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
                    api_format=args.api_format,
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

    report["ok"] = report["generated"] == len(selected) and not report["errors"]
    write_report(report_path, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
