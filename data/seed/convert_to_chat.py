#!/usr/bin/env python3
"""Convert dataset-v0 JSONL examples into a simple chat-style SFT format."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "seed" / "train.jsonl"
DEFAULT_OUTPUT = ROOT / "data" / "seed" / "train-chat.jsonl"
SUPPORTED_SCHEMA = "dataset-v0"

SYSTEM_PROMPT = (
    "You are a careful coding assistant focused on correctness, clear reasoning, "
    "and maintainable Python code. Follow the task instruction and use any "
    "provided artifacts as context. Return only the final code or requested "
    "artifact content."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to dataset-v0 JSONL input")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to chat-format JSONL output")
    return parser.parse_args()



def load_examples(path: Path) -> list[dict]:
    examples = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}: {exc}") from exc
            if record.get("schema_version") != SUPPORTED_SCHEMA:
                raise ValueError(
                    f"Unsupported schema_version on line {line_number}: {record.get('schema_version')!r}"
                )
            examples.append(record)
    return examples



def render_user_message(example: dict) -> str:
    sections = [f"Task: {example['instruction'].strip()}"]

    artifacts = example.get("artifacts", {})
    if artifacts:
        sections.append("Artifacts:")
        for name, content in artifacts.items():
            sections.append(f"[{name}]\n{content.rstrip()}")

    metadata = {
        "example_id": example["example_id"],
        "domain": example["domain"],
        "category": example["category"],
        "task_type": example["task_type"],
        "difficulty": example["difficulty"],
        "language": example["language"],
        "framework": example.get("framework"),
        "tags": example.get("tags", []),
    }
    sections.append("Metadata:\n" + json.dumps(metadata, ensure_ascii=False, indent=2))
    return "\n\n".join(sections).strip() + "\n"



def convert_example(example: dict) -> dict:
    return {
        "format": "chat-sft-v1",
        "source_schema": SUPPORTED_SCHEMA,
        "example_id": example["example_id"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": render_user_message(example)},
            {"role": "assistant", "content": example["response"].rstrip() + "\n"},
        ],
        "metadata": {
            "domain": example["domain"],
            "category": example["category"],
            "task_type": example["task_type"],
            "difficulty": example["difficulty"],
            "language": example["language"],
            "framework": example.get("framework"),
            "tags": example.get("tags", []),
            "source": example["source"],
            **example.get("metadata", {}),
        },
    }



def write_examples(path: Path, examples: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(json.dumps(example, ensure_ascii=False) + "\n")



def main() -> None:
    args = parse_args()
    examples = load_examples(args.input)
    converted = [convert_example(example) for example in examples]
    write_examples(args.output, converted)
    print(f"Wrote {len(converted)} chat examples to {args.output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
