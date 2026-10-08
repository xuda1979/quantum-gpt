from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from training.model_backend import load_model_config_metadata, load_tokenizer_config_metadata


@dataclass
class TextPreprocessorBackend:
    render_backend: Any
    text_backend: Any
    save_backend: Any
    backend_kind: str


def supports_text_backend(candidate: Any) -> bool:
    return candidate is not None and callable(candidate) and hasattr(candidate, "pad")


def _load_tokenizers_backend_via_autotokenizer(
    model_name: str,
    auto_tokenizer_cls: Any,
) -> TextPreprocessorBackend | None:
    tokenizer_config = load_tokenizer_config_metadata(model_name)
    if tokenizer_config.get("tokenizer_class") != "TokenizersBackend":
        return None

    tokenizer = auto_tokenizer_cls.from_pretrained(model_name, trust_remote_code=False)
    return TextPreprocessorBackend(
        render_backend=tokenizer,
        text_backend=tokenizer,
        save_backend=tokenizer,
        backend_kind="tokenizer.tokenizers_backend_native",
    )


def _load_model_chat_template(model_name: str) -> str | None:
    chat_template_path = Path(model_name) / "chat_template.jinja"
    if not chat_template_path.exists():
        return None
    return chat_template_path.read_text(encoding="utf-8")


def _load_model_specific_tokenizers_backend(
    model_name: str,
    *,
    explicit_tokenizer_fast_classes: tuple[Any, ...] | None = None,
) -> TextPreprocessorBackend | None:
    tokenizer_config = load_tokenizer_config_metadata(model_name)
    if tokenizer_config.get("tokenizer_class") != "TokenizersBackend":
        return None

    candidate_classes = list(explicit_tokenizer_fast_classes or ())
    if not candidate_classes:
        model_config = load_model_config_metadata(model_name)
        model_type = str(model_config.get("model_type") or "")
        if model_type.startswith("qwen"):
            from transformers import Qwen2TokenizerFast

            candidate_classes.append(Qwen2TokenizerFast)

    if not candidate_classes:
        return None

    chat_template = _load_model_chat_template(model_name)
    last_error: Exception | None = None
    for tokenizer_cls in candidate_classes:
        try:
            tokenizer = tokenizer_cls.from_pretrained(model_name)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue
        if chat_template and not getattr(tokenizer, "chat_template", None):
            tokenizer.chat_template = chat_template
        return TextPreprocessorBackend(
            render_backend=tokenizer,
            text_backend=tokenizer,
            save_backend=tokenizer,
            backend_kind=f"tokenizer.{tokenizer.__class__.__name__}",
        )

    if last_error is not None:
        raise last_error
    return None


def load_tokenizers_backend_fallback(
    model_name: str, pretrained_tokenizer_fast_cls: Any
) -> TextPreprocessorBackend | None:
    tokenizer_config = load_tokenizer_config_metadata(model_name)
    if tokenizer_config.get("tokenizer_class") != "TokenizersBackend":
        return None

    tokenizer_path = Path(model_name) / "tokenizer.json"
    if not tokenizer_path.exists():
        return None

    additional_special_tokens = []
    for key in (
        "image_token",
        "video_token",
        "vision_bos_token",
        "vision_eos_token",
        "audio_bos_token",
        "audio_eos_token",
        "audio_token",
    ):
        value = tokenizer_config.get(key)
        if value and value not in additional_special_tokens:
            additional_special_tokens.append(value)

    tokenizer = pretrained_tokenizer_fast_cls(
        tokenizer_file=str(tokenizer_path),
        pad_token=tokenizer_config.get("pad_token"),
        eos_token=tokenizer_config.get("eos_token"),
        additional_special_tokens=additional_special_tokens or None,
        clean_up_tokenization_spaces=bool(
            tokenizer_config.get("clean_up_tokenization_spaces", False)
        ),
        model_max_length=int(tokenizer_config.get("model_max_length", 262144)),
    )
    return TextPreprocessorBackend(
        render_backend=tokenizer,
        text_backend=tokenizer,
        save_backend=tokenizer,
        backend_kind="pretrained_tokenizer_fast_fallback",
    )


def load_text_preprocessor_backend(
    model_name: str,
    auto_tokenizer_cls: Any,
    auto_processor_cls: Any,
    pretrained_tokenizer_fast_cls: Any,
    explicit_tokenizer_fast_classes: tuple[Any, ...] | None = None,
) -> TextPreprocessorBackend:
    processor_error: Exception | None = None
    try:
        processor = auto_processor_cls.from_pretrained(model_name, trust_remote_code=True)
        processor_tokenizer = getattr(processor, "tokenizer", None)
        if supports_text_backend(processor_tokenizer):
            render_backend = (
                processor if hasattr(processor, "apply_chat_template") else processor_tokenizer
            )
            return TextPreprocessorBackend(
                render_backend=render_backend,
                text_backend=processor_tokenizer,
                save_backend=processor,
                backend_kind="processor.tokenizer",
            )
    except Exception as exc:  # noqa: BLE001
        processor_error = exc

    tokenizer_backend_error: Exception | None = None
    try:
        tokenizers_backend = _load_tokenizers_backend_via_autotokenizer(
            model_name, auto_tokenizer_cls
        )
        if tokenizers_backend is not None:
            return tokenizers_backend
    except Exception as exc:  # noqa: BLE001
        tokenizer_backend_error = exc

    explicit_tokenizer_error: Exception | None = None
    try:
        explicit_tokenizer_backend = _load_model_specific_tokenizers_backend(
            model_name,
            explicit_tokenizer_fast_classes=explicit_tokenizer_fast_classes,
        )
        if explicit_tokenizer_backend is not None:
            return explicit_tokenizer_backend
    except Exception as exc:  # noqa: BLE001
        explicit_tokenizer_error = exc

    try:
        tokenizer = auto_tokenizer_cls.from_pretrained(model_name, trust_remote_code=True)
        return TextPreprocessorBackend(
            render_backend=tokenizer,
            text_backend=tokenizer,
            save_backend=tokenizer,
            backend_kind="tokenizer",
        )
    except Exception as exc:  # noqa: BLE001
        fallback = load_tokenizers_backend_fallback(model_name, pretrained_tokenizer_fast_cls)
        if fallback is not None:
            return fallback
        error_parts = [f"AutoTokenizer load failed: {type(exc).__name__}: {exc}"]
        if tokenizer_backend_error is not None:
            error_parts.append(
                "TokenizersBackend native load failed: "
                f"{type(tokenizer_backend_error).__name__}: {tokenizer_backend_error}"
            )
        if explicit_tokenizer_error is not None:
            error_parts.append(
                "Model-specific tokenizer fallback failed: "
                f"{type(explicit_tokenizer_error).__name__}: {explicit_tokenizer_error}"
            )
        if processor_error is not None:
            error_parts.append(
                f"AutoProcessor fallback also failed: {type(processor_error).__name__}: {processor_error}"
            )
        raise SystemExit(
            "Unable to load a text preprocessing backend. " + " | ".join(error_parts)
        ) from exc


def render_messages(render_backend: Any, record: dict) -> str:
    messages = record.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError(f"Record {record.get('example_id')} has no messages")
    if hasattr(render_backend, "apply_chat_template"):
        return render_backend.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )

    parts = []
    for message in messages:
        role = str(message.get("role", "user")).upper()
        content = str(message.get("content", ""))
        parts.append(f"{role}: {content}")
    return "\n\n".join(parts)


def build_supervised_text_example(
    record: dict,
    backend: TextPreprocessorBackend,
    max_length: int,
    *,
    train_on_completions_only: bool = False,
) -> dict[str, Any]:
    working_record = copy.deepcopy(record)
    full_text = render_messages(backend.render_backend, working_record)
    encoded = backend.text_backend(
        full_text,
        truncation=True,
        max_length=max_length,
        padding=False,
        return_attention_mask=True,
    )
    input_ids = list(encoded["input_ids"])
    attention_mask = list(encoded["attention_mask"])
    example: dict[str, Any] = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "example_id": working_record.get("example_id"),
    }
    if train_on_completions_only:
        messages = working_record.get("messages", [])
        if len(messages) >= 2 and messages[-1].get("role") == "assistant":
            prompt_text = render_messages(backend.render_backend, {"messages": messages[:-1]})
            try:
                completion_text = render_messages(
                    backend.render_backend, {"messages": [messages[-1]]}
                )
            except Exception:
                if full_text.startswith(prompt_text):
                    completion_text = full_text[len(prompt_text) :]
                else:
                    try:
                        dummy_messages = [{"role": "user", "content": "hello"}] + [messages[-1]]
                        dummy_text = render_messages(
                            backend.render_backend, {"messages": dummy_messages}
                        )
                        dummy_prompt = render_messages(
                            backend.render_backend,
                            {"messages": [{"role": "user", "content": "hello"}]},
                        )
                        if dummy_text.startswith(dummy_prompt):
                            completion_text = dummy_text[len(dummy_prompt) :]
                        else:
                            completion_text = messages[-1].get("content", "")
                    except Exception:
                        completion_text = messages[-1].get("content", "")
            prompt_ids = list(
                backend.text_backend(
                    prompt_text,
                    truncation=True,
                    max_length=max_length,
                    padding=False,
                    return_attention_mask=False,
                )["input_ids"]
            )
            completion_ids = list(
                backend.text_backend(
                    completion_text,
                    truncation=True,
                    max_length=max_length,
                    padding=False,
                    return_attention_mask=False,
                )["input_ids"]
            )
            prompt_token_count = min(len(prompt_ids), len(input_ids))
            if prompt_token_count >= len(input_ids) and completion_ids:
                completion_keep = min(len(completion_ids), max_length)
                prompt_keep = max(0, max_length - completion_keep)
                rebuilt_ids = (
                    prompt_ids[-prompt_keep:] + completion_ids[-completion_keep:]
                    if prompt_keep
                    else completion_ids[-completion_keep:]
                )
                input_ids = rebuilt_ids[-max_length:]
                attention_mask = [1] * len(input_ids)
                prompt_token_count = max(0, len(input_ids) - min(completion_keep, len(input_ids)))
                example["input_ids"] = input_ids
                example["attention_mask"] = attention_mask
            if prompt_token_count < len(input_ids):
                example["prompt_token_count"] = prompt_token_count
    return example


def pad_supervised_text_batch(
    batch: list[dict[str, Any]],
    text_backend: Any,
    torch_module: Any,
    *,
    add_mm_token_type_ids: bool = False,
    pad_to_max_length: int | None = None,
) -> dict[str, Any]:
    if pad_to_max_length and pad_to_max_length > 0:
        # Static padding to a fixed length keeps tensor shapes constant across
        # every step. This is critical on Ascend NPU hosts with few CPU cores,
        # where dynamic (per-batch) shapes force the TBE compiler to recompile
        # kernels for each new sequence length, stalling training.
        pad_kwargs = {"padding": "max_length", "max_length": int(pad_to_max_length)}
    else:
        pad_kwargs = {"padding": True}
    padded = text_backend.pad(
        [
            {"input_ids": item["input_ids"], "attention_mask": item["attention_mask"]}
            for item in batch
        ],
        return_tensors="pt",
        **pad_kwargs,
    )
    labels = padded["input_ids"].clone()
    labels[padded["attention_mask"] == 0] = -100
    for row_index, item in enumerate(batch):
        prompt_token_count = item.get("prompt_token_count")
        if prompt_token_count:
            labels[row_index, :prompt_token_count] = -100
    padded["labels"] = labels
    if add_mm_token_type_ids:
        # Gemma 4 requires mm_token_type_ids during training; all-zero means text-only (no vision tokens).
        padded["mm_token_type_ids"] = torch_module.zeros_like(padded["input_ids"])
    return padded
