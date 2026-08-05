"""Typed quantum-semantic verifiers (review 2026-08-05 #6, first piece).

A generic `1 - failures/detail_budget` verifier fraction depends on how many
assertions a test author happened to write and is not a reliable semantic
distance. Tasks may declare a ``verifier_type`` in ``task.json``; the matching
verifier then produces a CONTINUOUS semantic score in [0, 1] used as the shaped
``verifier_reward`` (the executable tests.py remains the authoritative pass
gate).

Implemented types:

- ``state_preparation``: candidate exposes ``meta["verifier_entry"]`` (default
  ``build_state``) returning amplitudes / a qiskit ``Statevector``; score =
  state fidelity vs the task's verified reference, randomized over
  ``meta["verifier_params"]`` when present. Fidelity ignores global phase
  (|⟨ψ|φ⟩|²), so equivalent states score 1.0.
- ``distribution``: candidate exposes a function returning a probability
  vector / counts dict; score = 1 - total-variation distance vs the reference
  distribution (correct for measured algorithms' output distributions).
- ``process_fidelity``: candidate exposes a function returning a
  ``QuantumCircuit``; score = process fidelity vs the reference unitary
  (gate/unitary synthesis tasks; equal up to global phase).

Tasks without ``verifier_type`` fall back to the generic verifier fraction.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any


def _load_candidate_module(code: str, task_dir: Path) -> Any:
    """Import candidate code from an isolated temp file (same pattern as the
    execution harness; candidates never see tests.py or the reference)."""
    with tempfile.TemporaryDirectory(prefix="fv_gspo_verifier_") as tmp_dir:
        candidate_path = Path(tmp_dir) / "candidate.py"
        candidate_path.write_text(code, encoding="utf-8")
        spec = importlib.util.spec_from_file_location(
            f"verifier_candidate_{uuid.uuid4().hex[:8]}", str(candidate_path)
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            return None
        return module


def _load_reference_module(task_dir: Path, meta: dict[str, Any]) -> Any:
    candidate_file = meta.get("candidate_file")
    if not candidate_file:
        return None
    ref_path = task_dir / str(candidate_file)
    if not ref_path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(
        f"verifier_reference_{uuid.uuid4().hex[:8]}", str(ref_path)
    )
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _entry_fn(module: Any, meta: dict[str, Any]) -> Callable | None:
    entry = meta.get("verifier_entry") or "build_state"
    fn = getattr(module, entry, None)
    return fn if callable(fn) else None


def _as_statevector(value: Any):
    from qiskit.quantum_info import Statevector

    if isinstance(value, Statevector):
        return value
    if isinstance(value, list):
        return Statevector(value)
    if hasattr(value, "to_statevector"):
        return value.to_statevector()
    return None


def _as_counts(value: Any) -> dict[str, float] | None:
    if isinstance(value, dict):
        return {str(k): float(v) for k, v in value.items()}
    if hasattr(value, "get_counts"):
        counts = value.get_counts()
        if isinstance(counts, dict):
            return {str(k): float(v) for k, v in counts.items()}
    return None


def _counts_to_probs(counts: dict[str, float]) -> dict[str, float]:
    total = max(1e-12, sum(counts.values()))
    return {k: v / total for k, v in counts.items()}


def _total_variation(p: dict[str, float], q: dict[str, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def verify_state_preparation(
    code: str, task_dir: Path, meta: dict[str, Any]
) -> dict[str, Any] | None:
    from qiskit.quantum_info import state_fidelity

    candidate = _load_candidate_module(code, task_dir)
    reference = _load_reference_module(task_dir, meta)
    candidate_fn = _entry_fn(candidate, meta) if candidate is not None else None
    reference_fn = _entry_fn(reference, meta) if reference is not None else None
    if candidate_fn is None or reference_fn is None:
        return None

    param_sets = meta.get("verifier_params") or [None]
    scores: list[float] = []
    for params in param_sets:
        try:
            candidate_state = _as_statevector(
                candidate_fn(params) if params is not None else candidate_fn()
            )
            reference_state = _as_statevector(
                reference_fn(params) if params is not None else reference_fn()
            )
        except Exception:
            return None
        if candidate_state is None or reference_state is None:
            return None
        if candidate_state.dim != reference_state.dim:
            return None
        try:
            scores.append(float(state_fidelity(candidate_state, reference_state)))
        except Exception:
            return None
    if not scores:
        return None
    return {
        "score": min(1.0, max(0.0, sum(scores) / len(scores))),
        "details": [f"state fidelity over {len(scores)} parameter set(s)"],
    }


def verify_distribution(code: str, task_dir: Path, meta: dict[str, Any]) -> dict[str, Any] | None:
    candidate = _load_candidate_module(code, task_dir)
    reference = _load_reference_module(task_dir, meta)
    candidate_fn = _entry_fn(candidate, meta) if candidate is not None else None
    reference_fn = _entry_fn(reference, meta) if reference is not None else None
    if candidate_fn is None or reference_fn is None:
        return None
    param_sets = meta.get("verifier_params") or [None]
    distances: list[float] = []
    for params in param_sets:
        try:
            candidate_counts = _as_counts(
                candidate_fn(params) if params is not None else candidate_fn()
            )
            reference_counts = _as_counts(
                reference_fn(params) if params is not None else reference_fn()
            )
        except Exception:
            return None
        if candidate_counts is None or reference_counts is None:
            return None
        tvd = _total_variation(
            _counts_to_probs(candidate_counts), _counts_to_probs(reference_counts)
        )
        distances.append(tvd)
    if not distances:
        return None
    mean_tvd = sum(distances) / len(distances)
    return {
        "score": min(1.0, max(0.0, 1.0 - mean_tvd)),
        "details": [f"mean total-variation distance {mean_tvd:.4f}"],
    }


def verify_process_fidelity(
    code: str, task_dir: Path, meta: dict[str, Any]
) -> dict[str, Any] | None:
    from qiskit.quantum_info import Operator, process_fidelity

    candidate = _load_candidate_module(code, task_dir)
    reference = _load_reference_module(task_dir, meta)
    candidate_fn = _entry_fn(candidate, meta) if candidate is not None else None
    reference_fn = _entry_fn(reference, meta) if reference is not None else None
    if candidate_fn is None or reference_fn is None:
        return None
    param_sets = meta.get("verifier_params") or [None]
    scores: list[float] = []
    for params in param_sets:
        try:
            candidate_circuit = candidate_fn(params) if params is not None else candidate_fn()
            reference_circuit = reference_fn(params) if params is not None else reference_fn()
            candidate_op = Operator(candidate_circuit)
            reference_op = Operator(reference_circuit)
        except Exception:
            return None
        if candidate_op.dim != reference_op.dim:
            return None
        try:
            scores.append(float(process_fidelity(candidate_op, reference_op)))
        except Exception:
            return None
    if not scores:
        return None
    return {
        "score": min(1.0, max(0.0, sum(scores) / len(scores))),
        "details": [f"process fidelity over {len(scores)} parameter set(s)"],
    }


TYPED_VERIFIERS: dict[str, Callable[[str, Path, dict[str, Any]], dict[str, Any] | None]] = {
    "state_preparation": verify_state_preparation,
    "distribution": verify_distribution,
    "process_fidelity": verify_process_fidelity,
}


def run_typed_verifier(code: str, task_dir: Path, meta: dict[str, Any]) -> dict[str, Any] | None:
    """Dispatch on ``meta["verifier_type"]``; None for untyped tasks or when
    the verifier cannot run (caller falls back to the generic fraction).

    Missing task fields (``candidate_file``, ``verifier_entry``) are merged
    from ``task_dir/task.json`` when present.
    """
    merged = dict(meta or {})
    if not merged.get("candidate_file"):
        task_json = Path(task_dir) / "task.json"
        if task_json.is_file():
            try:
                import json as _json

                merged.update(_json.loads(task_json.read_text(encoding="utf-8")))
            except Exception:
                pass
    verifier_type = merged.get("verifier_type")
    if not verifier_type:
        return None
    verifier = TYPED_VERIFIERS.get(str(verifier_type))
    if verifier is None:
        return None
    try:
        return verifier(code, task_dir, merged)
    except Exception:
        return None


def score_from_typed_verifier(
    code: str, task_dir: Path, meta: dict[str, Any]
) -> tuple[float, dict[str, Any] | None]:
    """Continuous verifier score + info for the trainer; (fallback, None) when
    the task is untyped or verification cannot run."""
    result = run_typed_verifier(code, task_dir, meta)
    if result is None:
        return 0.0, None
    return float(result.get("score", 0.0)), result
