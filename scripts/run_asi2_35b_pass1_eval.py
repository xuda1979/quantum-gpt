#!/usr/bin/env python3
"""Pass@1-only evaluator for the ASI2 Qwen3.6 35B W8A8 LoRA run.

This script is intentionally narrower than the rubric evaluator: it only
generates one candidate per task, executes the task tests, and writes the
generated code plus failure details.  The previous rubric report omitted code
and therefore made a bad generation path look like a model-quality result.
"""

from __future__ import annotations

import argparse
import gc
import importlib.util
import json
import logging
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch
import transformers
from peft import PeftModel
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer,
    PreTrainedTokenizerFast,
)

# This transformers build logs ``Model config {config}`` at INFO during
# AutoConfig.from_pretrained, which triggers PretrainedConfig.__repr__ ->
# to_diff_dict -> recursive_diff_dict. With the qwen3_5_moe overlay's nested
# sub-config stored as a plain dict, recursive_diff_dict raises
# "'dict' object has no attribute 'to_dict'", crashing the whole load. That repr
# fires *before* _coerce_sub_configs runs, so coercion alone cannot prevent it.
# We never need that repr, so (1) silence the config logger and (2) replace the
# fragile __repr__ with a safe one that does not walk nested diff dicts.
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("transformers.configuration_utils").setLevel(logging.ERROR)
transformers.logging.set_verbosity_error()
try:
    from transformers.configuration_utils import PretrainedConfig as _PretrainedConfig

    def _safe_config_repr(self):  # noqa: ANN001
        return f"{self.__class__.__name__}(model_type={getattr(self, 'model_type', '?')})"

    _PretrainedConfig.__repr__ = _safe_config_repr
except Exception:  # noqa: BLE001
    pass

# Same root cause (overlay keeps a nested text_config as a plain dict) breaks
# GenerationConfig.from_model_config during model __init__:
# ``decoder_config.to_dict()`` on a dict. We only need a usable generation
# config for eval (no sampling), so fall back to a default GenerationConfig
# whenever the model-config-derived construction raises.
try:
    from transformers.generation.configuration_utils import GenerationConfig as _GenerationConfig

    _orig_from_model_config = _GenerationConfig.from_model_config.__func__

    def _safe_from_model_config(cls, model_config):  # noqa: ANN001
        try:
            return _orig_from_model_config(cls, model_config)
        except Exception:  # noqa: BLE001
            gc_obj = cls()
            for attr in ("bos_token_id", "eos_token_id", "pad_token_id"):
                val = getattr(model_config, attr, None)
                if val is not None:
                    setattr(gc_obj, attr, val)
            gc_obj._from_model_config = True
            return gc_obj

    _GenerationConfig.from_model_config = classmethod(_safe_from_model_config)
except Exception:  # noqa: BLE001
    pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.model_backend import select_transformers_model_loader
from training.runtime_overlay import (
    apply_transformers_peft_compat_shims,
    register_qwen35_moe_runtime,
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
    parser.add_argument("--npu-max-memory-gib", type=int, default=56)
    parser.add_argument("--max-new-tokens", type=int, default=768)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--models", choices=["base", "adapter", "both"], default="both")
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


def visible_npus() -> list[int]:
    raw = os.environ.get("ASCEND_RT_VISIBLE_DEVICES") or os.environ.get("ASCEND_VISIBLE_DEVICES")
    if not raw:
        return list(range(8))
    out: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            out.append(int(item) if item.isdigit() else len(out))
    return out or [0]


def config_get(config: Any, key: str) -> Any:
    if hasattr(config, key):
        return getattr(config, key)
    if isinstance(config, dict):
        return config.get(key)
    return None


def build_balanced_npu_layer_device_map(config: Any, devices: list[int]) -> dict[str, int]:
    text_config = config_get(config, "text_config") or config_get(config, "llm_config") or config
    num_layers = config_get(text_config, "num_hidden_layers") or config_get(
        text_config, "num_layers"
    )
    if not num_layers:
        raise SystemExit("Cannot build device map: num_hidden_layers missing from config")
    ordinals = list(range(len(devices)))
    last = ordinals[-1]
    # Build a *superset* map covering both the plain CausalLM module layout
    # (model.layers.*) and the multimodal ConditionalGeneration layout
    # (model.language_model.layers.*), plus the vision/audio towers that
    # multimodal checkpoints (Qwen3.5-MoE W8A8) ship. The caller filters this
    # superset down to keys that actually exist via meta-model introspection,
    # so strict accelerate builds (which reject keys matching no submodule) load
    # cleanly while every real parameter still receives a device.
    device_map: dict[str, int] = {
        "model.embed_tokens": ordinals[0],
        "model.norm": last,
        "model.rotary_emb": ordinals[0],
        "model.language_model.embed_tokens": ordinals[0],
        "model.language_model.norm": last,
        "model.language_model.rotary_emb": ordinals[0],
        "lm_head": last,
        "model.visual": ordinals[0],
        "visual": ordinals[0],
        "model.vision_tower": ordinals[0],
        "model.audio_tower": ordinals[0],
        "model.multi_modal_projector": ordinals[0],
    }
    for layer_idx in range(int(num_layers)):
        target = ordinals[layer_idx * len(ordinals) // int(num_layers)]
        device_map[f"model.layers.{layer_idx}"] = target
        device_map[f"model.language_model.layers.{layer_idx}"] = target
    return device_map


def filter_device_map_to_existing_modules(
    device_map: dict[str, int], model_loader: Any, model_config: Any
) -> dict[str, int]:
    """Prune device_map keys that match no submodule of the model.

    Strict accelerate builds raise "device_map keys do not match any submodules"
    for keys like ``model.layers.N`` on a multimodal checkpoint whose text tree
    lives under ``model.language_model.layers.N``. We instantiate the model on
    the meta device (no weights, ~free) to learn the real module names and keep
    only the matching keys. Falls back to the unfiltered map on any error.
    """
    try:
        from accelerate import init_empty_weights

        with init_empty_weights():
            meta_model = model_loader.from_config(model_config, trust_remote_code=True)
        valid_names = {name for name, _ in meta_model.named_modules()}
        del meta_model
        gc.collect()
        filtered = {key: dev for key, dev in device_map.items() if key in valid_names}
        return filtered or device_map
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {"stage": "device_map_filter_skipped", "error": f"{type(exc).__name__}: {exc}"}
            ),
            flush=True,
        )
        return device_map


def load_backend(model_path: Path):
    backend = load_text_preprocessor_backend(
        str(model_path), AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast
    )
    tokenizer = backend.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    return backend


def _coerce_sub_configs(config: Any) -> None:
    """Coerce nested sub-configs (text_config / vision_config) from plain dicts
    into their proper config classes.

    This transformers build can return a Qwen3_5MoeConfig whose ``text_config``
    and ``vision_config`` remain plain dicts (the from_dict path bypasses the
    __init__ coercion). Downstream model construction then crashes on
    ``vision_config.dtype`` / ``decoder_config.to_dict()``. We rebuild each
    sub-config via the parent's ``sub_configs`` mapping so every sub-config is a
    real config object before model instantiation.
    """
    sub_configs = getattr(type(config), "sub_configs", None) or getattr(config, "sub_configs", None)
    if not isinstance(sub_configs, dict):
        return
    for attr_name, sub_cls in sub_configs.items():
        value = getattr(config, attr_name, None)
        if isinstance(value, dict):
            try:
                setattr(config, attr_name, sub_cls(**value))
            except Exception:  # noqa: BLE001
                try:
                    setattr(config, attr_name, sub_cls.from_dict(value))
                except Exception:  # noqa: BLE001
                    pass
        elif value is None:
            try:
                setattr(config, attr_name, sub_cls())
            except Exception:  # noqa: BLE001
                pass
        else:
            _coerce_sub_configs(value)


def load_35b_model(model_path: Path, args: argparse.Namespace):
    registration = register_qwen35_moe_runtime(
        transformers,
        auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM,
    )
    # Apply compat shims BEFORE model loading to prevent OOM from caching_allocator_warmup
    apply_transformers_peft_compat_shims(transformers)
    model_config = AutoConfig.from_pretrained(str(model_path), trust_remote_code=True)
    _coerce_sub_configs(model_config)
    devices = visible_npus()
    kwargs: dict[str, Any] = {
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "torch_dtype": "auto",
    }
    model_loader, runtime_compat, loader_metadata = select_transformers_model_loader(
        str(model_path),
        auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM,
        transformers_module=transformers,
    )
    if args.device == "npu":
        device_map = build_balanced_npu_layer_device_map(model_config, devices)
        device_map = filter_device_map_to_existing_modules(device_map, model_loader, model_config)
        kwargs["device_map"] = device_map
        kwargs["max_memory"] = {idx: f"{args.npu_max_memory_gib}GiB" for idx in range(len(devices))}
    model = model_loader.from_pretrained(str(model_path), **kwargs)
    if getattr(model, "generation_config", None) is not None:
        model.generation_config.do_sample = False
        model.generation_config.temperature = None
        model.generation_config.top_p = None
        model.generation_config.top_k = None
    model.eval()
    return model, {
        "runtime_registration": registration,
        "runtime_compat": runtime_compat,
        "model_loader": loader_metadata,
        "visible_npus": devices,
        "device_map": kwargs.get("device_map"),
    }


def first_parameter_device(model: Any, fallback: str) -> Any:
    try:
        return next(model.parameters()).device
    except StopIteration:
        return fallback


def render_prompt(backend: Any, prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "Return only a complete Python candidate.py file. No markdown. No explanation.",
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
        "Implement candidate.py so the tests pass. Return only Python source.\n\n"
        "Tests:\n```python\n"
        f"{tests[:9000]}\n"
        "```\n\nExisting/reference API shape:\n```python\n"
        f"{existing[:3000]}\n"
        "```\n"
    )


def sanitize_code(text: str) -> str:
    value = text.strip()
    fenced = re.search(r"```(?:python)?\s*(.*?)```", value, re.S | re.I)
    if fenced:
        value = fenced.group(1).strip()
    for marker in ("Here is", "Explanation:", "The code"):
        if value.startswith(marker):
            value = "\n".join(value.splitlines()[1:]).strip()
    return value + "\n"


def generate_code(
    model: Any, backend: Any, prompt: str, device: Any, max_new_tokens: int
) -> tuple[str, str]:
    prompt_text = render_prompt(backend, prompt)
    tokens = backend.text_backend(prompt_text, return_tensors="pt")
    prompt_len = tokens["input_ids"].shape[1]
    tokens = {k: v.to(device) for k, v in tokens.items()}
    with torch.inference_mode():
        output = model.generate(
            **tokens,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=backend.text_backend.eos_token_id,
            eos_token_id=backend.text_backend.eos_token_id,
        )
    raw = backend.text_backend.decode(
        output[0, prompt_len:].detach().cpu(), skip_special_tokens=True
    )
    return sanitize_code(raw), raw


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


def run_model(
    model_name: str,
    model: Any,
    backend: Any,
    tasks: list[tuple[Path, dict[str, Any]]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    records = []
    device = first_parameter_device(model, args.device)
    for index, (task_json, meta) in enumerate(tasks, 1):
        print(
            json.dumps(
                {"stage": "generate", "model": model_name, "index": index, "task": meta["id"]}
            ),
            flush=True,
        )
        task_dir = task_json.parent
        code, raw = generate_code(
            model, backend, build_prompt(task_dir, meta), device, args.max_new_tokens
        )
        candidate_path = args.output.parent / "pass1_candidates" / model_name / f"{meta['id']}.py"
        result = run_single_file_test(task_dir, meta, code, candidate_path)
        records.append(
            {
                "model": model_name,
                "task_id": meta["id"],
                "name": meta["name"],
                "domain": meta["domain"],
                "category": meta["category"],
                "candidate_path": str(candidate_path),
                "passed": result["passed"],
                "details": result["details"],
                "output_chars": len(code),
                "raw_output_head": raw[:500],
                "code_head": code[:500],
            }
        )
    return records


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_model[record["model"]].append(record)
    for model_name, items in by_model.items():
        passed = sum(1 for item in items if item["passed"])
        out[model_name] = {
            "pass_at_1": f"{passed}/{len(items)}",
            "pass_rate": passed / max(1, len(items)),
            "by_domain": {},
        }
        domains: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in items:
            domains[item["domain"]].append(item)
        for domain, subset in domains.items():
            domain_passed = sum(1 for item in subset if item["passed"])
            out[model_name]["by_domain"][domain] = {
                "pass_at_1": f"{domain_passed}/{len(subset)}",
                "pass_rate": domain_passed / max(1, len(subset)),
            }
    return out


def main() -> int:
    args = parse_args()
    started = time.time()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    selected = TASK_IDS[: args.limit] if args.limit else TASK_IDS
    tasks = [(find_task(task_id), load_json(find_task(task_id))) for task_id in selected]
    tasks = [(path, meta) for path, meta in tasks if not meta.get("candidate_files")]

    backend = load_backend(args.base_model)
    records: list[dict[str, Any]] = []
    load_metadata: dict[str, Any] = {}

    if args.models in ("base", "both"):
        print(json.dumps({"stage": "load_base"}), flush=True)
        base, load_metadata = load_35b_model(args.base_model, args)
        records.extend(run_model("base", base, backend, tasks, args))
        del base
        gc.collect()
        if args.device == "npu" and hasattr(torch, "npu"):
            torch.npu.empty_cache()

    if args.models in ("adapter", "both"):
        print(json.dumps({"stage": "load_adapter"}), flush=True)
        adapter_base, load_metadata = load_35b_model(args.base_model, args)
        adapter = PeftModel.from_pretrained(adapter_base, str(args.adapter))
        adapter.eval()
        records.extend(run_model("adapter", adapter, backend, tasks, args))

    payload = {
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_model": str(args.base_model),
        "adapter": str(args.adapter),
        "task_ids": [meta["id"] for _, meta in tasks],
        "summary": summarize(records),
        "records": records,
        "load_metadata": load_metadata,
        "duration_sec": round(time.time() - started, 3),
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
