#!/usr/bin/env python3
"""Evaluate base vs LoRA adapter on ASI2 with executable and rubric scores."""

from __future__ import annotations

import argparse
import ast
import gc
import json
import math
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch

try:  # 2026-09-02: peft is box-side only; local prompt-isolation tests import
    # this module for its PROMPT BUILDER, not its model loader (H-83 class).
    from peft import PeftModel
except ImportError:  # pragma: no cover - exercised only on box
    PeftModel = None

from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer,
    PreTrainedTokenizerFast,
)

ROOT = Path(os.environ.get("QG_ROOT", str(Path(__file__).resolve().parents[1])))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.runner.candidate_sanitize import sanitize_candidate_text
from training.model_backend import (
    ensure_text_backend_preflight,
    load_causal_lm_with_text_backend_preflight,
)
from training.text_preprocessor_backend import load_text_preprocessor_backend

DEFAULT_BENCHMARK = "evals/benchmarks/quantum_grpo_training_v1.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=ROOT / DEFAULT_BENCHMARK,
        help="benchmark file: one task id per line, '#' comments (default: 13-task training set)",
    )
    parser.add_argument("--device", default="npu")
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--limit", type=int, default=0)
    # 2026-09-14 (parallel-eval speedup): slice the benchmark task list so
    # multiple independent workers -- each sharded over its OWN NPU subset --
    # can evaluate disjoint task groups CONCURRENTLY instead of one serial
    # worker. Each worker sets ASCEND_RT_VISIBLE_DEVICES to its NPU subset and
    # passes a disjoint --task-start/--task-count. Guards: clamp to the real
    # list length; count<=0 means "rest of the list".
    parser.add_argument(
        "--task-start",
        type=int,
        default=0,
        help="0-based index of the first task this worker handles (parallel-eval split)",
    )
    parser.add_argument(
        "--task-count",
        type=int,
        default=0,
        help="number of tasks this worker handles; 0 = through the end of the list",
    )
    parser.add_argument("--harness-timeout", type=int, default=300)
    parser.add_argument(
        "--hide-reference",
        action="store_true",
        help="accepted for compatibility; the no-leak prompt is now unconditional",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_task_ids(bench_path: Path) -> list[str]:
    if not bench_path.is_file():
        raise SystemExit(f"benchmark file not found: {bench_path}")
    ids: list[str] = []
    for line in bench_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ids.append(line.split()[0])
    if not ids:
        raise SystemExit(f"benchmark file {bench_path} has no task ids")
    return ids


def find_task(task_id: str) -> Path:
    suffix = task_id.split("_", 1)[1] if "_" in task_id else task_id
    for path in (ROOT / "evals" / "tasks").glob("*/*/task.json"):
        data = load_json(path)
        if data.get("id") == task_id or path.parent.name == suffix:
            return path
    raise FileNotFoundError(task_id)


def load_backend(model_path: Path):
    ensure_text_backend_preflight(str(model_path), AutoConfig)
    backend = load_text_preprocessor_backend(
        str(model_path), AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast
    )
    tokenizer = backend.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return backend


def load_model(model_path: Path, device: str):
    model_kwargs = {"trust_remote_code": True, "low_cpu_mem_usage": True, "torch_dtype": "auto"}
    if device.startswith("npu"):
        # 2026-08-22: the full 27B (54GB bf16) on ONE 64GB card fragments the
        # NPU pool at 44-59 GiB and OOMs the load (repeated). Use the trainer's
        # PROVEN balanced-layers shard across ALL visible NPUs (~7GB/card).
        from training.qwen_sft_peft import (
            _visible_npu_indices,
            build_balanced_npu_layer_device_map,
        )

        visible = _visible_npu_indices()
        cfg = AutoConfig.from_pretrained(str(model_path), trust_remote_code=True)
        model_kwargs["device_map"] = build_balanced_npu_layer_device_map(cfg, visible)
        model_kwargs["max_memory"] = {f"npu:{idx}": "54GiB" for idx in range(len(visible))}
    model = load_causal_lm_with_text_backend_preflight(
        str(model_path),
        auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM,
        model_kwargs=model_kwargs,
    )
    if not device.startswith("npu"):
        model = model.to(device)
    return model
    if getattr(model, "generation_config", None) is not None:
        model.generation_config.do_sample = False
        model.generation_config.temperature = 1.0
        model.generation_config.top_p = 1.0
        model.generation_config.top_k = 50
    model.eval()
    return model


def render_prompt(backend: Any, prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "Return only a complete Python solution. Do not include markdown fences or explanation.",
        },
        {"role": "user", "content": prompt},
    ]
    renderer = backend.render_backend
    if hasattr(renderer, "apply_chat_template"):
        try:
            return renderer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
            )
        except TypeError:
            return renderer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
    return "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)


def build_prompt(task_dir: Path, meta: dict[str, Any], hide_reference: bool = False) -> str:
    # 2026-08-21 (review finding): QUESTION-ONLY prompt. The old prompt embedded
    # tests.py (up to 8k chars — for distillation tasks that is the EXPECTED
    # stdout verbatim) plus the reference candidate.py — a live leak that
    # inflated base pass@1 (10/12). Prompt mirrors the trainer's build_prompt:
    # task_prompt > description > name, + domain/category. (hide_reference kept
    # for call-site compatibility; embedding is gone entirely.)
    if meta.get("task_prompt"):
        first = str(meta["task_prompt"])
    elif meta.get("description"):
        first = f"Task: {meta['description']}"
    else:
        first = f"Task: {meta.get('name', task_dir.name)}"
    return "\n\n".join(
        [
            first,
            f"Domain: {meta.get('domain', 'unknown')}\nCategory: {meta.get('category', 'unknown')}",
            "Return only the final Python code.",
        ]
    )


def sanitize_code(text: str) -> str:
    # 2026-09-08: delegate to the canonical sanitizer (repo convention, pinned
    # by tests/test_script_candidate_sanitize_wiring.py). Fixes the wave-6
    # failure class: the old inline fence regex required a CLOSING fence, so
    # token-cap-truncated generations starting "```python" hit ast.parse raw
    # and scored ~0. Prose-marker trimming stays FIRST (canonical sanitizer has
    # no prose-marker handling); fences/think-blocks/terminal markers and the
    # longest-parseable-prefix repair are the canonical sanitizer's job.
    value = text.strip()
    markers = ["Here is", "Explanation:"]
    lines = value.splitlines()
    while lines and any(lines[0].strip().startswith(marker) for marker in markers):
        lines.pop(0)
    value = "\n".join(lines).strip()
    sanitized = sanitize_candidate_text(value) if value else ""
    return sanitized if sanitized.endswith("\n") or not sanitized else sanitized + "\n"


def generate(model: Any, backend: Any, prompt: str, device: str, max_new_tokens: int) -> str:
    prompt_text = render_prompt(backend, prompt)
    tokens = backend.text_backend(prompt_text, return_tensors="pt")
    tokens = {k: v.to(device) for k, v in tokens.items()}
    prompt_len = tokens["input_ids"].shape[1]
    with torch.inference_mode():
        output = model.generate(
            **tokens,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=backend.text_backend.eos_token_id,
        )
    return sanitize_code(
        backend.text_backend.decode(output[0][prompt_len:], skip_special_tokens=True)
    )


def run_single_file_test(
    task_dir: Path, meta: dict[str, Any], code: str, out_path: Path, timeout: int
) -> dict[str, Any]:
    """Run the harness in a FRESH interpreter (fork-safe on the NPU box)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(code, encoding="utf-8")
    runner = ROOT / "evals" / "runner" / "single_candidate_eval.py"
    if not runner.is_file():
        return {
            "passed": False,
            "details": [f"single_candidate_eval.py missing at {runner} (deploy it first)"],
        }
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(runner),
                "--candidate",
                str(out_path),
                "--tests",
                str(task_dir / meta.get("test_file", "tests.py")),
                "--task-dir",
                str(task_dir),
                "--meta",
                str(task_dir / "task.json"),
                "--timeout",
                str(timeout),
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 60,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "details": ["harness subprocess timed out"]}
    lines = [ln for ln in (proc.stdout or "").strip().splitlines() if ln.strip()]
    if not lines:
        return {
            "passed": False,
            "details": [f"harness produced no output: {(proc.stderr or '')[:200]}"],
        }
    try:
        result = json.loads(lines[-1])
    except json.JSONDecodeError:
        return {
            "passed": False,
            "details": [f"harness output unparseable: {lines[-1][:200]}"],
        }
    harness = result.get("harness")
    if isinstance(harness, dict) and "passed" in harness:
        return {"passed": bool(harness["passed"]), "details": list(harness.get("details", []))}
    return {
        "passed": False,
        "details": [f"harness returned no result: {str(result.get('error'))[:200]}"],
    }


def static_scores(code: str, passed: bool) -> dict[str, float]:
    try:
        tree = ast.parse(code)
        syntax_ok = True
    except SyntaxError:
        tree = None
        syntax_ok = False
    lines = [line for line in code.splitlines() if line.strip()]
    line_count = len(lines)
    has_defs = bool(
        tree
        and any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))  # noqa: UP038
            for node in ast.walk(tree)
        )
    )
    has_doc = bool(tree and ast.get_docstring(tree))
    long_lines = sum(1 for line in lines if len(line) > 100)
    nested_loops = 0
    if tree:
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):  # noqa: UP038
                nested_loops += sum(
                    isinstance(child, (ast.For, ast.While))  # noqa: UP038
                    for child in ast.walk(node)
                    if child is not node
                )
    grammar = 5.0 if syntax_ok else 0.0
    algorithm = 5.0 if passed else (2.0 if syntax_ok else 0.0)
    code_quality = (
        1.0 + (1.5 if syntax_ok else 0.0) + (1.0 if has_defs else 0.0) + (0.5 if has_doc else 0.0)
    )
    code_quality += 1.0 if 5 <= line_count <= 160 else 0.3
    code_quality -= min(1.0, long_lines * 0.2)
    efficiency = 4.0 if syntax_ok else 0.0
    efficiency += 1.0 if nested_loops <= 1 else 0.0
    efficiency -= 0.5 if line_count > 200 else 0.0
    return {
        "grammar": round(max(0.0, min(5.0, grammar)), 2),
        "algorithm": round(max(0.0, min(5.0, algorithm)), 2),
        "code_quality": round(max(0.0, min(5.0, code_quality)), 2),
        "efficiency": round(max(0.0, min(5.0, efficiency)), 2),
        "overall": round(
            max(0.0, min(5.0, (grammar + algorithm + code_quality + efficiency) / 4)), 2
        ),
    }


def eval_loss(
    model: Any, backend: Any, eval_file: Path, device: str, limit: int = 20
) -> dict[str, float]:
    if not eval_file.is_file():
        return {"loss": None, "perplexity": None, "examples": 0}
    losses: list[float] = []
    rows = [
        json.loads(line)
        for line in eval_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for row in rows[:limit]:
        messages = row.get("messages", [])
        text = backend.render_backend.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        tokens = backend.text_backend(text, return_tensors="pt", truncation=True, max_length=512)
        labels = tokens["input_ids"].clone()
        tokens = {k: v.to(device) for k, v in tokens.items()}
        labels = labels.to(device)
        with torch.inference_mode():
            loss = model(**tokens, labels=labels).loss
        losses.append(float(loss.detach().cpu()))
    mean_loss = sum(losses) / max(1, len(losses))
    return {"loss": mean_loss, "perplexity": math.exp(mean_loss), "examples": len(losses)}


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_model[record["model"]].append(record)
    out = {}
    for model_name, items in by_model.items():
        out[model_name] = {
            "pass_at_1": f"{sum(1 for x in items if x['passed'])}/{len(items)}",
            "scores": {
                key: round(sum(x["scores"][key] for x in items) / len(items), 3)
                for key in ("grammar", "algorithm", "code_quality", "efficiency", "overall")
            },
            "by_domain": {},
            "by_category": {},
        }
        for field, target in (("domain", "by_domain"), ("category", "by_category")):
            groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for item in items:
                groups[item[field]].append(item)
            for group, subset in groups.items():
                out[model_name][target][group] = {
                    "pass_at_1": f"{sum(1 for x in subset if x['passed'])}/{len(subset)}",
                    "overall": round(sum(x["scores"]["overall"] for x in subset) / len(subset), 3),
                }
    return out


def run_model(
    model_name: str,
    model: Any,
    backend: Any,
    tasks: list[tuple[Path, dict[str, Any]]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    records = []
    for index, (task_json, meta) in enumerate(tasks, 1):
        task_dir = task_json.parent
        prompt = build_prompt(task_dir, meta)
        print(
            json.dumps(
                {"stage": "generate", "model": model_name, "index": index, "task": meta["id"]}
            ),
            flush=True,
        )
        # C-0049 per-task fail-closed containment: a poisoned candidate
        # (generation raises or returns None) grades FAIL for ITS task
        # only -- the pinned crash-class token -- and the leg continues
        # to the remaining tasks. Never a skip, never a pass.
        code = ""
        try:
            code = generate(model, backend, prompt, args.device, args.max_new_tokens)
            candidate_path = args.output.parent / "candidates" / model_name / f"{meta['id']}.py"
            test_result = run_single_file_test(
                task_dir, meta, code, candidate_path, args.harness_timeout
            )
        except Exception as exc:  # noqa: BLE001
            test_result = dict(
                passed=False,
                details=[
                    "candidate_none_graded_fail",
                    f"{type(exc).__name__}: {exc}",
                ],
            )
            print(
                json.dumps(
                    dict(
                        stage="task_contained",
                        model=model_name,
                        task=meta["id"],
                        token="candidate_none_graded_fail",
                    )
                ),
                flush=True,
            )
        scores = static_scores(code if isinstance(code, str) else "", test_result["passed"])
        records.append(
            {
                "model": model_name,
                "task_id": meta["id"],
                "name": meta["name"],
                "domain": meta["domain"],
                "category": meta["category"],
                "candidate_path": str(candidate_path),
                "passed": test_result["passed"],
                "details": test_result["details"],
                "scores": scores,
                "output_chars": len(code) if isinstance(code, str) else 0,
                "reference_hidden": True,
                "prompt_mode": "question-only",
            }
        )
    return records


def main() -> int:
    args = parse_args()
    # C-0024: fail-closed freeze check BEFORE any eval work. Drift in, or a
    # missing file from, the pinned 18-task holdout or the scorer chain aborts
    # the leg with a nonzero exit.
    from evals.runner.holdout_freeze import HoldoutFreezeError, verify_holdout_freeze

    try:
        verify_holdout_freeze()
    except HoldoutFreezeError as exc:
        print("[freeze] FAIL-CLOSED: " + str(exc), file=sys.stderr)
        return 2
    started = time.time()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    task_ids = load_task_ids(args.benchmark)
    selected = task_ids[: args.limit] if args.limit else task_ids
    # 2026-09-14 (parallel-eval speedup): apply the disjoint slice. --task-count
    # of 0 means run to the end of the list. Clamp --task-start so it cannot
    # exceed the list.
    if args.task_start or args.task_count:
        start = max(0, min(args.task_start, len(selected)))
        if args.task_count > 0:
            selected = selected[start : start + args.task_count]
        else:
            selected = selected[start:]
        if not selected:
            raise SystemExit(f"task slice [{args.task_start}:+{args.task_count}] selects no tasks")
    tasks = []
    for task_id in selected:
        task_json = find_task(task_id)
        meta = load_json(task_json)
        if meta.get("candidate_files"):
            continue
        tasks.append((task_json, meta))
    if not tasks:
        raise SystemExit(f"no tasks selected from {args.benchmark}")
    print(
        json.dumps({"stage": "tasks", "benchmark": str(args.benchmark), "n": len(tasks)}),
        flush=True,
    )

    backend = load_backend(args.base_model)
    eval_file = (
        ROOT
        / "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft/eval_chatml.jsonl"
    )

    print(json.dumps({"stage": "load_base"}), flush=True)
    base = load_model(args.base_model, args.device)
    base_records = run_model("base", base, backend, tasks, args)
    base_eval_loss = eval_loss(base, backend, eval_file, args.device)
    del base
    gc.collect()
    if args.device == "npu" and hasattr(torch, "npu"):
        torch.npu.empty_cache()

    print(json.dumps({"stage": "load_adapter"}), flush=True)
    # 2026-08-22 (fix): the old path loaded base on CPU and then
    # ``adapter.to("npu")`` moved the ENTIRE 54GB merged model onto ONE card,
    # which OOMs whenever concurrent training holds HBM there (2 runs ~29GB on
    # card 0 -> 2.9MiB free). Mirror the trainer (qwen_sft_peft.py): load the
    # base SHARDED across all visible NPUs (balanced layer map), then wrap with
    # PeftModel directly — PEFT injects LoRA at forward time, no merge
    # transient, weights stay ~13.5GB/card.
    adapter = load_model(args.base_model, args.device)
    adapter = PeftModel.from_pretrained(adapter, str(args.adapter))
    adapter.eval()
    adapter_records = run_model("adapter", adapter, backend, tasks, args)
    adapter_eval_loss = eval_loss(adapter, backend, eval_file, args.device)

    records = base_records + adapter_records
    payload = {
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_model": str(args.base_model),
        "adapter": str(args.adapter),
        "benchmark": str(args.benchmark),
        "prompt_mode": "question-only",
        "reference_hidden": True,
        "task_ids": [meta["id"] for _, meta in tasks],
        "heldout_sft_eval": {"base": base_eval_loss, "adapter": adapter_eval_loss},
        "summary": summarize(records),
        "records": records,
        "duration_sec": round(time.time() - started, 3),
        "score_scale": "0-5; algorithm is executable test pass/fail weighted, grammar is Python syntax, quality/efficiency are static heuristics",
    }
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(args.output)
    print(
        json.dumps(
            {"stage": "done", "output": str(args.output), "summary": payload["summary"]},
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
