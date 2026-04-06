from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

import tools.pdf_to_sft as pdf_to_sft


@pytest.fixture()
def sample_text():
    return (
        "Quantum computing enables new algorithms and error correction schemes. "
        "This paragraph ends before references."
    )


def test_clean_page_text_merges_hyphenation():
    text = "Quantum-\n computing \n\n\t advances"
    cleaned = pdf_to_sft._clean_page_text(text)
    assert cleaned == "Quantumcomputing\n\nadvances"


@pytest.mark.parametrize(
    "chunk_size, chunk_overlap",
    [
        (10, 2),
        (8, 0),
    ],
)
def test_chunk_text_produces_expected_overlap(chunk_size, chunk_overlap):
    text = "0123456789" * 2
    chunks = pdf_to_sft.chunk_text(text, chunk_size, chunk_overlap)
    assert chunks, "chunk_text should produce output"
    first_chunk, _start, _end = chunks[0]
    assert first_chunk == text[: len(first_chunk)]
    assert len(first_chunk) <= chunk_size

    for (chunk, _start, end), (next_chunk, next_start, _next_end) in zip(chunks, chunks[1:]):
        assert len(chunk) <= chunk_size
        assert next_start == max(0, end - chunk_overlap)
        assert next_chunk.startswith(text[next_start:next_start + len(next_chunk)])


@pytest.mark.parametrize(
    "chunk_size, chunk_overlap",
    [(0, 1), (10, 10), (5, -1)],
)
def test_chunk_text_validation(chunk_size, chunk_overlap):
    with pytest.raises(ValueError):
        pdf_to_sft.chunk_text("hello", chunk_size, chunk_overlap)


def test_strip_reference_section_removes_tail():
    body = "Intro text\nMore content\nReferences\n[1] Citation"
    assert pdf_to_sft._strip_reference_section(body) == "Intro text\nMore content"


def test_strip_reference_section_keeps_early_heading():
    body = "References\nBody text that follows."
    assert pdf_to_sft._strip_reference_section(body) == body


def test_iter_pdf_files_discovers_nested_pdfs(tmp_path: Path):
    root = tmp_path / "papers"
    root.mkdir()
    first = root / "paper1.pdf"
    first.write_text("dummy")
    subdir = root / "nested"
    subdir.mkdir()
    second = subdir / "paper2.PDF"
    second.write_text("dummy")
    unrelated = root / "notes.txt"
    unrelated.write_text("nope")

    discovered = list(pdf_to_sft.iter_pdf_files([root]))
    assert set(discovered) == {first, second}


def test_build_records_uses_templates(monkeypatch, tmp_path: Path, sample_text: str):
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_text("irrelevant content")

    def fake_extract(path: Path) -> str:
        assert path == pdf_path
        return sample_text

    monkeypatch.setattr(pdf_to_sft, "extract_text_from_pdf", fake_extract)

    records = list(
        pdf_to_sft.build_records(
            pdf_paths=[pdf_path],
            chunk_size=64,
            chunk_overlap=16,
            instruction_template="Summarise chunk {index}: {chunk}",
            target_template="Chunk {index}: {chunk}",
            analysis_template="Notes {index}",
            min_chunk_length=10,
            strip_references=True,
        )
    )

    assert records, "Expected at least one record from sample text"
    first = records[0]
    assert first["prompt"].startswith("Summarise chunk 1:")
    assert first["code"].startswith("Chunk 1:")
    assert first["analysis"] == "Notes 1"
    assert first["metadata"]["source"] == str(pdf_path)
    assert first["metadata"]["chunk_index"] == 1


@pytest.mark.parametrize("analysis_template", ["Analysis {index}", None])
def test_process_single_pdf_returns_list(monkeypatch, tmp_path: Path, sample_text: str, analysis_template):
    pdf_path = tmp_path / "single.pdf"
    pdf_path.write_text("irrelevant")

    monkeypatch.setattr(pdf_to_sft, "extract_text_from_pdf", lambda _path: sample_text)

    records = pdf_to_sft._process_single_pdf(
        pdf_path,
        chunk_size=32,
        chunk_overlap=0,
        instruction_template="Prompt {index}",
        target_template="Target {index}",
        analysis_template=analysis_template,
        min_chunk_length=10,
        strip_references=False,
    )

    assert isinstance(records, list)
    assert records
    assert all(record["metadata"]["source"] == str(pdf_path) for record in records)
    if analysis_template:
        assert all("analysis" in record for record in records)
    else:
        assert all("analysis" not in record for record in records)


def test_build_records_respects_min_chunk_length(monkeypatch, tmp_path: Path):
    pdf_path = tmp_path / "short.pdf"
    pdf_path.write_text("irrelevant")

    monkeypatch.setattr(pdf_to_sft, "extract_text_from_pdf", lambda _path: "short text")

    records = list(
        pdf_to_sft.build_records(
            pdf_paths=[pdf_path],
            chunk_size=64,
            chunk_overlap=0,
            instruction_template="Prompt",
            target_template="Target",
            analysis_template=None,
            min_chunk_length=20,
            strip_references=False,
        )
    )

    assert records == []
