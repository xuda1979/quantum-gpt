from __future__ import annotations

import json
import subprocess
import tarfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_delivery_artifact.py"


def test_build_delivery_artifact_creates_tarball_and_rewrites_manifest(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / "artifacts/deliveries").mkdir(parents=True)
    (repo_root / "outputs/run-001/adapter").mkdir(parents=True)
    (repo_root / "reports").mkdir(parents=True)

    (repo_root / "outputs/run-001/adapter/adapter_model.safetensors").write_bytes(
        b"adapter-weights"
    )
    (repo_root / "outputs/run-001/adapter/adapter_config.json").write_text("{}", encoding="utf-8")
    (repo_root / "outputs/run-001/metrics.json").write_text("{}", encoding="utf-8")
    (repo_root / "outputs/run-001/run_config.json").write_text("{}", encoding="utf-8")
    (repo_root / "reports/run_report.md").write_text("# report\n", encoding="utf-8")

    manifest_path = repo_root / "artifacts/deliveries/run-001.json"
    manifest_path.write_text(
        json.dumps(
            {
                "artifact": "artifacts/deliveries/run-001.tar.gz",
                "base_model": "models/base-model",
                "adapter_dir": "outputs/run-001/adapter",
                "metrics_file": "outputs/run-001/metrics.json",
                "report_file": "reports/run_report.md",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            str(SCRIPT_PATH),
            str(manifest_path),
            "--rewrite-manifest",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    artifact_path = repo_root / "artifacts/deliveries/run-001.tar.gz"
    assert artifact_path.exists()
    assert payload["member_count"] == 4

    updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert updated_manifest["sha256"] == payload["sha256"]
    assert updated_manifest["size_human"].endswith(("B", "K", "M", "G", "T"))

    with tarfile.open(artifact_path, "r:gz") as tar:
        members = tar.getnames()
    assert "outputs/run-001/adapter/adapter_model.safetensors" in members
    assert "outputs/run-001/metrics.json" in members
    assert "outputs/run-001/run_config.json" in members
    assert "reports/run_report.md" in members


def test_build_delivery_artifact_fails_without_adapter_weights(tmp_path: Path) -> None:
    repo_root = tmp_path
    (repo_root / "artifacts/deliveries").mkdir(parents=True)
    (repo_root / "outputs/run-001/adapter").mkdir(parents=True)
    (repo_root / "reports").mkdir(parents=True)

    (repo_root / "outputs/run-001/adapter/adapter_config.json").write_text("{}", encoding="utf-8")
    (repo_root / "outputs/run-001/metrics.json").write_text("{}", encoding="utf-8")
    (repo_root / "reports/run_report.md").write_text("# report\n", encoding="utf-8")

    manifest_path = repo_root / "artifacts/deliveries/run-001.json"
    manifest_path.write_text(
        json.dumps(
            {
                "artifact": "artifacts/deliveries/run-001.tar.gz",
                "base_model": "models/base-model",
                "adapter_dir": "outputs/run-001/adapter",
                "metrics_file": "outputs/run-001/metrics.json",
                "report_file": "reports/run_report.md",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            str(SCRIPT_PATH),
            str(manifest_path),
            "--check-only",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "adapter_model.safetensors" in result.stderr
