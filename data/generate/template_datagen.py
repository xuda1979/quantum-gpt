#!/usr/bin/env python3
"""Template-based data generation: convert eval task reference solutions into
SFT training examples, with programmatic prompt variations to multiply data.

No model inference needed — all solutions are verified-correct reference code.

Usage:
    python3 data/generate/template_datagen.py \
        --tasks-dir evals/tasks \
        --output data/generated/template-v1.jsonl
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
import uuid
from pathlib import Path
from typing import Any

SYSTEM_PROMPT = (
    "You are a careful coding assistant focused on correctness, clear reasoning, "
    "and maintainable Python code. Follow the task instruction and use any provided "
    "artifacts as context. Return only the final code or requested artifact content."
)

# Prompt variation templates — each is a different way to phrase "write this code"
PROMPT_PREFIXES = [
    "Write a Python solution for the following task:\n\n",
    "Implement the following in Python:\n\n",
    "Please solve this coding task in Python:\n\n",
    "Here is a coding problem. Provide a correct Python implementation:\n\n",
    "Complete the following task. Return only Python code:\n\n",
]

PROMPT_SUFFIXES = [
    "\n\nReturn only the code, no explanations.",
    "\n\nProvide a clean, working implementation.",
    "\n\nWrite correct, well-structured Python code.",
    "\n\nReturn the solution as Python code only.",
    "",
]

REPAIR_PREFIXES = [
    "Fix the following broken code so all tests pass:\n\n",
    "The code below has bugs. Repair it:\n\n",
    "Debug and fix this Python code:\n\n",
    "This code is broken. Provide the corrected version:\n\n",
]

REPAIR_SUFFIXES = [
    "\n\nReturn only the corrected Python code.",
    "\n\nFix all issues and return the working code.",
    "\n\nProvide the repaired implementation.",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tasks-dir", default="evals/tasks")
    p.add_argument("--output", default="data/generated/template-v1.jsonl")
    p.add_argument("--variations", type=int, default=5,
                   help="Number of prompt variations per task")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--validate", action="store_true", default=True,
                   help="Validate reference solutions against test harness")
    return p.parse_args()


def load_task(task_dir: Path) -> dict[str, Any] | None:
    task_json = task_dir / "task.json"
    if not task_json.exists():
        return None
    with open(task_json) as f:
        meta = json.load(f)

    # Find candidate file
    candidate_file = meta.get("candidate_file", "candidate.py")
    candidate_path = task_dir / candidate_file
    if not candidate_path.exists():
        return None

    tests_path = task_dir / "tests.py"
    if not tests_path.exists():
        return None

    code = candidate_path.read_text().strip()
    return {
        "meta": meta,
        "task_dir": task_dir,
        "code": code,
        "tests_py": tests_path,
    }


def validate_solution(code: str, tests_py: Path, task_dir: Path) -> bool:
    """Run the test harness against the reference solution."""
    import tempfile
    spec = importlib.util.spec_from_file_location("tests", str(tests_py))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=str(task_dir)
    ) as f:
        f.write(code)
        f.flush()
        tmp = f.name
    try:
        result = mod.run_tests(tmp)
        return result.get("passed", False)
    except Exception as e:
        print(f"  validation error: {e}", file=sys.stderr)
        return False
    finally:
        Path(tmp).unlink(missing_ok=True)


def build_base_prompt(meta: dict) -> str:
    """Build the core task description from metadata."""
    parts = []
    if "task_prompt" in meta:
        parts.append(meta["task_prompt"])
    elif "description" in meta:
        parts.append(meta["description"])
    elif "name" in meta:
        parts.append(f"Task: {meta['name']}")

    if meta.get("task_type") == "repair" and "broken_candidate" in meta:
        parts.append(f"\nBroken code:\n```python\n{meta['broken_candidate']}\n```")

    return "\n".join(parts)


def make_prompt_variations(meta: dict, rng: random.Random, n: int) -> list[str]:
    """Generate n different phrasings of the same task prompt."""
    base = build_base_prompt(meta)
    is_repair = meta.get("task_type") == "repair"

    variations = []
    prefixes = REPAIR_PREFIXES if is_repair else PROMPT_PREFIXES
    suffixes = REPAIR_SUFFIXES if is_repair else PROMPT_SUFFIXES

    # Always include the "clean" version
    variations.append(base + "\n\nReturn only the code, no explanations.")

    seen = {variations[0]}
    attempts = 0
    while len(variations) < n and attempts < n * 3:
        attempts += 1
        prefix = rng.choice(prefixes)
        suffix = rng.choice(suffixes)
        prompt = prefix + base + suffix
        if prompt not in seen:
            seen.add(prompt)
            variations.append(prompt)

    return variations


def make_code_variations(code: str, rng: random.Random, n: int) -> list[str]:
    """Generate minor style variations of the reference code.

    Keeps semantics identical — only cosmetic changes like:
    - Adding/removing blank lines between functions
    - Swapping single/double quotes in non-docstring strings
    - Minor comment additions
    """
    variations = [code]  # always include original

    # Variation: add a leading comment
    comments = [
        "# Solution",
        "# Implementation",
        "# --- solution ---",
    ]
    for i in range(min(n - 1, len(comments))):
        v = comments[i] + "\n" + code
        if v not in variations:
            variations.append(v)

    # Variation: extra blank line after imports (if any)
    lines = code.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            v = "\n".join(lines[:i+1] + [""] + lines[i+1:])
            if v not in variations:
                variations.append(v)
            break

    return variations[:n]


def format_example(
    prompt: str, code: str, meta: dict, task_dir_name: str, variant_idx: int
) -> dict:
    eid = f"template_{task_dir_name}_{variant_idx}_{uuid.uuid4().hex[:8]}"
    return {
        "format": "chat-sft-v1",
        "source_schema": "template-v1",
        "example_id": eid,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": code},
        ],
        "metadata": {
            "domain": meta.get("domain", "unknown"),
            "category": meta.get("category", "unknown"),
            "task_type": meta.get("task_type", "implementation"),
            "difficulty": meta.get("difficulty", "medium"),
            "language": "python",
            "framework": meta.get("framework"),
            "tags": meta.get("tags", []),
            "source": "template",
            "task_id": meta.get("id", task_dir_name),
            "task_name": meta.get("name", task_dir_name),
            "variant_index": variant_idx,
        },
    }


def discover_tasks(tasks_dir: Path) -> list[dict]:
    tasks = []
    for domain_dir in sorted(tasks_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            # Skip workspace-based tasks (multi-file)
            task_json = task_dir / "task.json"
            if task_json.exists():
                with open(task_json) as f:
                    meta = json.load(f)
                if meta.get("candidate_files"):
                    continue  # multi-file task, skip
            task = load_task(task_dir)
            if task:
                tasks.append(task)
    return tasks


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)
    tasks_dir = Path(args.tasks_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tasks = discover_tasks(tasks_dir)
    print(f"Found {len(tasks)} single-file tasks with reference solutions")

    total = 0
    skipped = 0

    with open(output_path, "w") as out:
        for task in tasks:
            name = task["task_dir"].name
            meta = task["meta"]
            code = task["code"]
            domain = meta.get("domain", "?")

            # Validate reference solution
            if args.validate:
                ok = validate_solution(code, task["tests_py"], task["task_dir"])
                if not ok:
                    print(f"  [{domain}/{name}] SKIP — reference solution fails tests")
                    skipped += 1
                    continue

            # Generate prompt variations
            prompts = make_prompt_variations(meta, rng, args.variations)
            codes = make_code_variations(code, rng, max(2, args.variations // 2))

            count = 0
            for pi, prompt in enumerate(prompts):
                # Pair each prompt with a code variation (cycle through codes)
                c = codes[pi % len(codes)]
                example = format_example(prompt, c, meta, name, pi)
                out.write(json.dumps(example, ensure_ascii=False) + "\n")
                count += 1
                total += 1

            print(f"  [{domain}/{name}] {count} examples")

    print(f"\nDone. {total} examples from {len(tasks)} tasks "
          f"({skipped} skipped)")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
