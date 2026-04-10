from __future__ import annotations

import ast
from pathlib import Path

from training.text_preprocessor_backend import load_text_preprocessor_backend


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
            raise AssertionError("TokenizersBackend models should be attempted without trust_remote_code first")
        return _TokenizerStub()


class _UnusedPreTrainedTokenizerFast:
    def __init__(self, *args, **kwargs):
        raise AssertionError("fast-tokenizer fallback should not run in this path")


def test_load_text_preprocessor_backend_prefers_native_tokenizers_backend() -> None:
    _TokenizersBackendAwareAutoTokenizer.calls = []

    backend = load_text_preprocessor_backend(
        "models/OmniCoder-9B",
        _TokenizersBackendAwareAutoTokenizer,
        _AutoProcessorAlwaysFails,
        _UnusedPreTrainedTokenizerFast,
    )

    assert backend.backend_kind == "tokenizer.tokenizers_backend_native"
    assert _TokenizersBackendAwareAutoTokenizer.calls == [False]


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
