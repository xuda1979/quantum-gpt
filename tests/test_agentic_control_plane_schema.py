from __future__ import annotations

import json
from pathlib import Path

from training.agentic_control_plane_schema import (
    AGENTIC_TRACE_REQUIRED_FIELDS,
    CONTROL_PLANE_SCHEMA_VERSION,
    RUN_MANIFEST_REQUIRED_FIELDS,
    build_agentic_trace_record,
    build_run_manifest,
    validate_agentic_trace_jsonl,
    validate_agentic_trace_record,
    validate_run_manifest,
)


def valid_manifest() -> dict[str, object]:
    return build_run_manifest(
        run_id="agentic-run-001",
        created_at_utc="2026-05-26T00:00:00+00:00",
        trainer="training.agentic_grpo_trainer",
        model_name="models/Qwen3.6-27B",
        output_dir="outputs/agentic-run-001",
        tasks_dir="evals/tasks",
        benchmark_file="evals/benchmarks/agentic_coding_trajectory_training_v1.txt",
        planned_steps=64,
        group_size=4,
        max_turns=8,
        max_test_runs=3,
        artifact_paths={
            "run_config": "outputs/agentic-run-001/run_config.json",
            "step_metrics_jsonl": "outputs/agentic-run-001/grpo_step_metrics.jsonl",
            "agentic_trace_jsonl": "outputs/agentic-run-001/agentic_trace.jsonl",
            "live_status": "outputs/agentic-run-001/live_status.json",
            "adapter_dir": "outputs/agentic-run-001/adapter",
        },
    )


def valid_trace_record() -> dict[str, object]:
    return build_agentic_trace_record(
        run_id="agentic-run-001",
        trajectory_id="agentic-run-001-step-00001-group-00",
        timestamp_utc="2026-05-26T00:00:01+00:00",
        step=1,
        group_index=0,
        task_id="quantum_demo",
        domain="quantum",
        candidate_filename="candidate.py",
        termination="final_answer",
        passed=True,
        total_reward=1.02,
        reward_breakdown={
            "pass_reward": 1.0,
            "syntax_reward": 1.0,
            "interface_reward": 1.0,
            "verifier_reward": 1.0,
            "trajectory_behavior_reward": 0.02,
        },
        tool_counts={"read_file": 1, "write_file": 1, "run_tests": 1, "final_answer": 1},
        turns=[
            {
                "turn_index": 0,
                "assistant": '{"tool": "read_file", "path": "candidate.py"}',
                "tool": "read_file",
                "observation": "candidate.py: ...",
            },
            {
                "turn_index": 1,
                "assistant": '{"tool": "final_answer", "content": "def solve(): pass"}',
                "tool": "final_answer",
                "observation": "final_answer ok",
            },
        ],
    )


def test_schema_constants_define_bounded_required_fields() -> None:
    assert CONTROL_PLANE_SCHEMA_VERSION == "agentic-control-plane-v1"
    assert RUN_MANIFEST_REQUIRED_FIELDS == (
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
    assert AGENTIC_TRACE_REQUIRED_FIELDS == (
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


def test_validate_run_manifest_accepts_canonical_manifest() -> None:
    assert validate_run_manifest(valid_manifest()) == []


def test_validate_run_manifest_reports_missing_and_mistyped_fields() -> None:
    manifest = valid_manifest()
    del manifest["run_id"]
    manifest["planned_steps"] = 0
    manifest["artifact_paths"] = {
        "run_config": "outputs/run/run_config.json",
        "step_metrics_jsonl": "",
    }

    errors = validate_run_manifest(manifest)

    assert "run_manifest.run_id is required" in errors
    assert "run_manifest.planned_steps must be >= 1" in errors
    assert "run_manifest.artifact_paths.agentic_trace_jsonl is required" in errors
    assert "run_manifest.artifact_paths.live_status is required" in errors
    assert "run_manifest.artifact_paths.adapter_dir is required" in errors
    assert "run_manifest.artifact_paths.step_metrics_jsonl must be a non-empty string" in errors


def test_validate_agentic_trace_record_accepts_canonical_record() -> None:
    assert validate_agentic_trace_record(valid_trace_record()) == []


def test_validate_agentic_trace_record_rejects_bad_counts_and_turns() -> None:
    record = valid_trace_record()
    record["passed"] = 1
    record["total_reward"] = True
    record["tool_counts"] = {"read_file": True, "write_file": -1}
    record["turns"] = [
        {"turn_index": 0, "assistant": "no tool", "tool": None},
        "not an object",
    ]

    errors = validate_agentic_trace_record(record)

    assert "agentic_trace.passed must be a boolean" in errors
    assert "agentic_trace.total_reward must be a number" in errors
    assert "agentic_trace.tool_counts.read_file must be an integer" in errors
    assert "agentic_trace.tool_counts.write_file must be >= 0" in errors
    assert "agentic_trace.turns[0].observation is required" in errors
    assert "agentic_trace.turns[1] must be an object" in errors


def test_validate_agentic_trace_jsonl_reports_line_scoped_errors(tmp_path: Path) -> None:
    trace_path = tmp_path / "agentic_trace.jsonl"
    bad_record = valid_trace_record()
    del bad_record["trajectory_id"]
    trace_path.write_text(
        json.dumps(valid_trace_record()) + "\n" + "{not json}\n" + json.dumps(bad_record) + "\n",
        encoding="utf-8",
    )

    errors = validate_agentic_trace_jsonl(trace_path)

    assert errors[0].startswith(f"{trace_path}:2: invalid JSON")
    assert f"{trace_path}:3: agentic_trace.trajectory_id is required" in errors


def test_validate_agentic_trace_jsonl_can_require_records(tmp_path: Path) -> None:
    trace_path = tmp_path / "empty.jsonl"
    trace_path.write_text("\n", encoding="utf-8")

    assert validate_agentic_trace_jsonl(trace_path) == [
        f"{trace_path}: no agentic trace records found"
    ]
    assert validate_agentic_trace_jsonl(trace_path, require_records=False) == []
