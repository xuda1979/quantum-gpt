"""Regression tests for scripts/run_lineage.py and scripts/compare_runs.py.

Verifies that:
  - run_lineage.py builds a well-formed lineage.json from a synthetic run dir
    (run_config.json + metrics.json + dataset manifest + adapter marker)
  - lineage includes correct model/dataset/hyperparameter/metric extraction
  - compare_runs.py renders a table from lineage.json files
  - compare_runs.py --json emits valid JSON
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def synthetic_run(tmp_path, monkeypatch):
    """Create a synthetic run dir with run_config.json + metrics.json +
    a dataset manifest + an adapter marker, under a fake repo root."""
    # Fake repo root containing the run dir + data/generated + evals/runs
    root = tmp_path / "repo"
    run_dir = root / "outputs" / "test-run-20260708T120000Z"
    run_dir.mkdir(parents=True)
    # run_config.json (SFT shape, matching training/qwen_sft_peft.py output)
    (run_dir / "run_config.json").write_text(
        json.dumps(
            {
                "signature": {
                    "model_name": "/root/work/filestorage/Qwen3.6-27B",
                    "adapter_init": None,
                    "train_file": "data/generated/glm52_soft_distill_sft_100/train.jsonl",
                    "eval_file": "data/generated/glm52_soft_distill_sft_100/eval.jsonl",
                    "max_length": 2048,
                    "per_device_batch_size": 1,
                    "gradient_accumulation_steps": 8,
                    "learning_rate": 5e-6,
                    "num_epochs": 2,
                    "lora_rank": 16,
                    "lora_alpha": 32,
                    "lora_dropout": 0.0,
                },
                "resolved_target_modules": ["q_proj", "v_proj"],
                "trainable_parameter_count": 123456,
            }
        ),
        encoding="utf-8",
    )
    # metrics.json (matching training/qwen_sft_peft.py output)
    (run_dir / "metrics.json").write_text(
        json.dumps(
            {
                "completed_steps": 20,
                "max_steps": 20,
                "train_examples": 90,
                "eval_examples": 10,
                "final_eval": {"loss": 0.7353, "perplexity": 2.086},
                "world_size": 2,
                "signature": {"model_name": "/root/work/filestorage/Qwen3.6-27B"},
            }
        ),
        encoding="utf-8",
    )
    # Dataset manifest
    ds_dir = root / "data" / "generated" / "glm52_soft_distill_sft_100"
    ds_dir.mkdir(parents=True)
    (ds_dir / "manifest.json").write_text(
        json.dumps(
            {
                "source_sha256": "abc123",
                "train_out": 90,
                "eval_out": 10,
                "split_method": "stable_sha256_sorted_90_10",
            }
        ),
        encoding="utf-8",
    )
    # Adapter marker
    (run_dir / "adapter").mkdir()
    (run_dir / "adapter" / "adapter_config.json").write_text("{}", encoding="utf-8")
    # Linked eval (v1 scorecard under evals/runs/)
    ev_dir = root / "evals" / "runs" / "test-run-20260708T120000Z-eval"
    ev_dir.mkdir(parents=True)
    (ev_dir / "scorecard.json").write_text(
        json.dumps(
            {
                "scored_at_utc": "2026-07-08T13:00:00Z",
                "results": [
                    {"id": "quantum_bell", "passed": True},
                    {"id": "software_bug", "passed": True},
                    {"id": "quantum_depolarizing", "passed": False},
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(root)
    return root, run_dir


def test_build_lineage_extracts_all_sections(synthetic_run):
    root, run_dir = synthetic_run
    rl = _load_script("run_lineage")
    lineage = rl.build_lineage(run_dir)
    # Top-level identity
    assert lineage["lineage_schema_version"] == 1
    assert lineage["run_name"] == "test-run-20260708T120000Z"
    # Model
    assert "Qwen3.6-27B" in lineage["model"]["model_name"]
    # Dataset manifest found
    ds = lineage["dataset"]
    assert ds["manifest"] is not None
    assert ds["manifest"]["train_out"] == 90
    assert ds["manifest"]["eval_out"] == 10
    # Hyperparameters
    hp = lineage["hyperparameters"]
    assert hp["lora_rank"] == 16
    assert hp["learning_rate"] == 5e-6
    # Metrics
    m = lineage["metrics"]
    assert m["completed_steps"] == 20
    assert m["final_eval"]["loss"] == pytest.approx(0.7353)
    # Adapter
    assert lineage["adapter"]["exists"] is True
    # Linked eval
    assert len(lineage["linked_evals"]) == 1
    ev = lineage["linked_evals"][0]
    assert ev["n_tasks"] == 3
    assert ev["n_pass"] == 2
    assert ev["pass_at_1"] == pytest.approx(2 / 3, abs=0.01)
    # Artifact hashes
    assert lineage["artifact_hashes"]["run_config.json"] is not None
    assert lineage["artifact_hashes"]["metrics.json"] is not None


def test_build_lineage_handles_missing_metrics(tmp_path, monkeypatch):
    """A run dir with only run_config.json should not crash."""
    root = tmp_path / "repo"
    run_dir = root / "outputs" / "bare-run"
    run_dir.mkdir(parents=True)
    (run_dir / "run_config.json").write_text(
        json.dumps(
            {
                "signature": {"model_name": "Qwen3.6-27B", "train_file": "x.jsonl"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(root)
    rl = _load_script("run_lineage")
    lineage = rl.build_lineage(run_dir)
    assert lineage["metrics"] is None
    assert lineage["adapter"]["exists"] is False
    assert lineage["linked_evals"] == []


def test_compare_runs_table_renders(synthetic_run):
    root, run_dir = synthetic_run
    cr = _load_script("compare_runs")
    lineage_path = run_dir / "lineage.json"
    # First build lineage
    rl = _load_script("run_lineage")
    lineage = rl.build_lineage(run_dir)
    lineage_path.write_text(json.dumps(lineage), encoding="utf-8")
    # Run compare_runs as a subprocess
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "compare_runs.py"), str(lineage_path)],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    assert "1 runs compared" in r.stdout
    assert "test-run-20260708T120000Z" in r.stdout
    assert "loss=0.7353" in r.stdout
    assert "67%" in r.stdout  # 2/3 pass@1


def test_compare_runs_json_output(synthetic_run):
    root, run_dir = synthetic_run
    rl = _load_script("run_lineage")
    lineage = rl.build_lineage(run_dir)
    lineage_path = run_dir / "lineage.json"
    lineage_path.write_text(json.dumps(lineage), encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "compare_runs.py"), str(lineage_path), "--json"],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    data = json.loads(r.stdout)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["run_name"] == "test-run-20260708T120000Z"
    assert data[0]["metrics"]["final_eval"]["loss"] == pytest.approx(0.7353)
    assert data[0]["adapter_exists"] is True


def test_run_lineage_scan_writes_lineage_files(synthetic_run):
    root, run_dir = synthetic_run
    r = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "run_lineage.py"), "scan", "outputs/"],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    assert r.returncode == 0, f"stderr:\n{r.stderr}"
    assert (run_dir / "lineage.json").exists()
    assert "1 written" in r.stdout
    # Second scan should skip
    r2 = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "run_lineage.py"), "scan", "outputs/"],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    assert r2.returncode == 0
    assert "1 skipped" in r2.stdout
