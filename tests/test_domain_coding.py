"""TDD tests for the coding domain monitor (evals/domain_monitor/domains/coding).

Contract (evals/domain_monitor/README.md):
  * manifest.json lists 10-15 EXISTING coding/SE benchmark task ids, each of
    which must appear verbatim in at least one evals/benchmarks/*.txt.
  * domain runners parse the standard eval JSON schema used across the repo
    (records[model, task_id, passed, scores.overall]) -- the same shape
    scripts/verdict_holdout.py::load_eval consumes.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CODING_DIR = REPO_ROOT / "evals" / "domain_monitor" / "domains" / "coding"
MANIFEST_PATH = CODING_DIR / "manifest.json"

# A real base-vs-adapter eval JSON in the run_asi2_base_adapter_rubric_eval /
# scripts.verdict_holdout schema that already lives in the repo.
REAL_EVAL_JSON = REPO_ROOT / "outputs" / "reeval_38_085136_step_000097_adapter.json"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _iter_benchmark_lines() -> set[str]:
    """Every task id line across all evals/benchmarks/*.txt (comments dropped)."""
    ids: set[str] = set()
    for txt in (REPO_ROOT / "evals" / "benchmarks").glob("*.txt"):
        for line in txt.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                ids.add(line)
    return ids


# ---------------------------------------------------------------------------
# manifest contract
# ---------------------------------------------------------------------------


def test_manifest_exists_and_is_json() -> None:
    assert MANIFEST_PATH.is_file(), f"missing {MANIFEST_PATH}"
    manifest = _load_manifest()
    assert manifest.get("domain") == "coding"


def test_manifest_has_between_10_and_15_task_ids() -> None:
    task_ids = _load_manifest()["task_ids"]
    assert 10 <= len(task_ids) <= 15, f"expected 10-15 ids, got {len(task_ids)}"
    assert len(set(task_ids)) == len(task_ids), "duplicate task ids in manifest"


def test_manifest_ids_are_coding_or_swe_flavored() -> None:
    # The vocabulary is the framework/SE surface this repo's coding tasks are
    # written against (Qiskit / Cirq / PennyLane / Stim) plus the SE concepts
    # they exercise. The original 10-token list omitted three frameworks
    # (cirq, pennylane, stim) and two task families (qaoa, grover, ...), so it
    # rejected genuine coding ids such as quantum_cirq_qaoa_line; completing it
    # keeps the "every id must be coding/SE flavored" requirement intact.
    flavors = (
        "qiskit",
        "cirq",
        "pennylane",
        "stim",
        "gate_",
        "circuit",
        "qaoa",
        "grover",
        "api_normalization",
        "canonicalizer",
        "codec",
        "decoder",
        "repair",
        "register",
        "software",
    )
    for tid in _load_manifest()["task_ids"]:
        assert any(f in tid for f in flavors), f"{tid} is not coding/SE flavored"
    # Non-vacuity (B-038 class): the vocabulary must still REJECT the
    # non-coding sciences, else the check above asserts nothing.
    non_coding = (
        "quantum_science_hamiltonian_simulation_qdrift_bound",
        "quantum_science_qec_surface_code_threshold",
        "density_matrix_partial_trace",
    )
    assert not any(
        f in tid for tid in non_coding for f in flavors
    ), "flavor vocabulary no longer discriminates coding from the other domains"


def test_every_manifest_id_exists_in_a_benchmarks_txt() -> None:
    available = _iter_benchmark_lines()
    task_ids = _load_manifest()["task_ids"]
    missing = [tid for tid in task_ids if tid not in available]
    assert not missing, f"manifest ids absent from evals/benchmarks/*.txt: {missing}"


def test_manifest_sources_point_at_real_files_containing_the_id() -> None:
    manifest = _load_manifest()
    for tid in manifest["task_ids"]:
        for rel in manifest["sources"][tid]:
            path = REPO_ROOT / rel
            assert path.is_file(), f"{tid}: source file missing: {rel}"
            lines = {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()}
            assert tid in lines, f"{tid} not found as a line in {rel}"


# ---------------------------------------------------------------------------
# eval JSON parsing (mirrors scripts/verdict_holdout.py)
# ---------------------------------------------------------------------------


def _parse_eval(eval_data: dict) -> list[dict]:
    """Extract coding-domain records in the verdict_holdout shape."""
    records = [
        {
            "model": r.get("model"),
            "task_id": r.get("task_id"),
            "passed": bool(r.get("passed")),
            "overall": (r.get("scores") or {}).get("overall", 0.0),
        }
        for r in eval_data.get("records", [])
    ]
    return records


def test_parser_reads_real_repo_eval_json() -> None:
    assert REAL_EVAL_JSON.is_file(), f"missing real eval JSON {REAL_EVAL_JSON}"
    eval_data = json.loads(REAL_EVAL_JSON.read_text(encoding="utf-8"))
    assert "records" in eval_data, "real eval JSON lacks records[]"
    records = _parse_eval(eval_data)
    assert records, "parser extracted no records from real eval JSON"
    for r in records:
        assert set(r) == {"model", "task_id", "passed", "overall"}
        assert isinstance(r["passed"], bool)
        assert isinstance(r["overall"], (int, float))


def test_parser_aligns_with_verdict_holdout_load_eval() -> None:
    """The shared schema must be readable by the reference repo parser too."""
    import sys

    sys.path.insert(0, str(REPO_ROOT))
    from scripts.verdict_holdout import load_eval

    eval_data = load_eval(REAL_EVAL_JSON)
    by_model: dict[str, list[dict]] = {}
    for r in eval_data["records"]:
        by_model.setdefault(r.get("model"), []).append(r)
    assert by_model, "verdict_holdout.load_eval found no models in real eval JSON"
    for model_records in by_model.values():
        for r in model_records:
            assert "task_id" in r and "passed" in r and "scores" in r


def test_real_eval_json_covers_manifest_coding_ids() -> None:
    """Sanity: at least one manifest id appears in the real eval JSON records."""
    eval_data = json.loads(REAL_EVAL_JSON.read_text(encoding="utf-8"))
    seen = {r.get("task_id") for r in eval_data.get("records", [])}
    overlap = seen & set(_load_manifest()["task_ids"])
    assert overlap, "real eval JSON shares no task ids with the coding manifest"
