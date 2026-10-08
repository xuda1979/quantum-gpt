"""Regression: pennylane_vqe_h2 scorer must be version-aware and reference-fair.

2026-08-25 (QA finding): the enriched tests.py counted terms with
``len(H.terms)``, but ``qml.Hamiltonian``/``LinearCombination`` expose
``.terms`` as a CALLABLE returning ``(coeffs, ops)`` on pennylane 0.38.0 AND
0.45.1 — so the scorer always measured 0 terms and the task's own REFERENCE
candidate failed its tests ("too few terms (0)"). Every leg scored this task
as a false negative (poisoned baseline).

These tests lock the version-aware form (callable-or-attribute, tuple-aware
count) and its binary invariance: the reference passes, a genuinely bad
candidate fails — under whichever pennylane the suite host has.
"""

from __future__ import annotations

import importlib.util
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "evals" / "tasks" / "quantum" / "pennylane_vqe_h2"

try:
    import pennylane  # noqa: F401
except Exception:  # pragma: no cover - plain-python3 suite host
    pennylane = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(
    pennylane is None,
    reason="requires pennylane on this host",
)


def _load_run_tests() -> object:
    spec = importlib.util.spec_from_file_location("vqe_h2_tests", str(TASK_DIR / "tests.py"))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _write_candidate(tmp_path: Path, body: str) -> str:
    p = tmp_path / "candidate.py"
    p.write_text(body, encoding="utf-8")
    return str(p)


REFERENCE = (TASK_DIR / "candidate.py").read_text(encoding="utf-8")


def test_reference_candidate_passes() -> None:
    """The task's own reference must pass its scorer (it fails under the old
    bare-len form on every pennylane version)."""
    rt = _load_run_tests()
    result = rt.run_tests(str(TASK_DIR / "candidate.py"))
    assert result["passed"], result["details"]


def test_failing_candidate_still_fails_binary_invariance(tmp_path: Path) -> None:
    """A genuinely bad candidate (too-few-terms Hamiltonian, no real VQE
    decrease) must still fail — the version-aware form must not be laxer."""
    mutant = textwrap.dedent(
        """
        import pennylane as qml
        from pennylane import numpy as np

        def h2_hamiltonian():
            # Only 2 of the >=4 expected terms.
            return qml.Hamiltonian([1.0, -0.5], [qml.PauliZ(0), qml.PauliZ(1)])

        def run_vqe(steps=80, seed=0):
            return {"energy": 0.5}  # no variational decrease
        """
    )
    rt = _load_run_tests()
    result = rt.run_tests(_write_candidate(tmp_path, mutant))
    assert not result["passed"], "mutant candidate must not pass"
    assert any(
        "too few terms" in d or "did not drop below" in d for d in result["details"]
    ), result["details"]


def test_wrong_return_shape_fails(tmp_path: Path) -> None:
    """A candidate returning a non-Hamiltonian object must fail exactly as
    before (hasattr terms guard preserved)."""
    rt = _load_run_tests()
    body = textwrap.dedent(
        """
        def h2_hamiltonian():
            return [1.0, 0.5]  # list, not a Hamiltonian

        def run_vqe(steps=80, seed=0):
            return {"energy": -2.0}
        """
    )
    result = rt.run_tests(_write_candidate(tmp_path, body))
    assert not result["passed"]
    assert any("Hamiltonian-like" in d for d in result["details"]), result["details"]
