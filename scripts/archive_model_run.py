#!/usr/bin/env python3
"""Archive a trained model run with the metadata needed for reproduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
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
    parser.add_argument(
        "--parent-run",
        type=Path,
        help="Optional parent output dir for lineage tracking. If omitted, adapter_init/adapter-init in the run config is used when present.",
    )
    parser.add_argument(
        "--delivery-manifest",
        type=Path,
        help="Optional delivery manifest linked to this archived run.",
    )
    parser.add_argument(
        "--handoff-manifest",
        type=Path,
        help="Optional handoff manifest linked to this archived run.",
    )
    parser.add_argument(
        "--paper-id",
        action="append",
        default=[],
        metavar="PAPER_ID",
        help="Optional related research paper id. Can be repeated.",
    )
    parser.add_argument(
        "--result-artifact",
        action="append",
        default=[],
        metavar="PATH",
        help="Optional result JSON artifact (override summary, scorecard, comparison summary, etc.). Can be repeated.",
    )
    parser.add_argument(
        "--storage-location",
        action="append",
        default=[],
        metavar="KIND=URI",
        help=(
            "Where the trained weights actually live, so the registry can answer "
            "'where is this model / is it backed up' even when output_dir is not "
            "present locally. Repeatable. KIND is a short tag such as nas, s3, "
            "local. Example: --storage-location nas=/root/work/filestorage/outputs/run/adapter "
            "--storage-location s3=iner:bucket/path/adapter"
        ),
    )
    parser.add_argument(
        "--storage-checksum",
        metavar="SHA256",
        help="Optional sha256 of the primary weight file (e.g. adapter_model.safetensors) recorded with the storage block for backup verification.",
    )
    parser.add_argument(
        "--storage-bytes",
        type=int,
        metavar="N",
        help="Optional size in bytes of the primary weight file, recorded with the storage block.",
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


def infer_parent_output_dir(signature: dict[str, Any], explicit_parent: Path | None) -> str | None:
    if explicit_parent is not None:
        return str(explicit_parent)
    adapter_init = signature.get("adapter_init") or signature.get("adapter-init")
    if not adapter_init:
        return None
    adapter_path = Path(str(adapter_init))
    if adapter_path.name == "adapter":
        return str(adapter_path.parent)
    return str(adapter_path)


def summarize_scorecard_payload(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload.get("results") or []
    overall_total = len(results)
    overall_passes = sum(1 for item in results if item.get("passed"))
    reference_total = sum(1 for item in results if item.get("source") == "reference")
    reference_passes = sum(
        1 for item in results if item.get("source") == "reference" and item.get("passed")
    )
    override_total = sum(1 for item in results if item.get("source") == "override")
    override_passes = sum(
        1 for item in results if item.get("source") == "override" and item.get("passed")
    )
    return {
        "kind": "scorecard",
        "overall_passes": overall_passes,
        "overall_total": overall_total,
        "reference_passes": reference_passes,
        "reference_total": reference_total,
        "override_passes": override_passes,
        "override_total": override_total,
    }


def summarize_result_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(payload.get("strict_override"), dict):
        strict = payload["strict_override"]
        return {
            "kind": "strict_override_comparison",
            "base_passes": strict.get("base_passes"),
            "base_total": strict.get("base_total"),
            "adapter_passes": strict.get("adapter_passes"),
            "adapter_total": strict.get("adapter_total"),
            "adapter_minus_base_passes": strict.get("adapter_minus_base_passes"),
            "adapter_minus_base_pass_rate": strict.get("adapter_minus_base_pass_rate"),
        }
    if "results" in payload and isinstance(payload.get("results"), list):
        return summarize_scorecard_payload(payload)
    if "examples" in payload and isinstance(payload.get("examples"), list):
        examples = payload.get("examples") or []
        task_ids = sorted({str(item.get("task_id")) for item in examples if item.get("task_id")})
        domains = sorted({str(item.get("domain")) for item in examples if item.get("domain")})
        return {
            "kind": "base_vs_adapter_example_slice",
            "example_count": len(examples),
            "task_ids": task_ids,
            "domains": domains,
        }
    if "override_passes" in payload and "override_total" in payload:
        summary = {
            "kind": "override_summary",
            "override_passes": payload.get("override_passes"),
            "override_total": payload.get("override_total"),
            "override_pass_rate": payload.get("override_pass_rate"),
        }
        if "overall_passes" in payload and "overall_total" in payload:
            summary["overall_passes"] = payload.get("overall_passes")
            summary["overall_total"] = payload.get("overall_total")
        return summary
    if "overall_passes" in payload and "overall_total" in payload:
        return {
            "kind": "overall_summary",
            "overall_passes": payload.get("overall_passes"),
            "overall_total": payload.get("overall_total"),
            "override_passes": payload.get("override_passes"),
            "override_total": payload.get("override_total"),
        }
    return None


def build_result_artifact_entry(path: Path) -> dict[str, Any]:
    entry = build_json_artifact_entry(path)
    if entry["valid_json"]:
        payload = load_json(path)
        summary = summarize_result_payload(payload)
        if summary is not None:
            entry["summary"] = summary
    return entry


def list_adapter_files(adapter_dir: Path) -> list[str]:
    if not adapter_dir.exists():
        return []
    return sorted(
        str(path.relative_to(adapter_dir)) for path in adapter_dir.rglob("*") if path.is_file()
    )


def build_storage_block(
    locations: list[str],
    checksum: str | None,
    size_bytes: int | None,
    adapter_dir: Path,
) -> dict[str, Any]:
    """Record where the trained weights actually live.

    The registry must answer "where is this model and is it backed up" even on a
    machine where the training output_dir is not present (weights typically live
    on a remote pod NAS and/or S3). Each location is ``KIND=URI`` (e.g.
    ``nas=/root/work/.../adapter`` or ``s3=iner:bucket/path/adapter``). A run is
    considered "reachable" if it has any recorded storage location OR a local
    adapter dir, which downstream tooling uses instead of a local-only check.
    """
    parsed: list[dict[str, Any]] = []
    has_offsite_backup = False
    for raw in locations:
        if "=" in raw:
            kind, uri = raw.split("=", 1)
        else:
            kind, uri = "unspecified", raw
        kind = kind.strip().lower()
        uri = uri.strip()
        if not uri:
            continue
        parsed.append({"kind": kind, "uri": uri})
        if kind in {"s3", "oss", "gcs", "iner", "minio"}:
            has_offsite_backup = True
    local_adapter_exists = adapter_dir.exists()
    return {
        "locations": parsed,
        "primary_weight_sha256": checksum,
        "primary_weight_bytes": size_bytes,
        "local_adapter_dir": str(adapter_dir),
        "local_adapter_exists": local_adapter_exists,
        # A run's weights are reachable if recorded anywhere (storage location)
        # or still present locally. This is the signal tracking tools should use
        # so that runs whose output_dir was cleaned locally are not treated as
        # lost/non-runnable.
        "weights_reachable": bool(parsed) or local_adapter_exists,
        "offsite_backup": has_offsite_backup,
    }


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
    parent_output_dir = infer_parent_output_dir(signature, args.parent_run)
    delivery_manifest = (
        build_json_artifact_entry(args.delivery_manifest) if args.delivery_manifest else None
    )
    handoff_manifest = (
        build_json_artifact_entry(args.handoff_manifest) if args.handoff_manifest else None
    )
    result_artifacts = [build_result_artifact_entry(Path(path)) for path in args.result_artifact]
    latest_headline = next(
        (item.get("summary") for item in result_artifacts if item.get("summary")), None
    )
    storage = build_storage_block(
        args.storage_location, args.storage_checksum, args.storage_bytes, adapter_dir
    )

    archive_entry: dict[str, Any] = {
        "archive_version": "model-run-archive-v2",
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
        "storage": storage,
        "model": {
            "base_model": metrics.get("model_name") or signature.get("model_name"),
            "base_model_family": infer_model_family(
                metrics.get("model_name") or signature.get("model_name")
            ),
            "training_method": "LoRA SFT",
            "training_method_detail": build_training_method(signature),
            "training_script": str(DEFAULT_TRAINING_SCRIPT),
            "training_command_reconstructed": build_training_command(signature),
        },
        "training_signature": signature,
        "lineage": {
            "parent_output_dir": parent_output_dir,
            "adapter_init": signature.get("adapter_init") or signature.get("adapter-init"),
            "paper_ids": sorted(set(args.paper_id)),
        },
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
            "result_artifacts": result_artifacts,
            "headline_summary": latest_headline,
        },
        "linked_artifacts": {
            "delivery_manifest": delivery_manifest,
            "handoff_manifest": handoff_manifest,
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
    archive_path.write_text(
        json.dumps(archive_entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    index_path = archive_dir / "index.json"
    if index_path.exists():
        index = load_json(index_path)
    else:
        index = {"archive_version": "model-run-index-v2", "runs": []}

    index_runs: list[dict[str, Any]] = [
        item for item in index.get("runs", []) if item.get("output_dir") != str(output_dir)
    ]
    index_runs.append(
        {
            "label": archive_entry["label"],
            "output_dir": str(output_dir),
            "archive_path": str(archive_path),
            "base_model": archive_entry["model"]["base_model"],
            "training_method": archive_entry["model"]["training_method"],
            "train_file": train_file,
            "eval_file": eval_file,
            "completed_steps": archive_entry["evaluation"]["quantitative"]["metrics"][
                "completed_steps"
            ],
            "final_eval_loss": (metrics.get("final_eval") or {}).get("loss"),
            "final_eval_perplexity": (metrics.get("final_eval") or {}).get("perplexity"),
            "parent_output_dir": parent_output_dir,
            "adapter_init": signature.get("adapter_init") or signature.get("adapter-init"),
            "paper_ids": sorted(set(args.paper_id)),
            "delivery_manifest": str(args.delivery_manifest) if args.delivery_manifest else None,
            "handoff_manifest": str(args.handoff_manifest) if args.handoff_manifest else None,
            "headline_summary": latest_headline,
            "storage_locations": storage["locations"],
            "weights_reachable": storage["weights_reachable"],
            "offsite_backup": storage["offsite_backup"],
            "head_commit": archive_entry["git"]["head_commit"],
        }
    )
    index["archive_version"] = "model-run-index-v2"
    index["runs"] = sorted(index_runs, key=lambda item: item["output_dir"])
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {"archive_path": str(archive_path), "index_path": str(index_path)},
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
