from __future__ import annotations

import json
from pathlib import Path

import scripts.model_registry_doctor as doctor


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_storage_summary_offsite_from_archive() -> None:
    archive = {
        "storage": {
            "locations": [{"kind": "s3", "uri": "iner:bucket/path"}],
            "weights_reachable": True,
            "offsite_backup": True,
        }
    }
    summary = doctor.storage_summary(archive, {})
    assert summary["weights_reachable"] is True
    assert summary["offsite_backup"] is True


def test_storage_summary_unreachable_when_nothing_recorded() -> None:
    summary = doctor.storage_summary({}, {"output_dir": "outputs/does-not-exist"})
    assert summary["weights_reachable"] is False
    assert summary["offsite_backup"] is False


def test_audit_flags_unreachable_and_unarchived(tmp_path: Path, monkeypatch) -> None:
    registry_dir = tmp_path / "artifacts" / "model-registry"
    outputs_dir = tmp_path / "outputs"
    registry_dir.mkdir(parents=True)
    outputs_dir.mkdir(parents=True)

    # One archived run with offsite backup (healthy), one with no storage
    # (unreachable), recorded in the index + per-run archive files.
    _write(
        registry_dir / "backed-up.json",
        {
            "storage": {
                "locations": [{"kind": "s3", "uri": "iner:b/p"}],
                "weights_reachable": True,
                "offsite_backup": True,
            }
        },
    )
    _write(registry_dir / "lost.json", {"storage": {}})
    _write(
        registry_dir / "index.json",
        {
            "archive_version": "model-run-index-v2",
            "runs": [
                {
                    "label": "backed-up",
                    "output_dir": "outputs/backed-up",
                    "archive_path": "artifacts/model-registry/backed-up.json",
                },
                {
                    "label": "lost",
                    "output_dir": "outputs/lost",
                    "archive_path": "artifacts/model-registry/lost.json",
                },
            ],
        },
    )

    # A completed local run that is NOT in the index -> unarchived_local_run.
    (outputs_dir / "fresh-run").mkdir()
    (outputs_dir / "fresh-run" / "metrics.json").write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(doctor, "ROOT", tmp_path)
    monkeypatch.setattr(doctor, "REGISTRY_DIR", registry_dir)
    monkeypatch.setattr(doctor, "INDEX_PATH", registry_dir / "index.json")
    monkeypatch.setattr(doctor, "OUTPUTS_DIR", outputs_dir)

    report = doctor.audit()
    kinds = {p["kind"] for p in report["problems"]}
    assert "weights_unreachable" in kinds
    assert "unarchived_local_run" in kinds
    # The backed-up run must not be flagged unreachable or unbacked.
    labels_unreachable = {
        p.get("label") for p in report["problems"] if p["kind"] == "weights_unreachable"
    }
    assert "lost" in labels_unreachable
    assert "backed-up" not in labels_unreachable
