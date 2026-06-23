#!/usr/bin/env python3
"""Minimal PEFT SFT runner for chat-style JSONL corpora."""

from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import math
import os
import re
import time
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.runtime_overlay import (
    apply_transformers_peft_compat_shims,
    configure_runtime_overlay_from_env,
    register_qwen35_moe_runtime,
)

configure_runtime_overlay_from_env()

if TYPE_CHECKING:
    from transformers import AutoProcessor, AutoTokenizer
    import torch

try:
    from torch.distributed.elastic.multiprocessing.errors import record as elastic_record
except Exception:  # noqa: BLE001
    def elastic_record(function: Any) -> Any:
        return function

from training.research_plugins import load_research_methods, summarize_methods
from training.model_backend import (
    probe_model_runtime_compat,
    run_text_forward_preflight,
    select_transformers_model_loader,
)
from training.text_preprocessor_backend import (
    TextPreprocessorBackend,
    build_supervised_text_example,
    load_text_preprocessor_backend,
    pad_supervised_text_batch,
)

DEFAULT_LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
COMMON_LORA_TARGET_MODULE_GROUPS = [
    DEFAULT_LORA_TARGET_MODULES,
    ["query_proj", "key_proj", "value_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    ["q_proj", "k_proj", "v_proj", "o_proj"],
]
# Standard projection suffix set used for full-path Gemma 4 / MoE-family discovery.
_PROJECTION_SUFFIXES = frozenset(
    ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj",
     "query_proj", "key_proj", "value_proj"]
)

def build_native_lora_linear(torch_module: Any, base_layer: Any, rank: int, alpha: int, dropout: float) -> Any:
    class _NativeLoraLinear(torch_module.nn.Module):
        def __init__(self, wrapped: Any) -> None:
            super().__init__()
            self.wrapped = wrapped
            for parameter in self.wrapped.parameters():
                parameter.requires_grad = False
            in_features = int(wrapped.in_features)
            out_features = int(wrapped.out_features)
            self.rank = int(rank)
            self.lora_alpha = int(alpha)
            self.scaling = float(alpha) / float(rank)
            self.lora_dropout = torch_module.nn.Dropout(float(dropout)) if dropout > 0 else torch_module.nn.Identity()
            self.lora_A = torch_module.nn.Linear(in_features, rank, bias=False)
            self.lora_B = torch_module.nn.Linear(rank, out_features, bias=False)
            torch_module.nn.init.kaiming_uniform_(self.lora_A.weight, a=math.sqrt(5))
            torch_module.nn.init.zeros_(self.lora_B.weight)
            device = wrapped.weight.device
            dtype = wrapped.weight.dtype if getattr(wrapped.weight, "is_floating_point", lambda: False)() else torch_module.float32
            self.lora_A.to(device=device, dtype=dtype)
            self.lora_B.to(device=device, dtype=dtype)

        def forward(self, x: Any) -> Any:
            result = self.wrapped(x)
            lora_input = x.to(dtype=self.lora_A.weight.dtype)
            update = self.lora_B(self.lora_A(self.lora_dropout(lora_input))) * self.scaling
            return result + update.to(dtype=result.dtype)

    return _NativeLoraLinear(base_layer)


def _get_parent_module(model: Any, module_name: str) -> tuple[Any, str]:
    parts = module_name.split(".")
    parent = model
    for part in parts[:-1]:
        parent = getattr(parent, part)
    return parent, parts[-1]


def apply_native_lora(
    model: Any,
    torch_module: Any,
    target_modules: list[str],
    rank: int,
    alpha: int,
    dropout: float,
) -> dict[str, Any]:
    suffixes = tuple(target_modules)
    wrapped_names: list[str] = []
    for name, module in list(model.named_modules()):
        if not name or not any(name == suffix or name.endswith("." + suffix) for suffix in suffixes):
            continue
        if not all(hasattr(module, attr) for attr in ("in_features", "out_features", "weight")):
            continue
        parent, child_name = _get_parent_module(model, name)
        setattr(parent, child_name, build_native_lora_linear(torch_module, module, rank, alpha, dropout))
        wrapped_names.append(name)
    if not wrapped_names:
        raise SystemExit(
            "Native LoRA did not wrap any torch.nn.Linear modules. "
            f"Requested target modules: {target_modules}"
        )
    for name, parameter in model.named_parameters():
        parameter.requires_grad = ".lora_A." in name or ".lora_B." in name
    return {
        "backend": "native",
        "wrapped_module_count": len(wrapped_names),
        "wrapped_module_sample": wrapped_names[:20],
    }


def save_native_lora_adapter(model: Any, adapter_dir: Path, torch_module: Any, config: dict[str, Any]) -> None:
    adapter_dir.mkdir(parents=True, exist_ok=True)
    state = {
        name: parameter.detach().cpu()
        for name, parameter in model.named_parameters()
        if ".lora_A." in name or ".lora_B." in name
    }
    torch_module.save(state, adapter_dir / "adapter_model.bin")
    (adapter_dir / "adapter_config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def persist_adapter(
    *,
    save_model: Any,
    adapter_dir: Path,
    torch_module: Any,
    lora_backend: str,
    adapter_init: Any,
    native_config: dict[str, Any],
    text_preprocessor: Any,
) -> None:
    """Save a LoRA adapter to ``adapter_dir`` using the same logic as the final
    end-of-training save. Reused by periodic (hourly) checkpointing so that any
    saved checkpoint is directly loadable for evaluation."""
    adapter_dir.mkdir(parents=True, exist_ok=True)
    if lora_backend == "native" and adapter_init is None:
        save_native_lora_adapter(save_model, adapter_dir, torch_module, native_config)
    else:
        save_model.save_pretrained(adapter_dir)
    text_preprocessor.save_backend.save_pretrained(adapter_dir)


def _resolve_lora_targets_full_path(model: Any) -> list[str] | None:
    """Return explicit full-path target module names for architectures where suffix-only
    discovery is unreliable (e.g. Gemma 4 MoE, which has vision-tower modules that are
    *not* standard ``nn.Linear`` and would cause PEFT to error).

    Strategy: look for a ``language_model`` sub-tree.  If found, collect full module
    paths whose leaf suffix is a known projection name and whose underlying module class
    is ``torch.nn.Linear`` (exact match — not a subclass).  This avoids wrapping
    ``Gemma4ClippableLinear`` or any other custom vision-tower wrapper.

    Returns ``None`` when the model does not appear to need full-path resolution (i.e.
    there is no ``language_model`` attribute), so the caller can fall back to the
    standard suffix-group heuristic.
    """
    import torch.nn as nn

    # Only activate for models that expose a language_model sub-tree (e.g. Gemma 4).
    has_language_model_subtree = any(
        name == "model.language_model" or name.startswith("model.language_model.")
        for name, _ in model.named_modules()
    )
    if not has_language_model_subtree:
        return None

    targets: list[str] = []
    for name, mod in model.named_modules():
        if type(mod) is not nn.Linear:  # exact type check — exclude subclasses
            continue
        suffix = name.rsplit(".", 1)[-1] if "." in name else name
        if suffix not in _PROJECTION_SUFFIXES:
            continue
        # Must be inside the language_model sub-tree.
        if "language_model" not in name:
            continue
        targets.append(name)

    return targets if targets else None


def resolve_lora_target_modules(
    requested_target_modules: list[str] | None,
    model: Any,
    requested_target_module_regex: list[str] | None = None,
) -> list[str]:
    if requested_target_modules:
        return list(requested_target_modules)

    if requested_target_module_regex:
        patterns = [re.compile(pattern) for pattern in requested_target_module_regex]
        matched = [
            module_name
            for module_name, _module in model.named_modules()
            if module_name and any(pattern.search(module_name) for pattern in patterns)
        ]
        if not matched:
            raise SystemExit(
                "Unable to resolve any LoRA target modules from --target-module-regex. "
                f"Requested regexes: {requested_target_module_regex}"
            )
        return matched

    # For architectures with a language_model sub-tree (e.g. Gemma 4), use full-path
    # discovery to avoid accidentally wrapping vision-tower modules that may be
    # non-standard Linear subclasses unsupported by PEFT.
    full_path_targets = _resolve_lora_targets_full_path(model)
    if full_path_targets is not None:
        return full_path_targets

    leaf_names = sorted(
        {
            module_name.rsplit(".", 1)[-1]
            for module_name, _module in model.named_modules()
            if module_name
        }
    )
    for candidate_group in COMMON_LORA_TARGET_MODULE_GROUPS:
        matches = [name for name in candidate_group if name in leaf_names]
        if len(matches) >= 4:
            return matches

    sample = ", ".join(leaf_names[:20])
    raise SystemExit(
        "Unable to infer LoRA target modules automatically from the loaded model. "
        "Pass --target-modules explicitly for this architecture. "
        f"Sample discovered module suffixes: {sample}"
    )


def _compile_name_patterns(patterns: list[str] | None, *, flag_name: str) -> list[re.Pattern[str]]:
    if not patterns:
        return []
    compiled: list[re.Pattern[str]] = []
    for pattern in patterns:
        try:
            compiled.append(re.compile(pattern))
        except re.error as exc:
            raise SystemExit(f"Invalid regex for {flag_name}: {pattern!r} ({exc})") from exc
    return compiled


def _matches_any_pattern(name: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(pattern.search(name) for pattern in patterns)


def apply_selective_training_controls(
    model: Any,
    trainable_param_regex: list[str] | None = None,
    freeze_param_regex: list[str] | None = None,
) -> dict[str, Any]:
    trainable_patterns = _compile_name_patterns(trainable_param_regex, flag_name="--trainable-param-regex")
    freeze_patterns = _compile_name_patterns(freeze_param_regex, flag_name="--freeze-param-regex")

    params = list(model.named_parameters())
    initially_trainable_names = {name for name, parameter in params if parameter.requires_grad}

    trainable_regex_matches: list[str] = []
    if trainable_patterns:
        for name, parameter in params:
            if parameter.requires_grad and _matches_any_pattern(name, trainable_patterns):
                trainable_regex_matches.append(name)
            if parameter.requires_grad and not _matches_any_pattern(name, trainable_patterns):
                parameter.requires_grad = False
        if not trainable_regex_matches:
            raise SystemExit(
                "No trainable parameters matched --trainable-param-regex. "
                f"Requested patterns: {trainable_param_regex}"
            )

    frozen_by_regex: list[str] = []
    if freeze_patterns:
        for name, parameter in params:
            if parameter.requires_grad and _matches_any_pattern(name, freeze_patterns):
                parameter.requires_grad = False
                frozen_by_regex.append(name)

    final_trainable_names = [name for name, parameter in params if parameter.requires_grad]
    if not final_trainable_names:
        raise SystemExit(
            "Selective training controls froze all parameters. "
            "Adjust --trainable-param-regex/--freeze-param-regex so at least one parameter stays trainable."
        )

    return {
        "trainable_param_regex": list(trainable_param_regex) if trainable_param_regex else None,
        "freeze_param_regex": list(freeze_param_regex) if freeze_param_regex else None,
        "initial_trainable_count": len(initially_trainable_names),
        "final_trainable_count": len(final_trainable_names),
        "trainable_regex_match_count": len(trainable_regex_matches),
        "frozen_by_regex_count": len(frozen_by_regex),
        "final_trainable_sample": final_trainable_names[:12],
    }


def collect_trainable_parameters(model: Any) -> tuple[list[Any], list[str], int]:
    named_trainable = [(name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad]
    if not named_trainable:
        raise SystemExit("No trainable parameters found after selective training controls.")
    trainable_tensors = [parameter for _name, parameter in named_trainable]
    trainable_names = [name for name, _parameter in named_trainable]
    trainable_count = int(sum(parameter.numel() for parameter in trainable_tensors))
    return trainable_tensors, trainable_names, trainable_count


def enable_layernorm_training(model: Any) -> dict[str, Any]:
    trainable_names: list[str] = []
    trainable_count = 0
    for name, parameter in model.named_parameters():
        normalized = name.lower()
        if not any(token in normalized for token in ("layernorm", "layer_norm", "rmsnorm", ".norm", "_norm")):
            continue
        parameter.requires_grad = True
        trainable_names.append(name)
        trainable_count += int(parameter.numel())
    return {
        "enabled": True,
        "trainable_layernorm_count": len(trainable_names),
        "trainable_layernorm_parameter_count": trainable_count,
        "trainable_layernorm_sample": trainable_names[:12],
    }


def enforce_trainable_parameter_budget(trainable_count: int, budget: int | None) -> dict[str, Any]:
    if budget is not None and trainable_count > budget:
        raise SystemExit(
            "Trainable parameter count exceeds --max-trainable-parameters: "
            f"{trainable_count} > {budget}. Reduce LoRA rank or target modules."
        )
    return {
        "max_trainable_parameters": budget,
        "within_budget": budget is None or trainable_count <= budget,
    }


def enforce_min_trainable_parameters(trainable_count: int, minimum: int | None) -> dict[str, Any]:
    if minimum is not None and trainable_count < minimum:
        raise SystemExit(
            "Trainable parameter count is below --min-trainable-parameters: "
            f"{trainable_count} < {minimum}. Increase LoRA rank or target more modules."
        )
    return {
        "min_trainable_parameters": minimum,
        "meets_minimum": minimum is None or trainable_count >= minimum,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True)
    parser.add_argument(
        "--adapter-init",
        type=Path,
        default=None,
        help="Optional existing PEFT adapter directory to continue training from.",
    )
    parser.add_argument("--train-file", type=Path, required=True)
    parser.add_argument("--eval-file", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda", "npu"], default="auto")
    parser.add_argument(
        "--npu-device-map",
        choices=["auto", "balanced-layers"],
        default="auto",
        help="For non-DDP NPU launches, optionally shard language-model layers explicitly across visible NPUs.",
    )
    parser.add_argument(
        "--npu-max-memory-gib",
        type=int,
        default=56,
        help="Per-NPU max_memory GiB used with --npu-device-map balanced-layers.",
    )
    parser.add_argument("--max-length", type=int, default=2048)
    parser.add_argument("--per-device-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument(
        "--warmup-steps",
        type=int,
        default=0,
        help="Number of linear LR warmup steps before cosine decay. 0 disables warmup.",
    )
    parser.add_argument("--num-epochs", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument("--eval-steps", type=int, default=5)
    parser.add_argument("--log-steps", type=int, default=1)
    parser.add_argument("--lora-rank", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument(
        "--lora-backend",
        choices=["peft", "native"],
        default="peft",
        help="Use PEFT when available, or a minimal built-in LoRA wrapper for offline Huanxin task images.",
    )
    parser.add_argument(
        "--train-layernorm",
        action="store_true",
        help="Also unfreeze per-layer norm parameters as a tiny, uniform low-risk companion to LoRA.",
    )
    parser.add_argument(
        "--max-trainable-parameters",
        type=int,
        default=None,
        help="Fail if the trainable parameter count exceeds this budget.",
    )
    parser.add_argument(
        "--min-trainable-parameters",
        type=int,
        default=None,
        help="Fail if the trainable parameter count is below this floor.",
    )
    parser.add_argument("--load-in-8bit", action="store_true")
    parser.add_argument(
        "--gradient-checkpointing",
        action="store_true",
        help="Reduce activation memory by enabling gradient checkpointing and disabling KV cache.",
    )
    parser.add_argument("--train-on-completions-only", action="store_true")
    parser.add_argument("--research-methods", nargs="*", default=[])
    parser.add_argument("--overwrite-output-dir", action="store_true")
    parser.add_argument("--allow-output-dir-reuse", action="store_true")
    parser.add_argument(
        "--checkpoint-interval-seconds",
        type=int,
        default=0,
        help=(
            "If > 0, periodically save a timestamped LoRA adapter checkpoint to "
            "<output-dir>/checkpoints/step-<N>/adapter every N seconds of wall-clock "
            "training time (rank 0 only). 0 disables periodic checkpointing."
        ),
    )
    parser.add_argument(
        "--target-modules",
        nargs="*",
        default=None,
        help="Optional explicit LoRA target module suffixes. Defaults to auto-discovery from the loaded model.",
    )
    parser.add_argument(
        "--target-module-regex",
        nargs="*",
        default=None,
        help="Optional regex patterns matched against full module names for router-only or expert-specific LoRA targeting.",
    )
    parser.add_argument(
        "--trainable-param-regex",
        nargs="*",
        default=None,
        help="Optional regex allowlist for trainable parameter names. Non-matching trainable params are frozen.",
    )
    parser.add_argument(
        "--freeze-param-regex",
        nargs="*",
        default=None,
        help="Optional regex denylist for parameter names to freeze after allowlist filtering.",
    )
    return parser.parse_args()


def _visible_npu_indices() -> list[int]:
    raw = os.environ.get("ASCEND_RT_VISIBLE_DEVICES") or os.environ.get("ASCEND_VISIBLE_DEVICES")
    if not raw:
        return [0]
    indices: list[int] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            indices.append(int(item))
        except ValueError:
            indices.append(len(indices))
    return indices or [0]


def _config_get(config: Any, key: str) -> Any:
    if hasattr(config, key):
        return getattr(config, key)
    if isinstance(config, dict):
        return config.get(key)
    return None


def build_balanced_npu_layer_device_map(config: Any, visible_npus: list[int]) -> dict[str, int]:
    text_config = _config_get(config, "text_config") or _config_get(config, "llm_config") or config
    num_layers = _config_get(text_config, "num_hidden_layers") or _config_get(text_config, "num_layers")
    if not num_layers:
        raise SystemExit("Cannot build balanced NPU device map: config does not expose num_hidden_layers.")
    devices = list(range(len(visible_npus)))
    last_device = devices[-1]
    device_map: dict[str, int] = {
        "model.embed_tokens": devices[0],
        "model.norm": last_device,
        "model.rotary_emb": devices[0],
        "model.language_model.embed_tokens": devices[0],
        "model.language_model.norm": last_device,
        "model.language_model.rotary_emb": devices[0],
        "lm_head": last_device,
        # Multimodal checkpoints (e.g. Qwen3.5-MoE W8A8) ship a vision tower that
        # text-only SFT never runs, but accelerate's check_device_map still
        # requires every parameter to be placed. Pin the vision/audio towers and
        # projectors to device 0 so loading does not fail with
        # "device_map provided does not give any device for model.visual.*".
        "model.visual": devices[0],
        "visual": devices[0],
        "model.vision_tower": devices[0],
        "model.audio_tower": devices[0],
        "model.multi_modal_projector": devices[0],
    }
    for layer_idx in range(int(num_layers)):
        device_map[f"model.layers.{layer_idx}"] = devices[layer_idx * len(devices) // int(num_layers)]
        device_map[f"model.language_model.layers.{layer_idx}"] = devices[layer_idx * len(devices) // int(num_layers)]
    return device_map


def checkpoint_has_quantization_config(config: Any) -> bool:
    quantization_config = _config_get(config, "quantization_config")
    return bool(quantization_config)


def maybe_force_compressed_tensors_decompression(config: Any) -> bool:
    """Force compressed-tensors checkpoints to decompress to their native float
    dtype at load time.

    Ascend NPUs reject the frozen int8 (W8A8) matmul path (``aclnnMm`` rejects
    ``DT_INT8``). Setting ``run_compressed=False`` makes compressed-tensors
    materialize bf16 weights so plain Linear matmuls run on the NPU and LoRA can
    train on top of a frozen bf16 base. Returns True when the override was
    applied.
    """
    quantization_config = _config_get(config, "quantization_config")
    if quantization_config is None:
        return False
    quant_method = _config_get(quantization_config, "quant_method")
    if quant_method is None and isinstance(quantization_config, dict):
        quant_method = quantization_config.get("quant_method")
    if str(quant_method).replace("_", "-").lower() != "compressed-tensors":
        return False
    if isinstance(quantization_config, dict):
        quantization_config["run_compressed"] = False
    else:
        try:
            setattr(quantization_config, "run_compressed", False)
        except Exception:
            return False
    return True


def first_parameter_device(model: Any, fallback: Any) -> Any:
    try:
        return next(model.parameters()).device
    except Exception:
        return fallback


def require_training_dependencies(lora_backend: str, adapter_init: Path | None) -> tuple[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]:
    try:
        import torch
        import transformers
        from torch.utils.data import DataLoader, Dataset
        from transformers import AutoConfig, AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast
    except ImportError as exc:
        raise SystemExit(
            "Missing training dependencies. Install the bootstrap stack first, for example: "
            "python3 -m pip install -r training/requirements-huanxin-cpu.txt"
        ) from exc

    LoraConfig = PeftModel = TaskType = get_peft_model = None
    if lora_backend == "peft" or adapter_init is not None:
        try:
            from peft import LoraConfig, PeftModel, TaskType, get_peft_model
        except ImportError as exc:
            raise SystemExit(
                "Missing PEFT dependency. Use --lora-backend native for first-run LoRA without adapter-init, "
                "or install peft before running this trainer."
            ) from exc

    apply_transformers_peft_compat_shims(transformers)

    try:
        import torch_npu  # noqa: F401
    except ImportError:
        pass

    return (
        torch,
        transformers,
        LoraConfig,
        PeftModel,
        TaskType,
        get_peft_model,
        DataLoader,
        Dataset,
        AutoConfig,
        AutoModelForCausalLM,
        AutoTokenizer,
        AutoProcessor,
        PreTrainedTokenizerFast,
    )


def resolve_device(torch: Any, choice: str) -> Any:
    if choice == "cpu":
        return torch.device("cpu")
    if choice == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but not available")
        return torch.device("cuda")
    if choice == "npu":
        if not hasattr(torch, "npu") or not torch.npu.is_available():
            raise RuntimeError("NPU requested but not available")
        return torch.device("npu")
    if hasattr(torch, "npu") and torch.npu.is_available():
        return torch.device("npu")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}: {exc}") from exc
    if not rows:
        raise ValueError(f"No rows found in {path}")
    return rows


class ChatSftDataset:
    def __init__(
        self,
        path: Path,
        backend: TextPreprocessorBackend,
        max_length: int,
        train_on_completions_only: bool = False,
        research_methods: list[Any] | None = None,
        stage: str = "sft",
    ) -> None:
        rows = load_jsonl(path)
        self.examples = []
        self.skipped_empty_completion_examples: list[Any] = []
        research_methods = research_methods or []
        for record in rows:
            working_record = copy.deepcopy(record)
            for method in research_methods:
                working_record = method.augment_sft_record(working_record, stage=stage)
            example = build_supervised_text_example(
                working_record,
                backend,
                max_length,
                train_on_completions_only=train_on_completions_only,
            )
            if train_on_completions_only and count_trainable_label_tokens(example) <= 0:
                self.skipped_empty_completion_examples.append(example.get("example_id"))
                continue
            self.examples.append(example)
        if not self.examples:
            raise ValueError(
                "No usable SFT examples remain after tokenization/truncation. "
                "Increase --max-length or use a shorter smoke split."
            )

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, index: int) -> dict:
        return self.examples[index]


def count_trainable_label_tokens(example: dict[str, Any]) -> int:
    return max(0, len(example["input_ids"]) - int(example.get("prompt_token_count") or 0))


def summarize_trainable_label_counts(dataset: ChatSftDataset) -> dict[str, Any]:
    counts = [count_trainable_label_tokens(example) for example in dataset.examples]
    if not counts:
        return {"min": 0, "max": 0, "mean": 0.0, "p50": 0, "p90": 0, "sample": []}
    ordered = sorted(counts)

    def percentile_index(fraction: float) -> int:
        return min(len(ordered) - 1, max(0, round((len(ordered) - 1) * fraction)))

    return {
        "min": min(counts),
        "max": max(counts),
        "mean": round(sum(counts) / len(counts), 3),
        "p50": ordered[percentile_index(0.5)],
        "p90": ordered[percentile_index(0.9)],
        "sample": counts[:8],
    }


class PaddingCollator:
    def __init__(self, text_backend: Any, torch_module: Any, *, add_mm_token_type_ids: bool = False) -> None:
        self.text_backend = text_backend
        self.torch_module = torch_module
        self.add_mm_token_type_ids = add_mm_token_type_ids

    def __call__(self, batch: list[dict]) -> dict[str, Any]:
        return pad_supervised_text_batch(
            batch,
            self.text_backend,
            self.torch_module,
            add_mm_token_type_ids=self.add_mm_token_type_ids,
        )


def _unwrap_causal_lm(model: Any) -> Any:
    """Return the underlying HF CausalLM, unwrapping DDP/PEFT wrappers."""
    inner = getattr(model, "module", model)  # DDP
    inner = getattr(inner, "base_model", inner)  # PEFT LoraModel -> base_model
    inner = getattr(inner, "model", inner)  # PEFT base_model.model -> HF model
    return inner


def _resolve_lm_head_and_backbone(model: Any):
    """Best-effort locate the lm_head and the backbone that returns hidden states."""
    inner = _unwrap_causal_lm(model)
    lm_head = getattr(inner, "lm_head", None)
    backbone = getattr(inner, "model", None)
    return inner, backbone, lm_head


def chunked_causal_lm_loss(
    model: Any,
    batch: dict,
    torch_module: Any,
    chunk_size: int = 1024,
    ignore_index: int = -100,
) -> Any:
    """Compute causal-LM cross-entropy WITHOUT materializing the full
    [B, seq, vocab] logits tensor.

    The vocab is ~150k, so on a 61 GiB Ascend NPU the fp32 logits+loss tensor at
    seq_len 512-768 alone OOMs. We run the transformer backbone once to get hidden
    states, then apply the lm_head + cross-entropy over short slices of the
    sequence so peak memory is capped at chunk_size tokens of logits at a time.

    Falls back to the model's built-in loss if we cannot locate the lm_head /
    backbone (so behaviour is never silently wrong).
    """
    inner, backbone, lm_head = _resolve_lm_head_and_backbone(model)
    labels = batch.get("labels")
    if labels is None or backbone is None or lm_head is None:
        # Cannot do the memory-frugal path; defer to the model's own loss.
        return model(**batch).loss

    backbone_inputs = {k: v for k, v in batch.items() if k != "labels"}
    outputs = backbone(**backbone_inputs)
    hidden = outputs[0] if isinstance(outputs, tuple) else outputs.last_hidden_state

    # Standard causal shift: predict token t+1 from hidden state at t.
    shift_hidden = hidden[:, :-1, :].contiguous()
    shift_labels = labels[:, 1:].contiguous()
    flat_hidden = shift_hidden.view(-1, shift_hidden.size(-1))
    flat_labels = shift_labels.view(-1)

    total_tokens = int((flat_labels != ignore_index).sum().item())
    if total_tokens == 0:
        return flat_hidden.sum() * 0.0  # keep graph, zero loss

    loss_sum = None
    n = flat_hidden.size(0)
    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        logits_chunk = lm_head(flat_hidden[start:end])
        if logits_chunk.dtype not in (torch_module.float32, torch_module.float64):
            logits_chunk = logits_chunk.float()
        labels_chunk = flat_labels[start:end]
        chunk_loss = torch_module.nn.functional.cross_entropy(
            logits_chunk,
            labels_chunk,
            ignore_index=ignore_index,
            reduction="sum",
        )
        loss_sum = chunk_loss if loss_sum is None else loss_sum + chunk_loss
        del logits_chunk
    return loss_sum / total_tokens


def evaluate(model: Any, loader: Any, device: Any, torch_module: Any) -> dict[str, float]:
    use_chunked = os.environ.get("QWEN_SFT_CHUNKED_LOSS", "0") == "1"
    chunk_size = int(os.environ.get("QWEN_SFT_LOSS_CHUNK", "1024") or "1024")
    model.eval()
    total_loss = 0.0
    total_items = 0
    with torch_module.no_grad():
        for batch in loader:
            batch = {name: tensor.to(device) for name, tensor in batch.items()}
            if use_chunked:
                loss = chunked_causal_lm_loss(model, batch, torch_module, chunk_size=chunk_size)
            else:
                loss = model(**batch).loss
            batch_items = batch["input_ids"].size(0)
            total_loss += float(loss.item()) * batch_items
            total_items += batch_items
    mean_loss = total_loss / max(total_items, 1)
    return {"loss": mean_loss, "perplexity": float(math.exp(min(mean_loss, 20.0)))}


def build_run_signature(args: argparse.Namespace) -> dict[str, Any]:
    signature = {
        "model_name": args.model_name,
        "adapter_init": str(args.adapter_init) if args.adapter_init else None,
        "train_file": str(args.train_file),
        "eval_file": str(args.eval_file) if args.eval_file else None,
        "device": args.device,
        "npu_device_map": args.npu_device_map,
        "npu_max_memory_gib": args.npu_max_memory_gib,
        "max_length": args.max_length,
        "per_device_batch_size": args.per_device_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "learning_rate": args.learning_rate,
        "num_epochs": args.num_epochs,
        "max_steps": args.max_steps,
        "eval_steps": args.eval_steps,
        "log_steps": args.log_steps,
        "lora_rank": args.lora_rank,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "lora_backend": args.lora_backend,
        "train_layernorm": args.train_layernorm,
        "max_trainable_parameters": args.max_trainable_parameters,
        "min_trainable_parameters": args.min_trainable_parameters,
        "load_in_8bit": args.load_in_8bit,
        "train_on_completions_only": args.train_on_completions_only,
        "research_methods": list(args.research_methods),
        "target_modules": list(args.target_modules) if args.target_modules else None,
        "target_module_regex": list(args.target_module_regex) if args.target_module_regex else None,
        "trainable_param_regex": list(args.trainable_param_regex) if args.trainable_param_regex else None,
        "freeze_param_regex": list(args.freeze_param_regex) if args.freeze_param_regex else None,
    }
    signature_json = json.dumps(signature, sort_keys=True)
    signature["signature_sha256"] = hashlib.sha256(signature_json.encode("utf-8")).hexdigest()
    return signature


def validate_output_dir(args: argparse.Namespace, run_signature: dict[str, Any]) -> None:
    config_path = args.output_dir / "run_config.json"
    has_existing_artifacts = config_path.exists() or (args.output_dir / "adapter").exists() or (args.output_dir / "metrics.json").exists()

    if args.overwrite_output_dir:
        return

    if not has_existing_artifacts:
        return

    if config_path.exists():
        existing = json.loads(config_path.read_text(encoding="utf-8"))
        existing_signature = existing.get("signature", {})
        if existing_signature != run_signature:
            raise SystemExit(
                "Refusing to reuse an existing output directory with a different training configuration. "
                f"Use a new --output-dir or pass --overwrite-output-dir if replacement is intentional: {args.output_dir}"
            )

    if not args.allow_output_dir_reuse:
        raise SystemExit(
            f"Output directory already contains prior run artifacts: {args.output_dir}. "
            "Use a new --output-dir, or pass --allow-output-dir-reuse / --overwrite-output-dir explicitly."
        )


@elastic_record
def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_signature = build_run_signature(args)
    validate_output_dir(args, run_signature)
    research_methods = load_research_methods(args.research_methods)
    print(json.dumps({"stage": "args_parsed", "output_dir": str(args.output_dir), "train_file": str(args.train_file), "eval_file": str(args.eval_file) if args.eval_file else None}, ensure_ascii=False), flush=True)
    print(json.dumps({"stage": "research_methods_loaded", "methods": summarize_methods(research_methods)}, ensure_ascii=False), flush=True)

    (
        torch,
        transformers,
        LoraConfig,
        PeftModel,
        TaskType,
        get_peft_model,
        DataLoader,
        _Dataset,
        AutoConfig,
        AutoModelForCausalLM,
        AutoTokenizer,
        AutoProcessor,
        PreTrainedTokenizerFast,
    ) = require_training_dependencies(args.lora_backend, args.adapter_init)
    qwen35_runtime_registration = None
    try:
        qwen35_runtime_registration = register_qwen35_moe_runtime(
            transformers,
            auto_config_cls=AutoConfig,
            auto_model_for_causal_lm_cls=AutoModelForCausalLM,
        )
    except Exception as exc:  # noqa: BLE001
        qwen35_runtime_registration = {
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    print(json.dumps({"stage": "deps_loaded"}, ensure_ascii=False), flush=True)
    print(json.dumps({"stage": "qwen35_moe_runtime_registration", **qwen35_runtime_registration}, ensure_ascii=False), flush=True)

    try:
        model_loader, runtime_compat, model_loader_metadata = select_transformers_model_loader(
            args.model_name,
            auto_config_cls=AutoConfig,
            auto_model_for_causal_lm_cls=AutoModelForCausalLM,
            transformers_module=transformers,
        )
    except SystemExit as exc:
        runtime_compat = probe_model_runtime_compat(args.model_name, AutoConfig)
        print(
            json.dumps(
                {
                    "stage": "trainer_backend_preflight",
                    "state": "blocked",
                    "model_type": (runtime_compat or {}).get("config_model_type"),
                    "architectures": (runtime_compat or {}).get("config_architectures"),
                    "error": str(exc),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        raise
    if runtime_compat is not None:
        print(
            json.dumps(
                {
                    "stage": "model_runtime_compat_checked",
                    **runtime_compat,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    print(json.dumps({"stage": "model_loader_selected", **model_loader_metadata}, ensure_ascii=False), flush=True)

    text_preprocessor = load_text_preprocessor_backend(args.model_name, AutoTokenizer, AutoProcessor, PreTrainedTokenizerFast)
    print(
        json.dumps(
            {
                "stage": "text_preprocessor_loaded",
                "backend_kind": text_preprocessor.backend_kind,
                "render_backend_class": text_preprocessor.render_backend.__class__.__name__,
                "text_backend_class": text_preprocessor.text_backend.__class__.__name__,
                "save_backend_class": text_preprocessor.save_backend.__class__.__name__,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    device = resolve_device(torch, args.device)
    print(json.dumps({"stage": "device_resolved", "device": str(device), "requested": args.device}, ensure_ascii=False), flush=True)

    # DDP setup
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    rank = int(os.environ.get("RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    distributed = world_size > 1
    if not distributed:
        local_rank = 0
        rank = 0

    if distributed:
        if device.type == "npu":
            torch.npu.set_device(local_rank)
            device = torch.device(f"npu:{local_rank}")
        torch.distributed.init_process_group(backend="hccl" if device.type == "npu" else "nccl")
    else:
        if device.type == "npu":
            torch.npu.set_device(0)
    print(json.dumps({"stage": "ddp_ready", "distributed": distributed, "rank": rank, "world_size": world_size, "device": str(device)}, ensure_ascii=False), flush=True)

    if rank == 0:
        (args.output_dir / "sft_step_metrics.jsonl").unlink(missing_ok=True)
        (args.output_dir / "metrics.json").unlink(missing_ok=True)

    tokenizer = text_preprocessor.text_backend
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print(json.dumps({"stage": "tokenizer_loaded", "pad_token": tokenizer.pad_token, "padding_side": tokenizer.padding_side}, ensure_ascii=False), flush=True)

    train_dataset = ChatSftDataset(
        args.train_file,
        text_preprocessor,
        args.max_length,
        train_on_completions_only=args.train_on_completions_only,
        research_methods=research_methods,
        stage="sft_train",
    )
    eval_dataset = ChatSftDataset(
        args.eval_file,
        text_preprocessor,
        args.max_length,
        train_on_completions_only=args.train_on_completions_only,
        research_methods=research_methods,
        stage="sft_eval",
    ) if args.eval_file else None
    train_label_summary = summarize_trainable_label_counts(train_dataset)
    eval_label_summary = summarize_trainable_label_counts(eval_dataset) if eval_dataset is not None else None
    print(
        json.dumps(
            {
                "stage": "datasets_ready",
                "train_examples": len(train_dataset),
                "eval_examples": len(eval_dataset) if eval_dataset is not None else 0,
                "max_length": args.max_length,
                "train_label_tokens": train_label_summary,
                "eval_label_tokens": eval_label_summary,
                "train_skipped_empty_completion_examples": len(train_dataset.skipped_empty_completion_examples),
                "train_skipped_empty_completion_sample": train_dataset.skipped_empty_completion_examples[:5],
                "eval_skipped_empty_completion_examples": len(eval_dataset.skipped_empty_completion_examples) if eval_dataset is not None else 0,
                "eval_skipped_empty_completion_sample": eval_dataset.skipped_empty_completion_examples[:5] if eval_dataset is not None else [],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    collator = PaddingCollator(
        text_preprocessor.text_backend,
        torch,
        add_mm_token_type_ids=(
            str(runtime_compat.get("config_model_type") if runtime_compat is not None else "").startswith("gemma4")
        ),
    )
    train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset, num_replicas=world_size, rank=rank, shuffle=True) if distributed else None
    train_loader = DataLoader(train_dataset, batch_size=args.per_device_batch_size, shuffle=(train_sampler is None), collate_fn=collator, sampler=train_sampler)
    eval_loader = None
    if eval_dataset is not None:
        eval_loader = DataLoader(eval_dataset, batch_size=args.per_device_batch_size, shuffle=False, collate_fn=collator)
    preflight_batch = collator([train_dataset[0]])

    optimizer_steps_per_epoch = len(train_loader) // args.gradient_accumulation_steps
    max_available_steps = optimizer_steps_per_epoch * args.num_epochs
    if optimizer_steps_per_epoch < 1:
        raise ValueError(
            "Not enough batches to produce one optimizer step. "
            "Lower --gradient-accumulation-steps or increase training data."
        )
    # --max-steps <= 0 means "train all available steps" (full requested epochs).
    if args.max_steps <= 0:
        args.max_steps = max_available_steps
    if args.max_steps > max_available_steps:
        raise ValueError(
            f"Requested --max-steps {args.max_steps} but current settings only allow "
            f"{max_available_steps} optimizer step(s) across {args.num_epochs} epoch(s). "
            "Increase --num-epochs, lower --gradient-accumulation-steps, or reduce --max-steps."
        )
    print(
        json.dumps(
            {
                "stage": "train_schedule_ready",
                "optimizer_steps_per_epoch": optimizer_steps_per_epoch,
                "max_available_steps": max_available_steps,
                "requested_max_steps": args.max_steps,
                "num_epochs": args.num_epochs,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    # Keep remote multi-rank launches from spiking host RAM while preserving the
    # checkpoint's native precision for OmniCoder/Qwen-family snapshots.
    model_config = AutoConfig.from_pretrained(args.model_name, trust_remote_code=True)
    checkpoint_is_quantized = checkpoint_has_quantization_config(model_config)
    decompress_quantized = (
        checkpoint_is_quantized
        and args.device == "npu"
        and os.environ.get("QWEN_SFT_DECOMPRESS_COMPRESSED_TENSORS", "1") != "0"
    )
    decompressed_compressed_tensors = (
        maybe_force_compressed_tensors_decompression(model_config) if decompress_quantized else False
    )
    if decompressed_compressed_tensors:
        load_dtype: Any = torch.bfloat16
    elif checkpoint_is_quantized:
        load_dtype = "auto"
    elif args.device == "npu":
        load_dtype = torch.bfloat16
    else:
        load_dtype = "auto"
    model_kwargs = {
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "torch_dtype": load_dtype,
        "config": model_config,
    }
    # Allow forcing the attention backend (e.g. eager) via env. On Ascend NPU the
    # Qwen3.5 hybrid model's flash-attention backward op
    # (aclnnFlashAttentionScoreGrad) fails, so QWEN_SFT_ATTN_IMPL=eager routes the
    # softmax-attention layers through the eager path instead.
    _attn_impl = os.environ.get("QWEN_SFT_ATTN_IMPL", "").strip()
    if _attn_impl:
        model_kwargs["attn_implementation"] = _attn_impl
        try:
            model_config._attn_implementation = _attn_impl
        except Exception:
            pass
    print(
        json.dumps(
            {
                "stage": "quantized_checkpoint_load_plan",
                "checkpoint_is_quantized": checkpoint_is_quantized,
                "decompressed_compressed_tensors": decompressed_compressed_tensors,
                "load_dtype": str(load_dtype),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    if args.device == "npu":
        if distributed:
            model_kwargs["device_map"] = {"": local_rank}
        elif args.npu_device_map == "balanced-layers":
            visible_npus = _visible_npu_indices()
            model_kwargs["device_map"] = build_balanced_npu_layer_device_map(model_config, visible_npus)
            model_kwargs["max_memory"] = {
                device_idx: f"{args.npu_max_memory_gib}GiB"
                for device_idx in range(len(visible_npus))
            }
            print(
                json.dumps(
                    {
                        "stage": "balanced_npu_device_map_ready",
                        "visible_npus": visible_npus,
                        "device_map_entries": len(model_kwargs["device_map"]),
                        "max_memory": model_kwargs["max_memory"],
                        "checkpoint_is_quantized": checkpoint_is_quantized,
                        "torch_dtype": str(model_kwargs.get("torch_dtype")),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
        else:
            model_kwargs["device_map"] = "auto"
    elif args.load_in_8bit:
        model_kwargs.pop("torch_dtype", None)
        model_kwargs["load_in_8bit"] = True
        model_kwargs["device_map"] = "auto"
    print(json.dumps({"stage": "model_load_start", "model_name": args.model_name, "t": time.time()}, ensure_ascii=False), flush=True)
    model_load_started_at = time.time()
    try:
        model = model_loader.from_pretrained(args.model_name, **model_kwargs)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "stage": "model_load_failed",
                    "t": time.time(),
                    "dt_model_load_sec": round(time.time() - model_load_started_at, 3),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        raise
    print(json.dumps({"stage": "model_loaded", "t": time.time(), "dt_model_load_sec": round(time.time() - model_load_started_at, 3)}, ensure_ascii=False), flush=True)
    lora_wrap_summary: dict[str, Any] = {"backend": args.lora_backend}
    if args.adapter_init is not None:
        if PeftModel is None:
            raise SystemExit("--adapter-init requires PEFT; native backend can only create new LoRA adapters.")
        model = PeftModel.from_pretrained(model, str(args.adapter_init), is_trainable=True)
        resolved_target_modules = None
        print(
            json.dumps(
                {
                    "stage": "adapter_init_loaded",
                    "adapter_init": str(args.adapter_init),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    elif args.lora_backend == "peft":
        if LoraConfig is None or TaskType is None or get_peft_model is None:
            raise SystemExit("PEFT backend selected but PEFT imports are unavailable.")
        resolved_target_modules = resolve_lora_target_modules(
            args.target_modules,
            model,
            args.target_module_regex,
        )
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            target_modules=resolved_target_modules,
            bias="none",
        )
        model = get_peft_model(model, lora_config)
        lora_wrap_summary = {"backend": "peft"}
        print(json.dumps({"stage": "lora_wrapped", "resolved_target_modules": resolved_target_modules, **lora_wrap_summary}, ensure_ascii=False), flush=True)
    else:
        resolved_target_modules = resolve_lora_target_modules(
            args.target_modules,
            model,
            args.target_module_regex,
        )
        lora_wrap_summary = apply_native_lora(
            model,
            torch,
            resolved_target_modules,
            args.lora_rank,
            args.lora_alpha,
            args.lora_dropout,
        )
        print(json.dumps({"stage": "lora_wrapped", "resolved_target_modules": resolved_target_modules, **lora_wrap_summary}, ensure_ascii=False), flush=True)
    if args.gradient_checkpointing:
        if hasattr(model, "config"):
            model.config.use_cache = False
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
        if hasattr(model, "gradient_checkpointing_enable"):
            model.gradient_checkpointing_enable()
        print(
            json.dumps(
                {
                    "stage": "gradient_checkpointing_enabled",
                    "use_cache": getattr(getattr(model, "config", None), "use_cache", None),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    layernorm_training = {"enabled": False, "trainable_layernorm_count": 0, "trainable_layernorm_parameter_count": 0}
    if args.train_layernorm:
        layernorm_training = enable_layernorm_training(model)
        print(json.dumps({"stage": "layernorm_training_enabled", **layernorm_training}, ensure_ascii=False), flush=True)
    selective_training = apply_selective_training_controls(
        model,
        trainable_param_regex=getattr(args, "trainable_param_regex", None),
        freeze_param_regex=getattr(args, "freeze_param_regex", None),
    )
    trainable_param_tensors, trainable_param_names, trainable_param_count = collect_trainable_parameters(model)
    trainable_parameter_budget = enforce_trainable_parameter_budget(trainable_param_count, args.max_trainable_parameters)
    trainable_parameter_floor = enforce_min_trainable_parameters(trainable_param_count, args.min_trainable_parameters)
    print(
        json.dumps(
            {
                "stage": "selective_training_applied",
                **selective_training,
                "layernorm_training": layernorm_training,
                "trainable_parameter_budget": trainable_parameter_budget,
                "trainable_parameter_floor": trainable_parameter_floor,
                "trainable_parameter_count": trainable_param_count,
                "trainable_parameter_sample": trainable_param_names[:12],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    if "device_map" not in model_kwargs:
        model.to(device)
    batch_device = first_parameter_device(model, device)
    print(
        json.dumps(
            {
                "stage": "model_on_device",
                "device": str(device),
                "batch_device": str(batch_device),
                "has_device_map": "device_map" in model_kwargs,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    text_forward_preflight = run_text_forward_preflight(
        model,
        preflight_batch,
        torch_module=torch,
        device=batch_device,
    )
    print(
        json.dumps(
            {
                "stage": "text_forward_preflight",
                **text_forward_preflight,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    if distributed:
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[local_rank])
        print(json.dumps({"stage": "ddp_wrapped"}, ensure_ascii=False), flush=True)
    model.train()
    print(json.dumps({"stage": "train_mode"}, ensure_ascii=False), flush=True)

    optimizer = torch.optim.AdamW(trainable_param_tensors, lr=args.learning_rate)
    total_train_steps = max(args.max_steps, 1)
    warmup_steps = max(int(getattr(args, "warmup_steps", 0) or 0), 0)
    warmup_steps = min(warmup_steps, max(total_train_steps - 1, 0))
    if warmup_steps > 0:
        warmup_scheduler = torch.optim.lr_scheduler.LinearLR(
            optimizer, start_factor=0.1, end_factor=1.0, total_iters=warmup_steps
        )
        cosine_scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=max(total_train_steps - warmup_steps, 1)
        )
        scheduler = torch.optim.lr_scheduler.SequentialLR(
            optimizer, schedulers=[warmup_scheduler, cosine_scheduler], milestones=[warmup_steps]
        )
    else:
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_train_steps)

    metrics: list[dict[str, float | int]] = []
    global_step = 0
    optimizer.zero_grad(set_to_none=True)

    # Native LoRA adapter config reused by both periodic and final saves.
    native_adapter_config = {
        "peft_type": "LORA",
        "task_type": "CAUSAL_LM",
        "lora_backend": "native",
        "r": args.lora_rank,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": args.lora_dropout,
        "target_modules": resolved_target_modules,
        "base_model_name_or_path": args.model_name,
        "bias": "none",
    }
    checkpoint_interval_seconds = max(int(getattr(args, "checkpoint_interval_seconds", 0) or 0), 0)
    last_checkpoint_time = time.time()
    # Memory-frugal loss: avoid materializing full [B, seq, vocab] logits, which
    # OOMs on Ascend NPU. Enabled via QWEN_SFT_CHUNKED_LOSS=1.
    use_chunked_loss = os.environ.get("QWEN_SFT_CHUNKED_LOSS", "0") == "1"
    loss_chunk_size = int(os.environ.get("QWEN_SFT_LOSS_CHUNK", "1024") or "1024")
    print(
        json.dumps({"stage": "loss_mode", "chunked": use_chunked_loss, "chunk_size": loss_chunk_size}, ensure_ascii=False),
        flush=True,
    )
    print(
        json.dumps(
            {
                "stage": "optimizer_ready",
                "max_steps": args.max_steps,
                "gradient_accumulation_steps": args.gradient_accumulation_steps,
                "trainable_parameter_count": trainable_param_count,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    for epoch in range(args.num_epochs):
        if train_sampler is not None:
            train_sampler.set_epoch(epoch)
        print(json.dumps({"stage": "epoch_start", "epoch": epoch + 1}, ensure_ascii=False), flush=True)
        for batch_index, batch in enumerate(train_loader, start=1):
            if batch_index == 1:
                first_batch_time = time.time()
                print(json.dumps({"stage": "first_batch_loaded", "batch_index": batch_index, "input_shape": list(batch["input_ids"].shape), "t": first_batch_time}, ensure_ascii=False), flush=True)
            batch = {name: tensor.to(batch_device) for name, tensor in batch.items()}
            if use_chunked_loss:
                raw_loss = chunked_causal_lm_loss(
                    model, batch, torch, chunk_size=loss_chunk_size
                )
            else:
                outputs = model(**batch)
                raw_loss = outputs.loss
            if batch_index == 1:
                print(json.dumps({"stage": "first_forward_done", "batch_index": batch_index, "t": time.time(), "dt_from_batch_loaded_sec": round(time.time() - first_batch_time, 3)}, ensure_ascii=False), flush=True)
            loss = raw_loss / args.gradient_accumulation_steps
            if batch_index == 1:
                print(json.dumps({"stage": "first_loss_ready", "batch_index": batch_index, "loss": float(loss.item())}, ensure_ascii=False), flush=True)
            loss.backward()
            if batch_index == 1:
                print(json.dumps({"stage": "first_backward_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)

            if batch_index % args.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(trainable_param_tensors, 1.0)
                if batch_index == 1:
                    print(json.dumps({"stage": "first_clip_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                optimizer.step()
                if batch_index == 1:
                    print(json.dumps({"stage": "first_optimizer_step_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                scheduler.step()
                if batch_index == 1:
                    print(json.dumps({"stage": "first_scheduler_step_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                optimizer.zero_grad(set_to_none=True)
                if batch_index == 1:
                    print(json.dumps({"stage": "first_zero_grad_done", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                global_step += 1

                if global_step % args.log_steps == 0:
                    import datetime
                    record: dict[str, Any] = {
                        "step": global_step,
                        "epoch": epoch + 1,
                        "train_loss": float(loss.item() * args.gradient_accumulation_steps),
                        "lr": float(scheduler.get_last_lr()[0]),
                        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    }
                    if batch_index == 1:
                        print(json.dumps({"stage": "first_record_ready", "batch_index": batch_index}, ensure_ascii=False), flush=True)
                    if eval_loader is not None and global_step % args.eval_steps == 0:
                        if batch_index == 1:
                            print(json.dumps({"stage": "first_eval_start", "batch_index": batch_index, "t": time.time()}, ensure_ascii=False), flush=True)
                        eval_started_at = time.time()
                        record.update({f"eval_{k}": v for k, v in evaluate(model.module if distributed else model, eval_loader, batch_device, torch).items()})
                        if batch_index == 1:
                            print(json.dumps({"stage": "first_eval_done", "batch_index": batch_index, "t": time.time(), "dt_eval_sec": round(time.time() - eval_started_at, 3)}, ensure_ascii=False), flush=True)
                        model.train()
                    metrics.append(record)
                    if rank == 0:
                        print(json.dumps(record, ensure_ascii=False))
                        step_metrics_file = args.output_dir / "sft_step_metrics.jsonl"
                        try:
                            step_metrics_file.parent.mkdir(parents=True, exist_ok=True)
                            with step_metrics_file.open("a", encoding="utf-8") as handle:
                                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                        except Exception as e:
                            print(f"Warning: failed to write sft_step_metrics.jsonl: {e}", sys.stderr)

                # Periodic (hourly) wall-clock checkpoint to a durable path so no
                # progress is lost if the session/pod ends mid-run. Rank 0 only.
                if (
                    rank == 0
                    and checkpoint_interval_seconds > 0
                    and (time.time() - last_checkpoint_time) >= checkpoint_interval_seconds
                ):
                    ckpt_adapter_dir = args.output_dir / "checkpoints" / f"step-{global_step}" / "adapter"
                    ckpt_started_at = time.time()
                    print(
                        json.dumps(
                            {"stage": "periodic_checkpoint_start", "step": global_step, "t": ckpt_started_at, "adapter_dir": str(ckpt_adapter_dir)},
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
                    try:
                        persist_adapter(
                            save_model=model.module if distributed else model,
                            adapter_dir=ckpt_adapter_dir,
                            torch_module=torch,
                            lora_backend=args.lora_backend,
                            adapter_init=args.adapter_init,
                            native_config=native_adapter_config,
                            text_preprocessor=text_preprocessor,
                        )
                        (ckpt_adapter_dir.parent / "checkpoint_meta.json").write_text(
                            json.dumps({"step": global_step, "epoch": epoch + 1, "saved_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2) + "\n",
                            encoding="utf-8",
                        )
                        last_checkpoint_time = time.time()
                        print(
                            json.dumps(
                                {"stage": "periodic_checkpoint_done", "step": global_step, "t": last_checkpoint_time, "dt_ckpt_sec": round(last_checkpoint_time - ckpt_started_at, 3)},
                                ensure_ascii=False,
                            ),
                            flush=True,
                        )
                    except Exception as e:  # never let checkpointing kill the run
                        print(f"Warning: periodic checkpoint failed at step {global_step}: {e}", file=sys.stderr, flush=True)
                        model.train()

                if global_step >= args.max_steps:
                    break
        if global_step >= args.max_steps:
            break

    final_eval = None
    if eval_loader is not None:
        print(json.dumps({"stage": "final_eval_start", "t": time.time()}, ensure_ascii=False), flush=True)
        final_eval_started_at = time.time()
        final_eval = evaluate(model.module if distributed else model, eval_loader, batch_device, torch)
        print(json.dumps({"stage": "final_eval_done", "t": time.time(), "dt_final_eval_sec": round(time.time() - final_eval_started_at, 3)}, ensure_ascii=False), flush=True)

    if rank == 0:
        save_model = model.module if distributed else model
        adapter_dir = args.output_dir / "adapter"
        print(json.dumps({"stage": "save_start", "t": time.time(), "adapter_dir": str(adapter_dir)}, ensure_ascii=False), flush=True)
        save_started_at = time.time()
        persist_adapter(
            save_model=save_model,
            adapter_dir=adapter_dir,
            torch_module=torch,
            lora_backend=args.lora_backend,
            adapter_init=args.adapter_init,
            native_config=native_adapter_config,
            text_preprocessor=text_preprocessor,
        )
        print(json.dumps({"stage": "save_done", "t": time.time(), "dt_save_sec": round(time.time() - save_started_at, 3)}, ensure_ascii=False), flush=True)

        summary = {
            "model_name": args.model_name,
            "signature": run_signature,
            "resolved_target_modules": resolved_target_modules if args.adapter_init is None else None,
            "lora_wrap_summary": lora_wrap_summary,
            "device": str(device),
            "text_forward_preflight": text_forward_preflight,
            "selective_training": selective_training,
            "layernorm_training": layernorm_training,
            "trainable_parameter_budget": trainable_parameter_budget,
            "trainable_parameter_floor": trainable_parameter_floor,
            "trainable_parameter_count": trainable_param_count,
            "trainable_parameter_sample": trainable_param_names[:12],
            "world_size": world_size,
            "train_examples": len(train_dataset),
            "eval_examples": len(eval_dataset) if eval_dataset is not None else 0,
            "optimizer_steps_per_epoch": optimizer_steps_per_epoch,
            "max_available_steps": max_available_steps,
            "requested_max_steps": args.max_steps,
            "completed_steps": global_step,
            "max_steps": global_step,
            "research_methods": summarize_methods(research_methods),
            "final_eval": final_eval,
            "metrics": metrics,
        }
        (args.output_dir / "run_config.json").write_text(
            json.dumps(
                {
                    "signature": run_signature,
                    "resolved_target_modules": resolved_target_modules if args.adapter_init is None else None,
                    "lora_wrap_summary": lora_wrap_summary,
                    "selective_training": selective_training,
                    "layernorm_training": layernorm_training,
                    "trainable_parameter_budget": trainable_parameter_budget,
                    "trainable_parameter_count": trainable_param_count,
                    "trainable_parameter_sample": trainable_param_names[:12],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (args.output_dir / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))


    if distributed:
        torch.distributed.destroy_process_group()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
