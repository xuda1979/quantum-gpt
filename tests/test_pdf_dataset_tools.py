from __future__ import annotations

import json
from pathlib import Path

from tools import pdf_to_sft, prepare_pdf_dataset


def test_clean_page_text_merges_hyphenation() -> None:
    text = "Quantum-\n computing \n\n\t advances"
    assert pdf_to_sft._clean_page_text(text) == "Quantumcomputing\n\nadvances"


def test_strip_reference_section_removes_tail() -> None:
    body = "Intro text\nMore content\nReferences\n[1] Citation"
    assert pdf_to_sft._strip_reference_section(body) == "Intro text\nMore content"


def test_chunk_text_validation() -> None:
    for chunk_size, chunk_overlap in [(0, 1), (10, 10), (5, -1)]:
        try:
            pdf_to_sft.chunk_text("hello", chunk_size, chunk_overlap)
        except ValueError:
            continue
        raise AssertionError("Expected ValueError for invalid chunk configuration")


def test_iter_pdf_files_discovers_nested_pdfs(tmp_path: Path) -> None:
    root = tmp_path / "papers"
    root.mkdir()
    first = root / "paper1.pdf"
    first.write_text("dummy")
    nested = root / "nested"
    nested.mkdir()
    second = nested / "paper2.PDF"
    second.write_text("dummy")
    assert set(pdf_to_sft.iter_pdf_files([root])) == {first, second}


def test_prepare_datasets_writes_expected_files(tmp_path: Path, monkeypatch) -> None:
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    dummy_pdf = pdf_dir / "paper.pdf"
    dummy_pdf.write_text("placeholder", encoding="utf-8")

    records = [{"prompt": f"Prompt {index}", "code": f"Code {index}"} for index in range(4)]

    monkeypatch.setattr(prepare_pdf_dataset.pdf_to_sft, "iter_pdf_files", lambda _roots: [dummy_pdf])
    monkeypatch.setattr(prepare_pdf_dataset, "_collect_records", lambda *args, **kwargs: list(records))

    train_path, valid_path = prepare_pdf_dataset.prepare_datasets(
        pdf_dir,
        tmp_path / "processed",
        dataset_name="quantum",
        train_ratio=0.5,
        seed=123,
    )
    assert train_path.exists()
    assert valid_path is not None and valid_path.exists()
    all_path = tmp_path / "processed" / "quantum_all.jsonl"
    assert all_path.exists()
    all_rows = [json.loads(line) for line in all_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(all_rows) == len(records)
