"""2026-08-26 code-review finding: the required-contract number selection
sorted NUMERIC STRINGS lexicographically ('100' < '1000' < '30' < '5'), so
the [:3] cap picked the wrong numbers — a prompt with '5 qubits, 30 layers,
100 shots, 1000 iterations' required 100/1000/30 and dropped the true qubit
count 5. The sort must be numeric."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.report_base_adapter_comprehensive import contract_score  # noqa: E402


def test_contract_score_number_selection_is_numeric_not_lexicographic() -> None:
    prompt = "Implement a VQE for 5 qubits, 30 layers, 100 shots, 1000 iterations."
    code = "n_qubits = 5\n"
    _, required, _ = contract_score(prompt, code)
    number_requirements = [r for r in required if r.startswith("number:")]
    # numeric order: 5, 30, 100 — the true qubit count must be required
    assert "number:5" in number_requirements
    assert number_requirements[:3] == ["number:5", "number:30", "number:100"]
