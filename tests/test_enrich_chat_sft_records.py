from __future__ import annotations

import json
from pathlib import Path

from scripts.enrich_chat_sft_records import enrich_record


def test_enrich_record_derives_interface_behavior_and_detail_budget(tmp_path: Path) -> None:
    task_dir = tmp_path / "evals" / "tasks" / "quantum" / "sample_task"
    task_dir.mkdir(parents=True)
    (task_dir / "candidate.py").write_text(
        "def solve(theta: float) -> int:\n    return 1\n",
        encoding="utf-8",
    )
    (task_dir / "tests.py").write_text(
        "\n".join(
            [
                "# Test returns the expected phase bucket",
                "details = []",
                "details.append('solve should map 0.25 to bucket 2')",
                "details.append('Preserve the solve(theta) interface')",
            ]
        ),
        encoding="utf-8",
    )
    (task_dir / "task.json").write_text(
        json.dumps(
            {
                "id": "sample_task",
                "domain": "quantum",
                "category": "algorithm_implementation",
                "name": "Sample task",
                "candidate_file": "candidate.py",
            }
        ),
        encoding="utf-8",
    )

    record = {
        "example_id": "sample-record",
        "messages": [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "user"},
            {"role": "assistant", "content": "assistant"},
        ],
        "metadata": {
            "task_id": "sample_task",
            "source_task_dir": str(task_dir),
        },
    }

    enriched = enrich_record(record, behavior_cap=6, detail_budget_cap=8)

    assert enriched["required_interface"] == ["solve(theta: float) -> int"]
    assert enriched["behavior_hints"][0] == "Test returns the expected phase bucket"
    assert "solve should map 0.25 to bucket 2" in enriched["behavior_hints"]
    assert enriched["detail_budget"] >= 2
    assert enriched["metadata"]["required_interface_count"] == 1
    assert enriched["metadata"]["behavior_hint_count"] == len(enriched["behavior_hints"])
    user_prompt = enriched["messages"][1]["content"]
    assert "Single-file guardrails:" in user_prompt
    assert (
        "Do not depend on repository-local helpers or invent non-standard modules." in user_prompt
    )


def test_enrich_record_falls_back_to_prompt_sections_without_task_dir() -> None:
    record = {
        "example_id": "fallback-record",
        "messages": [
            {"role": "system", "content": "sys"},
            {
                "role": "user",
                "content": (
                    "Implement Python code.\n\n"
                    "Required interface:\n"
                    "- normalize_gate_sequence(tokens)\n\n"
                    "Implementation notes:\n"
                    "- Preserve canonical gate aliases.\n"
                    "- Return only Python code.\n"
                ),
            },
            {"role": "assistant", "content": "assistant"},
        ],
        "metadata": {
            "task_id": "fallback_task",
        },
    }

    enriched = enrich_record(record, behavior_cap=6, detail_budget_cap=8)

    assert enriched["required_interface"] == ["normalize_gate_sequence(tokens)"]
    assert enriched["behavior_hints"] == [
        "Preserve canonical gate aliases.",
        "Return only Python code.",
    ]
    assert enriched["detail_budget"] == 3
    assert enriched["metadata"]["enrichment_source"] == "prompt_fallback"
