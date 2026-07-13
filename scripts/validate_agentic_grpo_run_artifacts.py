#!/usr/bin/env python3
"""Validate the expected run artifacts written by agentic GRPO training.

This validator is meant for trusted local run directories. It checks the
top-level status/checkpoint/eval files and, when a checkpoint is referenced,
verifies that the checkpoint directory contains a usable runtime state.
"""

from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
from typing import Any

import torch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path, help="Agentic GRPO output directory to validate.")
    parser.add_argument(
        "--output", type=Path, default=None, help="Optional path to write the JSON report."
    )
    return parser.parse_args()


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def add_check(
    checks: dict[str, bool], errors: list[str], name: str, passed: bool, message: str
) -> bool:
    checks[name] = bool(passed)
    if not passed:
        errors.append(message)
    return bool(passed)


def load_json_object(path: Path, *, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(f"missing required file: {path}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{label} is not valid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{label} must be a JSON object")
        return None
    return payload


def load_jsonl_objects(path: Path, *, label: str, errors: list[str]) -> list[dict[str, Any]] | None:
    if not path.exists():
        errors.append(f"missing required file: {path}")
        return None
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    errors.append(f"{label}:{line_no} must be a JSON object")
                    return None
                rows.append(payload)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{label} is not valid JSONL: {exc}")
        return None
    if not rows:
        errors.append(f"{label} is empty")
        return None
    return rows


def require_non_empty_string(
    payload: dict[str, Any],
    key: str,
    *,
    label: str,
    errors: list[str],
) -> bool:
    value = payload.get(key)
    if isinstance(value, str) and value.strip():
        return True
    errors.append(f"{label} missing non-empty string field: {key}")
    return False


def require_int_field(
    payload: dict[str, Any],
    key: str,
    *,
    label: str,
    errors: list[str],
    min_value: int | None = None,
) -> bool:
    value = payload.get(key)
    if not _is_int(value):
        errors.append(f"{label} missing integer field: {key}")
        return False
    if min_value is not None and int(value) < min_value:
        errors.append(f"{label} field {key} must be >= {min_value}")
        return False
    return True


def resolve_artifact_path(
    raw_path: str, *, output_dir: Path, anchor_dir: Path | None = None
) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path

    candidates: list[Path] = []
    if anchor_dir is not None:
        candidates.append((anchor_dir / path).resolve())

    output_parts = output_dir.parts
    raw_parts = path.parts
    overlap_base: Path | None = None
    for overlap in range(min(len(output_parts), len(raw_parts)), 0, -1):
        if tuple(output_parts[-overlap:]) == tuple(raw_parts[:overlap]):
            overlap_base = output_dir.parents[overlap - 1]
            break
    if overlap_base is not None:
        candidates.append((overlap_base / path).resolve())

    candidates.extend(
        [
            (output_dir / path).resolve(),
            (output_dir.parent / path).resolve(),
            (Path.cwd() / path).resolve(),
        ]
    )

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            return candidate
    if candidates:
        return candidates[0]
    return (output_dir / path).resolve()


def validate_live_status(payload: dict[str, Any], *, errors: list[str]) -> bool:
    ok = True
    ok &= require_non_empty_string(payload, "status", label="live_status.json", errors=errors)
    ok &= require_int_field(
        payload, "planned_steps", label="live_status.json", errors=errors, min_value=1
    )
    if not isinstance(payload.get("summary"), dict):
        errors.append("live_status.json missing object field: summary")
        ok = False
    if not isinstance(payload.get("recent"), dict):
        errors.append("live_status.json missing object field: recent")
        ok = False
    if not isinstance(payload.get("alerts"), list):
        errors.append("live_status.json missing list field: alerts")
        ok = False
    latest_checkpoint = payload.get("latest_checkpoint")
    if latest_checkpoint is not None and not isinstance(latest_checkpoint, dict):
        errors.append("live_status.json field latest_checkpoint must be null or an object")
        ok = False
    online_eval_latest = payload.get("online_eval_latest")
    if online_eval_latest is not None and not isinstance(online_eval_latest, dict):
        errors.append("live_status.json field online_eval_latest must be null or an object")
        ok = False
    return ok


def validate_checkpoint_payload(payload: dict[str, Any], *, label: str, errors: list[str]) -> bool:
    ok = True
    ok &= require_int_field(payload, "step", label=label, errors=errors, min_value=1)
    ok &= require_non_empty_string(payload, "checkpoint_dir", label=label, errors=errors)
    return ok


def validate_online_eval_payload(payload: dict[str, Any], *, label: str, errors: list[str]) -> bool:
    ok = True
    ok &= require_int_field(payload, "step", label=label, errors=errors, min_value=1)
    ok &= require_int_field(payload, "task_count", label=label, errors=errors, min_value=0)
    if not isinstance(payload.get("termination_counts"), dict):
        errors.append(f"{label} missing object field: termination_counts")
        ok = False
    if not isinstance(payload.get("failure_categories"), dict):
        errors.append(f"{label} missing object field: failure_categories")
        ok = False
    tasks = payload.get("tasks")
    if tasks is not None:
        if not isinstance(tasks, list):
            errors.append(f"{label} field tasks must be a list when present")
            ok = False
        elif _is_int(payload.get("task_count")) and len(tasks) != int(payload["task_count"]):
            errors.append(f"{label} field task_count does not match len(tasks)")
            ok = False
    return ok


def validate_checkpoint_state_payload(
    payload: dict[str, Any],
    *,
    expected_step: int,
    errors: list[str],
) -> bool:
    ok = True
    ok &= require_int_field(
        payload, "step", label="checkpoint_state.json", errors=errors, min_value=1
    )
    ok &= require_non_empty_string(
        payload, "runtime_state_path", label="checkpoint_state.json", errors=errors
    )
    if ok and int(payload["step"]) != expected_step:
        errors.append(
            "checkpoint_state.json step does not match latest_checkpoint.json "
            f"({payload['step']} != {expected_step})"
        )
        ok = False
    return ok


def load_runtime_state(path: Path, *, errors: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        errors.append(f"missing runtime state file: {path}")
        return None
    try:
        kwargs: dict[str, Any] = {"map_location": "cpu"}
        if "weights_only" in inspect.signature(torch.load).parameters:
            kwargs["weights_only"] = False
        payload = torch.load(path, **kwargs)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"could not load runtime state {path}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"runtime_state.pt must deserialize to a dict: {path}")
        return None
    return payload


def validate_runtime_state_payload(
    payload: dict[str, Any],
    *,
    expected_step: int,
    errors: list[str],
) -> bool:
    ok = True
    ok &= require_int_field(payload, "step", label="runtime_state.pt", errors=errors, min_value=1)
    for key in (
        "optimizer_state",
        "python_random_state",
        "torch_rng_state",
        "adaptive_temp_state",
        "curriculum_state",
    ):
        if key not in payload:
            errors.append(f"runtime_state.pt missing field: {key}")
            ok = False
    if ok and int(payload["step"]) != expected_step:
        errors.append(
            f"runtime_state.pt step does not match latest_checkpoint.json ({payload['step']} != {expected_step})"
        )
        ok = False
    return ok


def validate_run_artifacts(output_dir: Path) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    errors: list[str] = []
    checks: dict[str, bool] = {}

    live_status_path = output_dir / "live_status.json"
    latest_checkpoint_path = output_dir / "latest_checkpoint.json"
    checkpoint_history_path = output_dir / "checkpoint_history.jsonl"
    online_eval_latest_path = output_dir / "online_eval_latest.json"
    online_eval_history_path = output_dir / "online_eval_history.jsonl"

    live_status = load_json_object(live_status_path, label="live_status.json", errors=errors)
    latest_checkpoint = load_json_object(
        latest_checkpoint_path, label="latest_checkpoint.json", errors=errors
    )
    checkpoint_history = load_jsonl_objects(
        checkpoint_history_path,
        label="checkpoint_history.jsonl",
        errors=errors,
    )
    online_eval_latest = load_json_object(
        online_eval_latest_path,
        label="online_eval_latest.json",
        errors=errors,
    )
    online_eval_history = load_jsonl_objects(
        online_eval_history_path,
        label="online_eval_history.jsonl",
        errors=errors,
    )

    add_check(
        checks,
        errors,
        "live_status_valid",
        live_status is not None and validate_live_status(live_status, errors=errors),
        "live_status.json failed validation",
    )
    add_check(
        checks,
        errors,
        "latest_checkpoint_valid",
        latest_checkpoint is not None
        and validate_checkpoint_payload(
            latest_checkpoint, label="latest_checkpoint.json", errors=errors
        ),
        "latest_checkpoint.json failed validation",
    )

    checkpoint_history_ok = checkpoint_history is not None and all(
        validate_checkpoint_payload(row, label=f"checkpoint_history.jsonl:{index}", errors=errors)
        for index, row in enumerate(checkpoint_history, start=1)
    )
    add_check(
        checks,
        errors,
        "checkpoint_history_valid",
        checkpoint_history_ok,
        "checkpoint_history.jsonl failed validation",
    )

    add_check(
        checks,
        errors,
        "online_eval_latest_valid",
        online_eval_latest is not None
        and validate_online_eval_payload(
            online_eval_latest, label="online_eval_latest.json", errors=errors
        ),
        "online_eval_latest.json failed validation",
    )

    online_eval_history_ok = online_eval_history is not None and all(
        validate_online_eval_payload(row, label=f"online_eval_history.jsonl:{index}", errors=errors)
        for index, row in enumerate(online_eval_history, start=1)
    )
    add_check(
        checks,
        errors,
        "online_eval_history_valid",
        online_eval_history_ok,
        "online_eval_history.jsonl failed validation",
    )

    latest_checkpoint_matches_history = (
        checks["latest_checkpoint_valid"]
        and checks["checkpoint_history_valid"]
        and latest_checkpoint == checkpoint_history[-1]
    )
    add_check(
        checks,
        errors,
        "latest_checkpoint_matches_checkpoint_history",
        latest_checkpoint_matches_history,
        "latest_checkpoint.json does not match the last checkpoint_history.jsonl entry",
    )

    latest_checkpoint_matches_live_status = (
        checks["latest_checkpoint_valid"]
        and checks["live_status_valid"]
        and live_status is not None
        and live_status.get("latest_checkpoint") == latest_checkpoint
    )
    add_check(
        checks,
        errors,
        "latest_checkpoint_matches_live_status",
        latest_checkpoint_matches_live_status,
        "live_status.json latest_checkpoint does not match latest_checkpoint.json",
    )

    online_eval_matches_history = (
        checks["online_eval_latest_valid"]
        and checks["online_eval_history_valid"]
        and online_eval_latest == online_eval_history[-1]
    )
    add_check(
        checks,
        errors,
        "online_eval_latest_matches_online_eval_history",
        online_eval_matches_history,
        "online_eval_latest.json does not match the last online_eval_history.jsonl entry",
    )

    online_eval_matches_live_status = (
        checks["online_eval_latest_valid"]
        and checks["live_status_valid"]
        and live_status is not None
        and live_status.get("online_eval_latest") == online_eval_latest
    )
    add_check(
        checks,
        errors,
        "online_eval_latest_matches_live_status",
        online_eval_matches_live_status,
        "live_status.json online_eval_latest does not match online_eval_latest.json",
    )

    checkpoint_dir_path: Path | None = None
    checkpoint_state_path: Path | None = None
    runtime_state_path: Path | None = None

    if checks["latest_checkpoint_valid"] and latest_checkpoint is not None:
        checkpoint_dir_path = resolve_artifact_path(
            str(latest_checkpoint["checkpoint_dir"]),
            output_dir=output_dir,
            anchor_dir=output_dir,
        )
        add_check(
            checks,
            errors,
            "checkpoint_dir_exists",
            checkpoint_dir_path.exists() and checkpoint_dir_path.is_dir(),
            f"latest_checkpoint.json points to a missing checkpoint dir: {checkpoint_dir_path}",
        )
        checkpoint_state_path = checkpoint_dir_path / "checkpoint_state.json"
        checkpoint_state = load_json_object(
            checkpoint_state_path,
            label="checkpoint_state.json",
            errors=errors,
        )
        checkpoint_state_valid = checkpoint_state is not None and validate_checkpoint_state_payload(
            checkpoint_state,
            expected_step=int(latest_checkpoint["step"]),
            errors=errors,
        )
        add_check(
            checks,
            errors,
            "checkpoint_state_valid",
            checkpoint_state_valid,
            "checkpoint_state.json failed validation",
        )
        runtime_state_path = checkpoint_dir_path / "runtime_state.pt"
        if checkpoint_state_valid and checkpoint_state is not None:
            runtime_state_path = resolve_artifact_path(
                str(checkpoint_state["runtime_state_path"]),
                output_dir=output_dir,
                anchor_dir=checkpoint_dir_path,
            )
        runtime_state = load_runtime_state(runtime_state_path, errors=errors)
        runtime_state_valid = runtime_state is not None and validate_runtime_state_payload(
            runtime_state,
            expected_step=int(latest_checkpoint["step"]),
            errors=errors,
        )
        add_check(
            checks,
            errors,
            "runtime_state_valid",
            runtime_state_valid,
            "runtime_state.pt failed validation",
        )
    else:
        checks["checkpoint_dir_exists"] = False
        checks["checkpoint_state_valid"] = False
        checks["runtime_state_valid"] = False

    report = {
        "output_dir": str(output_dir),
        "ok": all(checks.values()),
        "checks": checks,
        "artifacts": {
            "live_status": str(live_status_path),
            "latest_checkpoint": str(latest_checkpoint_path),
            "checkpoint_history": str(checkpoint_history_path),
            "online_eval_latest": str(online_eval_latest_path),
            "online_eval_history": str(online_eval_history_path),
            "checkpoint_dir": str(checkpoint_dir_path) if checkpoint_dir_path else None,
            "checkpoint_state": str(checkpoint_state_path) if checkpoint_state_path else None,
            "runtime_state": str(runtime_state_path) if runtime_state_path else None,
        },
        "summary": {
            "status": live_status.get("status") if live_status is not None else None,
            "checkpoint_step": latest_checkpoint.get("step")
            if latest_checkpoint is not None
            else None,
            "online_eval_step": online_eval_latest.get("step")
            if online_eval_latest is not None
            else None,
        },
        "errors": errors,
    }
    return report


def main() -> int:
    args = parse_args()
    report = validate_run_artifacts(args.output_dir)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
