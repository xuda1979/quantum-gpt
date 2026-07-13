from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PLACEHOLDER_TEXT = "# Paste model output here.\n"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_command(
    command: str, env: dict[str, str], cwd: Path, timeout: int | None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=True,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def resolve_run_dir(run_dir: Path) -> Path:
    resolved = run_dir.resolve()
    manifest_path = resolved / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Run directory missing manifest.json: {resolved}")
    return resolved


HERMETIC_DIR = (ROOT / "evals" / "runner" / "_hermetic").resolve()


def apply_hermetic_env(env: dict[str, str], seed: int, allow_network: bool) -> dict[str, str]:
    """Make candidate code execution reproducible and (optionally) offline.

    Prepends the ``_hermetic`` directory to PYTHONPATH so its ``sitecustomize``
    module is auto-imported at interpreter startup, seeding RNGs and blocking
    outbound network. Single-thread BLAS/OpenMP pins remove another source of
    run-to-run nondeterminism so an S-tier "code passed" label is stable.
    """
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(HERMETIC_DIR) + (
        os.pathsep + existing_pythonpath if existing_pythonpath else ""
    )
    env["PYTHONHASHSEED"] = str(seed)
    env["EVAL_SEED"] = str(seed)
    env["EVAL_BLOCK_NETWORK"] = "0" if allow_network else "1"
    for thread_var in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        env[thread_var] = "1"
    env["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    env["TOKENIZERS_PARALLELISM"] = "false"
    return env


def build_env(
    base_env: dict[str, str],
    run_dir: Path,
    manifest: dict[str, Any],
    task: dict[str, Any],
    hermetic: bool = False,
    seed: int = 0,
    allow_network: bool = False,
) -> dict[str, str]:
    env = dict(base_env)
    prompt_path = (run_dir / task["prompt_file"]).resolve()
    candidate_path = (run_dir / task["candidate_file"]).resolve()
    system_prompt_path = (run_dir / "SYSTEM_PROMPT.txt").resolve()

    env.update(
        {
            "EVAL_RUN_DIR": str(run_dir),
            "EVAL_SYSTEM_PROMPT_PATH": str(system_prompt_path),
            "EVAL_PROMPT_PATH": str(prompt_path),
            "EVAL_CANDIDATE_PATH": str(candidate_path),
            "EVAL_TASK_ID": str(task["id"]),
            "EVAL_TASK_NAME": str(task.get("name", "")),
            "EVAL_TASK_DOMAIN": str(task.get("domain", "")),
            "EVAL_TASK_CATEGORY": str(task.get("category", "")),
            "EVAL_PROMPT_STYLE": str(manifest.get("prompt_style", "")),
            "EVAL_PROMPT_VERSION": str(manifest.get("prompt_version", "")),
        }
    )
    if hermetic:
        apply_hermetic_env(env, seed=seed, allow_network=allow_network)
    return env


def candidate_is_effectively_empty(candidate_path: Path) -> bool:
    if not candidate_path.exists():
        return True
    text = candidate_path.read_text()
    return text == PLACEHOLDER_TEXT or text.strip() == ""


def execute_task(
    command: str,
    run_dir: Path,
    manifest: dict[str, Any],
    task: dict[str, Any],
    timeout: int | None,
    force: bool,
) -> dict[str, Any]:
    prompt_path = (run_dir / task["prompt_file"]).resolve()
    candidate_path = (run_dir / task["candidate_file"]).resolve()
    stdout_path = run_dir / "logs" / f"{task['id']}.stdout.txt"
    stderr_path = run_dir / "logs" / f"{task['id']}.stderr.txt"

    if not candidate_is_effectively_empty(candidate_path) and not force:
        return {
            "task_id": task["id"],
            "status": "skipped_existing_candidate",
            "prompt_path": str(prompt_path),
            "candidate_path": str(candidate_path),
            "started_at_utc": utc_now(),
            "finished_at_utc": utc_now(),
            "returncode": None,
            "stdout_path": str(stdout_path.relative_to(run_dir)),
            "stderr_path": str(stderr_path.relative_to(run_dir)),
        }

    env = build_env(os.environ, run_dir, manifest, task)
    started_at = utc_now()
    try:
        completed = run_command(command=command, env=env, cwd=ROOT, timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        completed = subprocess.CompletedProcess(
            args=exc.cmd,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + f"\nTimed out after {timeout} seconds.\n",
        )

    stdout_text = completed.stdout or ""
    stderr_text = completed.stderr or ""
    stdout_path.write_text(stdout_text)
    stderr_path.write_text(stderr_text)

    status = "ok" if completed.returncode == 0 and not timed_out else "command_failed"
    if status == "ok":
        candidate_path.write_text(stdout_text)

    return {
        "task_id": task["id"],
        "status": status,
        "prompt_path": str(prompt_path),
        "candidate_path": str(candidate_path),
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "returncode": completed.returncode,
        "stdout_path": str(stdout_path.relative_to(run_dir)),
        "stderr_path": str(stderr_path.relative_to(run_dir)),
        "stdout_bytes": len(stdout_text.encode("utf-8")),
        "stderr_bytes": len(stderr_text.encode("utf-8")),
    }


def write_execution_log(
    run_dir: Path,
    command: str,
    task_results: list[dict[str, Any]],
    timeout: int | None,
    backend_metadata: dict[str, Any] | None = None,
) -> Path:
    payload = {
        "executed_at_utc": utc_now(),
        "command": command,
        "timeout_seconds": timeout,
        "backend": backend_metadata,
        "results": task_results,
    }
    path = run_dir / "execution-log.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return path


def score_run(run_dir: Path) -> int:
    candidate_map = run_dir / "candidate-map.json"
    cmd = [
        sys.executable,
        str(ROOT / "evals" / "runner" / "run_eval.py"),
        "--candidate-map",
        str(candidate_map),
    ]
    completed = subprocess.run(cmd, cwd=str(ROOT), text=True)
    return completed.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Execute a prepared eval run by invoking a shell command once per task, capturing stdout as the candidate file."
        )
    )
    parser.add_argument("run_dir", type=Path, help="Prepared run directory under evals/runs/.")
    parser.add_argument(
        "--command",
        required=True,
        help=(
            "Shell command to execute per task. It receives task context via env vars such as "
            "EVAL_SYSTEM_PROMPT_PATH, EVAL_PROMPT_PATH, and EVAL_CANDIDATE_PATH. "
            "The command should print the candidate file contents to stdout."
        ),
    )
    parser.add_argument(
        "--timeout", type=int, default=None, help="Optional per-task timeout in seconds."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite non-empty candidate files instead of skipping them.",
    )
    parser.add_argument(
        "--no-score",
        action="store_true",
        help="Execute tasks without invoking run_eval.py afterward.",
    )
    parser.add_argument(
        "--backend-name",
        default=None,
        help="Optional backend/provider label recorded in logs and run manifest.",
    )
    parser.add_argument(
        "--backend-model",
        default=None,
        help="Optional model identifier recorded in logs and run manifest.",
    )
    parser.add_argument(
        "--backend-settings-json",
        default=None,
        help="Optional JSON object of decoding/provider settings to record in logs and run manifest.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_dir = resolve_run_dir(args.run_dir)
    manifest_path = run_dir / "manifest.json"
    manifest = load_json(manifest_path)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    backend_settings = None
    if args.backend_settings_json:
        backend_settings = json.loads(args.backend_settings_json)
        if not isinstance(backend_settings, dict):
            raise SystemExit("--backend-settings-json must decode to a JSON object")

    backend_metadata = None
    if args.backend_name or args.backend_model or backend_settings:
        backend_metadata = {
            "name": args.backend_name,
            "model": args.backend_model,
            "settings": backend_settings or {},
        }
        manifest["backend"] = backend_metadata
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    task_results = []
    for task in manifest.get("tasks", []):
        result = execute_task(
            command=args.command,
            run_dir=run_dir,
            manifest=manifest,
            task=task,
            timeout=args.timeout,
            force=args.force,
        )
        task_results.append(result)
        print(f"[{result['status']}] {result['task_id']}")

    log_path = write_execution_log(
        run_dir,
        command=args.command,
        task_results=task_results,
        timeout=args.timeout,
        backend_metadata=backend_metadata,
    )
    print(f"Execution log written to: {log_path}")

    if not args.no_score:
        raise SystemExit(score_run(run_dir))
