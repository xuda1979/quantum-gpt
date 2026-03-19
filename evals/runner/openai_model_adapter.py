#!/usr/bin/env python3
"""OpenAI-backed model adapter for prepared eval runs.

Reads system/user prompt files from a prepared run, calls the OpenAI Responses API,
and prints plain candidate code to stdout so `execute_run.py` can capture it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "gpt-5.4"
DEFAULT_API_BASE = "https://api.openai.com/v1"
DEFAULT_MAX_OUTPUT_TOKENS = 1600


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system-prompt-path", type=Path, default=None)
    parser.add_argument("--prompt-path", type=Path, default=None)
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-base", default=os.environ.get("OPENAI_API_BASE", DEFAULT_API_BASE))
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=int(os.environ.get("OPENAI_MAX_OUTPUT_TOKENS", DEFAULT_MAX_OUTPUT_TOKENS)),
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Optional temperature override. Omitted by default for reasoning-capable models.",
    )
    parser.add_argument(
        "--reasoning-effort",
        default=os.environ.get("OPENAI_REASONING_EFFORT", "medium"),
        help="Responses API reasoning.effort value.",
    )
    parser.add_argument(
        "--no-sanitize",
        action="store_true",
        help="Disable markdown-fence stripping on model output.",
    )
    return parser.parse_args()


def read_text(path: Path | None, env_name: str) -> str:
    candidate = path or os.environ.get(env_name)
    if not candidate:
        raise SystemExit(f"Missing prompt path: provide {env_name} or matching CLI flag")
    resolved = Path(candidate)
    if not resolved.exists():
        raise SystemExit(f"Prompt file does not exist: {resolved}")
    return resolved.read_text()


def build_payload(args: argparse.Namespace, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": args.model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ],
        "max_output_tokens": args.max_output_tokens,
        "reasoning": {"effort": args.reasoning_effort},
    }
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    return payload


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenAI API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenAI API request failed: {exc}") from exc
    return json.loads(body)


def extract_output_text(response: dict[str, Any]) -> str:
    output_parts: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                output_parts.append(text)
    if output_parts:
        return "\n".join(output_parts).strip()

    output_text = response.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    raise SystemExit("OpenAI response did not contain any text output")


def sanitize_output(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 2:
            core = lines[1:]
            if core and core[-1].strip() == "```":
                core = core[:-1]
            return "\n".join(core).strip() + "\n"
    return text if text.endswith("\n") else text + "\n"


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required")

    system_prompt = read_text(args.system_prompt_path, "EVAL_SYSTEM_PROMPT_PATH")
    user_prompt = read_text(args.prompt_path, "EVAL_PROMPT_PATH")
    payload = build_payload(args, system_prompt=system_prompt, user_prompt=user_prompt)
    response = post_json(
        url=args.api_base.rstrip("/") + "/responses",
        payload=payload,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    text = extract_output_text(response)
    if not args.no_sanitize:
        text = sanitize_output(text)

    response_id = response.get("id", "unknown")
    usage = response.get("usage", {})
    sys.stderr.write(
        f"provider=openai model={args.model} response_id={response_id} "
        f"input_tokens={usage.get('input_tokens', 'na')} output_tokens={usage.get('output_tokens', 'na')}\n"
    )
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
