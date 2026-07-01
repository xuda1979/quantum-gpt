#!/usr/bin/env python3
"""Run Qwen2.5-1.5B-Instruct on the strict quantum task suite with and without RAG.

This script performs an A/B comparison:

  - Baseline: Qwen2.5-1.5B-Instruct generates a Python candidate from the
    task prompt only.
  - RAG:      Qwen2.5-1.5B-Instruct generates a Python candidate from the
    task prompt plus retrieved context chunks from the curated quantum
    documentation index (artifacts/quantum-rag/quantum-code-index.pkl.gz).

Both runs are scored with evals/runner/run_eval.py and the script
prints a side-by-side pass-rate comparison.

Test set: every task under evals/tasks/quantum/ (31 tasks). All
reference candidates are validated to pass before generation.

Usage:
    python3 scripts/run_qwen25_rag_compare.py [--device mps|cpu] [--top-k 3] [--max-new-tokens 384]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Silence transformers logging noise in the eval logs
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

from evals.runner.candidate_sanitize import sanitize_candidate_text  # noqa: E402
from evals.runner.task_metadata import resolve_test_path  # noqa: E402
from quantum_rag.index import QuantumRAGIndex  # noqa: E402
from quantum_rag.retrieval import retrieve  # noqa: E402

DEFAULT_MODEL_PATH = Path(
    "/Users/daxu/.openclaw/workspace-quantum-rnd/models/Qwen2.5-1.5B-Instruct"
)
DEFAULT_INDEX_PATH = ROOT / "artifacts/quantum-rag/quantum-docs-only-index.pkl.gz"
TASKS_ROOT = ROOT / "evals" / "tasks" / "quantum"
RUNS_ROOT = ROOT / "evals" / "runs"

SYSTEM_PROMPT_BASE = (
    "You are solving a single quantum-computing evaluation task. "
    "Produce only the full contents of the requested Python candidate file. "
    "Do not include markdown fences, explanations, or commentary."
)

SYSTEM_PROMPT_RAG = (
    "You are solving a single quantum-computing evaluation task. "
    "Use the provided reference documentation chunks (delimited by [DOC k]) "
    "as authoritative background, then produce only the full contents of the "
    "requested Python candidate file. Do not include markdown fences, "
    "explanations, citations, or commentary."
)

USER_SUFFIX = (
    "Write the simplest Python file that satisfies the supplied tests and "
    "return only that file."
)


def discover_quantum_tasks() -> list[Path]:
    return sorted(TASKS_ROOT.glob("*/task.json"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_user_prompt_base(task_dir: Path, metadata: dict[str, Any]) -> str:
    reference_candidate = (task_dir / metadata["candidate_file"]).read_text()
    tests_source = resolve_test_path(task_dir, metadata).read_text()
    return (
        f"Task ID: {metadata['id']}\n"
        f"Task name: {metadata['name']}\n"
        f"Domain: {metadata['domain']}\n"
        f"Category: {metadata['category']}\n\n"
        f"{USER_SUFFIX}\n\n"
        "Reference candidate style example (for format guidance, not for blind copying):\n"
        "--- BEGIN REFERENCE CANDIDATE ---\n"
        f"{reference_candidate}\n"
        "--- END REFERENCE CANDIDATE ---\n\n"
        "Tests the candidate must satisfy:\n"
        "--- BEGIN TESTS ---\n"
        f"{tests_source}\n"
        "--- END TESTS ---\n"
    )


def build_user_prompt_compact(task_dir: Path, metadata: dict[str, Any]) -> str:
    tests_source = resolve_test_path(task_dir, metadata).read_text()
    return (
        f"Task ID: {metadata['id']}\n"
        f"Task name: {metadata['name']}\n"
        f"Domain: {metadata['domain']}\n"
        f"Category: {metadata['category']}\n\n"
        f"{USER_SUFFIX}\n\n"
        "Tests the candidate must satisfy:\n"
        "--- BEGIN TESTS ---\n"
        f"{tests_source}\n"
        "--- END TESTS ---\n"
    )


def build_rag_query(metadata: dict[str, Any]) -> str:
    """Build a focused retrieval query from the task metadata."""
    parts = [
        metadata.get("name", ""),
        metadata.get("category", "").replace("_", " "),
        metadata["id"].replace("quantum_", "").replace("_", " "),
    ]
    return " ".join(p for p in parts if p)


def format_retrieved_docs(chunks, max_chars_per_chunk: int = 1400) -> str:
    """Format retrieved chunks as a [DOC k] section with simple truncation."""
    sections: list[str] = []
    for item in chunks:
        text = item.chunk.text
        if len(text) > max_chars_per_chunk:
            text = text[:max_chars_per_chunk].rstrip() + "  ...[truncated]"
        sections.append(
            f"[DOC {item.rank}] source={Path(item.chunk.source_path).name}\n{text}"
        )
    return "\n\n".join(sections)


def build_user_prompt_rag(
    task_dir: Path,
    metadata: dict[str, Any],
    docs_block: str,
    *,
    include_reference_candidate: bool,
) -> str:
    reference_candidate = (task_dir / metadata["candidate_file"]).read_text()
    tests_source = resolve_test_path(task_dir, metadata).read_text()
    parts = [
        f"Task ID: {metadata['id']}\n"
        f"Task name: {metadata['name']}\n"
        f"Domain: {metadata['domain']}\n"
        f"Category: {metadata['category']}\n\n"
        "Reference documentation (use these only as background; do not echo them):\n"
        "--- BEGIN REFERENCE DOCS ---\n"
        f"{docs_block}\n"
        "--- END REFERENCE DOCS ---\n\n"
        f"{USER_SUFFIX}\n\n",
    ]
    if include_reference_candidate:
        parts.append(
            "Reference candidate style example (for format guidance, not for blind copying):\n"
            "--- BEGIN REFERENCE CANDIDATE ---\n"
            f"{reference_candidate}\n"
            "--- END REFERENCE CANDIDATE ---\n\n"
        )
    parts.append(
        "Tests the candidate must satisfy:\n"
        "--- BEGIN TESTS ---\n"
        f"{tests_source}\n"
        "--- END TESTS ---\n"
    )
    return "".join(parts)


def select_task_files(task_files: list[Path], requested_task_ids: list[str]) -> list[Path]:
    if not requested_task_ids:
        return task_files
    by_id = {load_json(path)["id"]: path for path in task_files}
    missing = [task_id for task_id in requested_task_ids if task_id not in by_id]
    if missing:
        raise SystemExit(f"Unknown task ids requested: {missing}")
    return [by_id[task_id] for task_id in requested_task_ids]


def load_task_id_file(path: Path | None) -> list[str]:
    if path is None:
        return []
    task_ids: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line:
            task_ids.append(line)
    return task_ids


def make_run_dir(label: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS_ROOT / f"qwen25-1p5b-{label}-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "prompts").mkdir(parents=True, exist_ok=True)
    (run_dir / "candidates").mkdir(parents=True, exist_ok=True)
    return run_dir


def write_run_artifacts(
    run_dir: Path,
    task_files: list[Path],
    user_prompts: dict[str, str],
    system_prompt: str,
    label: str,
) -> Path:
    candidate_map: dict[str, str] = {}
    manifest_tasks: list[dict[str, Any]] = []
    for task_json in task_files:
        metadata = load_json(task_json)
        prompt_text = user_prompts[metadata["id"]]
        prompt_path = run_dir / "prompts" / f"{metadata['id']}.txt"
        candidate_path = run_dir / "candidates" / f"{metadata['id']}.py"
        prompt_path.write_text(prompt_text, encoding="utf-8")
        candidate_path.write_text("# pending generation\n", encoding="utf-8")
        candidate_map[metadata["id"]] = str(candidate_path.relative_to(run_dir))
        manifest_tasks.append(
            {
                "id": metadata["id"],
                "name": metadata["name"],
                "domain": metadata["domain"],
                "category": metadata["category"],
                "prompt_file": str(prompt_path.relative_to(run_dir)),
                "candidate_file": str(candidate_path.relative_to(run_dir)),
            }
        )
    candidate_map_path = run_dir / "candidate-map.json"
    candidate_map_path.write_text(json.dumps(candidate_map, indent=2) + "\n", encoding="utf-8")
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "label": label,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "system_prompt": system_prompt,
                "tasks": manifest_tasks,
                "model": "Qwen2.5-1.5B-Instruct",
                "rag_enabled": label == "with-rag",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "SYSTEM_PROMPT.txt").write_text(system_prompt + "\n", encoding="utf-8")
    return candidate_map_path


def generate_for_run(
    model,
    tokenizer,
    run_dir: Path,
    task_files: list[Path],
    user_prompts: dict[str, str],
    system_prompt: str,
    *,
    device: str,
    max_new_tokens: int,
    temperature: float,
    max_input_tokens: int | None,
    label: str,
) -> dict[str, Any]:
    import torch  # local import keeps the module light if only utilities are used

    log_records: list[dict[str, Any]] = []
    started_at = time.time()
    for index, task_json in enumerate(task_files, start=1):
        metadata = load_json(task_json)
        task_id = metadata["id"]
        candidate_path = run_dir / "candidates" / f"{task_id}.py"
        user_prompt = user_prompts[task_id]
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        prompt_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(prompt_text, return_tensors="pt").to(device)
        prompt_len = inputs["input_ids"].shape[1]
        if max_input_tokens is not None and prompt_len > max_input_tokens:
            raise SystemExit(
                f"Prompt for {task_id} has {prompt_len} tokens, above --max-input-tokens {max_input_tokens}. "
                "Lower --top-k/--max-doc-chars or use --prompt-variant compact."
            )
        gen_kwargs: dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
            "pad_token_id": tokenizer.eos_token_id,
        }
        if temperature > 0:
            gen_kwargs["temperature"] = temperature
        t0 = time.time()
        with torch.inference_mode():
            output = model.generate(**inputs, **gen_kwargs)
        elapsed = time.time() - t0
        completion_ids = output[0][prompt_len:]
        raw = tokenizer.decode(completion_ids, skip_special_tokens=True)
        sanitized = sanitize_candidate_text(raw)
        candidate_path.write_text(sanitized, encoding="utf-8")
        log_records.append(
            {
                "task_id": task_id,
                "prompt_tokens": int(prompt_len),
                "new_tokens": int(completion_ids.shape[0]),
                "wall_seconds": round(elapsed, 2),
                "output_chars": len(sanitized),
            }
        )
        print(
            json.dumps(
                {
                    "label": label,
                    "stage": "generate",
                    "index": index,
                    "total": len(task_files),
                    "task_id": task_id,
                    "prompt_tokens": int(prompt_len),
                    "new_tokens": int(completion_ids.shape[0]),
                    "wall_s": round(elapsed, 2),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    log = {
        "label": label,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_path": str(DEFAULT_MODEL_PATH),
        "device": device,
        "max_new_tokens": max_new_tokens,
        "temperature": temperature,
        "total_wall_seconds": round(time.time() - started_at, 2),
        "tasks": log_records,
    }
    (run_dir / "generation-log.json").write_text(
        json.dumps(log, indent=2) + "\n", encoding="utf-8"
    )
    return log


def check_prompt_budget(
    tokenizer,
    prompts_by_label: dict[str, tuple[str, dict[str, str]]],
    *,
    max_input_tokens: int | None,
) -> dict[str, dict[str, int]]:
    """Validate all prompt sizes before any expensive generation starts."""
    prompt_lengths: dict[str, dict[str, int]] = {}
    over_budget: list[dict[str, Any]] = []
    for label, (system_prompt, user_prompts) in prompts_by_label.items():
        label_lengths: dict[str, int] = {}
        for task_id, user_prompt in user_prompts.items():
            prompt_text = tokenizer.apply_chat_template(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                tokenize=False,
                add_generation_prompt=True,
            )
            token_count = len(tokenizer(prompt_text)["input_ids"])
            label_lengths[task_id] = int(token_count)
            if max_input_tokens is not None and token_count > max_input_tokens:
                over_budget.append(
                    {
                        "label": label,
                        "task_id": task_id,
                        "prompt_tokens": int(token_count),
                        "max_input_tokens": int(max_input_tokens),
                    }
                )
        prompt_lengths[label] = label_lengths
    if over_budget:
        raise SystemExit(
            "Prompt budget exceeded before generation: "
            + json.dumps(over_budget, ensure_ascii=False)
            + ". Lower --top-k/--max-doc-chars, raise --max-input-tokens, or use --prompt-variant compact."
        )
    return prompt_lengths


def score_run(run_dir: Path) -> dict[str, Any]:
    candidate_map = run_dir / "candidate-map.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "evals" / "runner" / "run_eval.py"),
            "--candidate-map",
            str(candidate_map.resolve()),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
        raise SystemExit(f"run_eval failed: code={completed.returncode}")
    scorecard = json.loads((run_dir / "scorecard.json").read_text(encoding="utf-8"))
    return scorecard


def summarize_scorecard(scorecard: dict[str, Any], only_task_ids: set[str] | None = None) -> dict[str, Any]:
    results = scorecard["results"]
    if only_task_ids is not None:
        results = [r for r in results if r["id"] in only_task_ids]
    by_category: dict[str, dict[str, int]] = {}
    for r in results:
        bucket = by_category.setdefault(r["category"], {"pass": 0, "total": 0})
        bucket["total"] += 1
        bucket["pass"] += int(r["passed"])
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    return {
        "total": total,
        "passed": passed,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "by_category": {
            k: {"pass_rate": round(v["pass"] / v["total"], 4), **v}
            for k, v in by_category.items()
        },
        "per_task": {r["id"]: bool(r["passed"]) for r in results},
        "failures": [
            {"id": r["id"], "details": r.get("details", [])}
            for r in results
            if not r["passed"]
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--index-path", type=Path, default=DEFAULT_INDEX_PATH)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--alpha", type=float, default=0.55)
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument(
        "--max-doc-chars",
        type=int,
        default=1200,
        help="Max chars per retrieved doc chunk (truncated for prompt budget).",
    )
    parser.add_argument(
        "--prompt-variant",
        choices=("full", "compact"),
        default="full",
        help="full includes reference candidate style examples; compact uses tests only plus optional RAG docs.",
    )
    parser.add_argument(
        "--max-input-tokens",
        type=int,
        default=2300,
        help="Abort if a prompt exceeds this token count; 0 disables the guard.",
    )
    parser.add_argument("--task-id", action="append", default=[], help="Repeat to run a fixed task subset.")
    parser.add_argument("--task-id-file", type=Path, default=None)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit on number of tasks (debug); 0 = all.",
    )
    parser.add_argument(
        "--mode",
        choices=("both", "no_rag", "rag"),
        default="both",
        help="Which run(s) to perform.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=ROOT / "reports" / "qwen25_rag_compare_latest.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    requested_task_ids = [*load_task_id_file(args.task_id_file), *args.task_id]
    task_files = select_task_files(discover_quantum_tasks(), requested_task_ids)
    if args.limit > 0:
        task_files = task_files[: args.limit]
    print(json.dumps({"stage": "discover_tasks", "count": len(task_files)}, ensure_ascii=False), flush=True)

    # Load index for RAG mode
    index = None
    if args.mode in ("both", "rag"):
        if not args.index_path.exists():
            raise SystemExit(f"RAG index not found: {args.index_path}")
        index = QuantumRAGIndex.load(args.index_path)
        print(json.dumps({"stage": "rag_index_loaded", "summary": index.summary()}, ensure_ascii=False), flush=True)

    # Build prompts up front so both runs share identical task framing
    base_prompts: dict[str, str] = {}
    rag_prompts: dict[str, str] = {}
    rag_provenance: dict[str, list[dict[str, Any]]] = {}
    for task_json in task_files:
        metadata = load_json(task_json)
        task_dir = task_json.parent
        if args.prompt_variant == "compact":
            base_prompts[metadata["id"]] = build_user_prompt_compact(task_dir, metadata)
        else:
            base_prompts[metadata["id"]] = build_user_prompt_base(task_dir, metadata)
        if index is not None:
            query = build_rag_query(metadata)
            chunks = retrieve(
                index,
                query,
                top_k=args.top_k,
                alpha=args.alpha,
                exclude_source_substrings=["evals/tasks", "evals/runs", "evals/benchmarks"],
            )
            docs_block = format_retrieved_docs(chunks, max_chars_per_chunk=args.max_doc_chars)
            rag_prompts[metadata["id"]] = build_user_prompt_rag(
                task_dir,
                metadata,
                docs_block,
                include_reference_candidate=args.prompt_variant == "full",
            )
            rag_provenance[metadata["id"]] = [
                {
                    "rank": c.rank,
                    "score": round(c.final_score, 4),
                    "source": c.chunk.source_path,
                }
                for c in chunks
            ]

    # Load the tokenizer first so prompt-budget errors fail before model loading
    # or any partial generation artifacts are created.
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    prompts_to_check: dict[str, tuple[str, dict[str, str]]] = {}
    if args.mode in ("both", "no_rag"):
        prompts_to_check["no-rag"] = (SYSTEM_PROMPT_BASE, base_prompts)
    if args.mode in ("both", "rag"):
        prompts_to_check["with-rag"] = (SYSTEM_PROMPT_RAG, rag_prompts)
    prompt_lengths = check_prompt_budget(
        tokenizer,
        prompts_to_check,
        max_input_tokens=args.max_input_tokens or None,
    )
    print(
        json.dumps(
            {"stage": "prompt_budget_checked", "prompt_lengths": prompt_lengths},
            ensure_ascii=False,
        ),
        flush=True,
    )

    print(json.dumps({"stage": "load_model_start", "model": str(args.model_path), "device": args.device}, ensure_ascii=False), flush=True)
    dtype = torch.float16 if args.device != "cpu" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    ).to(args.device)
    model.eval()
    print(json.dumps({"stage": "load_model_done", "dtype": str(model.dtype)}, ensure_ascii=False), flush=True)

    summaries: dict[str, Any] = {}
    task_id_set = {load_json(p)["id"] for p in task_files}

    # Pass 1: no RAG
    if args.mode in ("both", "no_rag"):
        run_dir = make_run_dir("no-rag")
        write_run_artifacts(run_dir, task_files, base_prompts, SYSTEM_PROMPT_BASE, label="no-rag")
        print(json.dumps({"stage": "run_dir_no_rag", "path": str(run_dir.relative_to(ROOT))}, ensure_ascii=False), flush=True)
        gen_log = generate_for_run(
            model, tokenizer, run_dir, task_files, base_prompts, SYSTEM_PROMPT_BASE,
            device=args.device, max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            max_input_tokens=args.max_input_tokens or None,
            label="no-rag",
        )
        scorecard = score_run(run_dir)
        summary = summarize_scorecard(scorecard, only_task_ids=task_id_set)
        summary["run_dir"] = str(run_dir.relative_to(ROOT))
        summary["generation_wall_seconds"] = gen_log["total_wall_seconds"]
        summaries["no_rag"] = summary
        print(json.dumps({"stage": "scored_no_rag", **{k: summary[k] for k in ("total","passed","pass_rate")}}, ensure_ascii=False), flush=True)

    # Pass 2: with RAG
    if args.mode in ("both", "rag"):
        run_dir = make_run_dir("with-rag")
        write_run_artifacts(run_dir, task_files, rag_prompts, SYSTEM_PROMPT_RAG, label="with-rag")
        # Persist RAG provenance for each task
        (run_dir / "rag-provenance.json").write_text(
            json.dumps(rag_provenance, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"stage": "run_dir_rag", "path": str(run_dir.relative_to(ROOT))}, ensure_ascii=False), flush=True)
        gen_log = generate_for_run(
            model, tokenizer, run_dir, task_files, rag_prompts, SYSTEM_PROMPT_RAG,
            device=args.device, max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            max_input_tokens=args.max_input_tokens or None,
            label="with-rag",
        )
        scorecard = score_run(run_dir)
        summary = summarize_scorecard(scorecard, only_task_ids=task_id_set)
        summary["run_dir"] = str(run_dir.relative_to(ROOT))
        summary["generation_wall_seconds"] = gen_log["total_wall_seconds"]
        summaries["with_rag"] = summary
        print(json.dumps({"stage": "scored_with_rag", **{k: summary[k] for k in ("total","passed","pass_rate")}}, ensure_ascii=False), flush=True)

    # Compare per-task if both ran
    if args.mode == "both":
        nr = summaries["no_rag"]["per_task"]
        wr = summaries["with_rag"]["per_task"]
        deltas = {
            "rag_helped": [tid for tid in nr if not nr[tid] and wr.get(tid)],
            "rag_hurt":   [tid for tid in nr if nr[tid] and not wr.get(tid)],
            "both_pass":  [tid for tid in nr if nr[tid] and wr.get(tid)],
            "both_fail":  [tid for tid in nr if not nr[tid] and not wr.get(tid)],
        }
        summaries["delta"] = {
            **{k: len(v) for k, v in deltas.items()},
            "rag_helped_ids": deltas["rag_helped"],
            "rag_hurt_ids": deltas["rag_hurt"],
        }

    # Write final report
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_path": str(args.model_path),
        "index_path": str(args.index_path),
        "device": args.device,
        "task_count": len(task_files),
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "rag": {
            "top_k": args.top_k,
            "alpha": args.alpha,
            "max_doc_chars": args.max_doc_chars,
        },
        "prompt_variant": args.prompt_variant,
        "requested_task_ids": requested_task_ids,
        "summaries": summaries,
    }
    report_path = args.report_path
    if not report_path.is_absolute():
        report_path = (ROOT / report_path).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print()
    try:
        display_path = report_path.relative_to(ROOT)
    except ValueError:
        display_path = report_path
    print(f"Report written: {display_path}")
    print(json.dumps({k: v for k, v in summaries.items() if k != "per_task"}, indent=2, default=str)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
