from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

from training.model_family_preflight import inference_backend_preflight_block, trainer_backend_preflight_block


def load_model_config_metadata(model_name: str) -> dict[str, Any]:
    from transformers import PretrainedConfig

    config_dict, _unused_kwargs = PretrainedConfig.get_config_dict(model_name, trust_remote_code=True)
    return config_dict


def load_tokenizer_config_metadata(model_name: str) -> dict[str, Any]:
    tokenizer_config_path = Path(model_name) / "tokenizer_config.json"
    if not tokenizer_config_path.exists():
        return {}
    import json

    return json.loads(tokenizer_config_path.read_text(encoding="utf-8"))


def runtime_autoconfig_requires_upgrade(model_type: str, exc: Exception) -> bool:
    if not model_type:
        return False
    message = str(exc).lower()
    return (
        "does not recognize this architecture" in message
        or "does not recognize this model type" in message
        or "unrecognized configuration class" in message
        or "transformers does not recognize this architecture" in message
    )


def probe_model_runtime_compat(model_name: str, auto_config_cls: Any) -> dict[str, Any] | None:
    try:
        config_dict = load_model_config_metadata(model_name)
    except Exception:
        return None

    model_type = str(config_dict.get("model_type") or "")
    architectures = [str(item) for item in (config_dict.get("architectures") or [])]
    summary: dict[str, Any] = {
        "config_model_type": model_type,
        "config_architectures": architectures,
        "runtime_autoconfig_ok": False,
    }
    checkpoint_transformers_version = config_dict.get("transformers_version")
    if checkpoint_transformers_version:
        summary["checkpoint_transformers_version"] = str(checkpoint_transformers_version)
    try:
        runtime_config = auto_config_cls.from_pretrained(model_name, trust_remote_code=True)
        summary["runtime_autoconfig_ok"] = True
        summary["runtime_config_class"] = runtime_config.__class__.__name__
    except Exception as exc:  # noqa: BLE001
        summary["runtime_autoconfig_error_type"] = type(exc).__name__
        summary["runtime_autoconfig_error"] = str(exc)
    return summary


def build_runtime_upgrade_message(model_name: str, runtime_compat: dict[str, Any]) -> str:
    model_type = str(runtime_compat.get("config_model_type") or "")
    architectures = [str(item) for item in (runtime_compat.get("config_architectures") or [])]
    base = (
        f"Transformers runtime is too old for '{model_name}' "
        f"(model_type='{model_type}', architectures={architectures}). "
        "Upgrade the bootstrap stack to a model-family-capable Transformers build before using this checkpoint."
    )
    checkpoint_transformers_version = runtime_compat.get("checkpoint_transformers_version")
    if checkpoint_transformers_version:
        base += f" Checkpoint metadata advertises transformers_version={checkpoint_transformers_version}."
    if model_type == "gemma4":
        base += (
            " Gemma 4 instruction checkpoints also advertise an any-to-any conditional-generation architecture, "
            "so the current text-only AutoModelForCausalLM path may still need a processor-aware "
            "conditional-generation backend after the runtime upgrade."
        )
        python_version = str(runtime_compat.get("python") or "")
        match = re.match(r"^(\d+)\.(\d+)", python_version)
        if match is not None:
            major = int(match.group(1))
            minor = int(match.group(2))
            if (major, minor) < (3, 10):
                base += (
                    f" Current Python is {python_version}; the verified source-build upgrade path for Gemma 4 "
                    "also requires Python >=3.10."
                )
    error = runtime_compat.get("runtime_autoconfig_error")
    if error:
        base += f" Underlying error: {error}."
    return base


def ensure_text_backend_preflight(
    model_name: str,
    auto_config_cls: Any,
    *,
    backend_blocker_fn: Any = trainer_backend_preflight_block,
) -> dict[str, Any] | None:
    runtime_compat = probe_model_runtime_compat(model_name, auto_config_cls)
    if runtime_compat is None:
        return None

    runtime_error = runtime_compat.get("runtime_autoconfig_error")
    if runtime_error and runtime_autoconfig_requires_upgrade(
        str(runtime_compat.get("config_model_type") or ""),
        Exception(str(runtime_error)),
    ):
        raise SystemExit(build_runtime_upgrade_message(model_name, runtime_compat))

    backend_blocker = backend_blocker_fn(
        str(runtime_compat.get("config_model_type") or ""),
        [str(item) for item in (runtime_compat.get("config_architectures") or [])],
    )
    if backend_blocker is not None:
        raise SystemExit(backend_blocker)
    return runtime_compat


def load_causal_lm_with_text_backend_preflight(
    model_name: str,
    *,
    auto_config_cls: Any,
    auto_model_for_causal_lm_cls: Any,
    model_kwargs: dict[str, Any] | None = None,
) -> Any:
    ensure_text_backend_preflight(
        model_name,
        auto_config_cls,
        backend_blocker_fn=inference_backend_preflight_block,
    )
    return auto_model_for_causal_lm_cls.from_pretrained(model_name, **(model_kwargs or {}))


def _extract_forward_loss(outputs: Any) -> Any:
    if isinstance(outputs, dict):
        return outputs.get("loss")
    return getattr(outputs, "loss", None)


def run_text_forward_preflight(
    model: Any,
    batch: dict[str, Any],
    *,
    torch_module: Any,
    device: Any | None = None,
) -> dict[str, Any]:
    prepared_batch: dict[str, Any] = {}
    for name, value in batch.items():
        if hasattr(value, "to") and device is not None:
            prepared_batch[name] = value.to(device)
        else:
            prepared_batch[name] = value

    was_training = bool(getattr(model, "training", False))
    if hasattr(model, "eval"):
        model.eval()
    try:
        with torch_module.no_grad():
            outputs = model(**prepared_batch)
    finally:
        if hasattr(model, "train"):
            model.train(was_training)

    loss = _extract_forward_loss(outputs)
    if loss is None:
        raise ValueError("Model forward preflight did not return a loss value.")

    loss_value = float(loss.detach().float().item() if hasattr(loss, "detach") else loss)
    if not math.isfinite(loss_value):
        raise ValueError(f"Model forward preflight produced a non-finite loss: {loss_value}")

    result = {
        "model_class": model.__class__.__name__,
        "loss": loss_value,
    }
    for key in ("input_ids", "labels", "attention_mask"):
        tensor = prepared_batch.get(key)
        if hasattr(tensor, "shape"):
            result[f"{key}_shape"] = list(tensor.shape)
    return result
