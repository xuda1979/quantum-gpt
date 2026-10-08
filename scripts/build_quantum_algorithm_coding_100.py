#!/usr/bin/env python3
"""Build the curated 100 quantum-algorithm-coding Q&A dataset.

Every entry is a high-quality question with a self-contained, self-checking
qiskit answer (the code ends in assertions + a print, so correctness is proven
by execution). The builder emits a dataset-v0 JSONL, a ChatML SFT JSONL, and a
diversity manifest.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from quantum_algorithm_coding_100_entries import ENTRIES

OUT = Path("data/curated")
DATASET = OUT / "quantum_algorithm_coding_100_v1.jsonl"
CHATML = OUT / "quantum_algorithm_coding_100_v1_chatml.jsonl"
MANIFEST = OUT / "quantum_algorithm_coding_100_v1_manifest.json"

SYSTEM_PROMPT = (
    "You are an expert quantum software engineer. Write correct, executable, "
    "professional quantum algorithm code with clear rationale and validation."
)


def build_response(entry: dict) -> str:
    rationale = entry["rationale"].strip()
    code = entry["code"].strip("\n")
    return f"Rationale: {rationale}\n\n```python\n{code}\n```\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    chatml = []
    ids = set()
    for entry in ENTRIES:
        eid = entry["id"]
        if eid in ids:
            raise ValueError(f"duplicate id {eid}")
        ids.add(eid)
        response = build_response(entry)
        row = {
            "example_id": eid,
            "domain": "quantum",
            "category": entry["family"],
            "algorithm": entry["algorithm"],
            "task_type": entry.get("task_type", "implementation"),
            "difficulty": entry["difficulty"],
            "framework": entry.get("framework", "qiskit"),
            "language": "python",
            "instruction": entry["question"].strip(),
            "response": response,
            "schema_version": "dataset-v0",
            "source": "curated_quantum_algorithm_coding_100_v1",
            "tags": sorted(
                {
                    "quantum",
                    "algorithm_coding",
                    entry["family"],
                    entry["algorithm"],
                    entry["difficulty"],
                }
            ),
            "metadata": {
                "curated": True,
                "validated": "execution",
                "validator": "scripts/validate_quantum_algorithm_coding_100.py",
            },
        }
        rows.append(row)
        chatml.append(
            {
                "example_id": eid,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": entry["question"].strip()},
                    {"role": "assistant", "content": response},
                ],
            }
        )

    with DATASET.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with CHATML.open("w") as f:
        for r in chatml:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    manifest = {
        "count": len(rows),
        "families": dict(sorted(Counter(r["category"] for r in rows).items())),
        "algorithms": dict(sorted(Counter(r["algorithm"] for r in rows).items())),
        "difficulty": dict(sorted(Counter(r["difficulty"] for r in rows).items())),
        "task_types": dict(sorted(Counter(r["task_type"] for r in rows).items())),
        "frameworks": dict(sorted(Counter(r["framework"] for r in rows).items())),
        "unique_algorithms": len(set(r["algorithm"] for r in rows)),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    print(f"\nWrote {len(rows)} rows -> {DATASET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
