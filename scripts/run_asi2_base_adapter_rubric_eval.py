#!/usr/bin/env python3
"""Evaluate base vs LoRA adapter on ASI2 with executable and rubric scores."""

from __future__ import annotations

import argparse
import ast
import gc
import importlib.util
import json
import math
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer,
    PreTrainedTokenizerFast,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.model_backend import (
    ensure_text_backend_preflight,
    load_causal_lm_with_text_backend_preflight,
)
from training.text_preprocessor_backend import load_text_preprocessor_backend

TASK_IDS = [
    "quantum_gate_alias_normalization",
    "quantum_phase_estimation_circuit",
    "quantum_qaoa_maxcut",
    "quantum_superdense_coding",
    "quantum_grover_oracle_diffusion",
    "quantum_density_matrix_partial_trace",
    "quantum_channel_depolarizing",
    "quantum_ghz_state_witness",
    "software_docstring_contract",
    "software_duplicate_logic_refactor",
    "software_off_by_one_bugfix",
    "software_retry_decorator",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="npu")
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_task(task_id: str) -> Path:
    suffix = task_id.split("_", 1)[1]
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
    model = load_causal_lm_with_text_backend_preflight(
        str(model_path),
        auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM,
        model_kwargs={"trust_remote_code": True, "low_cpu_mem_usage": True, "torch_dtype": "auto"},
    ).to(device)
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


def build_prompt(task_dir: Path, meta: dict[str, Any]) -> str:
    tests = (task_dir / meta.get("test_file", "tests.py")).read_text(encoding="utf-8")
    candidate_name = meta.get("candidate_file", "candidate.py")
    existing = (
        (task_dir / candidate_name).read_text(encoding="utf-8")
        if (task_dir / candidate_name).exists()
        else ""
    )
    return (
        f"Task: {meta['name']}\n"
        f"Domain: {meta['domain']}\n"
        f"Category: {meta['category']}\n\n"
        "Write candidate.py that satisfies this test harness.\n\n"
        "Tests:\n"
        "```python\n"
        f"{tests[:8000]}\n"
        "```\n\n"
        "Existing/reference API shape, if useful:\n"
        "```python\n"
        f"{existing[:3000]}\n"
        "```\n"
    )


def sanitize_code(text: str) -> str:
    value = text.strip()
    fenced = re.search(r"```(?:python)?\s*(.*?)```", value, re.S | re.I)
    if fenced:
        value = fenced.group(1).strip()
    markers = ["Here is", "Explanation:"]
    lines = value.splitlines()
    while lines and any(lines[0].strip().startswith(marker) for marker in markers):
        lines.pop(0)
    return "\n".join(lines).strip() + "\n"


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


def load_test_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_single_file_test(
    task_dir: Path, meta: dict[str, Any], code: str, out_path: Path
) -> dict[str, Any]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(code, encoding="utf-8")
    try:
        module = load_test_module(task_dir / meta.get("test_file", "tests.py"))
        result = module.run_tests(str(out_path))
        return {"passed": bool(result.get("passed")), "details": list(result.get("details", []))}
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "details": [f"{type(exc).__name__}: {exc}"]}


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
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            for node in ast.walk(tree)
        )
    )
    has_doc = bool(tree and ast.get_docstring(tree))
    long_lines = sum(1 for line in lines if len(line) > 100)
    nested_loops = 0
    if tree:
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                nested_loops += sum(
                    isinstance(child, (ast.For, ast.While))
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
        code = generate(model, backend, prompt, args.device, args.max_new_tokens)
        candidate_path = args.output.parent / "candidates" / model_name / f"{meta['id']}.py"
        test_result = run_single_file_test(task_dir, meta, code, candidate_path)
        scores = static_scores(code, test_result["passed"])
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
                "output_chars": len(code),
            }
        )
    return records


def main() -> int:
    args = parse_args()
    started = time.time()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    selected = TASK_IDS[: args.limit] if args.limit else TASK_IDS
    tasks = []
    for task_id in selected:
        task_json = find_task(task_id)
        meta = load_json(task_json)
        if meta.get("candidate_files"):
            continue
        tasks.append((task_json, meta))

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
    adapter_base = load_model(args.base_model, args.device)
    adapter = PeftModel.from_pretrained(adapter_base, str(args.adapter))
    adapter.eval()
    adapter_records = run_model("adapter", adapter, backend, tasks, args)
    adapter_eval_loss = eval_loss(adapter, backend, eval_file, args.device)

    records = base_records + adapter_records
    payload = {
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_model": str(args.base_model),
        "adapter": str(args.adapter),
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
