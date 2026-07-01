#!/usr/bin/env python3
"""Run a same-model no-RAG vs RAG answer-quality comparison."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_BENCHMARK = Path("evals/benchmarks/qwen36_27b_rag_ab_manager_v1.json")
DEFAULT_JSON = Path("reports/qwen36_27b_rag_ab_huanxin_ai_20260513.json")
DEFAULT_MARKDOWN = Path("reports/qwen36_27b_rag_ab_huanxin_ai_20260513.md")


@dataclass(frozen=True)
class Endpoint:
    name: str
    base_url: str
    model: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--no-rag-base-url", default="http://127.0.0.1:8001/v1")
    parser.add_argument("--no-rag-model", default="qwen3.6-27b-norag")
    parser.add_argument("--rag-base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--rag-model", default="quantum-intelligence-v0.1.0")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    return parser.parse_args()


def load_benchmark(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("benchmark must be a JSON list")
    return payload


def chat(endpoint: Endpoint, query: str, *, max_tokens: int, timeout_seconds: float) -> tuple[str, float]:
    payload = {
        "model": endpoint.model,
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    request = urllib.request.Request(
        endpoint.base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer dummy",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{endpoint.name} HTTP {exc.code}: {raw}") from exc
    elapsed = time.monotonic() - started
    return body["choices"][0]["message"]["content"].strip(), elapsed


def term_hits(answer: str, terms: list[str]) -> list[str]:
    lowered = answer.lower()
    return [term for term in terms if term.lower() in lowered]


def score_answer(
    answer: str,
    terms: list[str],
    minimum_term_hits: int,
    *,
    require_citation: bool,
) -> dict[str, Any]:
    hits = term_hits(answer, terms)
    has_citation = "[c" in answer.lower()
    term_coverage_passed = len(hits) >= minimum_term_hits
    return {
        "term_hits": hits,
        "term_hit_count": len(hits),
        "has_rag_citation": has_citation,
        "term_coverage_passed": term_coverage_passed,
        "passed": term_coverage_passed and (has_citation or not require_citation),
    }


def preview(answer: str, limit: int = 500) -> str:
    compact = " ".join(answer.split())
    return compact[:limit] + ("..." if len(compact) > limit else "")


def build_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# Qwen3.6-27B RAG A/B Test on Huanxin AI",
        "",
        "Same model, same NPU backend, same questions:",
        "",
        "- no RAG: Qwen3.6-27B served by vLLM Ascend without retrieved context",
        "- with RAG: Qwen3.6-27B served by the RAG proxy with local quantum documentation injected",
        "",
        "## Summary",
        "",
        f"- Questions: `{metrics['total_questions']}`",
        f"- no RAG passed: `{metrics['no_rag_passed']}/{metrics['total_questions']}`",
        f"- with RAG passed: `{metrics['rag_passed']}/{metrics['total_questions']}`",
        f"- no RAG average required-term hits: `{metrics['no_rag_avg_term_hits']:.2f}`",
        f"- with RAG average required-term hits: `{metrics['rag_avg_term_hits']:.2f}`",
        f"- improvement: `+{metrics['pass_rate_delta_percent']:.0f}` percentage points",
        "",
        "## Per-Question Results",
        "",
        "| Question | no RAG | with RAG |",
        "| --- | ---: | ---: |",
    ]
    for item in report["examples"]:
        lines.append(
            f"| `{item['id']}` | {item['no_rag']['term_hit_count']} terms, pass={item['no_rag']['passed']} | "
            f"{item['rag']['term_hit_count']} terms, pass={item['rag']['passed']} |"
        )
    lines.extend(["", "## Manager Demo Example", ""])
    demo = report["examples"][0]
    lines.extend(
        [
            f"Question: `{demo['query']}`",
            "",
            "no RAG preview:",
            "",
            "```text",
            preview(demo["no_rag"]["answer"]),
            "```",
            "",
            "with RAG preview:",
            "",
            "```text",
            preview(demo["rag"]["answer"]),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    no_rag = Endpoint("no_rag", args.no_rag_base_url, args.no_rag_model)
    rag = Endpoint("rag", args.rag_base_url, args.rag_model)
    benchmark = load_benchmark(args.benchmark)
    examples: list[dict[str, Any]] = []

    for item in benchmark:
        query = str(item["query"])
        expected_terms = [str(term) for term in item["expected_terms"]]
        minimum_term_hits = int(item["minimum_term_hits"])
        no_rag_answer, no_rag_seconds = chat(
            no_rag,
            query,
            max_tokens=args.max_tokens,
            timeout_seconds=args.timeout_seconds,
        )
        rag_answer, rag_seconds = chat(
            rag,
            query,
            max_tokens=args.max_tokens,
            timeout_seconds=args.timeout_seconds,
        )
        no_rag_score = score_answer(
            no_rag_answer,
            expected_terms,
            minimum_term_hits,
            require_citation=False,
        )
        rag_score = score_answer(
            rag_answer,
            expected_terms,
            minimum_term_hits,
            require_citation=True,
        )
        examples.append(
            {
                "id": item["id"],
                "query": query,
                "manager_reason": item.get("manager_reason", ""),
                "expected_terms": expected_terms,
                "minimum_term_hits": minimum_term_hits,
                "no_rag": {
                    **no_rag_score,
                    "elapsed_seconds": round(no_rag_seconds, 3),
                    "answer": no_rag_answer,
                },
                "rag": {
                    **rag_score,
                    "elapsed_seconds": round(rag_seconds, 3),
                    "answer": rag_answer,
                },
            }
        )

    total = len(examples)
    no_rag_passed = sum(1 for item in examples if item["no_rag"]["passed"])
    rag_passed = sum(1 for item in examples if item["rag"]["passed"])
    no_rag_avg_terms = sum(item["no_rag"]["term_hit_count"] for item in examples) / max(total, 1)
    rag_avg_terms = sum(item["rag"]["term_hit_count"] for item in examples) / max(total, 1)
    report = {
        "benchmark": str(args.benchmark),
        "no_rag_endpoint": no_rag.__dict__,
        "rag_endpoint": rag.__dict__,
        "scoring_rule": (
            "no RAG pass = required keyword coverage >= per-question threshold; "
            "RAG pass = required keyword coverage >= threshold and answer contains a document citation like [C1]"
        ),
        "metrics": {
            "total_questions": total,
            "no_rag_passed": no_rag_passed,
            "rag_passed": rag_passed,
            "no_rag_pass_rate": no_rag_passed / max(total, 1),
            "rag_pass_rate": rag_passed / max(total, 1),
            "pass_rate_delta_percent": 100 * (rag_passed - no_rag_passed) / max(total, 1),
            "no_rag_avg_term_hits": no_rag_avg_terms,
            "rag_avg_term_hits": rag_avg_terms,
        },
        "examples": examples,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
