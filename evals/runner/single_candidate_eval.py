#!/usr/bin/env python3
"""single_candidate_eval.py — evaluate ONE candidate code file against a task
harness (tests.py) + typed verifier in a FRESH interpreter.

Why: the trainer runs the 27B sharded across NPUs in one process. Importing a
generated candidate in-process lets the candidate's own imports (e.g. qiskit's
parallel_map) fork multiprocessing workers OUT of the NPU-laden trainer and
deadlock at 0% CPU (observed 2026-08-21: step-1 eval hung 27+ min in the
forked eval worker on ASI3). Running the whole candidate evaluation as a
subprocess with a hard timeout makes eval fork-safe and bounded.

Usage:
  python3 single_candidate_eval.py --candidate <path> --tests <tests.py> \
      --task-dir <task_dir> --meta <meta.json> [--timeout 300]

Prints one JSON line to stdout:
  {"harness": {...}, "typed_score": float, "typed_info": {...} | null,
   "error": null | "phase: message"}
Exit 0 on success (even if the candidate fails), 2 on usage error.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing as _mp
import sys
from pathlib import Path

from candidate_sanitize import sanitize_candidate_text
from candidate_security import reject_candidate_source

ROOT = Path(__file__).resolve().parents[2]

# 2026-09-13 (fork-deadlock class, live): this runner executes candidate code in
# a fresh interpreter, but a task's candidate/tests may themselves spawn worker
# processes (qiskit internals, Aer backends). On some platforms/multiprocessing
# versions the default `fork` start method hands a forked child a qiskit/Rust
# lock and it hangs at 0% CPU. Force `spawn` (fresh re-import per worker) so no
# inherited locked state can wedge the eval subprocess. Fail closed: if both
# spawn and forkserver are unsupported we still prefer spawn.
try:
    _mp.set_start_method("spawn", force=True)
except (RuntimeError, ValueError):
    try:
        _mp.set_start_method("spawn")
    except Exception:
        pass


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _clean(value):
    """Make harness/verifier output JSON-safe (details may hold exceptions).

    Bools/numbers must survive verbatim: the trainer does ``bool(result["passed"])``,
    and str() of False would be truthy.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    return str(value)


def _sanitize_candidate_file(candidate_path: str) -> dict | None:
    # C-0005 (2026-09-16), fence-import failure class: holdout legs score
    # candidates written by box-side producers we do not always control
    # (stale-deploy class, B-163): the Sep-8 18-task reeval lost 13/15
    # failing tasks at import on candidates starting with a markdown code
    # fence or truncated mid-fence/mid-docstring (reeval_38_094427Z s97).
    # Sanitize at the import boundary -- the one gate every producer
    # funnels into -- so a fenced/truncated file is repaired before
    # tests.run_tests imports it, regardless of producer staleness.
    # Fail-closed ordering: the security policy scans BOTH the raw file
    # (pre-existing behavior) and the sanitized text that will actually
    # execute; sanitization must never launder a rejection. The file is
    # rewritten in place so verdict-side candidate-diff instruments see
    # the code that actually ran.
    path = Path(candidate_path)
    raw = path.read_text(encoding="utf-8")
    rejection = reject_candidate_source(raw)
    if rejection is not None:
        return rejection
    sanitized = sanitize_candidate_text(raw)
    if sanitized == raw:
        return None
    rejection = reject_candidate_source(sanitized)
    if rejection is not None:
        return rejection
    path.write_text(sanitized, encoding="utf-8")
    return None


def run_harness(candidate_path: str, tests_path: Path) -> dict:
    rejection = _sanitize_candidate_file(candidate_path)
    if rejection is not None:
        return rejection
    tests = _load_module(tests_path, f"tests_{tests_path.stem}")
    if not hasattr(tests, "run_tests"):
        raise AttributeError(f"{tests_path} has no run_tests()")
    result = tests.run_tests(candidate_path)
    if not isinstance(result, dict):
        return {
            "passed": False,
            "details": [f"Unexpected harness return type: {type(result).__name__}"],
        }
    return _clean(result)


def run_typed(candidate_code: str, task_dir: Path, meta: dict) -> tuple:
    """Mirror training/quantum_verifiers.run_typed_verifier dispatch."""
    try:
        sys.path.insert(0, str(ROOT / "training"))
        from quantum_verifiers import TYPED_VERIFIERS  # noqa: PLC0415
    except Exception:
        return None, None
    merged = dict(meta or {})
    if not merged.get("candidate_file"):
        task_json = task_dir / "task.json"
        if task_json.is_file():
            try:
                merged.update(json.loads(task_json.read_text(encoding="utf-8")))
            except Exception:
                pass
    verifier_type = merged.get("verifier_type")
    if not verifier_type:
        return None, None
    verifier = TYPED_VERIFIERS.get(str(verifier_type))
    if verifier is None:
        return None, None
    try:
        info = verifier(candidate_code, task_dir, merged)
    except Exception:
        return None, None
    if info is None:
        return None, None
    return float(info.get("score", 0.0)), _clean(info)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--tests", required=True, type=Path)
    parser.add_argument("--task-dir", required=True, type=Path)
    parser.add_argument("--meta", type=Path, default=None)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    out: dict = {"harness": None, "typed_score": 0.0, "typed_info": None, "error": None}
    try:
        out["harness"] = run_harness(str(args.candidate), args.tests)
        meta = {}
        if args.meta and args.meta.is_file():
            meta = json.loads(args.meta.read_text(encoding="utf-8"))
        code = args.candidate.read_text(encoding="utf-8")
        score, info = run_typed(code, args.task_dir, meta)
        out["typed_score"], out["typed_info"] = score, info
    except Exception as exc:  # noqa: BLE001 - any eval error must not kill the step
        out["error"] = f"{type(exc).__name__}: {exc}"
        if out["harness"] is None:
            out["harness"] = {"passed": False, "details": [out["error"]]}

    print(json.dumps(out, ensure_ascii=False, default=str), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
