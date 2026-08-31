"""Regression: version-fragile holdout scorers (2026-08-25 QA round 2).

Same class as the vqe_h2 fix: the enriched/reverted scorers failed their own
REFERENCES on pennylane 0.38/0.45 and qiskit 1.4/2.x.

- qiskit_qft_entangled: QFT of GHZ has EXACTLY 7 non-zero amplitudes (one
  null at bitstring 100 for the no-swap convention) — the old all-8-uniform
  expectation is mathematically wrong and failed the reference on every
  qiskit version.
- pennylane_qml_iris_classification: fp64 kernel entries land at
  1.0000000000000004 — the exact [0,1] bounds failed the reference.

The version-aware forms must: reference passes, genuinely bad candidates
fail (binary invariance) — under whichever SDK version the suite host has.
"""

from __future__ import annotations

import importlib.util
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

try:
    import qiskit  # noqa: F401
except Exception:  # pragma: no cover
    qiskit = None  # type: ignore[assignment]

try:
    import pennylane  # noqa: F401
except Exception:  # pragma: no cover
    pennylane = None  # type: ignore[assignment]

QFT_DIR = ROOT / "evals" / "tasks" / "quantum" / "qiskit_qft_entangled"
IRIS_DIR = ROOT / "evals" / "tasks" / "quantum" / "pennylane_qml_iris_classification"


def _load_run_tests(dir_path: Path) -> object:
    spec = importlib.util.spec_from_file_location("t", str(dir_path / "tests.py"))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _write(tmp_path: Path, body: str) -> str:
    p = tmp_path / "candidate.py"
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return str(p)


# ─────────────────────────────── QFT ───────────────────────────────


@pytest.mark.skipif(qiskit is None, reason="requires qiskit on this host")
def test_qft_reference_candidate_passes() -> None:
    rt = _load_run_tests(QFT_DIR)
    result = rt.run_tests(str(QFT_DIR / "candidate.py"))
    assert result["passed"], result["details"]


@pytest.mark.skipif(qiskit is None, reason="requires qiskit on this host")
def test_qft_bad_candidates_still_fail(tmp_path: Path) -> None:
    rt = _load_run_tests(QFT_DIR)
    # Plain GHZ without QFT: 2 amplitudes -> fails the 7-8 count.
    ghz_only = _write(
        tmp_path,
        """
        import numpy as np
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector

        def ghz_circuit(n=3):
            c = QuantumCircuit(n)
            c.h(0)
            for i in range(n - 1):
                c.cx(i, i + 1)
            return c

        def qft_circuit(n=3):
            c = QuantumCircuit(n)
            c.h(0)
            return c

        def ghz_then_qft_statevector(n=3):
            c = ghz_circuit(n)
            c.compose(qft_circuit(n), inplace=True)
            return np.asarray(Statevector.from_instruction(c).data)

        def amplitude_histogram(n=3, tol=1e-9):
            sv = ghz_then_qft_statevector(n)
            return {format(i, f"0{n}b"): complex(a) for i, a in enumerate(sv) if abs(a) > tol}
        """,
    )
    result = rt.run_tests(ghz_only)
    assert not result["passed"], "GHZ-only candidate must not pass"
    assert any("non-zero amplitudes" in d for d in result["details"]), result["details"]


# ─────────────────────────────── IRIS ───────────────────────────────


@pytest.mark.skipif(pennylane is None, reason="requires pennylane on this host")
def test_iris_reference_candidate_passes() -> None:
    rt = _load_run_tests(IRIS_DIR)
    result = rt.run_tests(str(IRIS_DIR / "candidate.py"))
    assert result["passed"], result["details"]


@pytest.mark.skipif(pennylane is None, reason="requires pennylane on this host")
def test_iris_out_of_bounds_kernel_still_fails(tmp_path: Path) -> None:
    """A kernel matrix with entries far outside [0,1] must still fail (the
    tolerance is 1e-9, not lax)."""
    bad = _write(
        tmp_path,
        """
        import numpy as np

        def kernel_value(x, y):
            return 1.0 if x == y else 0.5

        def iris_2class_subset(seed=0):
            rng = np.random.default_rng(seed)
            X = rng.random((20, 4))
            y = np.array([0] * 10 + [1] * 10)
            return X, y

        def kernel_matrix(X1, X2):
            return np.full((20, 20), 1.7)  # far outside [0,1]

        def run_pipeline():
            return {"accuracy": 0.99}
        """,
    )
    rt = _load_run_tests(IRIS_DIR)
    result = rt.run_tests(bad)
    assert not result["passed"], "out-of-bounds kernel must not pass"
    assert any("kernel_matrix entries" in d for d in result["details"]), result["details"]
