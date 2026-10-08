from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def aggregate_sha256(payload: dict[str, Any]) -> str:
    return sha256_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


def repo_relative(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(root.resolve()))
    except ValueError:
        return str(resolved)


def resolve_repo_file(root: Path, value: str, label: str) -> Path:
    root = root.resolve()
    path = Path(value)
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    if not path.is_absolute():
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise SystemExit(f"Frozen {label} escapes repository root: {value}") from exc
    if not resolved.is_file():
        raise SystemExit(f"Frozen {label} is missing: {resolved}")
    return resolved


def verify_frozen_eval_contract(
    run_dir: Path,
    manifest: dict[str, Any],
    *,
    root: Path,
    verify_runner: bool = True,
) -> dict[str, str | None]:
    """Verify all immutable model-visible and scoring inputs for a run.

    Historical manifests remain readable: a contract is verified only when its
    corresponding hash is present. Promotion runs are expected to contain every
    hash written by ``prepare_prompts.py``.
    """
    run_dir = run_dir.resolve()
    root = root.resolve()

    expected_task_id_file = manifest.get("task_id_file_sha256")
    if expected_task_id_file is not None:
        task_id_path = resolve_repo_file(
            root, str(manifest.get("task_id_file", "")), "task-id manifest"
        )
        actual_task_id_file = sha256_file(task_id_path)
        if actual_task_id_file != expected_task_id_file:
            raise SystemExit(
                "Frozen task-id manifest hash mismatch: "
                f"expected {expected_task_id_file}, got {actual_task_id_file} "
                f"({task_id_path})"
            )

    expected_system = manifest.get("system_prompt_sha256")
    if expected_system is not None:
        system_path = run_dir / "SYSTEM_PROMPT.txt"
        actual_system = sha256_file(system_path)
        if actual_system != expected_system:
            raise SystemExit(
                "Frozen system prompt hash mismatch: "
                f"expected {expected_system}, got {actual_system} ({system_path})"
            )

    public_records: list[dict[str, str]] = []
    scorer_records: list[dict[str, str]] = []
    for task in manifest.get("tasks", []):
        task_id = str(task["id"])
        expected_prompt = task.get("prompt_sha256")
        if expected_prompt is not None:
            prompt_path = run_dir / str(task["prompt_file"])
            if not prompt_path.is_file():
                raise SystemExit(f"Frozen prompt file missing for {task_id}: {prompt_path}")
            actual_prompt = sha256_file(prompt_path)
            if actual_prompt != expected_prompt:
                raise SystemExit(
                    f"Frozen prompt hash mismatch for {task_id}: "
                    f"expected {expected_prompt}, got {actual_prompt} ({prompt_path})"
                )
            public_records.append(
                {
                    "id": task_id,
                    "prompt_sha256": str(expected_prompt),
                    "task_json_sha256": str(task.get("task_json_sha256", "")),
                }
            )

        expected_task_json = task.get("task_json_sha256")
        task_json_file = task.get("task_json_file")
        if expected_task_json is not None and task_json_file is not None:
            task_json_path = resolve_repo_file(
                root, str(task_json_file), f"task metadata for {task_id}"
            )
            actual_task_json = sha256_file(task_json_path)
            if actual_task_json != expected_task_json:
                raise SystemExit(
                    f"Frozen task metadata hash mismatch for {task_id}: "
                    f"expected {expected_task_json}, got {actual_task_json} "
                    f"({task_json_path})"
                )

        expected_test = task.get("test_file_sha256")
        test_file = task.get("test_file")
        if expected_test is not None and test_file is None:
            raise SystemExit(
                f"Frozen scorer hash present for {task_id} but test_file path is missing"
            )
        if expected_test is not None and test_file is not None:
            test_path = resolve_repo_file(root, str(test_file), f"scorer for {task_id}")
            actual_test = sha256_file(test_path)
            if actual_test != expected_test:
                raise SystemExit(
                    f"Frozen scorer hash mismatch for {task_id}: "
                    f"expected {expected_test}, got {actual_test} ({test_path})"
                )
            scorer_records.append(
                {
                    "id": task_id,
                    "task_json_sha256": str(expected_task_json or ""),
                    "test_file_sha256": str(expected_test),
                }
            )

    expected_public = manifest.get("public_eval_contract_sha256")
    actual_public = None
    if expected_public is not None:
        actual_public = aggregate_sha256(
            {
                "system_prompt_sha256": str(expected_system or ""),
                "tasks": public_records,
            }
        )
        if actual_public != expected_public:
            raise SystemExit(
                "Frozen public evaluation contract hash mismatch: "
                f"expected {expected_public}, got {actual_public}"
            )

    expected_runner = manifest.get("evaluation_runner_sha256")
    actual_runner = None
    if expected_runner is not None and verify_runner:
        runner_path = root / "evals" / "runner" / "run_eval.py"
        actual_runner = sha256_file(runner_path)
        if actual_runner != expected_runner:
            raise SystemExit(
                "Frozen evaluation runner hash mismatch: "
                f"expected {expected_runner}, got {actual_runner} ({runner_path})"
            )

    expected_scorer = manifest.get("scorer_contract_sha256")
    actual_scorer = None
    if expected_scorer is not None:
        actual_scorer = aggregate_sha256(
            {
                "evaluation_runner_sha256": str(expected_runner or ""),
                "tasks": scorer_records,
            }
        )
        if actual_scorer != expected_scorer:
            raise SystemExit(
                "Frozen scorer contract hash mismatch: "
                f"expected {expected_scorer}, got {actual_scorer}"
            )

    return {
        "public_eval_contract_sha256": actual_public,
        "scorer_contract_sha256": actual_scorer,
        "evaluation_runner_sha256": actual_runner,
    }
