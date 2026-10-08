from __future__ import annotations

import json
import sys
from pathlib import Path

import scripts.archive_model_run as archive_model_run


def test_infer_parent_output_dir_prefers_explicit_parent() -> None:
    signature = {"adapter_init": "outputs/parent-run/adapter"}
    parent = archive_model_run.infer_parent_output_dir(signature, Path("outputs/explicit-parent"))
    assert parent == "outputs/explicit-parent"


def test_infer_parent_output_dir_uses_adapter_init_parent() -> None:
    signature = {"adapter_init": "outputs/parent-run/adapter"}
    parent = archive_model_run.infer_parent_output_dir(signature, None)
    assert parent == "outputs/parent-run"


def test_summarize_result_payload_handles_override_summary_and_scorecard() -> None:
    override_summary = archive_model_run.summarize_result_payload(
        {"override_passes": 2, "override_total": 4, "override_pass_rate": 0.5}
    )
    assert override_summary == {
        "kind": "override_summary",
        "override_passes": 2,
        "override_total": 4,
        "override_pass_rate": 0.5,
    }

    scorecard_summary = archive_model_run.summarize_result_payload(
        {
            "results": [
                {"source": "reference", "passed": True},
                {"source": "reference", "passed": False},
                {"source": "override", "passed": True},
            ]
        }
    )
    assert scorecard_summary == {
        "kind": "scorecard",
        "overall_passes": 2,
        "overall_total": 3,
        "reference_passes": 1,
        "reference_total": 2,
        "override_passes": 1,
        "override_total": 1,
    }


def test_archive_model_run_records_lineage_and_headline_summary(
    tmp_path: Path, monkeypatch
) -> None:
    output_dir = tmp_path / "outputs" / "run-001"
    adapter_dir = output_dir / "adapter"
    data_dir = tmp_path / "data" / "run-dataset"
    archive_dir = tmp_path / "artifacts" / "model-registry"
    reports_dir = tmp_path / "reports"
    eval_runner_dir = tmp_path / "evals" / "runner"
    eval_tasks_dir = tmp_path / "evals" / "tasks"
    delivery_dir = tmp_path / "artifacts" / "deliveries"

    adapter_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    reports_dir.mkdir(parents=True)
    eval_runner_dir.mkdir(parents=True)
    eval_tasks_dir.mkdir(parents=True)
    delivery_dir.mkdir(parents=True)

    (output_dir / "metrics.json").write_text(
        json.dumps(
            {
                "model_name": "models/OmniCoder-9B",
                "world_size": 8,
                "train_examples": 1024,
                "eval_examples": 504,
                "completed_steps": 12,
                "final_eval": {"loss": 0.38, "perplexity": 1.47},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "run_config.json").write_text(
        json.dumps(
            {
                "signature": {
                    "model_name": "models/OmniCoder-9B",
                    "adapter_init": "outputs/parent-run/adapter",
                    "train_file": "data/run-dataset/train.jsonl",
                    "eval_file": "data/run-dataset/eval.jsonl",
                    "device": "npu",
                    "max_steps": 12,
                    "eval_steps": 6,
                    "learning_rate": 2e-4,
                    "train_on_completions_only": True,
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (adapter_dir / "adapter_model.safetensors").write_bytes(b"adapter")
    (data_dir / "train.jsonl").write_text(
        '{"example_id":"t1","metadata":{"task_id":"a","domain":"quantum","category":"debug_repair","task_type":"implementation","source":"template","prompt_variant":"v1"},"format":"chat-sft-v1","source_schema":"template-v1"}\n',
        encoding="utf-8",
    )
    (data_dir / "eval.jsonl").write_text(
        '{"example_id":"e1","metadata":{"task_id":"b","domain":"quantum","category":"reasoning","task_type":"implementation","source":"template","prompt_variant":"v2"},"format":"chat-sft-v1","source_schema":"template-v1"}\n',
        encoding="utf-8",
    )
    (eval_runner_dir / "scorecard.json").write_text('{"results":[]}\n', encoding="utf-8")
    (delivery_dir / "run-001-delivery.json").write_text(
        '{"artifact":"artifacts/deliveries/run-001.tar.gz"}\n', encoding="utf-8"
    )
    (delivery_dir / "run-001-handoff.json").write_text(
        '{"adapter":{"path":"outputs/run-001/adapter"}}\n', encoding="utf-8"
    )
    (reports_dir / "override_summary.json").write_text(
        '{"override_passes":2,"override_total":4,"override_pass_rate":0.5}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        archive_model_run,
        "DEFAULT_EVAL_SCORECARD",
        tmp_path / "evals" / "runner" / "scorecard.json",
    )
    monkeypatch.setattr(archive_model_run, "DEFAULT_EVAL_TASK_ROOT", tmp_path / "evals" / "tasks")
    monkeypatch.setattr(archive_model_run, "safe_git", lambda *args: "git-value")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "archive_model_run.py",
            str(output_dir),
            "--archive-dir",
            str(archive_dir),
            "--label",
            "run-001",
            "--delivery-manifest",
            "artifacts/deliveries/run-001-delivery.json",
            "--handoff-manifest",
            "artifacts/deliveries/run-001-handoff.json",
            "--paper-id",
            "autonomous_rd_cycle_system",
            "--result-artifact",
            "reports/override_summary.json",
            "--storage-location",
            "nas=/root/work/filestorage/outputs/run-001/adapter",
            "--storage-location",
            "s3=iner:bucket/outputs/run-001/adapter",
            "--storage-checksum",
            "deadbeef",
        ],
    )

    rc = archive_model_run.main()
    assert rc == 0

    archive_payload = json.loads((archive_dir / "run-001.json").read_text(encoding="utf-8"))
    assert archive_payload["archive_version"] == "model-run-archive-v2"
    assert archive_payload["lineage"]["parent_output_dir"] == "outputs/parent-run"
    assert archive_payload["lineage"]["paper_ids"] == ["autonomous_rd_cycle_system"]
    assert archive_payload["evaluation"]["headline_summary"]["override_passes"] == 2
    assert (
        archive_payload["linked_artifacts"]["delivery_manifest"]["path"]
        == "artifacts/deliveries/run-001-delivery.json"
    )
    assert archive_payload["storage"]["weights_reachable"] is True
    assert archive_payload["storage"]["offsite_backup"] is True
    assert archive_payload["storage"]["primary_weight_sha256"] == "deadbeef"
    assert [loc["kind"] for loc in archive_payload["storage"]["locations"]] == ["nas", "s3"]

    index_payload = json.loads((archive_dir / "index.json").read_text(encoding="utf-8"))
    assert index_payload["archive_version"] == "model-run-index-v2"
    run_entry = index_payload["runs"][0]
    assert run_entry["parent_output_dir"] == "outputs/parent-run"
    assert run_entry["headline_summary"]["kind"] == "override_summary"
    assert run_entry["weights_reachable"] is True
    assert run_entry["offsite_backup"] is True


def test_build_storage_block_marks_offsite_backup_for_s3(tmp_path: Path) -> None:
    adapter_dir = tmp_path / "adapter"
    storage = archive_model_run.build_storage_block(
        ["nas=/root/work/filestorage/outputs/run/adapter", "s3=iner:bucket/path/adapter"],
        checksum="abc123",
        size_bytes=5716411744,
        adapter_dir=adapter_dir,
    )
    assert [loc["kind"] for loc in storage["locations"]] == ["nas", "s3"]
    assert storage["primary_weight_sha256"] == "abc123"
    assert storage["primary_weight_bytes"] == 5716411744
    assert storage["weights_reachable"] is True
    assert storage["offsite_backup"] is True
    assert storage["local_adapter_exists"] is False


def test_build_storage_block_local_only_is_reachable_but_not_backed_up(tmp_path: Path) -> None:
    adapter_dir = tmp_path / "adapter"
    adapter_dir.mkdir()
    storage = archive_model_run.build_storage_block([], None, None, adapter_dir)
    assert storage["weights_reachable"] is True
    assert storage["offsite_backup"] is False
    assert storage["local_adapter_exists"] is True


def test_build_storage_block_no_storage_and_no_local_is_unreachable(tmp_path: Path) -> None:
    storage = archive_model_run.build_storage_block([], None, None, tmp_path / "missing")
    assert storage["weights_reachable"] is False
    assert storage["offsite_backup"] is False
    assert storage["local_adapter_exists"] is False
