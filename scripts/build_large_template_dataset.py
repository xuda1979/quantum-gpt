#!/usr/bin/env python3
"""Build a large deterministic chat-SFT corpus from single-file eval tasks.

This builder addresses two failure modes from the earlier template pipeline:
1. The old corpus was too small to support a meaningful held-out split.
2. Train and eval examples only differed by a tiny set of prompt rewrites.

The new policy keeps train/eval prompt families disjoint so eval examples are
not literal prompt variants seen during training, while still using verified
reference solutions from the task suite.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS_DIR = ROOT / "evals" / "tasks"
DEFAULT_OUT_DIR = ROOT / "data" / "generated" / "omnicoder-template-large-v1"

SYSTEM_PROMPT = (
    "You are a careful coding assistant focused on correctness, clear reasoning, "
    "and maintainable Python code. Follow the task instruction and use any provided "
    "artifacts as context. Return only the final code or requested artifact content."
)

TRAIN_FAMILIES = {
    "implementation_ticket": [
        "Implement the following Python task.",
        "Write a production-ready Python solution for this task.",
        "Complete this repository task in Python.",
        "Provide a correct Python implementation for the task below.",
    ],
    "interface_contract": [
        "Write Python code that satisfies this interface contract.",
        "Implement the requested Python behavior while preserving the required signatures.",
        "Fill in the Python implementation that matches the contract below.",
        "Produce the Python implementation for the following callable interface.",
    ],
    "behavior_first": [
        "Implement Python code that passes the behavioral checks below.",
        "Solve this Python task with the acceptance behavior in mind.",
        "Write the Python implementation so the listed behaviors hold.",
        "Use the behavior notes below to guide a correct Python solution.",
    ],
    "repo_handoff": [
        "A maintainer left this Python task for handoff.",
        "Finish this Python task as if you are taking over the repository.",
        "Pick up this pending Python implementation task.",
        "Complete this repository handoff task in Python.",
    ],
    "refactor_request": [
        "Refine the implementation into clean Python code.",
        "Produce a readable Python implementation that satisfies the request below.",
        "Write maintainable Python code for the following task.",
        "Implement this task in Python with clarity and correctness.",
    ],
    "deliverable_note": [
        "Prepare the requested Python deliverable.",
        "Return the final Python implementation for this task.",
        "Produce the Python artifact described below.",
        "Write the final Python solution requested here.",
    ],
}

EVAL_FAMILIES = {
    "acceptance_gate": [
        "Release blocker: provide Python code that clears the acceptance gate.",
        "This task is held out for evaluation. Return a correct Python solution.",
        "Write Python code that should pass an unseen acceptance review.",
        "Produce the Python implementation that satisfies this held-out check.",
    ],
    "spec_translation": [
        "Translate this specification into working Python code.",
        "Convert the following task specification into a correct Python implementation.",
        "Implement the spec below as Python code.",
        "Turn the following requirements into executable Python code.",
    ],
    "audit_followup": [
        "A reviewer requested a fresh Python implementation from the notes below.",
        "Resolve this task from the audit notes and interface hints.",
        "Use the notes below to produce a clean Python implementation.",
        "Write the Python solution implied by the review notes below.",
    ],
    "maintainer_check": [
        "A maintainer wants a final Python answer for the following held-out task.",
        "Return the Python implementation a maintainer would accept for this task.",
        "Produce a correct Python solution for this unseen maintainer check.",
        "Write the final Python code for the held-out repository task below.",
    ],
}

SUMMARY_STYLES = [
    "Task: {task_name}",
    "Task: {task_name}\nDomain: {domain}\nCategory: {category}",
    "Task id: {task_id}\nName: {task_name}\nCategory: {category}",
    "Repository task: {task_name}\nTask id: {task_id}\nLanguage: Python",
]

SECTION_ORDERS = [
    ("summary", "interface", "behavior", "constraints"),
    ("summary", "behavior", "interface", "constraints"),
    ("summary", "constraints", "interface", "behavior"),
]

INTERFACE_HEADERS = [
    "Required interface:",
    "Callable contract to preserve:",
    "Public interface:",
]

BEHAVIOR_HEADERS = [
    "Behavioral requirements:",
    "Acceptance checks to satisfy:",
    "Observed test expectations:",
]

CONSTRAINT_BLOCKS = [
    "Return only Python code. Do not include explanations.",
    "Return only the final code and keep the implementation self-contained.",
    "Produce only executable Python code with no surrounding commentary.",
    "Return the implementation only. No prose, no markdown.",
]

GUIDANCE_NOTES = [
    "Favor correctness over cleverness and preserve the stated interface.",
    "Keep the implementation concise but do not sacrifice edge-case handling.",
    "Prefer explicit logic that is easy to validate from tests.",
    "Write maintainable Python that matches the requested behavior exactly.",
]

CODE_STYLE_VARIANTS = (
    "plain",
    "commented",
    "spaced_imports",
    "commented_spaced_imports",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dir", type=Path, default=DEFAULT_TASKS_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--holdout-policy",
        choices=["split_family_disjoint_v1", "task_disjoint_v1"],
        default="split_family_disjoint_v1",
        help="How to separate train and eval. task_disjoint_v1 keeps source task ids disjoint.",
    )
    parser.add_argument(
        "--train-variants-per-task",
        type=int,
        default=96,
        help="Number of train examples to emit per single-file task.",
    )
    parser.add_argument(
        "--eval-variants-per-task",
        type=int,
        default=24,
        help="Number of held-out eval examples to emit per single-file task.",
    )
    parser.add_argument(
        "--domains",
        nargs="*",
        default=["quantum", "software"],
        help="Domains to include. Defaults to both quantum and software.",
    )
    parser.add_argument(
        "--seed-tag",
        default="omnicoder-template-large-v1",
        help="Stable tag embedded in example ids and manifest metadata.",
    )
    parser.add_argument(
        "--eval-task-id-file",
        type=Path,
        default=None,
        help="Optional text file listing held-out eval task ids for task_disjoint_v1.",
    )
    parser.add_argument(
        "--eval-tasks-per-domain",
        type=int,
        default=0,
        help="For task_disjoint_v1, deterministically hold out this many tasks per included domain.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip reference-solution validation against the task test harness.",
    )
    return parser.parse_args()


def load_task(task_dir: Path) -> dict[str, Any] | None:
    task_json = task_dir / "task.json"
    if not task_json.exists():
        return None
    meta = json.loads(task_json.read_text(encoding="utf-8"))

    # Keep this builder focused on single-file reference tasks. The workspace
    # tasks can be added later with a multi-artifact response format.
    if meta.get("candidate_files"):
        return None

    candidate_file = meta.get("candidate_file", "candidate.py")
    candidate_path = task_dir / candidate_file
    tests_path = task_dir / "tests.py"
    if not candidate_path.exists() or not tests_path.exists():
        return None

    return {
        "meta": meta,
        "task_dir": task_dir,
        "candidate_path": candidate_path,
        "tests_path": tests_path,
        "code": candidate_path.read_text(encoding="utf-8").rstrip() + "\n",
    }


def discover_tasks(tasks_dir: Path, allowed_domains: set[str]) -> list[dict[str, Any]]:
    tasks = []
    for domain_dir in sorted(tasks_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            task = load_task(task_dir)
            if task is None:
                continue
            domain = str(task["meta"].get("domain", "unknown"))
            if domain not in allowed_domains:
                continue
            tasks.append(task)
    return tasks


def validate_solution(code: str, tests_py: Path, task_dir: Path) -> bool:
    spec = importlib.util.spec_from_file_location(f"tests_{task_dir.name}", str(tests_py))
    if spec is None or spec.loader is None:
        raise ValueError(f"Unable to load test harness from {tests_py}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir=str(task_dir), encoding="utf-8") as handle:
        handle.write(code)
        handle.flush()
        candidate_path = handle.name
    try:
        result = mod.run_tests(candidate_path)
        return bool(result.get("passed"))
    except Exception as exc:  # noqa: BLE001
        print(f"[validate] {task_dir}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return False
    finally:
        Path(candidate_path).unlink(missing_ok=True)


def summarize_candidate_interface(candidate_path: Path) -> list[str]:
    import ast

    try:
        tree = ast.parse(candidate_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    lines: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            args: list[str] = []
            total_args = list(node.args.posonlyargs) + list(node.args.args)
            defaults = list(node.args.defaults)
            default_offset = len(total_args) - len(defaults)
            for index, arg in enumerate(total_args):
                arg_text = arg.arg
                if arg.annotation is not None:
                    arg_text += f": {ast.unparse(arg.annotation)}"
                if index >= default_offset:
                    arg_text += f" = {ast.unparse(defaults[index - default_offset])}"
                args.append(arg_text)
            if node.args.vararg is not None:
                args.append(f"*{node.args.vararg.arg}")
            if node.args.kwonlyargs:
                if node.args.vararg is None:
                    args.append("*")
                for kwarg, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
                    kwarg_text = kwarg.arg
                    if kwarg.annotation is not None:
                        kwarg_text += f": {ast.unparse(kwarg.annotation)}"
                    if default is not None:
                        kwarg_text += f" = {ast.unparse(default)}"
                    args.append(kwarg_text)
            if node.args.kwarg is not None:
                args.append(f"**{node.args.kwarg.arg}")
            signature = f"{node.name}({', '.join(args)})"
            if node.returns is not None:
                signature += f" -> {ast.unparse(node.returns)}"
            lines.append(signature)
        elif isinstance(node, ast.ClassDef):
            lines.append(f"class {node.name}")
    return lines


def extract_behavior_hints(tests_path: Path) -> list[str]:
    if not tests_path.exists():
        return []
    lines = tests_path.read_text(encoding="utf-8").splitlines()

    hints: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# Test "):
            comment = line.lstrip("#").strip()
            if len(comment) >= 12:
                hints.append(comment)
            continue
        if "append(" not in line:
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
            value = None
        if not isinstance(value, str) or not value:
            continue
        normalized = " ".join(value.split())
        lower = normalized.lower()
        if lower.endswith("was incorrect"):
            hints.append(normalized.removesuffix(" was incorrect"))
        elif any(token in lower for token in ("should", "expected", "raise", "retry", "preserved", "valid", "round-trip", "reject", "normalize")):
            hints.append(normalized)

    deduped: list[str] = []
    seen: set[str] = set()
    for hint in hints:
        if hint not in seen:
            seen.add(hint)
            deduped.append(hint)
        if len(deduped) >= 6:
            break
    return deduped


def bullet_block(lines: list[str]) -> str:
    return "\n".join(f"- {line}" for line in lines)


def task_summary(meta: dict[str, Any], style: str) -> str:
    task_name = str(meta.get("name") or meta.get("id") or "unknown task")
    return style.format(
        task_name=task_name,
        task_id=str(meta.get("id") or task_name),
        domain=str(meta.get("domain") or "unknown"),
        category=str(meta.get("category") or "unknown"),
    )


def build_prompt(
    *,
    task: dict[str, Any],
    family_name: str,
    headline: str,
    summary_style: str,
    section_order: tuple[str, ...],
    interface_header: str,
    behavior_header: str,
    constraint_block: str,
    guidance_note: str,
) -> str:
    meta = task["meta"]
    interface_lines = task["interface_lines"]
    behavior_hints = task["behavior_hints"]

    sections = {
        "summary": task_summary(meta, summary_style),
        "interface": f"{interface_header}\n{bullet_block(interface_lines)}" if interface_lines else "",
        "behavior": f"{behavior_header}\n{bullet_block(behavior_hints)}" if behavior_hints else "",
        "constraints": f"Implementation notes:\n- {guidance_note}\n- {constraint_block}",
    }

    parts = [headline]
    for section_name in section_order:
        section_text = sections[section_name]
        if section_text:
            parts.append(section_text)
    return "\n\n".join(parts).strip()


def apply_code_style(code: str, style_name: str) -> str:
    text = code.rstrip("\n")
    if style_name in {"commented", "commented_spaced_imports"}:
        text = "# Reference implementation\n" + text

    if style_name in {"spaced_imports", "commented_spaced_imports"}:
        lines = text.splitlines()
        last_import_index = -1
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                last_import_index = index
            elif stripped and last_import_index >= 0:
                break
        if last_import_index >= 0 and (last_import_index + 1 >= len(lines) or lines[last_import_index + 1].strip()):
            lines.insert(last_import_index + 1, "")
        text = "\n".join(lines)

    return text.rstrip() + "\n"


def stable_order_key(seed_tag: str, task_id: str, payload: str) -> str:
    return hashlib.sha256(f"{seed_tag}:{task_id}:{payload}".encode("utf-8")).hexdigest()


def load_task_ids(path: Path) -> list[str]:
    task_ids = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        task_ids.append(line)
    if not task_ids:
        raise ValueError(f"No task ids found in {path}")
    return task_ids


def describe_task(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": task["meta"].get("id", task["task_dir"].name),
        "task_dir": str(task["task_dir"].relative_to(ROOT)),
        "domain": task["meta"].get("domain", "unknown"),
        "category": task["meta"].get("category", "unknown"),
    }


def split_tasks_for_holdout(
    tasks: list[dict[str, Any]],
    *,
    holdout_policy: str,
    eval_task_id_file: Path | None,
    eval_tasks_per_domain: int,
    seed_tag: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if holdout_policy == "split_family_disjoint_v1":
        task_entries = [describe_task(task) for task in tasks]
        return tasks, tasks, {
            "name": "split_family_disjoint_v1",
            "shared_source_tasks": True,
            "train_task_count": len(tasks),
            "eval_task_count": len(tasks),
            "task_overlap_count": len(tasks),
            "train_tasks": task_entries,
            "eval_tasks": task_entries,
        }

    if eval_task_id_file is not None:
        eval_task_ids = set(load_task_ids(eval_task_id_file))
    else:
        if eval_tasks_per_domain < 1:
            raise ValueError("task_disjoint_v1 requires --eval-task-id-file or --eval-tasks-per-domain >= 1")
        eval_task_ids: set[str] = set()
        tasks_by_domain: dict[str, list[dict[str, Any]]] = {}
        for task in tasks:
            domain = str(task["meta"].get("domain", "unknown"))
            tasks_by_domain.setdefault(domain, []).append(task)
        for domain, domain_tasks in sorted(tasks_by_domain.items()):
            if len(domain_tasks) <= eval_tasks_per_domain:
                raise ValueError(
                    f"Domain {domain!r} has only {len(domain_tasks)} task(s); "
                    f"cannot hold out {eval_tasks_per_domain} and still keep train tasks."
                )
            ranked = sorted(
                domain_tasks,
                key=lambda task: stable_order_key(
                    f"{seed_tag}:task_holdout:{domain}",
                    str(task["meta"].get("id", task["task_dir"].name)),
                    str(task["task_dir"]),
                ),
            )
            eval_task_ids.update(str(task["meta"].get("id", task["task_dir"].name)) for task in ranked[:eval_tasks_per_domain])

    known_task_ids = {str(task["meta"].get("id", task["task_dir"].name)) for task in tasks}
    unknown_eval_task_ids = sorted(eval_task_ids - known_task_ids)
    if unknown_eval_task_ids:
        raise ValueError(f"Unknown eval task ids requested: {unknown_eval_task_ids}")

    train_tasks = [task for task in tasks if str(task["meta"].get("id", task["task_dir"].name)) not in eval_task_ids]
    eval_tasks = [task for task in tasks if str(task["meta"].get("id", task["task_dir"].name)) in eval_task_ids]
    if not train_tasks or not eval_tasks:
        raise ValueError("Task holdout must produce non-empty train and eval task sets")

    return train_tasks, eval_tasks, {
        "name": "task_disjoint_v1",
        "shared_source_tasks": False,
        "train_task_count": len(train_tasks),
        "eval_task_count": len(eval_tasks),
        "task_overlap_count": 0,
        "eval_task_id_file": str(eval_task_id_file) if eval_task_id_file else None,
        "eval_tasks_per_domain": eval_tasks_per_domain if eval_task_id_file is None else None,
        "train_tasks": [describe_task(task) for task in train_tasks],
        "eval_tasks": [describe_task(task) for task in eval_tasks],
    }


def make_examples_for_split(
    *,
    task: dict[str, Any],
    split: str,
    variants_per_task: int,
    families: dict[str, list[str]],
    seed_tag: str,
    holdout_policy_name: str,
) -> list[dict[str, Any]]:
    task_id = str(task["meta"].get("id") or task["task_dir"].name)
    per_family_records: dict[str, list[dict[str, Any]]] = {}
    family_quota = max(1, (variants_per_task + len(families) - 1) // len(families))

    for family_name, headlines in sorted(families.items()):
        family_records: list[dict[str, Any]] = []
        seen_prompts: set[str] = set()
        combo_iter = itertools.product(
            range(len(headlines)),
            SUMMARY_STYLES,
            SECTION_ORDERS,
            INTERFACE_HEADERS,
            BEHAVIOR_HEADERS,
            GUIDANCE_NOTES,
            CONSTRAINT_BLOCKS,
        )
        for combo_index, combo in enumerate(combo_iter):
            headline_index, summary_style, section_order, interface_header, behavior_header, guidance_note, constraint_block = combo
            prompt = build_prompt(
                task=task,
                family_name=family_name,
                headline=headlines[headline_index],
                summary_style=summary_style,
                section_order=section_order,
                interface_header=interface_header,
                behavior_header=behavior_header,
                constraint_block=constraint_block,
                guidance_note=guidance_note,
            )
            if prompt in seen_prompts:
                continue
            seen_prompts.add(prompt)

            code_style = CODE_STYLE_VARIANTS[(combo_index + headline_index) % len(CODE_STYLE_VARIANTS)]
            assistant_code = apply_code_style(task["code"], code_style)
            prompt_key = stable_order_key(seed_tag, task_id, prompt)
            family_records.append(
                {
                    "format": "chat-sft-v1",
                    "source_schema": "template-large-v1",
                    "example_id": "",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": assistant_code},
                    ],
                    "metadata": {
                        "domain": task["meta"].get("domain", "unknown"),
                        "category": task["meta"].get("category", "unknown"),
                        "task_type": task["meta"].get("task_type", "implementation"),
                        "difficulty": task["meta"].get("difficulty", "medium"),
                        "language": "python",
                        "framework": task["meta"].get("framework"),
                        "tags": task["meta"].get("tags", []),
                        "source": "template-large",
                        "task_id": task_id,
                        "task_name": task["meta"].get("name", task["task_dir"].name),
                        "split": split,
                        "prompt_family": family_name,
                        "assistant_style": code_style,
                        "source_task_dir": str(task["task_dir"].relative_to(ROOT)),
                        "holdout_policy": holdout_policy_name,
                        "prompt_key": prompt_key,
                    },
                }
            )
            if len(family_records) >= family_quota:
                break
        per_family_records[family_name] = family_records

    variants: list[dict[str, Any]] = []
    for round_index in range(family_quota):
        for family_name in sorted(per_family_records):
            family_records = per_family_records[family_name]
            if round_index >= len(family_records):
                continue
            record = dict(family_records[round_index])
            record["metadata"] = dict(family_records[round_index]["metadata"])
            record["example_id"] = f"{seed_tag}_{task_id}_{split}_{family_name}_{len(variants):03d}"
            variants.append(record)
            if len(variants) >= variants_per_task:
                break
        if len(variants) >= variants_per_task:
            break

    if len(variants) < variants_per_task:
        raise ValueError(
            f"Unable to generate {variants_per_task} unique prompts for {task_id} {split}; "
            f"only produced {len(variants)}"
        )
    return variants


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_domain = Counter()
    by_task = Counter()
    by_family = Counter()
    for row in rows:
        metadata = row.get("metadata", {})
        by_domain[str(metadata.get("domain", "unknown"))] += 1
        by_task[str(metadata.get("task_id", "unknown"))] += 1
        by_family[str(metadata.get("prompt_family", "unknown"))] += 1
    return {
        "count": len(rows),
        "domains": dict(sorted(by_domain.items())),
        "tasks": dict(sorted(by_task.items())),
        "prompt_families": dict(sorted(by_family.items())),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    if args.train_variants_per_task < 1 or args.eval_variants_per_task < 1:
        raise SystemExit("Variant counts must be >= 1")

    allowed_domains = {domain.strip() for domain in args.domains if domain.strip()}
    if not allowed_domains:
        raise SystemExit("At least one domain must be selected")

    tasks = discover_tasks(args.tasks_dir, allowed_domains)
    if not tasks:
        raise SystemExit("No single-file tasks matched the requested domains")

    prepared_tasks = []
    for task in tasks:
        if not args.skip_validate and not validate_solution(task["code"], task["tests_path"], task["task_dir"]):
            raise SystemExit(f"Reference solution failed validation for {task['task_dir']}")
        prepared = dict(task)
        prepared["interface_lines"] = summarize_candidate_interface(task["candidate_path"])
        prepared["behavior_hints"] = extract_behavior_hints(task["tests_path"])
        prepared_tasks.append(prepared)

    train_tasks, eval_tasks, holdout_policy_manifest = split_tasks_for_holdout(
        prepared_tasks,
        holdout_policy=args.holdout_policy,
        eval_task_id_file=args.eval_task_id_file,
        eval_tasks_per_domain=args.eval_tasks_per_domain,
        seed_tag=args.seed_tag,
    )

    train_rows: list[dict[str, Any]] = []
    eval_rows: list[dict[str, Any]] = []
    for task in train_tasks:
        train_rows.extend(
            make_examples_for_split(
                task=task,
                split="train",
                variants_per_task=args.train_variants_per_task,
                families=TRAIN_FAMILIES,
                seed_tag=args.seed_tag,
                holdout_policy_name=args.holdout_policy,
            )
        )
    for task in eval_tasks:
        eval_rows.extend(
            make_examples_for_split(
                task=task,
                split="eval",
                variants_per_task=args.eval_variants_per_task,
                families=EVAL_FAMILIES,
                seed_tag=args.seed_tag,
                holdout_policy_name=args.holdout_policy,
            )
        )

    train_rows.sort(key=lambda row: row["example_id"])
    eval_rows.sort(key=lambda row: row["example_id"])

    train_ids = {row["example_id"] for row in train_rows}
    eval_ids = {row["example_id"] for row in eval_rows}
    if train_ids & eval_ids:
        raise ValueError("Train/eval example_id overlap detected")

    train_families = {row["metadata"]["prompt_family"] for row in train_rows}
    eval_families = {row["metadata"]["prompt_family"] for row in eval_rows}
    if train_families & eval_families:
        raise ValueError("Train/eval prompt-family overlap detected")

    train_task_ids = {row["metadata"]["task_id"] for row in train_rows}
    eval_task_ids = {row["metadata"]["task_id"] for row in eval_rows}
    if args.holdout_policy == "task_disjoint_v1" and train_task_ids & eval_task_ids:
        raise ValueError("Task-disjoint holdout requested but train/eval task ids overlap")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "train.jsonl", train_rows)
    write_jsonl(args.out_dir / "eval.jsonl", eval_rows)
    (args.out_dir / "train_task_ids.txt").write_text("\n".join(sorted(train_task_ids)) + "\n", encoding="utf-8")
    (args.out_dir / "eval_task_ids.txt").write_text("\n".join(sorted(eval_task_ids)) + "\n", encoding="utf-8")

    manifest = {
        "manifest_version": "template-large-v1",
        "seed_tag": args.seed_tag,
        "tasks_dir": str(args.tasks_dir.relative_to(ROOT) if args.tasks_dir.is_relative_to(ROOT) else args.tasks_dir),
        "out_dir": str(args.out_dir.relative_to(ROOT) if args.out_dir.is_relative_to(ROOT) else args.out_dir),
        "domains": sorted(allowed_domains),
        "single_file_tasks": [describe_task(task) for task in prepared_tasks],
        "train_variants_per_task": args.train_variants_per_task,
        "eval_variants_per_task": args.eval_variants_per_task,
        "holdout_policy": {
            **holdout_policy_manifest,
            "train_prompt_families": sorted(train_families),
            "eval_prompt_families": sorted(eval_families),
            "train_eval_example_id_overlap": False,
            "train_eval_prompt_family_overlap": False,
            "train_eval_task_id_overlap": bool(train_task_ids & eval_task_ids),
        },
        "train_summary": summarize(train_rows),
        "eval_summary": summarize(eval_rows),
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
