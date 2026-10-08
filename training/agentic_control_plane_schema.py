from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

CONTROL_PLANE_SCHEMA_VERSION = "agentic-control-plane-v1"
RUN_MANIFEST_RECORD_TYPE = "run_manifest"
AGENTIC_TRACE_RECORD_TYPE = "agentic_trace"

RUN_MANIFEST_REQUIRED_FIELDS = (
    "schema_version",
    "record_type",
    "run_id",
    "created_at_utc",
    "trainer",
    "model_name",
    "output_dir",
    "tasks_dir",
    "benchmark_file",
    "planned_steps",
    "group_size",
    "max_turns",
    "max_test_runs",
    "artifact_paths",
)

RUN_MANIFEST_ARTIFACT_PATH_FIELDS = (
    "run_config",
    "step_metrics_jsonl",
    "agentic_trace_jsonl",
    "live_status",
    "adapter_dir",
)

AGENTIC_TRACE_REQUIRED_FIELDS = (
    "schema_version",
    "record_type",
    "run_id",
    "trajectory_id",
    "timestamp_utc",
    "step",
    "group_index",
    "task_id",
    "domain",
    "candidate_filename",
    "termination",
    "passed",
    "total_reward",
    "reward_breakdown",
    "tool_counts",
    "turns",
)

AGENTIC_TRACE_TURN_REQUIRED_FIELDS = (
    "turn_index",
    "assistant",
    "tool",
    "observation",
)


def build_run_manifest(
    *,
    run_id: str,
    created_at_utc: str,
    trainer: str,
    model_name: str,
    output_dir: str,
    tasks_dir: str,
    benchmark_file: str | None,
    planned_steps: int,
    group_size: int,
    max_turns: int,
    max_test_runs: int,
    artifact_paths: Mapping[str, str],
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema_version": CONTROL_PLANE_SCHEMA_VERSION,
        "record_type": RUN_MANIFEST_RECORD_TYPE,
        "run_id": run_id,
        "created_at_utc": created_at_utc,
        "trainer": trainer,
        "model_name": model_name,
        "output_dir": output_dir,
        "tasks_dir": tasks_dir,
        "benchmark_file": benchmark_file,
        "planned_steps": planned_steps,
        "group_size": group_size,
        "max_turns": max_turns,
        "max_test_runs": max_test_runs,
        "artifact_paths": dict(artifact_paths),
    }
    if extra:
        manifest.update(dict(extra))
    return manifest


def build_agentic_trace_record(
    *,
    run_id: str,
    trajectory_id: str,
    timestamp_utc: str,
    step: int,
    group_index: int,
    task_id: str,
    domain: str,
    candidate_filename: str,
    termination: str,
    passed: bool,
    total_reward: float,
    reward_breakdown: Mapping[str, Any],
    tool_counts: Mapping[str, int],
    turns: Sequence[Mapping[str, Any]],
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": CONTROL_PLANE_SCHEMA_VERSION,
        "record_type": AGENTIC_TRACE_RECORD_TYPE,
        "run_id": run_id,
        "trajectory_id": trajectory_id,
        "timestamp_utc": timestamp_utc,
        "step": step,
        "group_index": group_index,
        "task_id": task_id,
        "domain": domain,
        "candidate_filename": candidate_filename,
        "termination": termination,
        "passed": passed,
        "total_reward": total_reward,
        "reward_breakdown": dict(reward_breakdown),
        "tool_counts": dict(tool_counts),
        "turns": [dict(turn) for turn in turns],
    }
    if extra:
        record.update(dict(extra))
    return record


def validate_run_manifest(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, Mapping):
        return ["run_manifest must be a JSON object"]

    _require_fields(payload, RUN_MANIFEST_REQUIRED_FIELDS, "run_manifest", errors)

    _expect_exact(payload, "schema_version", CONTROL_PLANE_SCHEMA_VERSION, "run_manifest", errors)
    _expect_exact(payload, "record_type", RUN_MANIFEST_RECORD_TYPE, "run_manifest", errors)
    _expect_nonempty_string(payload, "run_id", "run_manifest", errors)
    _expect_nonempty_string(payload, "created_at_utc", "run_manifest", errors)
    _expect_nonempty_string(payload, "trainer", "run_manifest", errors)
    _expect_nonempty_string(payload, "model_name", "run_manifest", errors)
    _expect_nonempty_string(payload, "output_dir", "run_manifest", errors)
    _expect_nonempty_string(payload, "tasks_dir", "run_manifest", errors)
    _expect_optional_string(payload, "benchmark_file", "run_manifest", errors)
    _expect_int(payload, "planned_steps", "run_manifest", errors, minimum=1)
    _expect_int(payload, "group_size", "run_manifest", errors, minimum=1)
    _expect_int(payload, "max_turns", "run_manifest", errors, minimum=1)
    _expect_int(payload, "max_test_runs", "run_manifest", errors, minimum=0)

    artifact_paths = payload.get("artifact_paths")
    if not isinstance(artifact_paths, Mapping):
        errors.append("run_manifest.artifact_paths must be an object")
    else:
        _require_fields(
            artifact_paths, RUN_MANIFEST_ARTIFACT_PATH_FIELDS, "run_manifest.artifact_paths", errors
        )
        for key in RUN_MANIFEST_ARTIFACT_PATH_FIELDS:
            if key in artifact_paths:
                _expect_nonempty_string(artifact_paths, key, "run_manifest.artifact_paths", errors)

    return errors


def validate_agentic_trace_record(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, Mapping):
        return ["agentic_trace must be a JSON object"]

    _require_fields(payload, AGENTIC_TRACE_REQUIRED_FIELDS, "agentic_trace", errors)

    _expect_exact(payload, "schema_version", CONTROL_PLANE_SCHEMA_VERSION, "agentic_trace", errors)
    _expect_exact(payload, "record_type", AGENTIC_TRACE_RECORD_TYPE, "agentic_trace", errors)
    _expect_nonempty_string(payload, "run_id", "agentic_trace", errors)
    _expect_nonempty_string(payload, "trajectory_id", "agentic_trace", errors)
    _expect_nonempty_string(payload, "timestamp_utc", "agentic_trace", errors)
    _expect_int(payload, "step", "agentic_trace", errors, minimum=1)
    _expect_int(payload, "group_index", "agentic_trace", errors, minimum=0)
    _expect_nonempty_string(payload, "task_id", "agentic_trace", errors)
    _expect_nonempty_string(payload, "domain", "agentic_trace", errors)
    _expect_nonempty_string(payload, "candidate_filename", "agentic_trace", errors)
    _expect_nonempty_string(payload, "termination", "agentic_trace", errors)
    _expect_bool(payload, "passed", "agentic_trace", errors)
    _expect_number(payload, "total_reward", "agentic_trace", errors)
    _expect_mapping(payload, "reward_breakdown", "agentic_trace", errors)
    _expect_int_mapping(payload, "tool_counts", "agentic_trace", errors, minimum=0)
    _expect_turns(payload.get("turns"), errors)
    return errors


def validate_agentic_trace_jsonl(path: Path, *, require_records: bool = True) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"{path} does not exist"]

    record_count = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record_count += 1
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue
        for error in validate_agentic_trace_record(payload):
            errors.append(f"{path}:{line_number}: {error}")

    if require_records and record_count == 0:
        errors.append(f"{path}: no agentic trace records found")
    return errors


def is_valid_run_manifest(payload: Any) -> bool:
    return not validate_run_manifest(payload)


def is_valid_agentic_trace_record(payload: Any) -> bool:
    return not validate_agentic_trace_record(payload)


def _require_fields(
    payload: Mapping[str, Any], fields: Sequence[str], path: str, errors: list[str]
) -> None:
    for field in fields:
        if field not in payload:
            errors.append(f"{path}.{field} is required")


def _expect_exact(
    payload: Mapping[str, Any],
    key: str,
    expected: str,
    path: str,
    errors: list[str],
) -> None:
    if key not in payload:
        return
    if payload.get(key) != expected:
        errors.append(f"{path}.{key} must be {expected!r}")


def _expect_nonempty_string(
    payload: Mapping[str, Any], key: str, path: str, errors: list[str]
) -> None:
    if key not in payload:
        return
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}.{key} must be a non-empty string")


def _expect_optional_string(
    payload: Mapping[str, Any], key: str, path: str, errors: list[str]
) -> None:
    if key not in payload:
        return
    value = payload.get(key)
    if value is not None and not isinstance(value, str):
        errors.append(f"{path}.{key} must be a string or null")


def _expect_int(
    payload: Mapping[str, Any],
    key: str,
    path: str,
    errors: list[str],
    *,
    minimum: int,
) -> None:
    if key not in payload:
        return
    value = payload.get(key)
    if not _is_int(value):
        errors.append(f"{path}.{key} must be an integer")
        return
    if value < minimum:
        errors.append(f"{path}.{key} must be >= {minimum}")


def _expect_bool(payload: Mapping[str, Any], key: str, path: str, errors: list[str]) -> None:
    if key not in payload:
        return
    value = payload.get(key)
    if not isinstance(value, bool):
        errors.append(f"{path}.{key} must be a boolean")


def _expect_number(payload: Mapping[str, Any], key: str, path: str, errors: list[str]) -> None:
    if key not in payload:
        return
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{path}.{key} must be a number")


def _expect_mapping(payload: Mapping[str, Any], key: str, path: str, errors: list[str]) -> None:
    if key not in payload:
        return
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{path}.{key} must be an object")


def _expect_int_mapping(
    payload: Mapping[str, Any],
    key: str,
    path: str,
    errors: list[str],
    *,
    minimum: int,
) -> None:
    if key not in payload:
        return
    value = payload.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{path}.{key} must be an object")
        return
    for item_key, item_value in value.items():
        if not isinstance(item_key, str) or not item_key.strip():
            errors.append(f"{path}.{key} keys must be non-empty strings")
        if not _is_int(item_value):
            errors.append(f"{path}.{key}.{item_key} must be an integer")
        elif item_value < minimum:
            errors.append(f"{path}.{key}.{item_key} must be >= {minimum}")


def _expect_turns(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        errors.append("agentic_trace.turns must be a list")
        return
    for index, turn in enumerate(value):
        path = f"agentic_trace.turns[{index}]"
        if not isinstance(turn, Mapping):
            errors.append(f"{path} must be an object")
            continue
        _require_fields(turn, AGENTIC_TRACE_TURN_REQUIRED_FIELDS, path, errors)
        if "turn_index" in turn:
            _expect_int(turn, "turn_index", path, errors, minimum=0)
        if "assistant" in turn:
            _expect_optional_string(turn, "assistant", path, errors)
        if "tool" in turn:
            _expect_optional_string(turn, "tool", path, errors)
        if "observation" in turn:
            _expect_optional_string(turn, "observation", path, errors)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
