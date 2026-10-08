from __future__ import annotations

import json
from pathlib import Path

from scripts.delivery_registry import build_delivery_registry, write_delivery_registry


def test_build_delivery_registry_collects_models_deliveries_and_papers(tmp_path: Path) -> None:
    (tmp_path / "artifacts/model-registry").mkdir(parents=True)
    (tmp_path / "artifacts/deliveries/handoff-001").mkdir(parents=True)
    (tmp_path / "research/papers/test-paper").mkdir(parents=True)
    (tmp_path / "research/build").mkdir(parents=True)
    (tmp_path / "outputs/run-001").mkdir(parents=True)
    (tmp_path / "outputs/adapter-001").mkdir(parents=True)
    (tmp_path / "models/base-model").mkdir(parents=True)
    (tmp_path / "reports").mkdir(parents=True)
    (tmp_path / "scripts").mkdir(parents=True)

    (tmp_path / "artifacts/model-registry/run-001.json").write_text("{}", encoding="utf-8")
    (tmp_path / "artifacts/model-registry/index.json").write_text(
        json.dumps(
            {
                "archive_version": "model-run-index-v1",
                "runs": [
                    {
                        "label": "run-001",
                        "archive_path": "artifacts/model-registry/run-001.json",
                        "output_dir": "outputs/run-001",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "artifacts/deliveries/adapter_delivery.json").write_text(
        json.dumps(
            {
                "artifact": "artifacts/deliveries/adapter_delivery.tar.gz",
                "adapter_dir": "outputs/adapter-001",
                "metrics_file": "outputs/run-001/metrics.json",
                "report_file": "reports/adapter_report.md",
                "base_model": "models/base-model",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "artifacts/deliveries/adapter_delivery.tar.gz").write_bytes(b"tgz")
    (tmp_path / "outputs/adapter-001/adapter_model.safetensors").write_bytes(b"adapter-weights")
    (tmp_path / "outputs/run-001/metrics.json").write_text("{}", encoding="utf-8")
    (tmp_path / "reports/adapter_report.md").write_text("# report\n", encoding="utf-8")
    (tmp_path / "scripts/eval.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "reports/eval_slice.json").write_text("{}", encoding="utf-8")
    (tmp_path / "artifacts/deliveries/handoff-001/handoff_manifest.json").write_text(
        json.dumps(
            {
                "base_model": "models/base-model",
                "adapter": {"path": "outputs/adapter-001"},
                "eval_slice": {"path": "reports/eval_slice.json"},
                "script_inputs": [{"path": "scripts/eval.py"}],
                "blocker": {"blocked_command": "echo blocked"},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "research/papers/index.json").write_text(
        json.dumps(
            {
                "papers": [
                    {
                        "paper_id": "test-paper",
                        "title": "Test Paper",
                        "type": "system",
                        "has_plugin": False,
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "research/papers/test-paper/paper.md").write_text("# paper\n", encoding="utf-8")
    (tmp_path / "research/RESEARCH-REPORT.tex").write_text("% tex\n", encoding="utf-8")
    (tmp_path / "research/build/RESEARCH-REPORT.pdf").write_bytes(b"%PDF")

    payload = build_delivery_registry(tmp_path)

    assert payload["ok"] is True
    assert payload["summary"]["model_run_count"] == 1
    assert payload["summary"]["delivery_manifest_count"] == 1
    assert payload["summary"]["handoff_count"] == 1
    assert payload["summary"]["paper_count"] == 1
    assert payload["issues"] == []


def test_build_delivery_registry_reports_missing_referenced_artifacts(tmp_path: Path) -> None:
    (tmp_path / "artifacts/model-registry").mkdir(parents=True)
    (tmp_path / "artifacts/deliveries").mkdir(parents=True)
    (tmp_path / "research/papers").mkdir(parents=True)
    (tmp_path / "research/build").mkdir(parents=True)

    (tmp_path / "artifacts/model-registry/index.json").write_text(
        json.dumps(
            {
                "archive_version": "model-run-index-v1",
                "runs": [
                    {
                        "label": "missing-run",
                        "archive_path": "artifacts/model-registry/missing-run.json",
                        "output_dir": "outputs/missing-run",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "artifacts/deliveries/bad_delivery.json").write_text(
        json.dumps(
            {
                "artifact": "artifacts/deliveries/missing.tar.gz",
                "adapter_dir": "outputs/missing-adapter",
                "metrics_file": "outputs/missing-run/metrics.json",
                "report_file": "reports/missing.md",
                "base_model": "models/missing-base",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "research/papers/index.json").write_text(
        json.dumps(
            {
                "papers": [
                    {
                        "paper_id": "missing-paper",
                        "title": "Missing Paper",
                        "type": "method",
                        "has_plugin": True,
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "research/RESEARCH-REPORT.tex").write_text("% tex\n", encoding="utf-8")

    payload = build_delivery_registry(tmp_path)

    assert payload["ok"] is False
    problems = {(issue["scope"], issue["problem"]) for issue in payload["issues"]}
    assert ("model_registry", "missing-archive") in problems
    assert ("model_registry", "missing-output-dir") in problems
    assert ("deliveries", "missing-delivery-artifact") in problems
    assert ("deliveries", "missing-base-model") in problems
    assert ("papers", "missing-paper-directory") in problems
    assert ("canonical_report", "missing-report-pdf") in problems


def test_write_delivery_registry_persists_index(tmp_path: Path) -> None:
    payload = {
        "generated_at_utc": "2026-04-11T00:00:00+00:00",
        "workspace_root": str(tmp_path),
        "summary": {"issue_count": 0},
        "ok": True,
        "issues": [],
    }

    out_path = write_delivery_registry(payload, tmp_path / "artifacts/delivery-registry/index.json")

    assert out_path.exists()
    assert json.loads(out_path.read_text(encoding="utf-8"))["ok"] is True
