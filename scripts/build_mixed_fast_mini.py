#!/usr/bin/env python3
"""Build a deterministic codefirst+semantic mixed SFT dataset.

The two input datasets must contain the same example ids in the same order.
For each example id, we choose either the codefirst row or the semantic row
with a stable hash so the mix is reproducible across machines.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codefirst-dir", type=Path, default=Path("data/generated/fast-mini-codefirst"))
    parser.add_argument(
        "--semantic-dir",
        type=Path,
        default=Path("data/generated/fast-mini-interface-prefix-semantic-v4"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/generated/fast-mini-codefirst-semantic-mix75"),
    )
    parser.add_argument(
        "--semantic-ratio",
        type=float,
        default=0.75,
        help="Fraction of examples that should come from the semantic dataset.",
    )
    parser.add_argument(
        "--seed-tag",
        default="mix-v1",
        help="Stable tag mixed into the example-id hash for deterministic selection.",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def stable_score(example_id: str, seed_tag: str) -> float:
    digest = hashlib.sha256(f"{seed_tag}:{example_id}".encode("utf-8")).hexdigest()
    value = int(digest[:16], 16)
    return value / float(16**16 - 1)


def choose_source(example_id: str, semantic_ratio: float, seed_tag: str) -> str:
    return "semantic" if stable_score(example_id, seed_tag) < semantic_ratio else "codefirst"


def rewrite_split(
    codefirst_path: Path,
    semantic_path: Path,
    out_path: Path,
    semantic_ratio: float,
    seed_tag: str,
    mixed_prompt_variant: str,
) -> dict:
    code_rows = load_jsonl(codefirst_path)
    semantic_rows = load_jsonl(semantic_path)
    if len(code_rows) != len(semantic_rows):
        raise ValueError(
            f"Split size mismatch: {codefirst_path} has {len(code_rows)} rows, "
            f"{semantic_path} has {len(semantic_rows)} rows"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)

    counts = {"codefirst": 0, "semantic": 0}
    domain_counts = {
        "codefirst": {},
        "semantic": {},
    }

    with out_path.open("w", encoding="utf-8") as handle:
        for code_row, semantic_row in zip(code_rows, semantic_rows):
            code_id = code_row["example_id"]
            semantic_id = semantic_row["example_id"]
            if code_id != semantic_id:
                raise ValueError(f"Example id mismatch: {code_id} != {semantic_id}")

            chosen_source = choose_source(code_id, semantic_ratio, seed_tag)
            base_row = semantic_row if chosen_source == "semantic" else code_row
            row = copy.deepcopy(base_row)
            metadata = row.setdefault("metadata", {})
            metadata["mixed_source"] = chosen_source
            metadata["source_prompt_variant"] = base_row.get("metadata", {}).get("prompt_variant")
            metadata["prompt_variant"] = mixed_prompt_variant

            counts[chosen_source] += 1
            domain = metadata.get("domain", "unknown")
            domain_counts[chosen_source][domain] = domain_counts[chosen_source].get(domain, 0) + 1
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    return {
        "count": len(code_rows),
        "sources": counts,
        "domains_by_source": domain_counts,
        "path": str(out_path),
    }


def main() -> int:
    args = parse_args()
    if not 0.0 <= args.semantic_ratio <= 1.0:
        raise SystemExit("--semantic-ratio must be between 0 and 1")

    mixed_prompt_variant = f"codefirst-semantic-mix-r{int(args.semantic_ratio * 100):02d}-v1"
    train_stats = rewrite_split(
        args.codefirst_dir / "train.jsonl",
        args.semantic_dir / "train.jsonl",
        args.out_dir / "train.jsonl",
        args.semantic_ratio,
        args.seed_tag,
        mixed_prompt_variant,
    )
    eval_stats = rewrite_split(
        args.codefirst_dir / "eval.jsonl",
        args.semantic_dir / "eval.jsonl",
        args.out_dir / "eval.jsonl",
        args.semantic_ratio,
        args.seed_tag,
        mixed_prompt_variant,
    )

    manifest = {
        "manifest_version": "fast-mini-mix-v1",
        "codefirst_dir": str(args.codefirst_dir),
        "semantic_dir": str(args.semantic_dir),
        "out_dir": str(args.out_dir),
        "semantic_ratio": args.semantic_ratio,
        "seed_tag": args.seed_tag,
        "prompt_variant": mixed_prompt_variant,
        "splits": {
            "train": train_stats,
            "eval": eval_stats,
        },
    }
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
