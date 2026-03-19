from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_scorecard(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if "results" not in payload or not isinstance(payload["results"], list):
        raise ValueError(f"Scorecard missing 'results' list: {path}")
    return payload


def summarize_results(results: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        grouped[str(result.get(key, "unknown"))].append(result)

    summary: list[dict[str, Any]] = []
    for group_name in sorted(grouped):
        subset = grouped[group_name]
        passed = sum(1 for item in subset if item.get("passed"))
        summary.append(
            {
                "name": group_name,
                "passed": passed,
                "total": len(subset),
                "rate": passed / len(subset) if subset else 0.0,
            }
        )
    return summary


def format_rate(passed: int, total: int) -> str:
    pct = 0.0 if total == 0 else (passed / total) * 100
    return f"{passed}/{total} ({pct:.1f}%)"


def format_backend(backend: Any) -> str:
    if not isinstance(backend, dict):
        return "unknown"

    name = backend.get("name") or "unknown"
    model = backend.get("model")
    if model:
        return f"{name}/{model}"
    return str(name)



def render_run_summary(run_dir: Path) -> str:
    manifest = load_json(run_dir / "manifest.json")
    scorecard = load_scorecard(run_dir / "scorecard.json")
    results = scorecard["results"]
    passed = sum(1 for item in results if item.get("passed"))
    total = len(results)

    prompt_style = scorecard.get("prompt_style") or manifest.get("prompt_style", "unknown")
    prompt_version = scorecard.get("prompt_version") or manifest.get("prompt_version", "unknown")
    backend = scorecard.get("backend") or manifest.get("backend")

    lines = [
        f"Run: {run_dir.name}",
        f"  backend: {format_backend(backend)}",
        f"  prompt_style: {prompt_style}",
        f"  prompt_version: {prompt_version}",
    ]

    if isinstance(backend, dict) and backend.get("settings"):
        lines.append(f"  backend_settings: {json.dumps(backend['settings'], sort_keys=True)}")
    if manifest.get("notes"):
        lines.append(f"  notes: {manifest['notes']}")
    if scorecard.get("scored_at_utc"):
        lines.append(f"  scored_at_utc: {scorecard['scored_at_utc']}")

    lines.append(f"  overall: {format_rate(passed, total)}")

    domain_summary = summarize_results(results, "domain")
    if domain_summary:
        lines.append("  by_domain:")
        for entry in domain_summary:
            lines.append(f"    - {entry['name']}: {format_rate(entry['passed'], entry['total'])}")

    category_summary = summarize_results(results, "category")
    if category_summary:
        lines.append("  by_category:")
        for entry in category_summary:
            lines.append(f"    - {entry['name']}: {format_rate(entry['passed'], entry['total'])}")

    failing = [item for item in results if not item.get("passed")]
    if failing:
        lines.append("  failing_tasks:")
        for item in failing:
            lines.append(f"    - {item.get('id', 'unknown')}")
    else:
        lines.append("  failing_tasks: none")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare scored eval run directories.")
    parser.add_argument(
        "run_dirs",
        nargs="+",
        type=Path,
        help="Run directories containing manifest.json and scorecard.json.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rendered = []
    for run_dir in args.run_dirs:
        resolved = run_dir.resolve()
        rendered.append(render_run_summary(resolved))

    print("\n\n".join(rendered))
