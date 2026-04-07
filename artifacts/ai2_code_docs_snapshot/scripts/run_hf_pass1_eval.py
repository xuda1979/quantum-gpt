#!/usr/bin/env python3
"""Run a prepared eval batch against a local HF/PEFT model and score pass@1."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from peft import PeftModel
from training.qwen_sft_peft import TextPreprocessorBackend, load_text_preprocessor_backend

TOKEN_BUDGET_PRESETS = {
    "default": 192,
    # The harder quantum gate prompts plus code-only output can exceed 384 tokens.
    "quantum_heavy": 512,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, default=None)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--max-new-tokens", type=int, default=192)
    parser.add_argument(
        "--token-budget-preset",
        choices=sorted(TOKEN_BUDGET_PRESETS),
        default=None,
        help="Named max-new-token preset. If provided, overrides --max-new-tokens.",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=0, help="Optional max tasks to execute from manifest order.")
    parser.add_argument("--score", action="store_true", help="Run evals/runner/run_eval.py on the filled candidate map.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text_backend(model_path: Path) -> TextPreprocessorBackend:
    return load_text_preprocessor_backend(str(model_path), AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast)


def load_model(model_path: Path, device: str):
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        torch_dtype="auto",
    ).to(device)
    generation_config = getattr(model, "generation_config", None)
    if generation_config is not None:
        generation_config.do_sample = False
        generation_config.temperature = 1.0
        generation_config.top_p = 1.0
        generation_config.top_k = 50
    model.eval()
    return model


def render_prompt(backend: TextPreprocessorBackend, system_prompt: str, user_prompt: str) -> str:
    messages = []
    if system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    render_backend = backend.render_backend
    if hasattr(render_backend, "apply_chat_template"):
        try:
            return render_backend.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            return render_backend.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return "\n\n".join(f"{message['role'].upper()}: {message['content']}" for message in messages)


def build_inputs(backend: TextPreprocessorBackend, prompt_text: str, device: str):
    tokens = backend.text_backend(prompt_text, return_tensors="pt")
    return {key: value.to(device) for key, value in tokens.items()}


def sanitize_candidate_text(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("<think>") and "</think>" in stripped:
        stripped = stripped.split("</think>", 1)[1].lstrip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped + ("\n" if stripped else "")


def generate_candidate(
    model: Any,
    backend: TextPreprocessorBackend,
    system_prompt: str,
    user_prompt: str,
    max_new_tokens: int,
    temperature: float,
    device: str,
) -> str:
    prompt_text = render_prompt(backend, system_prompt=system_prompt, user_prompt=user_prompt)
    inputs = build_inputs(backend, prompt_text, device)
    prompt_len = inputs["input_ids"].shape[1]
    tokenizer = backend.text_backend
    generation_kwargs = {
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature > 0,
        "temperature": temperature if temperature > 0 else None,
        "pad_token_id": tokenizer.eos_token_id,
    }
    generation_kwargs = {key: value for key, value in generation_kwargs.items() if value is not None}
    with torch.inference_mode():
        output = model.generate(**inputs, **generation_kwargs)
    completion = output[0][prompt_len:]
    return sanitize_candidate_text(tokenizer.decode(completion, skip_special_tokens=True))


def score_run(run_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "evals" / "runner" / "run_eval.py"),
            "--candidate-map",
            str((run_dir / "candidate-map.json").resolve()),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    manifest = load_json(run_dir / "manifest.json")
    if args.token_budget_preset is None:
        manifest_preset = manifest.get("token_budget_preset")
        if manifest_preset is not None:
            if manifest_preset not in TOKEN_BUDGET_PRESETS:
                raise SystemExit(
                    f"Unknown token budget preset in {run_dir / 'manifest.json'}: {manifest_preset!r}"
                )
            args.token_budget_preset = manifest_preset
    if args.token_budget_preset is not None:
        args.max_new_tokens = TOKEN_BUDGET_PRESETS[args.token_budget_preset]
    system_prompt = (run_dir / "SYSTEM_PROMPT.txt").read_text(encoding="utf-8")
    tasks = manifest.get("tasks", [])
    if args.limit > 0:
        tasks = tasks[: args.limit]

    backend = load_text_backend(args.base_model)
    tokenizer = backend.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    print(json.dumps({"stage": "load_base_start", "model": str(args.base_model), "device": args.device}, ensure_ascii=False), flush=True)
    base_model = load_model(args.base_model, args.device)
    active_model = base_model
    if args.adapter is not None:
        print(json.dumps({"stage": "load_adapter_start", "adapter": str(args.adapter)}, ensure_ascii=False), flush=True)
        active_model = PeftModel.from_pretrained(base_model, str(args.adapter))
        active_model.eval()
        print(json.dumps({"stage": "load_adapter_done"}, ensure_ascii=False), flush=True)

    generation_records: list[dict[str, Any]] = []
    started_at = time.time()
    for index, task in enumerate(tasks, start=1):
        prompt_path = run_dir / task["prompt_file"]
        candidate_path = run_dir / task["candidate_file"]
        user_prompt = prompt_path.read_text(encoding="utf-8")
        print(json.dumps({"stage": "generate", "index": index, "total": len(tasks), "task_id": task["id"]}, ensure_ascii=False), flush=True)
        candidate_text = generate_candidate(
            active_model,
            backend,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            device=args.device,
        )
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.write_text(candidate_text, encoding="utf-8")
        generation_records.append(
            {
                "task_id": task["id"],
                "candidate_path": str(candidate_path.relative_to(run_dir)),
                "output_chars": len(candidate_text),
                "started_at_sec": round(time.time() - started_at, 3),
            }
        )

    generation_log = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_model": str(args.base_model),
        "adapter": str(args.adapter) if args.adapter else None,
        "device": args.device,
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "tasks": generation_records,
    }
    generation_log_path = run_dir / "hf-pass1-generation-log.json"
    generation_log_path.write_text(json.dumps(generation_log, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"stage": "generation_done", "log_path": str(generation_log_path)}, ensure_ascii=False), flush=True)

    if not args.score:
        return 0

    completed = score_run(run_dir)
    if completed.stdout:
        sys.stdout.write(completed.stdout)
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
