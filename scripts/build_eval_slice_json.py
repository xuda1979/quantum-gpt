#!/usr/bin/env python3
"""Create a concrete, repeatable qualitative comparison pack for base-vs-adapter review.

Reads the fixed eval-slice plan and the fast-mini eval data, then materializes a JSON report
with the prompt, reference answer, and a compact review checklist for each selected example.
This keeps the next manual comparison step deterministic even before a full generation harness.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/generated/fast-mini/eval.jsonl"
OUT_DIR = ROOT / "reports"
OUT_PATH = OUT_DIR / "base_vs_adapter_eval_slice.json"

TARGET_IDS = [
    "template_session_window_summary_10_ab155b35",
    "template_measurement_bug_repair_17_9fa09a1c",
    "template_stabilizer_tableau_update_repair_9_24ca0492",
    "template_session_event_log_5_ba6d5385",
    "template_session_window_summary_18_3c89bcaf",
]

REVIEW_CHECKLIST = [
    "required function/class names are present",
    "output is code-only with no explanations",
    "obvious validation behavior is present",
    "solution shape is semantically close to the reference",
    "no obvious likely test-breaking mistakes",
]


def load_rows(path: Path) -> list[dict]:
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw:
            rows.append(json.loads(raw))
    return rows


def main() -> int:
    rows = load_rows(SOURCE)
    by_id = {row["example_id"]: row for row in rows}

    materialized = []
    missing = []
    for example_id in TARGET_IDS:
        row = by_id.get(example_id)
        if row is None:
            missing.append(example_id)
            continue
        messages = row["messages"]
        user_prompt = next(msg["content"] for msg in messages if msg["role"] == "user")
        reference = next(msg["content"] for msg in messages if msg["role"] == "assistant")
        materialized.append(
            {
                "example_id": example_id,
                "task_id": row.get("metadata", {}).get("task_id"),
                "task_name": row.get("metadata", {}).get("task_name"),
                "domain": row.get("metadata", {}).get("domain"),
                "prompt": user_prompt,
                "reference": reference,
                "review_checklist": REVIEW_CHECKLIST,
            }
        )

    payload = {
        "source": str(SOURCE.relative_to(ROOT)),
        "selected_examples": len(materialized),
        "missing_examples": missing,
        "examples": materialized,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    if missing:
        print("missing:", ", ".join(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
