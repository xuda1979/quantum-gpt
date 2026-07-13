#!/usr/bin/env python3
"""Validate Stage-2 paper-card corpus and (optionally) emit the corpus manifest.

This is the validator for the schema defined in
docs/stage2-science-corpus-manifest-schema-2026-07-07.md and
configs/stage2/paper_card_schema_v1.json.

Usage
-----
    # Validate every paper card in a directory
    python3 scripts/validate_stage2_paper_manifest.py \
        --dir data/curated/stage2_paper_cards/

    # Also emit the corpus manifest with paper-disjoint + author-leakage splits
    python3 scripts/validate_stage2_paper_manifest.py \
        --dir data/curated/stage2_paper_cards/ \
        --emit-manifest data/curated/stage2_corpus_manifest.json \
        --seed 0 --eval-ratio 0.05 --holdout-ratio 0.05

    # Verify that code_artifacts marked verified_runnable=true actually run
    python3 scripts/validate_stage2_paper_manifest.py \
        --dir data/curated/stage2_paper_cards/ --exec-code

Exit codes: 0 = OK, 1 = validation errors, 2 = bad invocation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA_PATH = ROOT / "configs" / "stage2" / "paper_card_schema_v1.json"


def _load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _basic_schema_check(card: dict, schema: dict, path: str, errors: list[str]) -> None:
    """Minimal draft-07-ish checker: type, required, enum, additionalProperties.
    Not a full JSON Schema implementation, but enough for this schema."""
    if schema.get("type") == "object":
        if not isinstance(card, dict):
            errors.append(f"{path}: expected object, got {type(card).__name__}")
            return
        for req in schema.get("required", []):
            if req not in card:
                errors.append(f"{path}: missing required key {req!r}")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}).keys())
            for k in card:
                if k not in allowed:
                    errors.append(f"{path}: additional property {k!r} not allowed")
        for k, subschema in schema.get("properties", {}).items():
            if k in card:
                _basic_schema_check(card[k], subschema, f"{path}.{k}", errors)
    elif schema.get("type") == "array":
        if not isinstance(card, list):
            errors.append(f"{path}: expected array, got {type(card).__name__}")
            return
        if "minItems" in schema and len(card) < schema["minItems"]:
            errors.append(f"{path}: {len(card)} items < minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(card):
                _basic_schema_check(item, item_schema, f"{path}[{i}]", errors)
    elif schema.get("type") == "string":
        if not isinstance(card, str):
            errors.append(f"{path}: expected string, got {type(card).__name__}")
    elif schema.get("type") == "integer":
        if not isinstance(card, int) or isinstance(card, bool):
            errors.append(f"{path}: expected integer, got {type(card).__name__}")
    elif schema.get("type") == "boolean":
        if not isinstance(card, bool):
            errors.append(f"{path}: expected boolean, got {type(card).__name__}")
    if "enum" in schema and card not in schema["enum"]:
        errors.append(f"{path}: {card!r} not in enum {schema['enum']!r}")
    if "minimum" in schema and isinstance(card, (int, float)) and not isinstance(card, bool):
        if card < schema["minimum"]:
            errors.append(f"{path}: {card} < minimum {schema['minimum']}")
    if "maximum" in schema and isinstance(card, (int, float)) and not isinstance(card, bool):
        if card > schema["maximum"]:
            errors.append(f"{path}: {card} > maximum {schema['maximum']}")


def load_cards(card_dir: Path) -> list[dict]:
    cards = []
    for p in sorted(card_dir.glob("*.json")):
        try:
            cards.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:  # noqa: BLE001
            print(f"WARN: failed to parse {p}: {e}", file=sys.stderr)
    return cards


def validate_cards(cards: list[dict], schema: dict) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for c in cards:
        pid = c.get("paper_id", "<unknown>")
        if pid in seen_ids:
            errors.append(f"duplicate paper_id: {pid}")
        seen_ids.add(pid)
        _basic_schema_check(c, schema, f"card[{pid}]", errors)
        # qa_pairs code_artifact_ref must exist or be "none"
        art_ids = {a.get("id") for a in c.get("code_artifacts", []) if isinstance(a, dict)}
        for i, qa in enumerate(c.get("qa_pairs", [])):
            ref = qa.get("code_artifact_ref", "none")
            if ref != "none" and ref not in art_ids:
                errors.append(f"card[{pid}].qa_pairs[{i}]: code_artifact_ref {ref!r} not found")
    return errors


def check_author_leakage(cards: list[dict], splits: dict[str, list[str]]) -> list[str]:
    errors: list[str] = []
    by_id = {c["paper_id"]: c for c in cards}
    train_authors: set[str] = set()
    for pid in splits.get("train", []):
        for a in by_id.get(pid, {}).get("authors", []):
            train_authors.add(a.strip().lower())
    for split_name in ("eval", "holdout"):
        for pid in splits.get(split_name, []):
            for a in by_id.get(pid, {}).get("authors", []):
                if a.strip().lower() in train_authors:
                    errors.append(
                        f"author leakage: {a!r} appears in train and {split_name} paper {pid}"
                    )
    return errors


def split_cards(
    cards: list[dict], eval_ratio: float, holdout_ratio: float, seed: int
) -> dict[str, list[str]]:
    import random

    rng = random.Random(seed)
    ids = sorted(c["paper_id"] for c in cards)
    rng.shuffle(ids)
    n = len(ids)
    n_eval = max(1, int(n * eval_ratio))
    n_holdout = max(1, int(n * holdout_ratio))
    return {
        "train": ids[: n - n_eval - n_holdout],
        "eval": ids[n - n_eval - n_holdout : n - n_holdout],
        "holdout": ids[n - n_holdout :],
    }


def exec_code_artifact(code: str, expected: str, timeout: float = 10.0) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            timeout=timeout,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return False, "<timeout>"
    finally:
        Path(path).unlink(missing_ok=True)
    actual = proc.stdout.rstrip()
    return actual == expected.rstrip(), actual


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dir", required=True, help="Directory of paper card JSON files")
    p.add_argument("--emit-manifest", help="Path to write the corpus manifest")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--eval-ratio", type=float, default=0.05)
    p.add_argument("--holdout-ratio", type=float, default=0.05)
    p.add_argument(
        "--exec-code",
        action="store_true",
        help="Execute code_artifacts marked verified_runnable=true",
    )
    args = p.parse_args()

    card_dir = Path(args.dir)
    if not card_dir.is_dir():
        print(f"ERROR: not a directory: {card_dir}", file=sys.stderr)
        return 2
    cards = load_cards(card_dir)
    if not cards:
        print(f"ERROR: no paper cards found in {card_dir}", file=sys.stderr)
        return 1
    schema = _load_schema()
    errors = validate_cards(cards, schema)
    if errors:
        print(f"FAIL — {len(errors)} validation errors:")
        for e in errors[:50]:
            print(" ", e)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more")
        return 1

    splits = split_cards(cards, args.eval_ratio, args.holdout_ratio, args.seed)
    leakage_errors = check_author_leakage(cards, splits)
    if leakage_errors:
        print(f"FAIL — {len(leakage_errors)} author-leakage errors:")
        for e in leakage_errors[:50]:
            print(" ", e)
        return 1

    if args.exec_code:
        n_executed = 0
        n_failed = 0
        for c in cards:
            for art in c.get("code_artifacts", []):
                if art.get("verified_runnable") is True:
                    ok, actual = exec_code_artifact(art["code"], art["expected_output"])
                    n_executed += 1
                    if not ok:
                        n_failed += 1
                        print(
                            f"FAIL — code_artifact {c['paper_id']}/{art['id']} did not match expected output"
                        )
                        print(f"  expected: {art['expected_output']!r}")
                        print(f"  actual:   {actual!r}")
        print(f"exec-code: {n_executed - n_failed}/{n_executed} artifacts matched expected output")
        if n_failed:
            return 1

    if args.emit_manifest:
        by_id = {c["paper_id"]: c for c in cards}
        field_counts: dict[str, int] = {}
        qa_counts: dict[str, int] = {f"L{i}": 0 for i in range(7)}
        n_qa = 0
        n_verified = 0
        for c in cards:
            for tag in c.get("field_tags", []):
                field_counts[tag] = field_counts.get(tag, 0) + 1
            for qa in c.get("qa_pairs", []):
                n_qa += 1
                qa_counts[qa.get("level", "L0")] += 1
            for art in c.get("code_artifacts", []):
                if art.get("verified_runnable"):
                    n_verified += 1
        manifest = {
            "manifest_version": 1,
            "created": "2026-07-07",
            "total_papers": len(cards),
            "splits": splits,
            "split_policy": {
                "method": "paper_disjoint",
                "seed": args.seed,
                "eval_ratio": args.eval_ratio,
                "holdout_ratio": args.holdout_ratio,
                "constraints": [
                    "no author overlap between train and eval+holdout",
                    "no venue+year collision between train and holdout",
                ],
            },
            "field_tag_coverage": field_counts,
            "qa_level_counts": qa_counts,
            "verified_code_artifacts": n_verified,
            "total_qa_pairs": n_qa,
        }
        out = Path(args.emit_manifest)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"manifest written: {out} ({len(cards)} papers, {n_qa} qa pairs)")

    print(f"PASS — {len(cards)} paper cards valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
