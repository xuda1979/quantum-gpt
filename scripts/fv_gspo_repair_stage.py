#!/usr/bin/env python3
"""FV-GSPO repair stage: convert all-fail repair-queue records into verified SFT/DPO.

Consumes the trainer's `repair_queue.jsonl` (written by
`training/grpo_trainer.py` when the frontier router routes a group to
`repair_sft`). For each queued record (current-adapter failing candidate +
exact test failures) this stage:

1. obtains a smallest correction (trusted teacher via ``--teacher-command``,
   or the task's verified reference ``candidate.py`` as fallback);
2. executes the correction against the *same* task harness
   (``tests.py::run_tests``); the correction is rejected unless ALL tests pass;
3. emits ``repair_converted.jsonl`` (the conversion feed read by the trainer's
   ``all_fail_without_repair`` circuit breaker) and
4. emits ``repair_sft.jsonl`` and ``repair_dpo.jsonl`` in the repository's
   DPO pair schema (chosen = verified correction; rejected = the exact
   failing rollout with its traceback retained).

Usage:
    python3 scripts/fv_gspo_repair_stage.py \
        --queue <run>/repair_queue.jsonl \
        --tasks-dir evals/tasks \
        --output <run>/repair_stage \
        [--teacher-command 'bash scripts/ask_teacher.sh'] \
        [--limit N] [--require-traceback]

Design reference: docs/frontier-verifier-gspo-design-2026-08-04.md §5.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_utils import (  # noqa: E402
    extract_behavior_hints_from_test_source,
    summarize_python_interface,
)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def load_test_harness(tests_py: Path):
    spec = importlib.util.spec_from_file_location(
        f"repair_tests_{uuid.uuid4().hex[:6]}", str(tests_py)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_candidate_against_harness(code: str, tests_py: Path, task_dir: Path) -> dict[str, Any]:
    """Execute candidate code against the task's tests.py harness.

    The candidate is written inside ``task_dir`` because the harnesses import
    the candidate by path (the same pattern the GRPO trainer uses).
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=str(task_dir)
    ) as handle:
        handle.write(code)
        handle.flush()
        path = handle.name
    try:
        harness = load_test_harness(tests_py)
        result = harness.run_tests(path)
        if not isinstance(result, dict):
            result = {"passed": False, "details": [f"Unexpected harness return: {type(result)}"]}
    except Exception as exc:
        result = {"passed": False, "details": [f"{type(exc).__name__}: {exc}"]}
    finally:
        Path(path).unlink(missing_ok=True)
    return result


def classify_failure(details: list[str]) -> str:
    """Best-effort failure category; falls back to a generic label.

    Mirrors evals/subsystem/harness.py::classify_failure without importing the
    full eval subsystem.
    """
    text = " ".join(str(d) for d in details)
    if "SyntaxError" in text:
        return "syntax_error"
    if any(marker in text for marker in ("ImportError", "ModuleNotFoundError")):
        return "import_error"
    if "TimeoutError" in text or "timed out" in text:
        return "timeout"
    if any(marker in text for marker in ("NameError", "AttributeError", "TypeError")):
        return "runtime_error"
    if "AssertionError" in text or "assert" in text.lower():
        return "assertion_failure"
    return "unknown_failure"


def build_task_prompt(meta: dict[str, Any], failing_code: str, failures: list[str]) -> list[dict]:
    """ChatML prompt: task spec + failing program + exact failures (repair task)."""
    parts = [f"Task: {meta.get('description', meta.get('name', meta.get('id', '?')))}"]
    parts.append(f"Domain: {meta.get('domain', 'unknown')}")
    parts.append("The program below fails its test harness. Fix it with the smallest correction.")
    parts.append("FAILING PROGRAM:\n```python\n" + failing_code + "\n```")
    if failures:
        parts.append("EXACT TEST FAILURES:\n- " + "\n- ".join(failures[:8]))
    parts.append("Return only the final corrected Python code.")
    return [
        {
            "role": "system",
            "content": "You are a careful coding assistant that repairs failing code.",
        },
        {"role": "user", "content": "\n\n".join(parts)},
    ]


def ask_teacher(
    teacher_command: list[str] | None,
    record: dict[str, Any],
    task_dir: Path,
) -> str | None:
    """Ask the trusted teacher for the smallest correction.

    The teacher receives a JSON record on stdin (task metadata + failing code +
    exact failures) and must print the corrected code (or JSON with a ``code``
    field) on stdout. Returns None when no teacher is configured.
    """
    if not teacher_command:
        return None
    payload = {
        "task_id": record.get("task_id"),
        "task_dir": str(task_dir),
        "best_code": record.get("best_code"),
        "failures": record.get("failures", []),
    }
    proc = subprocess.run(
        teacher_command,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.returncode != 0:
        return None
    out = proc.stdout.strip()
    try:
        parsed = json.loads(out)
        if isinstance(parsed, dict) and parsed.get("code"):
            return str(parsed["code"])
    except json.JSONDecodeError:
        pass
    return out or None


def load_reference_correction(task_dir: Path, meta: dict[str, Any]) -> str | None:
    """Fallback correction: the task's verified reference candidate.py."""
    candidate_file = meta.get("candidate_file")
    if not candidate_file:
        return None
    path = task_dir / candidate_file
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--queue", required=True, type=Path)
    p.add_argument("--tasks-dir", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument(
        "--teacher-command",
        nargs=argparse.REMAINDER,
        default=None,
        help="Teacher CLI (e.g. --teacher-command bash scripts/ask_teacher.sh). "
        "Receives a JSON record on stdin, prints corrected code on stdout. "
        "Defaults to the task's verified reference candidate.py.",
    )
    p.add_argument(
        "--limit", type=int, default=0, help="Process at most N queue records (0 = all)."
    )
    p.add_argument(
        "--require-traceback",
        action="store_true",
        default=False,
        help="Skip records without retained failure details (exact failures required).",
    )
    return p.parse_args()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.queue.is_file():
        print(f"error: repair queue not found: {args.queue}", file=sys.stderr)
        return 2
    if not args.tasks_dir.is_dir():
        print(f"error: tasks dir not found: {args.tasks_dir}", file=sys.stderr)
        return 2
    args.output.mkdir(parents=True, exist_ok=True)
    converted_path = args.output / "repair_converted.jsonl"
    sft_path = args.output / "repair_sft.jsonl"
    dpo_path = args.output / "repair_dpo.jsonl"

    records = _load_jsonl(args.queue)
    if args.limit > 0:
        records = records[: args.limit]
    if not records:
        print("no queue records; nothing to do", file=sys.stderr)
        return 0

    seen_converted = {str(r.get("dedup_key", "")) for r in _load_jsonl(converted_path)}
    converted = 0
    rejected = 0
    skipped_no_task = 0
    skipped_no_failures = 0

    for record in records:
        dedup_key = str(record.get("dedup_key") or "")
        if dedup_key and dedup_key in seen_converted:
            continue
        task_id = str(record.get("task_id") or "")
        failures = [str(f) for f in (record.get("failures") or [])]
        if args.require_traceback and not failures:
            skipped_no_failures += 1
            continue

        # Locate the task by id: <domain>/<suffix> directory names.
        task_dir: Path | None = None
        meta: dict[str, Any] = {}
        for domain_dir in sorted(args.tasks_dir.iterdir()):
            if not domain_dir.is_dir():
                continue
            for candidate in sorted(domain_dir.iterdir()):
                if not candidate.is_dir():
                    continue
                task_json = candidate / "task.json"
                if task_json.is_file():
                    try:
                        loaded = json.loads(task_json.read_text(encoding="utf-8"))
                    except json.JSONDecodeError:
                        continue
                    if str(loaded.get("id", candidate.name)) == task_id:
                        task_dir = candidate
                        meta = loaded
                        break
            if task_dir is not None:
                break
        if task_dir is None:
            print(f"skip {task_id}: task not found in {args.tasks_dir}", file=sys.stderr)
            skipped_no_task += 1
            continue

        tests_py = task_dir / "tests.py"
        if not tests_py.is_file():
            print(f"skip {task_id}: tests.py missing", file=sys.stderr)
            skipped_no_task += 1
            continue

        failing_code = str(record.get("best_code") or "")
        # 1) obtain a correction (teacher first, verified reference fallback)
        correction = ask_teacher(args.teacher_command, record, task_dir)
        corrected_by = "teacher"
        if correction is None:
            correction = load_reference_correction(task_dir, meta)
            corrected_by = "reference"
        if correction is None or not correction.strip():
            print(f"skip {task_id}: no correction source available", file=sys.stderr)
            rejected += 1
            continue

        # 2) execution-grounded verification against the same harness
        result = run_candidate_against_harness(correction, tests_py, task_dir)
        passed = bool(result.get("passed")) if isinstance(result, dict) else False
        details = (
            [str(d) for d in (result.get("details") or [])] if isinstance(result, dict) else []
        )

        conversion = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "task_id": task_id,
            "dedup_key": dedup_key,
            "step": record.get("step"),
            "converted": passed,
            "corrected_by": corrected_by,
            "failure_category": classify_failure(failures),
            "verification_details": details[:4],
        }
        converted_path.open("a", encoding="utf-8").write(
            json.dumps(conversion, sort_keys=True) + "\n"
        )
        seen_converted.add(dedup_key)
        if not passed:
            rejected += 1
            continue
        converted += 1

        # 3) emit SFT/DPO records in the repository pair schema
        required_interface = summarize_python_interface(
            (task_dir / str(meta.get("candidate_file", "candidate.py"))).read_text(encoding="utf-8")
            if meta.get("candidate_file") and (task_dir / str(meta.get("candidate_file"))).is_file()
            else ""
        )
        behavior_hints = extract_behavior_hints_from_test_source(
            tests_py.read_text(encoding="utf-8"), cap=6
        )
        prompt = build_task_prompt(meta, failing_code, failures)
        if required_interface:
            prompt[1]["content"] += "\n\nRequired interface:\n" + "\n".join(
                f"- {line}" for line in required_interface
            )
        if behavior_hints:
            prompt[1]["content"] += "\n\nBehavioral requirements:\n" + "\n".join(
                f"- {line}" for line in behavior_hints
            )
        chosen = [{"role": "assistant", "content": correction}]
        rejected_side = [{"role": "assistant", "content": failing_code}]
        pair_id = hashlib.sha256(f"{task_id}:{dedup_key}:{corrected_by}".encode()).hexdigest()[:16]

        sft_record = {
            "prompt": prompt,
            "chosen": chosen,
            "task_id": task_id,
            "pair_id": pair_id,
            "failure_category": classify_failure(failures),
            "source": "fv_gspo_repair_stage",
        }
        sft_path.open("a", encoding="utf-8").write(json.dumps(sft_record, sort_keys=True) + "\n")

        if failing_code.strip():
            dpo_record = {
                "prompt": prompt,
                "chosen": chosen,
                "rejected": rejected_side,
                "task_id": task_id,
                "pair_id": pair_id,
                "failure_category": classify_failure(failures),
                "source": "fv_gspo_repair_stage",
            }
            dpo_path.open("a", encoding="utf-8").write(
                json.dumps(dpo_record, sort_keys=True) + "\n"
            )

    print(
        json.dumps(
            {
                "records_processed": len(records),
                "converted": converted,
                "rejected": rejected,
                "skipped_no_task": skipped_no_task,
                "skipped_no_failures": skipped_no_failures,
                "converted_path": str(converted_path),
                "sft_path": str(sft_path),
                "dpo_path": str(dpo_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
