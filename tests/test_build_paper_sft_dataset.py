from __future__ import annotations

import json
from pathlib import Path

from scripts.build_paper_sft_dataset import build_messages_from_record, prepare_text_documents


def test_build_messages_from_record_preserves_analysis_and_metadata() -> None:
    record = {
        "prompt": "Summarise the quantum paper chunk.",
        "code": "Quantum circuits enable novel algorithms.",
        "analysis": "Think step by step before answering.",
        "metadata": {"source": "paper.pdf", "chunk_index": 1},
    }
    item = build_messages_from_record(record)
    assert item["messages"][1]["content"] == "Summarise the quantum paper chunk."
    assert "Think step by step" in item["messages"][2]["content"]
    assert "Quantum circuits enable novel algorithms." in item["messages"][2]["content"]
    assert item["metadata"]["source"] == "paper.pdf"


def test_prepare_text_documents_writes_message_jsonl(tmp_path: Path) -> None:
    paper_path = tmp_path / "quantum-paper.tex"
    paper_path.write_text(
        "Quantum computing enables new algorithms and error correction schemes. " * 40,
        encoding="utf-8",
    )
    train_path, valid_path = prepare_text_documents(
        [paper_path],
        tmp_path / "out",
        "quantum_papers",
        chunk_size=256,
        chunk_overlap=32,
        min_chunk_length=50,
        train_ratio=0.5,
        seed=7,
    )
    assert train_path.exists()
    rows = [json.loads(line) for line in train_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows
    assert rows[0]["messages"][0]["role"] == "system"
    assert rows[0]["messages"][1]["role"] == "user"
    assert rows[0]["messages"][2]["role"] == "assistant"
    if valid_path is not None:
        assert valid_path.exists()
