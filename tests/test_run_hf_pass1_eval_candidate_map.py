from __future__ import annotations

import json
from pathlib import Path

from scripts.run_hf_pass1_eval import write_candidate_map


def test_write_candidate_map_records_selected_tasks(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    tasks = [
        {
            "id": "quantum_gate_alias_normalization",
            "candidate_file": "candidates/quantum_gate_alias_normalization.py",
        },
        {
            "id": "quantum_qaoa_maxcut",
            "candidate_file": "candidates/quantum_qaoa_maxcut.py",
        },
    ]

    candidate_map_path = write_candidate_map(run_dir, tasks)

    assert candidate_map_path == run_dir / "candidate-map.json"
    payload = json.loads(candidate_map_path.read_text(encoding="utf-8"))
    assert payload == {
        "quantum_gate_alias_normalization": "candidates/quantum_gate_alias_normalization.py",
        "quantum_qaoa_maxcut": "candidates/quantum_qaoa_maxcut.py",
    }
