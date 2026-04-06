#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_utils import extract_behavior_hints_from_test_source

TASKS_ROOT = ROOT / "evals" / "tasks"


def old_extract_behavior_hints(test_source: str, cap: int = 6) -> list[str]:
    hints: list[str] = []
    for raw_line in test_source.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# Test "):
            comment = line.lstrip("#").strip()
            if len(comment) >= 12:
                hints.append(comment)
            continue
        marker = None
        if "failures.append(" in line:
            marker = "failures.append("
        elif "details.append(" in line:
            marker = "details.append("
        if marker is None:
            continue
        expr = line.split(marker, 1)[1].rstrip(")")
        try:
            value = eval(expr, {"__builtins__": {}}, {})
        except Exception:
            continue
        if not isinstance(value, str) or not value:
            continue
        normalized = " ".join(value.split())
        if normalized not in hints:
            hints.append(normalized)
        if len(hints) >= cap:
            break
    return hints


def fstring_append_count(test_source: str) -> int:
    try:
        tree = ast.parse(test_source)
    except Exception:
        return 0
    count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "append":
            continue
        if not isinstance(node.func.value, ast.Name):
            continue
        if node.func.value.id not in {"failures", "details", "error_failures"}:
            continue
        if node.args and isinstance(node.args[0], ast.JoinedStr):
            count += 1
    return count


def main() -> None:
    rows: list[dict[str, object]] = []
    for task_json in sorted(TASKS_ROOT.glob("*/*/task.json")):
        task_dir = task_json.parent
        tests_py = task_dir / "tests.py"
        if not tests_py.exists():
            continue
        meta = json.loads(task_json.read_text(encoding="utf-8"))
        test_source = tests_py.read_text(encoding="utf-8")
        old_hints = old_extract_behavior_hints(test_source, cap=6)
        new_hints = extract_behavior_hints_from_test_source(test_source, cap=6)
        rows.append(
            {
                "task_id": meta["id"],
                "old_hint_count": len(old_hints),
                "new_hint_count": len(new_hints),
                "fstring_appends": fstring_append_count(test_source),
                "old_hints": old_hints,
                "new_hints": new_hints,
            }
        )

    improved = [row for row in rows if int(row["new_hint_count"]) > int(row["old_hint_count"])]
    payload = {
        "task_count": len(rows),
        "improved_task_count": len(improved),
        "total_old_hints": sum(int(row["old_hint_count"]) for row in rows),
        "total_new_hints": sum(int(row["new_hint_count"]) for row in rows),
        "tasks_with_fstring_failures": sum(1 for row in rows if int(row["fstring_appends"]) > 0),
        "improved_tasks": improved,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
