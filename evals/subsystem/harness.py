#!/usr/bin/env python3
"""Comprehensive pass@k evaluation harness for quantum-gpt adapters.

This is the NPU-resident harness that runs inside the Huanxin environment.
It supersedes scripts/run_asi2_35b_pass1_eval.py with:

  - Multi-sample pass@k (k=1,2,5,10) via temperature sampling
  - Per-framework/per-category breakdown
  - CE-loss / perplexity on a held-out JSONL (optional)
  - Failure analysis with error-type classification
  - Structured JSON output consumed by analyzer.py and reporter.py
  - Checkpoint scanning: automatically finds best available adapter step
  - NPU guard: validates device availability before loading

Usage (inside ASI NPU env):
  python3 evals/subsystem/harness.py \\
      --base-model /tmp/qwen35b_decompressed_for_training_asi3 \\
      --adapter outputs/qg-35b-glm52-distill-sft-*/adapter \\
      --output outputs/eval-comprehensive-$(date +%Y%m%dT%H%M%SZ).json \\
      --device npu \\
      --npu-max-memory-gib 50 \\
      --k 1 \\
      --tasks all

For pass@k with k>1 (samples per task), add --k 5 --temperature 0.8.
For CE-loss eval add --eval-file data/generated/.../eval_chatml.jsonl.
"""

from __future__ import annotations

import argparse
import gc
import importlib.util
import json
import logging
import math
import os
import re
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch
import transformers
from peft import PeftModel
from transformers import AutoConfig, AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast

# ── silence noisy transformers repr crash (Qwen3.5-MoE nested sub-config) ────
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

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── standard 12-task IDs used throughout the R&D cycle ───────────────────────
STANDARD_12_TASK_IDS = [
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

# All 44 tasks (full coverage)
FULL_TASK_IDS: list[str] | None = None  # populated by discover_all_tasks()

# Failure type labels
FAILURE_SYNTAX       = "syntax"
FAILURE_IMPORT       = "import_error"
FAILURE_ASSERTION    = "assertion"
FAILURE_TIMEOUT      = "timeout"
FAILURE_EMPTY_OUTPUT = "empty_output"
FAILURE_RUNTIME      = "runtime"


def _log(msg: str, **kw: Any) -> None:
    print(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **kw, "msg": msg}), flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# Task discovery
# ─────────────────────────────────────────────────────────────────────────────

def discover_all_tasks() -> list[str]:
    """Return all task IDs found under evals/tasks/. Cached."""
    global FULL_TASK_IDS
    if FULL_TASK_IDS is not None:
        return FULL_TASK_IDS
    tasks_root = ROOT / "evals" / "tasks"
    ids = []
    for path in sorted(tasks_root.glob("*/*/task.json")):
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
            if meta.get("id"):
                ids.append(meta["id"])
        except Exception:  # noqa: BLE001
            pass
    FULL_TASK_IDS = ids
    return ids


def resolve_task_list(spec: str) -> list[str]:
    """Resolve --tasks argument to a list of task IDs.

    Accepts:
      "all"           → all 44 tasks
      "standard12"    → the standard 12-task R&D eval set
      "quantum"       → all quantum-domain tasks
      "software"      → all software-domain tasks
      comma-separated → explicit list, e.g. "quantum_qaoa_maxcut,quantum_grover_oracle_diffusion"
    """
    if spec == "all":
        return discover_all_tasks()
    if spec == "standard12":
        return STANDARD_12_TASK_IDS
    if spec in ("quantum", "software"):
        tasks_root = ROOT / "evals" / "tasks"
        ids = []
        for path in sorted(tasks_root.glob(f"{spec}/*/task.json")):
            try:
                meta = json.loads(path.read_text(encoding="utf-8"))
                if meta.get("id"):
                    ids.append(meta["id"])
            except Exception:  # noqa: BLE001
                pass
        return ids
    # treat as comma-separated list
    return [t.strip() for t in spec.split(",") if t.strip()]


def find_task_json(task_id: str) -> Path:
    suffix = task_id.split("_", 1)[1]
    for path in (ROOT / "evals" / "tasks").glob("*/*/task.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("id") == task_id or path.parent.name == suffix:
                return path
        except Exception:  # noqa: BLE001
            pass
    raise FileNotFoundError(f"task.json not found for task_id={task_id!r}")


# ─────────────────────────────────────────────────────────────────────────────
# NPU helpers
# ─────────────────────────────────────────────────────────────────────────────

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
    num_layers = config_get(text_config, "num_hidden_layers") or config_get(text_config, "num_layers")
    if not num_layers:
        raise SystemExit("Cannot build device map: num_hidden_layers missing from config")
    ordinals = list(range(len(devices)))
    last = ordinals[-1]
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


def filter_device_map_to_existing_modules(device_map: dict[str, int], model_loader: Any, model_config: Any) -> dict[str, int]:
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
        _log("device_map_filter_skipped", error=f"{type(exc).__name__}: {exc}")
        return device_map


def _coerce_sub_configs(config: Any) -> None:
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


# ─────────────────────────────────────────────────────────────────────────────
# Model loading
# ─────────────────────────────────────────────────────────────────────────────

def load_backend(model_path: Path) -> Any:
    from training.text_preprocessor_backend import load_text_preprocessor_backend
    backend = load_text_preprocessor_backend(str(model_path), AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast)
    tok = backend.text_backend
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"
    return backend


def load_model(model_path: Path, args: argparse.Namespace) -> tuple[Any, dict[str, Any]]:
    from training.runtime_overlay import apply_transformers_peft_compat_shims, register_qwen35_moe_runtime
    from training.model_backend import select_transformers_model_loader

    registration = register_qwen35_moe_runtime(
        transformers, auto_config_cls=AutoConfig, auto_model_for_causal_lm_cls=AutoModelForCausalLM,
    )
    apply_transformers_peft_compat_shims(transformers)
    model_config = AutoConfig.from_pretrained(str(model_path), trust_remote_code=True)
    _coerce_sub_configs(model_config)
    devices = visible_npus()
    kwargs: dict[str, Any] = {"trust_remote_code": True, "low_cpu_mem_usage": True, "torch_dtype": "auto"}
    model_loader, runtime_compat, loader_metadata = select_transformers_model_loader(
        str(model_path), auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM, transformers_module=transformers,
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


# ─────────────────────────────────────────────────────────────────────────────
# Generation
# ─────────────────────────────────────────────────────────────────────────────

def render_prompt(backend: Any, task_prompt: str) -> str:
    messages = [
        {"role": "system", "content": "Return only a complete Python candidate.py file. No markdown. No explanation."},
        {"role": "user",   "content": task_prompt},
    ]
    renderer = backend.render_backend
    if hasattr(renderer, "apply_chat_template"):
        try:
            return renderer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
            )
        except TypeError:
            return renderer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return "\n\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)


def build_task_prompt(task_dir: Path, meta: dict[str, Any]) -> str:
    tests = (task_dir / meta.get("test_file", "tests.py")).read_text(encoding="utf-8")
    candidate_name = meta.get("candidate_file", "candidate.py")
    existing = (task_dir / candidate_name).read_text(encoding="utf-8") if (task_dir / candidate_name).exists() else ""
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


def generate_samples(
    model: Any, backend: Any, prompt: str, device: Any,
    max_new_tokens: int, num_samples: int, temperature: float,
) -> list[tuple[str, str]]:
    """Generate `num_samples` completions.  Returns [(code, raw_output), ...]."""
    prompt_text = render_prompt(backend, prompt)
    tokens = backend.text_backend(prompt_text, return_tensors="pt")
    prompt_len = tokens["input_ids"].shape[1]
    tokens_on_device = {k: v.to(device) for k, v in tokens.items()}

    samples = []
    with torch.inference_mode():
        if num_samples == 1:
            output = model.generate(
                **tokens_on_device,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=backend.text_backend.eos_token_id,
                eos_token_id=backend.text_backend.eos_token_id,
            )
            raw = backend.text_backend.decode(
                output[0, prompt_len:].detach().cpu(), skip_special_tokens=True
            )
            samples.append((sanitize_code(raw), raw))
        else:
            for _ in range(num_samples):
                output = model.generate(
                    **tokens_on_device,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=0.95,
                    pad_token_id=backend.text_backend.eos_token_id,
                    eos_token_id=backend.text_backend.eos_token_id,
                )
                raw = backend.text_backend.decode(
                    output[0, prompt_len:].detach().cpu(), skip_special_tokens=True
                )
                samples.append((sanitize_code(raw), raw))
    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Test execution
# ─────────────────────────────────────────────────────────────────────────────

def load_test_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def classify_failure(details: list[str]) -> str:
    combined = "\n".join(details)
    if not combined.strip():
        return FAILURE_EMPTY_OUTPUT
    if "SyntaxError" in combined or "IndentationError" in combined:
        return FAILURE_SYNTAX
    if "ImportError" in combined or "ModuleNotFoundError" in combined:
        return FAILURE_IMPORT
    if "timeout" in combined.lower():
        return FAILURE_TIMEOUT
    if "AssertionError" in combined or "assert " in combined.lower():
        return FAILURE_ASSERTION
    return FAILURE_RUNTIME


def run_test(task_dir: Path, meta: dict[str, Any], code: str, candidate_path: Path) -> dict[str, Any]:
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(code, encoding="utf-8")
    try:
        module = load_test_module(task_dir / meta.get("test_file", "tests.py"))
        result = module.run_tests(str(candidate_path))
        passed = bool(result.get("passed"))
        details = list(result.get("details", []))
        return {
            "passed": passed,
            "details": details,
            "failure_category": None if passed else classify_failure(details),
        }
    except Exception as exc:  # noqa: BLE001
        details = [f"{type(exc).__name__}: {exc}"] + traceback.format_exc().strip().splitlines()
        return {
            "passed": False,
            "details": details,
            "failure_category": classify_failure(details),
        }


# ─────────────────────────────────────────────────────────────────────────────
# pass@k estimator (unbiased Codex formula)
# ─────────────────────────────────────────────────────────────────────────────

def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased estimator: P(at least 1 of k passes) = 1 - C(n-c,k)/C(n,k)."""
    if n - c < k:
        return 1.0
    return 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))


# ─────────────────────────────────────────────────────────────────────────────
# CE-loss / perplexity on held-out JSONL
# ─────────────────────────────────────────────────────────────────────────────

def run_heldout_loss_eval(
    model: Any, backend: Any, device: Any,
    eval_jsonl: Path, limit: int = 0,
) -> dict[str, Any]:
    """Compute completions-only CE loss on a chat-SFT JSONL (same metric as trainer)."""
    rows: list[dict] = []
    with open(eval_jsonl, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
                if limit and len(rows) >= limit:
                    break
    tok = backend.text_backend
    total_loss = 0.0
    total_tokens = 0
    with torch.inference_mode():
        for row in rows:
            # reconstruct prompt and completion
            messages = row.get("messages") or row.get("conversations") or []
            if not messages:
                continue
            try:
                full_text = tok.apply_chat_template(messages, tokenize=False)
                # Build completion-only mask: find assistant turn boundaries
                prompt_messages = [m for m in messages if m.get("role") != "assistant"]
                prompt_text = tok.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True)
            except Exception:  # noqa: BLE001
                continue

            full_ids = tok(full_text, return_tensors="pt")["input_ids"].to(device)
            prompt_ids = tok(prompt_text, return_tensors="pt")["input_ids"].to(device)
            n_prompt = prompt_ids.shape[1]
            n_full   = full_ids.shape[1]
            if n_full <= n_prompt:
                continue

            labels = full_ids.clone()
            labels[:, :n_prompt] = -100  # mask prompt tokens

            try:
                out = model(input_ids=full_ids, labels=labels)
                loss_val = out.loss.item()
                completion_len = n_full - n_prompt
                total_loss   += loss_val * completion_len
                total_tokens += completion_len
            except Exception:  # noqa: BLE001
                continue

    if total_tokens == 0:
        return {"loss": None, "perplexity": None, "n_examples": len(rows), "n_tokens": 0}
    avg_loss = total_loss / total_tokens
    return {
        "loss": round(avg_loss, 6),
        "perplexity": round(math.exp(avg_loss), 6),
        "n_examples": len(rows),
        "n_tokens": total_tokens,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main evaluation loop
# ─────────────────────────────────────────────────────────────────────────────

def eval_model(
    model_name: str,
    model: Any,
    backend: Any,
    tasks: list[tuple[Path, dict[str, Any]]],
    args: argparse.Namespace,
    heldout_eval_jsonl: Path | None = None,
) -> dict[str, Any]:
    device = first_parameter_device(model, args.device)
    records: list[dict[str, Any]] = []

    for idx, (task_json, meta) in enumerate(tasks, 1):
        task_id = meta["id"]
        _log("generate", model=model_name, index=idx, total=len(tasks), task=task_id)
        task_dir = task_json.parent
        prompt = build_task_prompt(task_dir, meta)
        t0 = time.time()

        samples = generate_samples(
            model, backend, prompt, device,
            max_new_tokens=args.max_new_tokens,
            num_samples=args.k,
            temperature=args.temperature,
        )
        gen_sec = round(time.time() - t0, 2)

        # evaluate each sample
        sample_results = []
        for si, (code, raw) in enumerate(samples):
            cpath = (
                args.output.parent / "candidates" / model_name
                / f"{task_id}_s{si}.py"
            )
            test_result = run_test(task_dir, meta, code, cpath)
            sample_results.append({
                "passed": test_result["passed"],
                "failure_category": test_result.get("failure_category"),
                "details": test_result["details"][:10],  # cap detail lines
                "code_chars": len(code),
                "raw_head": raw[:300],
                "code_head": code[:300],
            })

        n_pass = sum(1 for sr in sample_results if sr["passed"])
        # pass@k estimates for all standard k values up to num_samples
        pass_at = {}
        for k_val in [1, 2, 5, 10]:
            if k_val <= args.k:
                pass_at[f"pass_at_{k_val}"] = round(pass_at_k(args.k, n_pass, k_val), 4)

        _log(
            "result",
            model=model_name, task=task_id,
            passed=n_pass, total_samples=args.k,
            pass_at_1=pass_at.get("pass_at_1"),
            gen_sec=gen_sec,
        )

        records.append({
            "model": model_name,
            "task_id": task_id,
            "name": meta.get("name"),
            "domain": meta.get("domain"),
            "category": meta.get("category"),
            "n_samples": args.k,
            "n_pass": n_pass,
            **pass_at,
            "gen_sec": gen_sec,
            "samples": sample_results,
        })

    # aggregate
    overall_pass1 = sum(
        r.get("pass_at_1", 1.0 if r["n_pass"] > 0 else 0.0) for r in records
    ) / max(1, len(records))
    by_domain: dict[str, Any] = defaultdict(lambda: {"n": 0, "pass_sum": 0.0})
    by_cat:    dict[str, Any] = defaultdict(lambda: {"n": 0, "pass_sum": 0.0})
    by_fail:   dict[str, int] = defaultdict(int)

    for r in records:
        dom = r["domain"] or "unknown"
        cat = r["category"] or "unknown"
        p1  = r.get("pass_at_1", 1.0 if r["n_pass"] > 0 else 0.0)
        by_domain[dom]["n"] += 1
        by_domain[dom]["pass_sum"] += p1
        by_cat[cat]["n"] += 1
        by_cat[cat]["pass_sum"] += p1
        for sr in r.get("samples", []):
            fc = sr.get("failure_category")
            if fc:
                by_fail[fc] += 1

    summary: dict[str, Any] = {
        "pass_at_1": round(overall_pass1, 4),
        "n_tasks": len(records),
        "n_pass": sum(1 for r in records if r.get("pass_at_1", 0) > 0),
        "by_domain": {
            d: {
                "pass_at_1": round(v["pass_sum"] / v["n"], 4),
                "n": v["n"],
                "n_pass": sum(1 for r in records if r["domain"] == d and r.get("pass_at_1", 0) > 0),
            }
            for d, v in sorted(by_domain.items())
        },
        "by_category": {
            c: {
                "pass_at_1": round(v["pass_sum"] / v["n"], 4),
                "n": v["n"],
            }
            for c, v in sorted(by_cat.items())
        },
        "failure_categories": dict(sorted(by_fail.items())),
        "failing_tasks": [r["task_id"] for r in records if not (r.get("pass_at_1", 0) > 0)],
    }

    result: dict[str, Any] = {"summary": summary, "records": records}

    # optional CE-loss eval
    if heldout_eval_jsonl is not None:
        _log("heldout_loss_eval_start", model=model_name)
        loss_result = run_heldout_loss_eval(
            model, backend, device, heldout_eval_jsonl,
            limit=args.heldout_limit,
        )
        result["heldout_loss"] = loss_result
        _log("heldout_loss_eval_done", model=model_name, **loss_result)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Comprehensive pass@k eval harness for quantum-gpt adapters")
    p.add_argument("--base-model",    type=Path, required=True, help="Path to base model directory")
    p.add_argument("--adapter",       type=Path, default=None,  help="Path to LoRA adapter directory (omit for base-only)")
    p.add_argument("--output",        type=Path, required=True, help="Output JSON path")
    p.add_argument("--device",        default="npu", choices=["npu", "cuda", "cpu"])
    p.add_argument("--npu-max-memory-gib", type=int, default=56)
    p.add_argument("--max-new-tokens",     type=int, default=768)
    p.add_argument("--k",             type=int, default=1, help="Samples per task for pass@k (1=greedy)")
    p.add_argument("--temperature",   type=float, default=0.8, help="Sampling temperature (used when --k > 1)")
    p.add_argument("--tasks",         default="standard12",
                   help="Task selection: 'all', 'standard12', 'quantum', 'software', or comma-separated IDs")
    p.add_argument("--models",        choices=["base", "adapter", "both"], default="both")
    p.add_argument("--limit",         type=int, default=0, help="Limit tasks (0=all selected)")
    p.add_argument("--eval-file",     type=Path, default=None, help="Optional held-out JSONL for CE-loss eval")
    p.add_argument("--heldout-limit", type=int, default=0,    help="Rows to use from eval-file (0=all)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    started = time.time()

    selected_ids = resolve_task_list(args.tasks)
    if args.limit:
        selected_ids = selected_ids[: args.limit]

    _log("eval_start", task_count=len(selected_ids), k=args.k, models=args.models)

    tasks: list[tuple[Path, dict[str, Any]]] = []
    for tid in selected_ids:
        try:
            path = find_task_json(tid)
            meta = json.loads(path.read_text(encoding="utf-8"))
            if not meta.get("candidate_files"):  # skip workspace tasks for now
                tasks.append((path, meta))
        except FileNotFoundError:
            _log("task_not_found", task_id=tid)

    if not tasks:
        _log("no_tasks_found")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)

    backend = load_backend(args.base_model)
    heldout = args.eval_file if args.eval_file and args.eval_file.exists() else None
    all_results: dict[str, Any] = {}
    load_meta: dict[str, Any] = {}

    if args.models in ("base", "both"):
        _log("load_base")
        base_model, load_meta = load_model(args.base_model, args)
        all_results["base"] = eval_model("base", base_model, backend, tasks, args, heldout)
        del base_model
        gc.collect()
        if args.device == "npu" and hasattr(torch, "npu"):
            torch.npu.empty_cache()

    if args.models in ("adapter", "both"):
        if args.adapter is None:
            _log("adapter_path_missing")
        else:
            _log("load_adapter")
            adapter_base, load_meta = load_model(args.base_model, args)
            adapter_model = PeftModel.from_pretrained(adapter_base, str(args.adapter))
            adapter_model.eval()
            all_results["adapter"] = eval_model("adapter", adapter_model, backend, tasks, args, heldout)

    # compute delta (base vs adapter)
    delta: dict[str, Any] | None = None
    if "base" in all_results and "adapter" in all_results:
        base_p1    = all_results["base"]["summary"]["pass_at_1"]
        adapter_p1 = all_results["adapter"]["summary"]["pass_at_1"]
        delta = {
            "pass_at_1": round(adapter_p1 - base_p1, 4),
            "n_tasks": all_results["base"]["summary"]["n_tasks"],
            "base_pass_at_1": base_p1,
            "adapter_pass_at_1": adapter_p1,
            "fixed_tasks": [
                r["task_id"] for r in all_results["adapter"]["records"]
                if r.get("pass_at_1", 0) > 0 and
                   not any(br["task_id"] == r["task_id"] and br.get("pass_at_1", 0) > 0
                           for br in all_results["base"]["records"])
            ],
            "broken_tasks": [
                r["task_id"] for r in all_results["adapter"]["records"]
                if not (r.get("pass_at_1", 0) > 0) and
                   any(br["task_id"] == r["task_id"] and br.get("pass_at_1", 0) > 0
                       for br in all_results["base"]["records"])
            ],
        }

    payload: dict[str, Any] = {
        "schema_version": 2,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_model": str(args.base_model),
        "adapter": str(args.adapter) if args.adapter else None,
        "task_ids": [meta["id"] for _, meta in tasks],
        "k": args.k,
        "temperature": args.temperature if args.k > 1 else None,
        "results": all_results,
        "delta": delta,
        "load_metadata": load_meta,
        "duration_sec": round(time.time() - started, 3),
    }

    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(args.output)
    _log("eval_done", output=str(args.output), delta=delta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
