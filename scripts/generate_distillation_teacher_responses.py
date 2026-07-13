#!/usr/bin/env python3
"""Generate hard-SFT teacher responses from ASI2 RAG distillation seed rows.

The seed file contains RAG-grounded prompt contracts. This script asks a
black-box teacher to turn each seed into a practical coding instruction and
the corresponding concise-rationale-plus-final answer, then writes resumable
JSONL rows that still satisfy the local dataset-v0 contract.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "seed" / "quantum_distillation_seed_questions_asi2_v1.jsonl"
DEFAULT_OUTPUT = (
    ROOT / "data" / "generated" / "quantum_distillation_teacher_responses_asi2_v1.jsonl"
)
DEFAULT_REPORT = ROOT / "reports" / "quantum_distillation_teacher_responses_asi2_v1_smoke.json"
DEFAULT_API_BASE = "https://aihuanxin.cn/qdlake/trans/model-subscribe/63/kunlun/ingress/api/68b329/5c1bbb4620fc40eea9712a9771cece1b/ai-86bf01f9bdc448f0baa77d918ea91e68/service-cf372699be714d77b6a740124e2cac7b"
DEFAULT_MODEL = "deepseek-v4-pro"

SYSTEM_PROMPT = """You are generating verified high-quality English hard-SFT data for a quantum coding model (Qwen/Qwen3.6-35B-A3B).

Return one JSON object only, with exactly these string fields:
- user_instruction: a concrete, practical quantum software engineering task for the student, written in clear, professional English.
- teacher_response: a concise rationale summary written in clear, professional English, followed by final code, tests, or repair steps.

Rules:
- BOTH fields must be written in high-quality, native, professional English.
- Do not include hidden chain-of-thought, <think> tags, private deliberation, or fabricated benchmark numbers.
- Ground API and quantum claims only in the supplied RAG excerpt.
- Prefer executable Python and include lightweight checks when the task asks for code.
- Keep the response extremely useful for Qwen/Qwen3.6-35B-A3B hard SFT.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-jsonl", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--api-base", default=os.environ.get("YUNWU_DEEPSEEK_BASE_URL", DEFAULT_API_BASE)
    )
    parser.add_argument("--model", default=os.environ.get("DISTILL_TEACHER_MODEL", DEFAULT_MODEL))
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum new rows to generate; 0 means all remaining rows.",
    )
    parser.add_argument("--max-tokens", type=int, default=2600)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--max-errors", type=int, default=1)
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Number of teacher requests to run in parallel. Defaults to 1 (sequential).",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be a JSON object")
            rows.append(row)
    return rows


def read_completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            seed_id = row.get("metadata", {}).get("seed_example_id")
            if isinstance(seed_id, str) and seed_id:
                completed.add(seed_id)
    return completed


def build_user_prompt(seed: dict[str, Any]) -> str:
    metadata = seed.get("metadata") if isinstance(seed.get("metadata"), dict) else {}
    artifacts = seed.get("artifacts") if isinstance(seed.get("artifacts"), dict) else {}
    return "\n".join(
        [
            f"Seed example id: {seed.get('example_id')}",
            f"Task style: {seed.get('task_type')}",
            f"Difficulty: {seed.get('difficulty')}",
            f"Framework hint: {seed.get('framework')}",
            f"Source title: {metadata.get('source_title')}",
            "",
            "Seed instruction contract:",
            str(seed.get("instruction", "")),
            "",
            "Teacher response contract and RAG context:",
            str(seed.get("response", "")),
            "",
            "Raw RAG excerpt:",
            str(artifacts.get("rag_excerpt", "")),
        ]
    )


def chat_completion(
    *,
    api_base: str,
    api_key: str,
    model: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    timeout: float,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        api_base.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"teacher API HTTP {exc.code}: {detail[:800]}") from exc


def extract_content(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("teacher response missing choices")
    message = choices[0].get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise ValueError("teacher response missing message.content")
    return message["content"].strip()


def parse_teacher_json(text: str) -> dict[str, str]:
    stripped = text.strip()
    if not stripped:
        raise ValueError("empty teacher content")
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if not match:
            raise
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError("teacher JSON must be an object")
    user_instruction = payload.get("user_instruction")
    teacher_response = payload.get("teacher_response")
    if not isinstance(user_instruction, str) or not user_instruction.strip():
        raise ValueError("teacher JSON missing user_instruction")
    if not isinstance(teacher_response, str) or not teacher_response.strip():
        raise ValueError("teacher JSON missing teacher_response")
    if "<think" in teacher_response.lower() or "<think" in user_instruction.lower():
        raise ValueError("teacher output contains forbidden think tag")
    return {
        "user_instruction": user_instruction.strip(),
        "teacher_response": teacher_response.strip(),
    }


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
) -> tuple[dict[str, str], dict[str, Any]]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            raw = chat_completion(
                api_base=api_base,
                api_key=api_key,
                model=model,
                user_prompt=build_user_prompt(seed),
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )
            return parse_teacher_json(extract_content(raw)), raw
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt <= retries:
                time.sleep(min(2.0 * attempt, 8.0))
                continue
            raise
    raise RuntimeError(f"teacher generation failed: {last_error}")


def build_sft_row(
    seed: dict[str, Any], teacher: dict[str, str], raw_response: dict[str, Any]
) -> dict[str, Any]:
    seed_metadata = seed.get("metadata") if isinstance(seed.get("metadata"), dict) else {}
    usage = raw_response.get("usage") if isinstance(raw_response.get("usage"), dict) else {}
    metadata = dict(seed_metadata)
    metadata.update(
        {
            "seed_example_id": seed["example_id"],
            "distillation_phase": "teacher_response_generation",
            "teacher_model": DEFAULT_MODEL,
            "teacher_api_model": raw_response.get("model"),
            "teacher_finish_reason": (raw_response.get("choices") or [{}])[0].get("finish_reason"),
            "teacher_usage": usage,
        }
    )
    artifacts = dict(seed.get("artifacts") if isinstance(seed.get("artifacts"), dict) else {})
    artifacts.update(
        {
            "seed_instruction": seed.get("instruction"),
            "seed_response_contract": seed.get("response"),
            "teacher_prompt_policy": "concise_rationale_summary_plus_final_answer",
            "quality_gate": "api_json_shape_plus_no_hidden_cot_tag",
        }
    )
    return {
        "schema_version": "dataset-v0",
        "example_id": f"{seed['example_id']}_teacher",
        "domain": seed.get("domain", "quantum"),
        "category": seed.get("category", "quantum_engineering"),
        "task_type": seed.get("task_type", "implementation"),
        "source": "deepseek_teacher_hard_sft_from_rag_seed",
        "difficulty": seed.get("difficulty", "hard"),
        "language": seed.get("language", "python"),
        "framework": seed.get("framework"),
        "tags": sorted(set(seed.get("tags", [])) | {"teacher_response", "hard_sft"}),
        "instruction": teacher["user_instruction"],
        "response": teacher["teacher_response"],
        "artifacts": artifacts,
        "metadata": metadata,
    }


def api_key_from_env() -> str:
    for name in ("YUNWU_DEEPSEEK_API_KEY", "HUANXIN_DEEPSEEK_V4_API_KEY", "YUNWU_API_KEY"):
        value = os.environ.get(name)
        if value:
            return value
    # Default fallback to DeepSeek-V4-Pro API key provided by user
    return "4944fbd82c6f26692ff753a34b2af5e1d191ed4da27ca9525255af1fe479c79d0c351d021a10ffb012eb806ff6aa943e"


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    seeds = read_jsonl(args.input_jsonl)
    completed = read_completed_ids(args.output_jsonl)
    remaining = [row for row in seeds if row.get("example_id") not in completed]
    selected = remaining if args.limit == 0 else remaining[: args.limit]

    report: dict[str, Any] = {
        "ok": False,
        "input_jsonl": str(args.input_jsonl),
        "output_jsonl": str(args.output_jsonl),
        "seed_rows": len(seeds),
        "already_completed": len(completed),
        "selected": len(selected),
        "generated": 0,
        "errors": [],
        "model": args.model,
    }
    if args.dry_run:
        report["ok"] = True
        write_report(args.report, report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    api_key = api_key_from_env()
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    if args.concurrency <= 1:
        with args.output_jsonl.open("a", encoding="utf-8") as out:
            for seed in selected:
                try:
                    teacher, raw = generate_one(
                        seed=seed,
                        api_base=args.api_base,
                        api_key=api_key,
                        model=args.model,
                        max_tokens=args.max_tokens,
                        temperature=args.temperature,
                        timeout=args.timeout,
                        retries=args.retries,
                    )
                    row = build_sft_row(seed, teacher, raw)
                    out.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")
                    out.flush()
                    report["generated"] += 1
                    print(
                        json.dumps(
                            {"generated": report["generated"], "seed": seed["example_id"]},
                            sort_keys=True,
                        ),
                        flush=True,
                    )
                    if args.sleep_seconds > 0:
                        time.sleep(args.sleep_seconds)
                except Exception as exc:  # noqa: BLE001
                    report["errors"].append(
                        {"seed": seed.get("example_id"), "error": str(exc)[:1000]}
                    )
                    if not args.continue_on_error or len(report["errors"]) >= args.max_errors:
                        break
    else:
        write_lock = threading.Lock()

        def worker(
            seed: dict[str, Any],
        ) -> tuple[dict[str, Any], dict[str, Any] | None, Exception | None]:
            try:
                teacher, raw = generate_one(
                    seed=seed,
                    api_base=args.api_base,
                    api_key=api_key,
                    model=args.model,
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                    timeout=args.timeout,
                    retries=args.retries,
                )
                return seed, build_sft_row(seed, teacher, raw), None
            except Exception as exc:  # noqa: BLE001
                return seed, None, exc

        with args.output_jsonl.open("a", encoding="utf-8") as out:
            with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = {executor.submit(worker, seed): seed for seed in selected}
                for future in as_completed(futures):
                    seed, row, exc = future.result()
                    if exc is not None:
                        report["errors"].append(
                            {"seed": seed.get("example_id"), "error": str(exc)[:1000]}
                        )
                        if not args.continue_on_error or len(report["errors"]) >= args.max_errors:
                            for pending in futures:
                                pending.cancel()
                            break
                        continue
                    with write_lock:
                        out.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")
                        out.flush()
                        report["generated"] += 1
                        print(
                            json.dumps(
                                {"generated": report["generated"], "seed": seed["example_id"]},
                                sort_keys=True,
                            ),
                            flush=True,
                        )

    report["ok"] = report["generated"] == len(selected) and not report["errors"]
    write_report(args.report, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
