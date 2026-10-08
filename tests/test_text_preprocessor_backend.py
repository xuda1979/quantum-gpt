from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from training.text_preprocessor_backend import (
    TextPreprocessorBackend,
    build_supervised_text_example,
    load_text_preprocessor_backend,
)


class _TokenizerStub:
    def __call__(self, *args, **kwargs):
        return {"input_ids": [1], "attention_mask": [1]}

    def pad(self, *args, **kwargs):
        return {"input_ids": [[1]], "attention_mask": [[1]]}


class _AutoProcessorAlwaysFails:
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        raise RuntimeError("processor unavailable")


class _TokenizersBackendAwareAutoTokenizer:
    calls: list[bool] = []

    @classmethod
    def from_pretrained(cls, model_name: str, *, trust_remote_code: bool):
        cls.calls.append(trust_remote_code)
        if trust_remote_code:
            raise AssertionError(
                "TokenizersBackend models should be attempted without trust_remote_code first"
            )
        return _TokenizerStub()


class _UnusedPreTrainedTokenizerFast:
    def __init__(self, *args, **kwargs):
        raise AssertionError("fast-tokenizer fallback should not run in this path")


class _TokenizersBackendAlwaysFailsAutoTokenizer:
    calls: list[bool] = []

    @classmethod
    def from_pretrained(cls, model_name: str, *, trust_remote_code: bool):
        cls.calls.append(trust_remote_code)
        raise ValueError(f"auto tokenizer unavailable for trust_remote_code={trust_remote_code}")


class _ExplicitQwenTokenizerStub(_TokenizerStub):
    calls: list[str] = []

    @classmethod
    def from_pretrained(cls, model_name: str, **kwargs):
        cls.calls.append(model_name)
        tokenizer = cls()
        tokenizer.chat_template = None
        return tokenizer


class _SpaceTokenizer:
    pad_token = "<pad>"
    eos_token = "</s>"
    padding_side = "right"

    def __call__(self, text, **kwargs):
        tokens = str(text).split()
        max_length = kwargs.get("max_length")
        if kwargs.get("truncation") and max_length:
            tokens = tokens[-int(max_length) :]
        ids = [abs(hash(token)) % 10000 + 1 for token in tokens]
        return {"input_ids": ids, "attention_mask": [1] * len(ids)}

    def pad(self, batch, *, padding=True, return_tensors="pt"):
        import torch

        max_len = max(len(item["input_ids"]) for item in batch)
        input_ids = []
        attention = []
        for item in batch:
            pad_len = max_len - len(item["input_ids"])
            input_ids.append(item["input_ids"] + [0] * pad_len)
            attention.append(item["attention_mask"] + [0] * pad_len)
        return {"input_ids": torch.tensor(input_ids), "attention_mask": torch.tensor(attention)}


class _SimpleRenderer:
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        return " ".join(f"{message['role']}: {message['content']}" for message in messages)


def test_load_text_preprocessor_backend_prefers_native_tokenizers_backend() -> None:
    if not Path("models/OmniCoder-9B/tokenizer_config.json").exists():
        pytest.skip("local OmniCoder tokenizer snapshot is not present")
    _TokenizersBackendAwareAutoTokenizer.calls = []

    backend = load_text_preprocessor_backend(
        "models/OmniCoder-9B",
        _TokenizersBackendAwareAutoTokenizer,
        _AutoProcessorAlwaysFails,
        _UnusedPreTrainedTokenizerFast,
    )

    assert backend.backend_kind == "tokenizer.tokenizers_backend_native"
    assert _TokenizersBackendAwareAutoTokenizer.calls == [False]


def test_load_text_preprocessor_backend_uses_model_specific_tokenizer_when_auto_fails() -> None:
    if not Path("models/OmniCoder-9B/tokenizer_config.json").exists():
        pytest.skip("local OmniCoder tokenizer snapshot is not present")
    _TokenizersBackendAlwaysFailsAutoTokenizer.calls = []
    _ExplicitQwenTokenizerStub.calls = []

    backend = load_text_preprocessor_backend(
        "models/OmniCoder-9B",
        _TokenizersBackendAlwaysFailsAutoTokenizer,
        _AutoProcessorAlwaysFails,
        _UnusedPreTrainedTokenizerFast,
        explicit_tokenizer_fast_classes=(_ExplicitQwenTokenizerStub,),
    )

    assert backend.backend_kind == "tokenizer._ExplicitQwenTokenizerStub"
    assert _TokenizersBackendAlwaysFailsAutoTokenizer.calls == [False]
    assert _ExplicitQwenTokenizerStub.calls == ["models/OmniCoder-9B"]
    assert backend.text_backend.chat_template


def test_run_hf_pass1_eval_does_not_import_peft_at_module_top_level() -> None:
    for script_path in (
        "scripts/run_hf_pass1_eval.py",
        "scripts/serve_openai_chat_adapter.py",
        "scripts/export_merged_peft_model.py",
    ):
        source = Path(script_path).read_text(encoding="utf-8")
        module = ast.parse(source)

        top_level_peft_imports = [
            node
            for node in module.body
            if isinstance(node, ast.ImportFrom) and node.module == "peft"
        ]

        assert top_level_peft_imports == []


def test_completion_only_truncation_preserves_trainable_labels() -> None:
    backend = TextPreprocessorBackend(
        render_backend=_SimpleRenderer(),
        text_backend=_SpaceTokenizer(),
        save_backend=_SimpleRenderer(),
        backend_kind="stub",
    )
    record = {
        "example_id": "long_prompt",
        "messages": [
            {"role": "user", "content": " ".join(f"prompt{i}" for i in range(200))},
            {"role": "assistant", "content": "answer token"},
        ],
    }

    example = build_supervised_text_example(record, backend, 8, train_on_completions_only=True)

    assert example["prompt_token_count"] < len(example["input_ids"])
    assert len(example["input_ids"]) <= 8
    assert len(example["input_ids"]) - example["prompt_token_count"] > 0


def test_chat_sft_dataset_skips_empty_completion_examples_after_truncation(tmp_path: Path) -> None:
    from training.qwen_sft_peft import ChatSftDataset

    class SelectiveEmptyCompletionTokenizer(_SpaceTokenizer):
        def __call__(self, text, **kwargs):
            if "drop_completion" in str(text):
                return {"input_ids": [], "attention_mask": []}
            return super().__call__(text, **kwargs)

    backend = TextPreprocessorBackend(
        render_backend=_SimpleRenderer(),
        text_backend=SelectiveEmptyCompletionTokenizer(),
        save_backend=_SimpleRenderer(),
        backend_kind="stub",
    )
    dataset_path = tmp_path / "train.jsonl"
    rows = [
        {
            "example_id": "too_long_prompt",
            "format": "chat-sft-v1",
            "messages": [
                {"role": "user", "content": " ".join(f"prompt{i}" for i in range(200))},
                {"role": "assistant", "content": "drop_completion"},
            ],
        },
        {
            "example_id": "usable",
            "format": "chat-sft-v1",
            "messages": [
                {"role": "user", "content": "debug circuit"},
                {"role": "assistant", "content": "fixed"},
            ],
        },
    ]
    dataset_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    dataset = ChatSftDataset(dataset_path, backend, 8, train_on_completions_only=True)

    assert len(dataset) == 1
    assert dataset[0]["example_id"] == "usable"
    assert dataset.skipped_empty_completion_examples == ["too_long_prompt"]
