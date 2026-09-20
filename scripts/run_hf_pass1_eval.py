#!/usr/bin/env python3
"""Run a prepared eval batch against a local HF/PEFT model and score pass@1."""

from __future__ import annotations

import argparse
import inspect
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.runtime_overlay import configure_runtime_overlay_from_env

configure_runtime_overlay_from_env()

import torch
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer,
    PreTrainedTokenizerFast,
)

from evals.runner.candidate_sanitize import sanitize_candidate_text
from training.model_backend import (
    ensure_text_backend_preflight,
    load_causal_lm_with_text_backend_preflight,
)
from training.text_preprocessor_backend import (
    TextPreprocessorBackend,
    load_text_preprocessor_backend,
)

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
    parser.add_argument(
        "--limit", type=int, default=0, help="Optional max tasks to execute from manifest order."
    )
    parser.add_argument(
        "--score",
        action="store_true",
        help="Run evals/runner/run_eval.py on the filled candidate map.",
    )
    parser.add_argument(
        "--turboquant-enable",
        action="store_true",
        help="Enable experimental TurboQuant-style KV-cache mode during generation.",
    )
    parser.add_argument(
        "--turboquant-backend",
        default="turboquant",
        help="TurboQuant runtime backend id passed into the TurboQuant config.",
    )
    parser.add_argument(
        "--turboquant-nbits",
        type=int,
        default=4,
        help="TurboQuant KV quantization bit-width.",
    )
    parser.add_argument(
        "--turboquant-group-size",
        type=int,
        default=64,
        help="TurboQuant quantization group size.",
    )
    parser.add_argument(
        "--turboquant-residual-length",
        type=int,
        default=128,
        help="TurboQuant residual cache length kept in higher precision.",
    )
    parser.add_argument(
        "--turboquant-axis-key",
        type=int,
        default=0,
        help="TurboQuant quantization axis for key states.",
    )
    parser.add_argument(
        "--turboquant-axis-value",
        type=int,
        default=0,
        help="TurboQuant quantization axis for value states.",
    )
    parser.add_argument(
        "--turboquant-q-group-size",
        type=int,
        default=64,
        help="TurboQuant q_group_size forwarded to cache config for compatibility.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# SAPO adapter-key remapping and integrity helpers
# ---------------------------------------------------------------------------


def _remap_sapo_keys(keys: list[str]) -> list[str]:
    """Insert ``language_model`` segment into text-only-namespace SAPO keys.

    The full multimodal model keeps every language-model weight under
    ``model.model.language_model.*``; a text-only-namespace key that is NOT
    remapped is silently dropped by peft -> partial (or zero) merge.
    Keys that already contain ``language_model`` are left untouched, as are
    non-adapter keys (no SAPO-namespace prefix).
    """
    remapped: list[str] = []
    for key in keys:
        if "language_model" in key:
            remapped.append(key)
            continue
        # Three-segment prefix: base_model.model.model.<rest>
        if key.startswith("base_model.model.model."):
            rest = key[len("base_model.model.model.") :]
            remapped.append(f"base_model.model.model.language_model.{rest}")
        # Two-segment prefix: base_model.model.<rest>
        elif key.startswith("base_model.model."):
            rest = key[len("base_model.model.") :]
            remapped.append(f"base_model.model.language_model.{rest}")
        else:
            remapped.append(key)
    return remapped


def _missing_loaded_tensors(model: Any, state_dict: dict[str, Any]) -> list[str]:
    """Report state-dict keys that were silently dropped by peft.

    On-disk keys (no ``.default``) must match in-model names (with it).
    Returns a list of missing tensor names (without the ``base_model.`` prefix).
    """
    # Build a set of model param names, stripping the ``.default`` segment
    # that peft inserts (e.g. ``lora_B.default.weight`` -> ``lora_B.weight``)
    # so on-disk keys (without ``.default``) can match.
    model_param_names: set[str] = set()
    for name, _ in model.named_parameters():
        model_param_names.add(name.replace(".default", ""))

    missing: list[str] = []
    for key in state_dict:
        cmp_key = key.replace(".default", "")
        if cmp_key in model_param_names:
            continue
        # Not found -- report with ``base_model.`` prefix stripped
        report = key.replace(".default", "")
        if report.startswith("base_model."):
            report = report[len("base_model.") :]
        missing.append(report)
    return missing


def _state_inert(state_dict: dict[str, Any]) -> bool:
    """Check whether a LoRA state dict is effectively inert (identity).

    A LoRA delta is inert when every lora_B tensor is zero (the product
    lora_A @ lora_B is zero regardless of lora_A).  Non-LoRA tensors
    (modules_to_save) cannot be proven inert.  An empty checkpoint fails
    closed (returns False).
    """
    if not state_dict:
        return False

    has_lora_b = False
    for key, tensor in state_dict.items():
        if "lora_B" in key:
            has_lora_b = True
            if hasattr(tensor, "abs") and tensor.abs().max().item() > 0:
                return False
        elif "lora_A" not in key:
            # Non-LoRA tensor (e.g. modules_to_save) -- cannot prove inert
            return False
    return has_lora_b


def _adapter_effectively_zero(merged: Any, base: Any) -> bool:
    """Check whether the merged model is effectively identical to base.

    Parameters that are the SAME object (shared via submodule reference) are
    skipped.  For adapter-only parameters (not in base):
    - lora_B tensors must be zero (the delta lora_A @ lora_B is then zero
      regardless of lora_A).
    - Any non-lora_B adapter parameter (modules_to_save-style) must be zero
      (it represents a direct weight replacement, not a factored delta).
    """
    base_param_ids: set[int] = set()
    for _, param in base.named_parameters():
        base_param_ids.add(id(param))

    for name, param in merged.named_parameters():
        if id(param) in base_param_ids:
            continue
        # Adapter-only parameter
        is_zero = not hasattr(param, "abs") or param.abs().max().item() == 0
        if is_zero:
            continue
        # Nonzero: only lora_A is allowed (delta is lora_A @ lora_B, so
        # lora_A alone does not change the output when lora_B is zero).
        if "lora_A" in name:
            continue
        return False

    return True


def _probe_differs(base: Any, adapter: Any, probe: str, backend: Any) -> bool:
    """Check whether the adapter changes first-step logits vs base.

    Greedy tokens can stay identical for a weak-but-real delta; logits cannot.
    Compares the first-step scores (logits) from ``model.generate`` with
    ``return_dict_in_generate=True, output_scores=True``.
    """
    import torch

    def _first_scores(model: Any, text: str) -> Any:
        tokenizer = backend.text_backend
        inputs = tokenizer(text, return_tensors="pt")
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=1,
                return_dict_in_generate=True,
                output_scores=True,
            )
        if output.scores is not None and len(output.scores) > 0:
            return output.scores[0]
        return None

    base_scores = _first_scores(base, probe)
    adapter_scores = _first_scores(adapter, probe)

    if base_scores is None or adapter_scores is None:
        return False

    return bool(base_scores.ne(adapter_scores).any())


def verify_prompt_contract(run_dir: Path, manifest: dict[str, Any]) -> str:
    """Verify that all frozen prompt/scorer hashes in *manifest* still match.

    Delegates to ``evals.runner.frozen_contract.verify_frozen_eval_contract``.
    Returns the ``public_eval_contract_sha256`` on success, raises
    ``SystemExit`` on any mismatch.
    """
    from evals.runner.frozen_contract import verify_frozen_eval_contract

    result = verify_frozen_eval_contract(run_dir, manifest, root=ROOT, verify_runner=True)
    return str(result["public_eval_contract_sha256"])


def write_candidate_map(run_dir: Path, tasks: list[dict[str, Any]]) -> Path:
    candidate_map = {
        str(task["id"]): str(task["candidate_file"])
        for task in tasks
        if task.get("id") and task.get("candidate_file")
    }
    candidate_map_path = run_dir / "candidate-map.json"
    candidate_map_path.write_text(json.dumps(candidate_map, indent=2) + "\n", encoding="utf-8")
    return candidate_map_path


def load_text_backend(model_path: Path) -> TextPreprocessorBackend:
    ensure_text_backend_preflight(str(model_path), AutoConfig)
    return load_text_preprocessor_backend(
        str(model_path), AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast
    )


def load_model(model_path: Path, device: str):
    model = load_causal_lm_with_text_backend_preflight(
        str(model_path),
        auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM,
        model_kwargs={
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
            "torch_dtype": "auto",
        },
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
            return render_backend.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
    return "\n\n".join(f"{message['role'].upper()}: {message['content']}" for message in messages)


def build_inputs(backend: TextPreprocessorBackend, prompt_text: str, device: str):
    tokens = backend.text_backend(prompt_text, return_tensors="pt")
    return {key: value.to(device) for key, value in tokens.items()}


def _filter_kwargs(callable_obj: Any, raw_kwargs: dict[str, Any]) -> dict[str, Any]:
    try:
        signature = inspect.signature(callable_obj)
    except (TypeError, ValueError):
        return raw_kwargs
    accepts_var_kw = any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    if accepts_var_kw:
        return raw_kwargs
    allowed = {
        name
        for name, parameter in signature.parameters.items()
        if parameter.kind
        in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    }
    return {key: value for key, value in raw_kwargs.items() if key in allowed}


def resolve_turboquant_settings(args: argparse.Namespace, device: str) -> dict[str, Any] | None:
    if not args.turboquant_enable:
        return None
    return {
        "enabled": True,
        "backend": args.turboquant_backend,
        "nbits": args.turboquant_nbits,
        "group_size": args.turboquant_group_size,
        "q_group_size": args.turboquant_q_group_size,
        "residual_length": args.turboquant_residual_length,
        "axis_key": args.turboquant_axis_key,
        "axis_value": args.turboquant_axis_value,
        "device": device,
    }


def build_turboquant_cache(settings: dict[str, Any], model: Any) -> Any:
    try:
        import training.turboquant as turboquant_runtime
    except ImportError as exc:  # noqa: BLE001
        raise RuntimeError(
            "TurboQuant cache mode was requested, but training.turboquant is unavailable. "
            "Add the TurboQuant runtime module before using --turboquant-enable."
        ) from exc

    config_payload = {
        "backend": settings["backend"],
        "nbits": settings["nbits"],
        "group_size": settings["group_size"],
        "q_group_size": settings["q_group_size"],
        "residual_length": settings["residual_length"],
        "axis_key": settings["axis_key"],
        "axis_value": settings["axis_value"],
        "device": settings["device"],
    }
    model_dtype = getattr(model, "dtype", None)
    if model_dtype is not None:
        config_payload["compute_dtype"] = model_dtype

    if hasattr(turboquant_runtime, "TurboQuantConfig"):
        config_cls = turboquant_runtime.TurboQuantConfig
        config = config_cls(**_filter_kwargs(config_cls, config_payload))
    elif hasattr(turboquant_runtime, "build_turboquant_config"):
        builder = turboquant_runtime.build_turboquant_config
        config = builder(**_filter_kwargs(builder, config_payload))
    else:
        config = config_payload

    if hasattr(turboquant_runtime, "TurboQuantCache"):
        cache_cls = turboquant_runtime.TurboQuantCache
        cache_kwargs = _filter_kwargs(cache_cls, {"config": config, "cache_config": config})
        if cache_kwargs:
            return cache_cls(**cache_kwargs)
        return cache_cls(config)
    if hasattr(turboquant_runtime, "build_turboquant_cache"):
        builder = turboquant_runtime.build_turboquant_cache
        cache_kwargs = _filter_kwargs(builder, {"config": config, "cache_config": config})
        if cache_kwargs:
            return builder(**cache_kwargs)
        return builder(config)
    raise RuntimeError(
        "TurboQuant runtime module is present but does not expose TurboQuantCache "
        "or build_turboquant_cache."
    )


def generate_candidate(
    model: Any,
    backend: TextPreprocessorBackend,
    system_prompt: str,
    user_prompt: str,
    max_new_tokens: int,
    temperature: float,
    device: str,
    turboquant_settings: dict[str, Any] | None = None,
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
    if turboquant_settings is not None:
        generation_kwargs["past_key_values"] = build_turboquant_cache(turboquant_settings, model)
    generation_kwargs = {
        key: value for key, value in generation_kwargs.items() if value is not None
    }
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
    turboquant_settings = resolve_turboquant_settings(args, args.device)
    system_prompt = (run_dir / "SYSTEM_PROMPT.txt").read_text(encoding="utf-8")
    tasks = manifest.get("tasks", [])
    if args.limit > 0:
        tasks = tasks[: args.limit]
    write_candidate_map(run_dir, tasks)

    backend = load_text_backend(args.base_model)
    tokenizer = backend.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    print(
        json.dumps(
            {"stage": "load_base_start", "model": str(args.base_model), "device": args.device},
            ensure_ascii=False,
        ),
        flush=True,
    )
    base_model = load_model(args.base_model, args.device)
    active_model = base_model
    if args.adapter is not None:
        from peft import PeftModel

        print(
            json.dumps(
                {"stage": "load_adapter_start", "adapter": str(args.adapter)}, ensure_ascii=False
            ),
            flush=True,
        )
        active_model = PeftModel.from_pretrained(base_model, str(args.adapter))
        active_model.eval()
        print(json.dumps({"stage": "load_adapter_done"}, ensure_ascii=False), flush=True)

    generation_records: list[dict[str, Any]] = []
    started_at = time.time()
    for index, task in enumerate(tasks, start=1):
        prompt_path = run_dir / task["prompt_file"]
        candidate_path = run_dir / task["candidate_file"]
        user_prompt = prompt_path.read_text(encoding="utf-8")
        print(
            json.dumps(
                {"stage": "generate", "index": index, "total": len(tasks), "task_id": task["id"]},
                ensure_ascii=False,
            ),
            flush=True,
        )
        candidate_text = generate_candidate(
            active_model,
            backend,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            device=args.device,
            turboquant_settings=turboquant_settings,
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
        "turboquant": turboquant_settings,
        "tasks": generation_records,
    }
    generation_log_path = run_dir / "hf-pass1-generation-log.json"
    generation_log_path.write_text(json.dumps(generation_log, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"stage": "generation_done", "log_path": str(generation_log_path)}, ensure_ascii=False
        ),
        flush=True,
    )

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
