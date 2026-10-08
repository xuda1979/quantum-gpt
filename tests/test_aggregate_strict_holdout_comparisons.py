from __future__ import annotations

import json
from pathlib import Path

import scripts.aggregate_strict_holdout_comparisons as aggregate_strict_holdout_comparisons


def _comparison_payload(
    *,
    baseline_label: str = "qwen25_base",
    baseline_scorecard: str = "/tmp/base/scorecard.json",
    candidate_label: str,
    candidate_scorecard: str,
    base_override_passes: int = 0,
    candidate_override_passes: int = 0,
    override_total: int = 4,
    base_full_passes: int = 22,
    candidate_full_passes: int = 22,
    full_total: int = 26,
    failed_override_task_ids: list[str] | None = None,
) -> dict[str, object]:
    failed_override_task_ids = failed_override_task_ids or ["task_a"]
    strict_delta_passes = candidate_override_passes - base_override_passes
    full_delta_passes = candidate_full_passes - base_full_passes
    return {
        "kind": "strict_override_comparison",
        "baseline": {
            "label": baseline_label,
            "scorecard": baseline_scorecard,
            "overall_passes": base_full_passes,
            "overall_total": full_total,
            "override_passes": base_override_passes,
            "override_total": override_total,
            "failed_override_task_ids": failed_override_task_ids,
        },
        "candidate": {
            "label": candidate_label,
            "scorecard": candidate_scorecard,
            "overall_passes": candidate_full_passes,
            "overall_total": full_total,
            "override_passes": candidate_override_passes,
            "override_total": override_total,
            "failed_override_task_ids": failed_override_task_ids,
        },
        "strict_override": {
            "base_passes": base_override_passes,
            "base_total": override_total,
            "adapter_passes": candidate_override_passes,
            "adapter_total": override_total,
            "adapter_minus_base_passes": strict_delta_passes,
            "adapter_minus_base_pass_rate": strict_delta_passes / override_total
            if override_total
            else None,
        },
        "full_scorecard": {
            "base_passes": base_full_passes,
            "base_total": full_total,
            "candidate_passes": candidate_full_passes,
            "candidate_total": full_total,
            "candidate_minus_base_passes": full_delta_passes,
            "candidate_minus_base_pass_rate": full_delta_passes / full_total
            if full_total
            else None,
        },
    }


def test_build_row_extracts_table_ready_scores() -> None:
    payload = _comparison_payload(
        candidate_label="qwen25_stage2",
        candidate_scorecard="/tmp/stage2/scorecard.json",
        candidate_override_passes=2,
        candidate_full_passes=24,
        failed_override_task_ids=["quantum_qaoa_maxcut", "quantum_superdense_coding"],
    )

    row = aggregate_strict_holdout_comparisons.build_row(
        Path("reports/qwen25_strict_holdout_base_vs_stage2.json"), payload
    )

    assert row["base_strict_score"] == "0/4"
    assert row["finetuned_strict_score"] == "2/4"
    assert row["strict_delta_passes"] == 2
    assert row["strict_delta_percentage_points"] == 50.0
    assert row["base_full_score"] == "22/26"
    assert row["finetuned_full_score"] == "24/26"
    assert row["full_delta_passes"] == 2
    assert round(float(row["full_delta_percentage_points"]), 6) == round((2 / 26) * 100.0, 6)


def test_build_table_artifact_sorts_best_strict_delta_first(tmp_path: Path, monkeypatch) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "qwen25_strict_holdout_base_vs_flat.json").write_text(
        json.dumps(
            _comparison_payload(
                candidate_label="flat",
                candidate_scorecard="/tmp/flat/scorecard.json",
                candidate_override_passes=0,
                candidate_full_passes=22,
            )
        )
        + "\n",
        encoding="utf-8",
    )
    (reports_dir / "qwen25_strict_holdout_base_vs_gain.json").write_text(
        json.dumps(
            _comparison_payload(
                candidate_label="gain",
                candidate_scorecard="/tmp/gain/scorecard.json",
                candidate_override_passes=1,
                candidate_full_passes=23,
            )
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    artifact = aggregate_strict_holdout_comparisons.build_table_artifact(
        ["reports/qwen25_strict_holdout_base_vs_*.json"]
    )

    assert artifact["comparison_count"] == 2
    assert artifact["baseline_consistent"] is True
    assert artifact["rows"][0]["finetuned_label"] == "gain"
    assert artifact["rows"][1]["finetuned_label"] == "flat"


def test_main_writes_default_output_from_real_fixture_pattern(tmp_path: Path, monkeypatch) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    (reports_dir / "qwen25_strict_holdout_base_vs_fastlora_small_20260412.json").write_text(
        json.dumps(
            _comparison_payload(
                baseline_label="Qwen2.5-1.5B base (rerun 2026-04-12)",
                baseline_scorecard="/tmp/base-rerun/scorecard.json",
                candidate_label="Qwen2.5-1.5B fast-lora small",
                candidate_scorecard="/tmp/fastlora/scorecard.json",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["aggregate_strict_holdout_comparisons.py"])
    exit_code = aggregate_strict_holdout_comparisons.main()

    assert exit_code == 0
    output_path = reports_dir / "qwen25_strict_holdout_comparison_table.json"
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["kind"] == "strict_holdout_comparison_table"
    assert payload["comparison_count"] == 1
    assert (
        payload["rows"][0]["comparison_id"]
        == "qwen25_strict_holdout_base_vs_fastlora_small_20260412"
    )
