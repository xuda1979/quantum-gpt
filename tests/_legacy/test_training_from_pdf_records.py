from __future__ import annotations

import json
from pathlib import Path
from typing import List

import train_peft
import train_sft


class DummyTokenizer:
    """A minimal tokenizer that records the raw texts passed in."""

    def __init__(self) -> None:
        self.invocations: List[List[str]] = []

    def __call__(self, texts, *_, **__):  # type: ignore[override]
        self.invocations.append(list(texts))
        return {"input_ids": []}


def _write_sample(tmp_path: Path, include_analysis: bool) -> Path:
    record = {
        "prompt": "Summarise the quantum paper chunk.",
        "code": "Quantum circuits enable novel algorithms.",
        "metadata": {"source": "paper.pdf", "chunk_index": 1},
    }
    if include_analysis:
        record["analysis"] = "Think step by step before answering."

    path = tmp_path / "sample.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False)
        handle.write("\n")
    return path


def test_train_sft_preserves_analysis(tmp_path: Path):
    path = _write_sample(tmp_path, include_analysis=True)
    samples = train_sft.load_jsonl(str(path))
    assert samples == [
        {
            "prompt": "Summarise the quantum paper chunk.",
            "code": "Quantum circuits enable novel algorithms.",
            "analysis": "Think step by step before answering.",
        }
    ]

    tokenizer = DummyTokenizer()
    train_sft.prepare_dataset(samples, tokenizer)
    assert tokenizer.invocations, "Tokenizer should receive the formatted text"
    formatted = tokenizer.invocations[0][0]
    assert "Think step by step" in formatted
    assert formatted.endswith("<|assistant|>Think step by step before answering.\n\nQuantum circuits enable novel algorithms.<|end|>")


def test_train_peft_builds_text_with_analysis(tmp_path: Path):
    path = _write_sample(tmp_path, include_analysis=True)
    samples = train_peft.load_jsonl(str(path))
    assert samples[0]["analysis"] == "Think step by step before answering."
    text = train_peft.build_training_text(samples[0])
    assert "Think step by step" in text
    assert text.endswith("<|assistant|>Think step by step before answering.\n\nQuantum circuits enable novel algorithms.<|end|>")


def test_train_peft_builds_text_without_analysis(tmp_path: Path):
    path = _write_sample(tmp_path, include_analysis=False)
    sample = train_peft.load_jsonl(str(path))[0]
    text = train_peft.build_training_text(sample)
    assert "Think step by step" not in text
    assert text.endswith("<|assistant|>Quantum circuits enable novel algorithms.<|end|>")
