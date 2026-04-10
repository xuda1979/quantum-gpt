from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from training.model_backend import load_tokenizer_config_metadata


@dataclass
class TextPreprocessorBackend:
    render_backend: Any
    text_backend: Any
    save_backend: Any
    backend_kind: str


def supports_text_backend(candidate: Any) -> bool:
    return candidate is not None and hasattr(candidate, "__call__") and hasattr(candidate, "pad")


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


def load_tokenizers_backend_fallback(model_name: str, pretrained_tokenizer_fast_cls: Any) -> TextPreprocessorBackend | None:
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
        clean_up_tokenization_spaces=bool(tokenizer_config.get("clean_up_tokenization_spaces", False)),
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
) -> TextPreprocessorBackend:
    processor_error: Exception | None = None
    try:
        processor = auto_processor_cls.from_pretrained(model_name, trust_remote_code=True)
        processor_tokenizer = getattr(processor, "tokenizer", None)
        if supports_text_backend(processor_tokenizer):
            render_backend = processor if hasattr(processor, "apply_chat_template") else processor_tokenizer
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
        tokenizers_backend = _load_tokenizers_backend_via_autotokenizer(model_name, auto_tokenizer_cls)
        if tokenizers_backend is not None:
            return tokenizers_backend
    except Exception as exc:  # noqa: BLE001
        tokenizer_backend_error = exc

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
        if processor_error is not None:
            error_parts.append(f"AutoProcessor fallback also failed: {type(processor_error).__name__}: {processor_error}")
        raise SystemExit("Unable to load a text preprocessing backend. " + " | ".join(error_parts)) from exc


def render_messages(render_backend: Any, record: dict) -> str:
    messages = record.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError(f"Record {record.get('example_id')} has no messages")
    if hasattr(render_backend, "apply_chat_template"):
        return render_backend.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

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
    example: dict[str, Any] = {
        "input_ids": encoded["input_ids"],
        "attention_mask": encoded["attention_mask"],
        "example_id": working_record.get("example_id"),
    }
    if train_on_completions_only:
        messages = working_record.get("messages", [])
        if len(messages) >= 2 and messages[-1].get("role") == "assistant":
            prompt_text = render_messages(backend.render_backend, {"messages": messages[:-1]})
            prompt_ids = backend.text_backend(
                prompt_text,
                truncation=True,
                max_length=max_length,
                padding=False,
                return_attention_mask=False,
            )["input_ids"]
            example["prompt_token_count"] = min(len(prompt_ids), len(example["input_ids"]))
    return example


def pad_supervised_text_batch(batch: list[dict[str, Any]], text_backend: Any, torch_module: Any) -> dict[str, Any]:
    padded = text_backend.pad(
        [{"input_ids": item["input_ids"], "attention_mask": item["attention_mask"]} for item in batch],
        padding=True,
        return_tensors="pt",
    )
    labels = padded["input_ids"].clone()
    labels[padded["attention_mask"] == 0] = -100
    for row_index, item in enumerate(batch):
        prompt_token_count = item.get("prompt_token_count")
        if prompt_token_count:
            labels[row_index, :prompt_token_count] = -100
    padded["labels"] = labels
    return padded
