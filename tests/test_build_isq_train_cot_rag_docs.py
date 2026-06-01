from __future__ import annotations

import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_isq_train_cot_rag_docs.py"
SPEC = importlib.util.spec_from_file_location("build_isq_train_cot_rag_docs", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def test_renders_training_record_as_retrieval_markdown() -> None:
    record = {
        "task_id": "isqQA/isq_language/1_install",
        "task_type": "qa_concept",
        "prompt": "How do I install ISQ?",
        "difficulty": "intro",
        "category": "isq_language",
        "concept_tags": ["install", "isqc"],
        "cot_reasoning": "Find the compiler setup first.",
        "reference_answer": "Install the ISQ toolchain and use isqc.",
    }

    rendered = mod.render_record(record, ordinal=1)

    assert "isqQA/isq_language/1_install" in rendered
    assert "How do I install ISQ?" in rendered
    assert "Find the compiler setup first." in rendered
    assert "Install the ISQ toolchain" in rendered
    assert "`isqc`" in rendered


def test_writes_category_shards_and_manifest(tmp_path: Path) -> None:
    records = [
        {
            "task_id": "a",
            "category": "isq_language",
            "prompt": "Install ISQ?",
            "reference_answer": "Use isqc.",
        },
        {
            "task_id": "b",
            "category": "quantum_algorithms",
            "prompt": "Explain Grover.",
            "reference_answer": "Grover uses an oracle and diffusion.",
        },
    ]

    manifest = mod.write_docs(records, tmp_path, records_per_file=1, clean=True)

    assert manifest["record_count"] == 2
    assert manifest["category_count"] == 2
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "isq_language-001.md").exists()
    assert (tmp_path / "quantum_algorithms-001.md").exists()
    loaded = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert loaded["categories"]["isq_language"] == 1
