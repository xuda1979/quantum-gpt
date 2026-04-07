from pathlib import Path
import json

from tools import prepare_pdf_dataset


def _read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def test_prepare_datasets_writes_expected_files(tmp_path, monkeypatch):
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    dummy_pdf = pdf_dir / "paper.pdf"
    dummy_pdf.write_text("placeholder", encoding="utf-8")

    records = [
        {"prompt": f"Prompt {i}", "code": f"Code {i}"} for i in range(4)
    ]

    monkeypatch.setattr(
        prepare_pdf_dataset.pdf_to_sft,
        "iter_pdf_files",
        lambda _: [dummy_pdf],
    )
    monkeypatch.setattr(
        prepare_pdf_dataset,
        "_collect_records",
        lambda *args, **kwargs: list(records),
    )

    output_dir = tmp_path / "processed"
    train_path, valid_path = prepare_pdf_dataset.prepare_datasets(
        pdf_dir,
        output_dir,
        dataset_name="quantum",
        train_ratio=0.5,
        seed=123,
    )

    assert train_path.exists()
    assert valid_path and valid_path.exists()
    all_path = output_dir / "quantum_all.jsonl"
    assert all_path.exists()

    train_records = _read_jsonl(train_path)
    valid_records = _read_jsonl(valid_path)
    all_records = _read_jsonl(all_path)

    assert len(train_records) + len(valid_records) == len(records)
    assert len(all_records) == len(records)
    assert {item["prompt"] for item in all_records} == {item["prompt"] for item in records}
