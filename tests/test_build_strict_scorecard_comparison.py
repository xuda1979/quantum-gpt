from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_builds_same_protocol_comparison(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    output = tmp_path / "comparison.json"

    baseline.write_text(
        json.dumps(
            {
                "results": [
                    {"id": "ref_a", "source": "reference", "passed": True},
                    {"id": "ref_b", "source": "reference", "passed": True},
                    {"id": "ovr_a", "source": "override", "passed": False},
                    {"id": "ovr_b", "source": "override", "passed": False},
                ]
            }
        ),
        encoding="utf-8",
    )
    candidate.write_text(
        json.dumps(
            {
                "results": [
                    {"id": "ref_a", "source": "reference", "passed": True},
                    {"id": "ref_b", "source": "reference", "passed": True},
                    {"id": "ovr_a", "source": "override", "passed": True},
                    {"id": "ovr_b", "source": "override", "passed": False},
                ]
            }
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_strict_scorecard_comparison.py"),
            "--baseline-scorecard",
            str(baseline),
            "--baseline-label",
            "base",
            "--candidate-scorecard",
            str(candidate),
            "--candidate-label",
            "adapter",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["kind"] == "strict_override_comparison"
    assert payload["strict_override"]["base_passes"] == 0
    assert payload["strict_override"]["adapter_passes"] == 1
    assert payload["strict_override"]["adapter_minus_base_passes"] == 1
    assert payload["full_scorecard"]["base_total"] == 4
    assert payload["full_scorecard"]["candidate_minus_base_passes"] == 1
