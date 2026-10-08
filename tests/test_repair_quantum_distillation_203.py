from __future__ import annotations

import json
from pathlib import Path

from scripts import repair_quantum_distillation_203 as repair

SOURCE = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203/all_chatml.jsonl"
)


def test_append_question_suffix_once() -> None:
    prompt = "请实现一个贝尔态电路。"
    fixed = repair.append_question_suffix(prompt, repair.QUESTION_SUFFIX)
    assert fixed.endswith(repair.QUESTION_SUFFIX)
    assert repair.append_question_suffix(fixed, repair.QUESTION_SUFFIX) == fixed


def test_repair_answer_appends_smoke_for_bare_python() -> None:
    bare = "def foo(x):\n    return x + 1\n"
    repaired, changed = repair.repair_answer(bare)
    assert changed is True
    assert 'if __name__ == "__main__"' in repaired
    assert "foo(" in repaired


def test_repair_dataset_manifest_and_row_shape(tmp_path: Path) -> None:
    out_dir = tmp_path / "repaired"
    assert SOURCE.exists()

    data = [
        json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    row = data[1]
    repaired_row, changed = repair.repair_row(row, repair.QUESTION_SUFFIX)

    assert repaired_row["messages"][1]["content"].endswith(repair.QUESTION_SUFFIX)
    assert changed["prompt_suffix"] is True
    assert repaired_row["messages"][2]["content"]

    answer = repaired_row["messages"][2]["content"]
    if "def " in answer and "if __name__" not in answer:
        raise AssertionError("expected repaired python answer to include a runnable smoke block")

    payload = [repaired_row]
    repair.write_jsonl(out_dir / "all_chatml.jsonl", payload)
    manifest = {
        "ok": True,
        "total_rows": len(payload),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert (out_dir / "all_chatml.jsonl").exists()
    assert (out_dir / "manifest.json").exists()
