from __future__ import annotations

from scripts.verify_holdout_dataset import summarize_rows


def test_summarize_rows_counts_tasks_and_prompt_families() -> None:
    rows = [
        {
            "example_id": "a",
            "metadata": {"task_id": "t1", "prompt_family": "p1", "domain": "quantum"},
        },
        {
            "example_id": "b",
            "metadata": {"task_id": "t1", "prompt_family": "p2", "domain": "quantum"},
        },
        {
            "example_id": "c",
            "metadata": {"task_id": "t2", "prompt_family": "p2", "domain": "software"},
        },
    ]
    summary = summarize_rows(rows)
    assert summary["count"] == 3
    assert summary["unique_example_ids"] == 3
    assert summary["duplicate_example_ids"] == []
    assert summary["task_counts"] == {"t1": 2, "t2": 1}
    assert summary["prompt_family_counts"] == {"p1": 1, "p2": 2}
    assert summary["domain_counts"] == {"quantum": 2, "software": 1}


def test_summarize_rows_detects_duplicate_example_ids() -> None:
    rows = [
        {"example_id": "dup", "metadata": {"task_id": "t1", "prompt_family": "p1", "domain": "quantum"}},
        {"example_id": "dup", "metadata": {"task_id": "t2", "prompt_family": "p2", "domain": "quantum"}},
    ]
    summary = summarize_rows(rows)
    assert summary["duplicate_example_ids"] == ["dup"]
