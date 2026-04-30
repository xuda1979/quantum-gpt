#!/usr/bin/env python3
"""Query the local hybrid RAG index and optionally call a Responses-compatible model."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from quantum_rag.cache import AnswerCache, index_summary_hash
from quantum_rag.eval import evaluate_answer
from quantum_rag.generation import ChatCompletionsClient, ResponsesClient, build_rag_messages, format_retrieved_context
from quantum_rag.index import QuantumRAGIndex
from quantum_rag.retrieval import QueryExpansionConfig, retrieve


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--index",
        type=Path,
        default=ROOT / "artifacts" / "quantum-rag" / "index.pkl.gz",
    )
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--alpha", type=float, default=0.55)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-output-tokens", type=int, default=600)
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=None,
        help="Trim each retrieved chunk to this many characters before sending it to the model.",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout-seconds", type=float, default=180.0)
    parser.add_argument("--context-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--disable-query-expansion", action="store_true")
    parser.add_argument("--max-chunks-per-source", type=int, default=None)
    parser.add_argument(
        "--exclude-source-substring",
        action="append",
        dest="exclude_source_substrings",
        default=[],
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=ROOT / "artifacts" / "quantum-rag" / "answer-cache.jsonl",
        help="Path to the answer cache file.",
    )
    parser.add_argument("--no-cache", action="store_true", help="Disable answer cache.")
    parser.add_argument("--eval", action="store_true", help="Run answer quality evaluation.")
    parser.add_argument(
        "--api-style",
        choices=["responses", "chat"],
        default="responses",
        help="API style: 'responses' for /v1/responses, 'chat' for /v1/chat/completions.",
    )
    parser.add_argument("--api-key", default="dummy", help="API key for the model server.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    index = QuantumRAGIndex.load(args.index)
    retrieved = retrieve(
        index,
        args.query,
        top_k=args.top_k,
        alpha=args.alpha,
        expansion=QueryExpansionConfig(enabled=not args.disable_query_expansion),
        max_chunks_per_source=args.max_chunks_per_source,
        exclude_source_substrings=args.exclude_source_substrings,
    )
    context = format_retrieved_context(
        retrieved,
        max_chars_per_chunk=args.max_context_chars,
        query=args.query,
    )

    payload = {
        "query": args.query,
        "results": [
            {
                "rank": item.rank,
                "source_path": item.chunk.source_path,
                "score": item.final_score,
                "lexical_score": item.lexical_score,
                "semantic_score": item.semantic_score,
                "char_start": item.chunk.char_start,
                "char_end": item.chunk.char_end,
                "preview": item.chunk.text[:280],
            }
            for item in retrieved
        ],
        "context": context,
    }

    if args.context_only or not (args.base_url and args.model):
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"Query: {args.query}\n")
            print(context)
        return 0

    # Check answer cache first
    cache: AnswerCache | None = None
    idx_hash = ""
    if not args.no_cache:
        cache = AnswerCache(args.cache)
        idx_hash = index_summary_hash(index.summary())
        cached = cache.get(args.query, idx_hash)
        if cached is not None:
            payload["answer"] = cached.answer
            payload["cache_hit"] = True
            if args.json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print(f"[cache hit]\n{cached.answer}")
                print("\n---\n")
                print(context)
            return 0

    if args.api_style == "chat":
        client = ChatCompletionsClient(
            base_url=args.base_url,
            model=args.model,
            api_key=args.api_key,
            timeout_seconds=args.timeout_seconds,
        )
    else:
        client = ResponsesClient(
            base_url=args.base_url,
            model=args.model,
            timeout_seconds=args.timeout_seconds,
        )
    messages = build_rag_messages(
        args.query,
        retrieved,
        max_chars_per_chunk=args.max_context_chars,
    )
    answer = client.generate(
        messages,
        max_output_tokens=args.max_output_tokens,
        temperature=args.temperature,
    )
    payload["answer"] = answer
    payload["cache_hit"] = False

    # Store in cache
    if cache is not None:
        cache.put(args.query, idx_hash, answer, metadata={
            "model": args.model,
            "base_url": args.base_url,
            "top_k": args.top_k,
            "alpha": args.alpha,
        })

    # Optionally evaluate answer quality
    if args.eval:
        eval_result = evaluate_answer(args.query, answer, retrieved)
        payload["eval"] = eval_result.to_dict()

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(answer)
        if args.eval:
            eval_result = evaluate_answer(args.query, answer, retrieved)
            print(f"\n--- Eval ---")
            print(f"faithfulness: {eval_result.faithfulness_score:.3f}")
            print(f"relevance:    {eval_result.relevance_score:.3f}")
            print(f"groundedness: {eval_result.groundedness_score:.3f}")
            print(f"composite:    {eval_result.composite_score:.3f}")
        print("\n---\n")
        print(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
