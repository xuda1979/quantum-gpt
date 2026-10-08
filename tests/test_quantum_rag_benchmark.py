from __future__ import annotations

import json
from pathlib import Path

from quantum_rag.corpus import build_chunks_from_roots
from quantum_rag.index import QuantumRAGIndex
from scripts.score_quantum_rag_retrieval import score_example


def test_retrieval_benchmark_example_hits_expected_source(tmp_path: Path) -> None:
    root = tmp_path / "corpus"
    root.mkdir()
    project = root / "PROJECT.md"
    project.write_text(
        "\n".join(
            [
                "Local validation is mandatory before remote training.",
                "Transfer code via S3 scripts, then run remote Huanxin shell commands.",
            ]
        ),
        encoding="utf-8",
    )
    note = root / "note.md"
    note.write_text("This note is unrelated to remote training.", encoding="utf-8")

    chunks = build_chunks_from_roots([root], chunk_size=300, chunk_overlap=50, min_chunk_chars=20)
    index = QuantumRAGIndex.build(chunks, max_features=512, dense_components=8)
    item = {
        "id": "remote_rule",
        "query": "How should code be moved before remote training?",
        "expected_source_substrings": ["PROJECT.md"],
    }
    result = score_example(
        item,
        index=index,
        top_k=3,
        alpha=0.55,
        query_expansion_enabled=True,
        max_chunks_per_source=1,
        exclude_source_substrings=[],
    )
    assert result.hit_at_k
    assert result.first_hit_rank == 1


def test_benchmark_manifest_is_valid_json() -> None:
    path = Path("evals/benchmarks/quantum_rag_retrieval_v1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert payload
    for item in payload:
        assert "id" in item
        assert "query" in item
        assert "expected_source_substrings" in item
        assert item["expected_source_substrings"]
