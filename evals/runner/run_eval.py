from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from evals.runner.task_metadata import resolve_test_path
except ModuleNotFoundError:  # pragma: no cover - script execution path
    from task_metadata import resolve_test_path

ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = ROOT / "evals" / "tasks"

SYNTAX_ERROR_NAMES = {"SyntaxError", "IndentationError", "TabError"}
DEPENDENCY_ERROR_NAMES = {"ImportError", "ModuleNotFoundError"}
PACKAGING_ERROR_HINTS = (
    "missing test file",
    "workspace directory not found",
    "candidate directory override",
)


def discover_tasks() -> list[Path]:
    return sorted(TASKS_ROOT.glob("*/*/task.json"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def classify_exception(exc: BaseException) -> str:
    error_name = type(exc).__name__
    if error_name in SYNTAX_ERROR_NAMES:
        return "syntax"
    if error_name in DEPENDENCY_ERROR_NAMES:
        return "dependency"
    if isinstance(exc, AssertionError):
        return "assertion"
    if isinstance(exc, FileNotFoundError):
        return "packaging"

    message = str(exc).lower()
    if isinstance(exc, ValueError) and any(hint in message for hint in PACKAGING_ERROR_HINTS):
        return "packaging"
    return "runtime"


def classify_failure_details(details: list[str]) -> str:
    combined = "\n".join(details)
    combined_lower = combined.lower()

    if any(name in combined for name in SYNTAX_ERROR_NAMES):
        return "syntax"
    if any(name in combined for name in DEPENDENCY_ERROR_NAMES):
        return "dependency"
    if any(hint in combined_lower for hint in PACKAGING_ERROR_HINTS):
        return "packaging"
    return "assertion"


def summarize_failure_categories(results: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(
        str(result["failure_category"]) for result in results if result.get("failure_category")
    )
    return dict(sorted(counts.items()))


def load_test_module(test_path: Path):
    spec = importlib.util.spec_from_file_location(test_path.stem, test_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load test module: {test_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_candidate_overrides(path: Path | None) -> dict[str, Path]:
    if path is None:
        return {}

    path = path.resolve()
    payload = load_json(path)
    base_dir = path.parent
    overrides: dict[str, Path] = {}

    for task_id, candidate_value in payload.items():
        candidate_path = Path(candidate_value)
        if not candidate_path.is_absolute():
            candidate_path = (base_dir / candidate_path).resolve()
        overrides[task_id] = candidate_path

    return overrides


def resolve_candidate_paths(
    metadata: dict[str, Any], task_dir: Path, override_path: Path | None
) -> tuple[dict[str, Path], str]:
    candidate_files = metadata.get("candidate_files")
    if candidate_files:
        source = "override" if override_path else "reference"
        if override_path:
            override_root = override_path
            if override_root.is_file():
                raise ValueError(
                    f"Task {metadata['id']} expects a candidate directory override, got file: {override_root}"
                )
            return {
                relative_path: override_root / relative_path for relative_path in candidate_files
            }, source

        return {
            relative_path: task_dir / relative_path for relative_path in candidate_files
        }, source

    candidate_file = metadata["candidate_file"]
    return {
        candidate_file: override_path or (task_dir / candidate_file)
    }, "override" if override_path else "reference"


def run_single_file_task(module: Any, candidate_path: Path) -> dict[str, Any]:
    return module.run_tests(str(candidate_path))


def run_workspace_task(
    module: Any, task_dir: Path, metadata: dict[str, Any], candidate_paths: dict[str, Path]
) -> dict[str, Any]:
    workspace_dir_value = metadata.get("workspace_dir")
    if not workspace_dir_value:
        raise ValueError(f"Task {metadata['id']} declares candidate_files but no workspace_dir")

    workspace_src = task_dir / workspace_dir_value
    if not workspace_src.exists():
        raise FileNotFoundError(
            f"Workspace directory not found for task {metadata['id']}: {workspace_src}"
        )

    with tempfile.TemporaryDirectory(prefix=f"eval-{metadata['id']}-") as tmpdir:
        temp_root = Path(tmpdir)
        shutil.copytree(workspace_src, temp_root, dirs_exist_ok=True)

        for relative_path, source_path in candidate_paths.items():
            destination = temp_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, destination)

        sys.path.insert(0, str(temp_root))
        try:
            if hasattr(module, "run_workspace_tests"):
                return module.run_workspace_tests(
                    str(temp_root), [str(temp_root / rel) for rel in candidate_paths]
                )
            return module.run_tests(str(temp_root))
        finally:
            if sys.path and sys.path[0] == str(temp_root):
                sys.path.pop(0)


def run_task(
    task_json_path: Path, candidate_overrides: dict[str, Path] | None = None
) -> dict[str, Any]:
    task_dir = task_json_path.parent
    metadata = load_json(task_json_path)
    override_path = (candidate_overrides or {}).get(metadata["id"])
    candidate_paths: dict[str, Path] = {}
    source = "override" if override_path else "reference"

    try:
        test_path = resolve_test_path(task_dir, metadata)
        candidate_paths, source = resolve_candidate_paths(metadata, task_dir, override_path)
        module = load_test_module(test_path)
        if metadata.get("candidate_files"):
            result = run_workspace_task(module, task_dir, metadata, candidate_paths)
        else:
            only_candidate_path = next(iter(candidate_paths.values()))
            result = run_single_file_task(module, only_candidate_path)
        passed = bool(result.get("passed", False))
        details = list(result.get("details", []))
        error_type = None
        failure_category = None if passed else classify_failure_details(details)
    except Exception as exc:
        passed = False
        error_type = type(exc).__name__
        failure_category = classify_exception(exc)
        details = [
            f"runner_exception: {error_type}: {exc}",
            "traceback:",
            *traceback.format_exc().strip().splitlines(),
        ]

    return {
        "id": metadata["id"],
        "domain": metadata["domain"],
        "category": metadata["category"],
        "name": metadata["name"],
        "passed": passed,
        "details": details,
        "candidate_path": str(next(iter(candidate_paths.values())))
        if candidate_paths
        else str(override_path or ""),
        "candidate_paths": {relative: str(path) for relative, path in candidate_paths.items()},
        "workspace_mode": bool(metadata.get("candidate_files")),
        "source": source,
        "error_type": error_type,
        "failure_category": failure_category,
    }


def summarize(results: list[dict[str, Any]]) -> None:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"Overall: {passed}/{total} passed")

    for domain in sorted({r["domain"] for r in results}):
        subset = [r for r in results if r["domain"] == domain]
        ok = sum(1 for r in subset if r["passed"])
        print(f"  {domain}: {ok}/{len(subset)} passed")

    for category in sorted({r["category"] for r in results}):
        subset = [r for r in results if r["category"] == category]
        ok = sum(1 for r in subset if r["passed"])
        print(f"  {category}: {ok}/{len(subset)} passed")

    failure_counts = summarize_failure_categories(results)
    if failure_counts:
        print("  failure_categories:")
        for failure_category, count in failure_counts.items():
            print(f"    {failure_category}: {count}")


def maybe_write_scorecard(
    results: list[dict[str, Any]], candidate_map_path: Path | None
) -> Path | None:
    if candidate_map_path is None:
        return None

    run_dir = candidate_map_path.resolve().parent
    scorecard_path = run_dir / "scorecard.json"

    manifest_path = run_dir / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else None

    payload = {
        "scored_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_map": str(candidate_map_path.resolve()),
        "backend": manifest.get("backend") if manifest else None,
        "prompt_style": manifest.get("prompt_style") if manifest else None,
        "prompt_version": manifest.get("prompt_version") if manifest else None,
        "failure_category_summary": summarize_failure_categories(results),
        "results": results,
    }
    scorecard_path.write_text(json.dumps(payload, indent=2) + "\n")
    return scorecard_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local eval tasks against reference or override candidate files."
    )
    parser.add_argument(
        "--candidate-map",
        type=Path,
        default=None,
        help="Optional JSON file mapping task ids to candidate file paths.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    task_files = discover_tasks()
    if not task_files:
        raise SystemExit("No tasks found under evals/tasks")

    candidate_overrides = load_candidate_overrides(args.candidate_map)
    results = [run_task(path, candidate_overrides) for path in task_files]

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['id']} - {result['name']} ({result['source']})")
        print(f"    candidate: {result['candidate_path']}")
        for detail in result["details"]:
            print(f"    - {detail}")

    summarize(results)
    scorecard_path = maybe_write_scorecard(results, args.candidate_map)
    if scorecard_path is not None:
        print(f"Scorecard written to: {scorecard_path}")
