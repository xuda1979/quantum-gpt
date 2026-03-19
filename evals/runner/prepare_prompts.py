from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = ROOT / "evals" / "tasks"
RUNS_ROOT = ROOT / "evals" / "runs"
PROMPT_VERSION = "v2"

PROMPT_STYLES: dict[str, dict[str, str]] = {
    "direct": {
        "system_prompt": (
            "You are solving a single evaluation task. Produce only the full contents of the requested Python candidate file. "
            "Do not add markdown fences, explanations, or surrounding commentary unless the task explicitly asks for it."
        ),
        "user_suffix": (
            "Write a Python file that passes the supplied tests.\n"
            "Return only the candidate file contents."
        ),
    },
    "plan_then_code": {
        "system_prompt": (
            "You are solving a single evaluation task. Think through the constraints silently, then produce only the final Python candidate file. "
            "Do not include your plan, markdown fences, or commentary in the output."
        ),
        "user_suffix": (
            "Study the tests, infer the required behavior, and write a Python file that passes them.\n"
            "You may reason privately, but return only the final candidate file contents."
        ),
    },
    "repair_focused": {
        "system_prompt": (
            "You are solving a single evaluation task as a careful repair engineer. Produce only the final Python candidate file. "
            "Preserve simplicity, avoid unnecessary abstractions, and do not emit markdown or explanation text."
        ),
        "user_suffix": (
            "Treat this as a minimal-edit repair or implementation task.\n"
            "Write the simplest Python file that satisfies the supplied tests and return only that file."
        ),
    },
}


def discover_tasks() -> list[Path]:
    return sorted(TASKS_ROOT.glob("*/*/task.json"))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sanitize_text(text: str) -> str:
    return text.replace("\r\n", "\n")


def build_user_prompt(task_dir: Path, metadata: dict[str, Any], prompt_style: str) -> str:
    reference_candidate = sanitize_text((task_dir / metadata["candidate_file"]).read_text())
    tests_source = sanitize_text((task_dir / metadata["test_file"]).read_text())
    style = PROMPT_STYLES[prompt_style]

    return (
        f"Task ID: {metadata['id']}\n"
        f"Task name: {metadata['name']}\n"
        f"Domain: {metadata['domain']}\n"
        f"Category: {metadata['category']}\n\n"
        f"{style['user_suffix']}\n\n"
        "Reference candidate style example (for format guidance, not for blind copying):\n"
        "--- BEGIN REFERENCE CANDIDATE ---\n"
        f"{reference_candidate}\n"
        "--- END REFERENCE CANDIDATE ---\n\n"
        "Tests the candidate must satisfy:\n"
        "--- BEGIN TESTS ---\n"
        f"{tests_source}\n"
        "--- END TESTS ---\n"
    )


def create_run_dir(run_name: str | None) -> Path:
    if run_name:
        run_id = run_name
    else:
        run_id = datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
    run_dir = RUNS_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_run_artifacts(run_dir: Path, prompt_style: str, notes: str | None) -> None:
    prompts_dir = run_dir / "prompts"
    candidates_dir = run_dir / "candidates"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir.mkdir(parents=True, exist_ok=True)

    style = PROMPT_STYLES[prompt_style]
    candidate_map: dict[str, str] = {}
    manifest: dict[str, Any] = {
        "prompt_version": PROMPT_VERSION,
        "prompt_style": prompt_style,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "system_prompt": style["system_prompt"],
        "notes": notes,
        "tasks": [],
    }

    for task_json in discover_tasks():
        task_dir = task_json.parent
        metadata = load_json(task_json)
        prompt_text = build_user_prompt(task_dir, metadata, prompt_style)
        prompt_path = prompts_dir / f"{metadata['id']}.txt"
        candidate_path = candidates_dir / f"{metadata['id']}.py"
        prompt_path.write_text(prompt_text)
        candidate_path.write_text("# Paste model output here.\n")
        candidate_map[metadata["id"]] = str(candidate_path.relative_to(run_dir))
        manifest["tasks"].append(
            {
                "id": metadata["id"],
                "name": metadata["name"],
                "domain": metadata["domain"],
                "category": metadata["category"],
                "prompt_file": str(prompt_path.relative_to(run_dir)),
                "candidate_file": str(candidate_path.relative_to(run_dir)),
            }
        )

    (run_dir / "candidate-map.json").write_text(json.dumps(candidate_map, indent=2) + "\n")
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (run_dir / "SYSTEM_PROMPT.txt").write_text(style["system_prompt"] + "\n")
    (run_dir / "README.txt").write_text(
        "This run directory captures prompt inputs and candidate output slots for a single eval batch.\n\n"
        f"Prompt style: {prompt_style}\n"
        f"Prompt version: {PROMPT_VERSION}\n\n"
        "Workflow:\n"
        "1. Use SYSTEM_PROMPT.txt as the system message.\n"
        "2. For each task, send prompts/<task_id>.txt as the user message.\n"
        "3. Save the raw model code output into candidates/<task_id>.py.\n"
        "4. Score the batch with:\n"
        f"   python3 evals/runner/run_eval.py --candidate-map {run_dir.relative_to(ROOT) / 'candidate-map.json'}\n"
    )



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a timestamped eval run directory with prompts and candidate slots.")
    parser.add_argument("--run-name", default=None, help="Optional deterministic run directory name under evals/runs/.")
    parser.add_argument(
        "--prompt-style",
        default="direct",
        choices=sorted(PROMPT_STYLES),
        help="Prompt style variant to materialize for this run.",
    )
    parser.add_argument("--notes", default=None, help="Optional free-text note recorded in manifest.json.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_dir = create_run_dir(args.run_name)
    write_run_artifacts(run_dir, prompt_style=args.prompt_style, notes=args.notes)
    print(run_dir.relative_to(ROOT))
