#!/usr/bin/env python3
"""Archive a trained model run with the metadata needed for reproduction."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_LOCAL_EVAL = Path("evals/runner/run_eval.py")
DEFAULT_TRAINING_SCRIPT = Path("training/qwen_sft_peft.py")
DEFAULT_EVAL_TASK_ROOT = Path("evals/tasks")
DEFAULT_EVAL_SCORECARD = Path("evals/runner/scorecard.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="Training output dir containing metrics.json")
    parser.add_argument(
        "--archive-dir",
        type=Path,
        default=Path("artifacts/model-registry"),
        help="Directory where per-run archive JSON files and index.json are written",
    )
    parser.add_argument("--label", help="Optional human-readable label for this model run")
    parser.add_argument(
        "--qual-report",
        action="append",
        default=[],
        metavar="PATH",
        help="Optional qualitative report JSON path. Can be repeated.",
    )
    parser.add_argument(
        "--qual-slice",
        action="append",
        default=[],
        metavar="PATH",
        help="Optional qualitative eval slice path. Can be repeated.",
    )
    parser.add_argument(
        "--eval-command",
        action="append",
        default=[],
        metavar="CMD",
        help="Optional evaluation command text to record. Can be repeated.",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional free-form notes recorded into the archive entry.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def safe_git(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def count_jsonl_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    count = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                count += 1
    return count


def iter_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def validate_json(path: Path) -> tuple[bool, str | None]:
    if not path.exists():
        return False, "missing"
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def summarize_dataset_rows(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    rows = iter_jsonl_rows(path)
    if not rows:
        return {"row_count": 0}

    domain_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    task_type_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    prompt_variant_counts: Counter[str] = Counter()
    task_ids: set[str] = set()
    example_ids: set[str] = set()
    format_counts: Counter[str] = Counter()
    source_schema_counts: Counter[str] = Counter()

    for row in rows:
        metadata = row.get("metadata") or {}
        if row.get("format"):
            format_counts[str(row["format"])] += 1
        if row.get("source_schema"):
            source_schema_counts[str(row["source_schema"])] += 1
        if metadata.get("domain"):
            domain_counts[str(metadata["domain"])] += 1
        if metadata.get("category"):
            category_counts[str(metadata["category"])] += 1
        if metadata.get("task_type"):
            task_type_counts[str(metadata["task_type"])] += 1
        if metadata.get("source"):
            source_counts[str(metadata["source"])] += 1
        if metadata.get("prompt_variant"):
            prompt_variant_counts[str(metadata["prompt_variant"])] += 1
        if metadata.get("task_id"):
            task_ids.add(str(metadata["task_id"]))
        if row.get("example_id"):
            example_ids.add(str(row["example_id"]))

    return {
        "row_count": len(rows),
        "unique_example_ids": len(example_ids),
        "unique_task_ids": len(task_ids),
        "task_ids": sorted(task_ids),
        "formats": dict(sorted(format_counts.items())),
        "source_schemas": dict(sorted(source_schema_counts.items())),
        "domains": dict(sorted(domain_counts.items())),
        "categories": dict(sorted(category_counts.items())),
        "task_types": dict(sorted(task_type_counts.items())),
        "sources": dict(sorted(source_counts.items())),
        "prompt_variants": dict(sorted(prompt_variant_counts.items())),
    }


def resolve_dataset_entry(path_str: str | None) -> dict[str, Any] | None:
    if not path_str:
        return None
    path = Path(path_str)
    manifest_path = path.parent / "manifest.json"
    manifest_valid, manifest_error = validate_json(manifest_path)
    entry: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() else None,
        "rows": count_jsonl_rows(path),
        "manifest_path": str(manifest_path),
        "manifest_exists": manifest_path.exists(),
        "manifest_valid_json": manifest_valid,
        "manifest_error": manifest_error,
        "dataset_summary": summarize_dataset_rows(path),
    }
    if manifest_valid:
        entry["manifest"] = load_json(manifest_path)
    return entry


def infer_model_family(model_name: str | None) -> str | None:
    if not model_name:
        return None
    lowered = model_name.lower()
    if "omnicoder" in lowered:
        return "omnicoder"
    if "qwen" in lowered:
        return "qwen"
    return None


def build_training_command(signature: dict[str, Any]) -> str:
    ordered_keys = [
        "model_name",
        "train_file",
        "eval_file",
        "device",
        "max_length",
        "per_device_batch_size",
        "gradient_accumulation_steps",
        "learning_rate",
        "num_epochs",
        "max_steps",
        "eval_steps",
        "log_steps",
        "lora_rank",
        "lora_alpha",
        "lora_dropout",
    ]
    parts = ["python3", str(DEFAULT_TRAINING_SCRIPT)]
    for key in ordered_keys:
        value = signature.get(key)
        if value in (None, "", False):
            continue
        cli_name = "--" + key.replace("_", "-")
        parts.extend([cli_name, str(value)])

    if signature.get("load_in_8bit"):
        parts.append("--load-in-8bit")
    if signature.get("train_on_completions_only"):
        parts.append("--train-on-completions-only")

    target_modules = signature.get("target_modules") or []
    if target_modules:
        parts.append("--target-modules")
        parts.extend(str(item) for item in target_modules)

    return " ".join(parts)


def archive_name(output_dir: Path) -> str:
    return output_dir.name + ".json"


def build_json_artifact_entry(path: Path) -> dict[str, Any]:
    valid, error = validate_json(path)
    return {
        "path": str(path),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() else None,
        "valid_json": valid,
        "validation_error": error,
    }


def list_adapter_files(adapter_dir: Path) -> list[str]:
    if not adapter_dir.exists():
        return []
    return sorted(str(path.relative_to(adapter_dir)) for path in adapter_dir.rglob("*") if path.is_file())


def build_training_method(signature: dict[str, Any]) -> dict[str, Any]:
    return {
        "stage": "supervised_fine_tuning",
        "adapter_strategy": "LoRA",
        "training_method": "LoRA SFT",
        "loss_function": {
            "name": "causal_lm_cross_entropy",
            "label_masking": "padding tokens masked to -100; prompt tokens also masked when train_on_completions_only=true",
            "train_on_completions_only": bool(signature.get("train_on_completions_only")),
        },
        "optimizer": {
            "name": "AdamW",
            "learning_rate": signature.get("learning_rate"),
        },
        "scheduler": {
            "name": "CosineAnnealingLR",
            "t_max_steps": signature.get("max_steps"),
        },
    }


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir
    metrics_path = output_dir / "metrics.json"
    run_config_path = output_dir / "run_config.json"
    adapter_dir = output_dir / "adapter"

    if not metrics_path.exists():
        raise SystemExit(f"missing metrics file: {metrics_path}")
    if not run_config_path.exists():
        raise SystemExit(f"missing run config file: {run_config_path}")

    metrics = load_json(metrics_path)
    run_config = load_json(run_config_path)
    signature = run_config.get("signature") or metrics.get("signature") or {}

    train_file = signature.get("train_file")
    eval_file = signature.get("eval_file")

    archive_entry: dict[str, Any] = {
        "archive_version": "model-run-archive-v1",
        "archived_at_utc": datetime.now(timezone.utc).isoformat(),
        "label": args.label or output_dir.name,
        "output_dir": str(output_dir),
        "artifacts": {
            "metrics_path": str(metrics_path),
            "metrics_sha256": sha256_file(metrics_path),
            "run_config_path": str(run_config_path),
            "run_config_sha256": sha256_file(run_config_path),
            "adapter_dir": str(adapter_dir),
            "adapter_exists": adapter_dir.exists(),
            "adapter_model_path": str(adapter_dir / "adapter_model.safetensors"),
            "adapter_model_exists": (adapter_dir / "adapter_model.safetensors").exists(),
            "adapter_files": list_adapter_files(adapter_dir),
        },
        "model": {
            "base_model": metrics.get("model_name") or signature.get("model_name"),
            "base_model_family": infer_model_family(metrics.get("model_name") or signature.get("model_name")),
            "training_method": "LoRA SFT",
            "training_method_detail": build_training_method(signature),
            "training_script": str(DEFAULT_TRAINING_SCRIPT),
            "training_command_reconstructed": build_training_command(signature),
        },
        "training_signature": signature,
        "training_data": {
            "train": resolve_dataset_entry(train_file),
            "eval": resolve_dataset_entry(eval_file),
        },
        "evaluation": {
            "quantitative": {
                "local_eval_runner": str(DEFAULT_LOCAL_EVAL),
                "datasets": [
                    {
                        "path": str(DEFAULT_EVAL_TASK_ROOT),
                        "exists": DEFAULT_EVAL_TASK_ROOT.exists(),
                        "kind": "executable_task_suite",
                    }
                ],
                "scorecard": build_json_artifact_entry(DEFAULT_EVAL_SCORECARD),
                "metrics": {
                    "device": metrics.get("device"),
                    "world_size": metrics.get("world_size"),
                    "train_examples": metrics.get("train_examples"),
                    "eval_examples": metrics.get("eval_examples"),
                    "optimizer_steps_per_epoch": metrics.get("optimizer_steps_per_epoch"),
                    "max_available_steps": metrics.get("max_available_steps"),
                    "requested_max_steps": metrics.get("requested_max_steps"),
                    "completed_steps": metrics.get("completed_steps", metrics.get("max_steps")),
                    "final_eval": metrics.get("final_eval"),
                },
            },
            "qualitative": {
                "reports": [build_json_artifact_entry(Path(path)) for path in args.qual_report],
                "slices": [build_json_artifact_entry(Path(path)) for path in args.qual_slice],
                "eval_commands": args.eval_command,
            },
        },
        "git": {
            "head_commit": safe_git("rev-parse", "HEAD"),
            "head_commit_short": safe_git("rev-parse", "--short", "HEAD"),
            "status_porcelain": safe_git("status", "--short"),
        },
        "notes": args.notes,
    }

    archive_dir = args.archive_dir
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / archive_name(output_dir)
    archive_path.write_text(json.dumps(archive_entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    index_path = archive_dir / "index.json"
    if index_path.exists():
        index = load_json(index_path)
    else:
        index = {"archive_version": "model-run-index-v1", "runs": []}

    index_runs: list[dict[str, Any]] = [item for item in index.get("runs", []) if item.get("output_dir") != str(output_dir)]
    index_runs.append(
        {
            "label": archive_entry["label"],
            "output_dir": str(output_dir),
            "archive_path": str(archive_path),
            "base_model": archive_entry["model"]["base_model"],
            "training_method": archive_entry["model"]["training_method"],
            "train_file": train_file,
            "eval_file": eval_file,
            "completed_steps": archive_entry["evaluation"]["quantitative"]["metrics"]["completed_steps"],
            "final_eval_loss": (metrics.get("final_eval") or {}).get("loss"),
            "final_eval_perplexity": (metrics.get("final_eval") or {}).get("perplexity"),
            "head_commit": archive_entry["git"]["head_commit"],
        }
    )
    index["runs"] = sorted(index_runs, key=lambda item: item["output_dir"])
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"archive_path": str(archive_path), "index_path": str(index_path)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
