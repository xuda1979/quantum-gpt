#!/usr/bin/env python3
"""Self-play data generation: sample solutions from the base model, validate
against test harnesses, and keep passing examples as training data.

Works CPU-only for generation (slow but functional). For faster generation,
run on Huanxin with NPU inference.

Usage:
    python3 data/generate/self_play_datagen.py \
        --model-name models/Qwen2.5-1.5B-Instruct \
        --tasks-dir evals/tasks \
        --output data/generated/self-play-v1.jsonl \
        --samples-per-task 16 \
        --temperature 0.8
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any


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
    p.add_argument("--model-name", required=True, help="Path or HF name of base model")
    p.add_argument("--tasks-dir", default="evals/tasks", help="Root of eval tasks")
    p.add_argument("--output", default="data/generated/self-play-v1.jsonl")
    p.add_argument("--samples-per-task", type=int, default=16)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--top-p", type=float, default=0.95)
    p.add_argument("--max-new-tokens", type=int, default=2048)
    p.add_argument("--device", default="cpu", help="cpu, npu, or cuda")
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def load_task(task_dir: Path) -> dict[str, Any] | None:
    """Load a task.json and its test harness."""
    task_json = task_dir / "task.json"
    tests_py = task_dir / "tests.py"
    if not task_json.exists() or not tests_py.exists():
        return None
    with open(task_json) as f:
        task = json.load(f)
    return {"meta": task, "task_dir": task_dir, "tests_py": tests_py}


def load_test_harness(tests_py: Path):
    """Dynamically load the test module."""
    spec = importlib.util.spec_from_file_location("tests", str(tests_py))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_base_prompt(meta: dict[str, Any], task_dir: Path) -> str:
    """Build the core task description from task metadata and candidate interface hints."""
    parts: list[str] = []
    if "task_prompt" in meta:
        parts.append(meta["task_prompt"])
    elif "description" in meta:
        parts.append(meta["description"])
    elif "name" in meta:
        parts.append(f"Task: {meta['name']}")

    candidate_file = meta.get("candidate_file")
    if candidate_file:
        candidate_path = task_dir / candidate_file
        if candidate_path.exists():
            interface_lines = summarize_candidate_interface(candidate_path)
            if interface_lines:
                parts.append("Required interface:")
                parts.extend(f"- {line}" for line in interface_lines)

    behavior_hints = extract_behavior_hints(task_dir / "tests.py")
    if behavior_hints:
        parts.append("Behavioral requirements:")
        parts.extend(f"- {line}" for line in behavior_hints)

    if meta.get("task_type") == "repair" and "broken_candidate" in meta:
        parts.append(f"\nBroken code:\n```python\n{meta['broken_candidate']}\n```")

    return "\n".join(parts).strip()


def extract_behavior_hints(tests_path: Path) -> list[str]:
    """Pull compact behavioral hints from the test harness text."""
    if not tests_path.exists():
        return []

    hints: list[str] = []
    try:
        lines = tests_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith(("import ", "from ", "def ", "return ", "module = ", "spec = ", "assert ")):
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

        text = line.split(marker, 1)[1].rstrip(")")
        try:
            value = eval(text, {"__builtins__": {}}, {})
        except Exception:
            value = None
        if not isinstance(value, str) or not value:
            continue

        normalized = " ".join(value.split())
        lower = normalized.lower()
        if lower.endswith("was incorrect"):
            hints.append(normalized.replace(" was incorrect", ""))
        elif any(token in lower for token in ["should", "expected", "raise", "retry", "round-trip", "preserved", "valid json", "did not raise", "no retry"]):
            hints.append(normalized)

    deduped: list[str] = []
    seen: set[str] = set()
    for hint in hints:
        if len(hint) < 8:
            continue
        if hint.isdigit():
            continue
        normalized = " ".join(hint.split())
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)
        if len(deduped) >= 6:
            break
    return deduped


def summarize_candidate_interface(candidate_path: Path) -> list[str]:
    """Extract function/class signatures from the reference candidate when available."""
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
                    default_value = defaults[index - default_offset]
                    arg_text += f" = {ast.unparse(default_value)}"
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


def build_prompt(task: dict, sample_index: int) -> str:
    """Build a richer user prompt from task metadata with template variation."""
    meta = task["meta"]
    base = build_base_prompt(meta, task["task_dir"])
    is_repair = meta.get("task_type") == "repair"

    prefixes = REPAIR_PREFIXES if is_repair else PROMPT_PREFIXES
    suffixes = REPAIR_SUFFIXES if is_repair else PROMPT_SUFFIXES

    prefix = prefixes[sample_index % len(prefixes)]
    suffix = suffixes[sample_index % len(suffixes)]
    prompt = prefix + base + suffix

    if not base:
        fallback_name = meta.get("task_name") or meta.get("name") or task["task_dir"].name
        prompt = prefix + f"Task: {fallback_name}" + suffix

    return prompt.strip()


SYSTEM_PROMPT = (
    "You are a careful coding assistant focused on correctness, clear reasoning, "
    "and maintainable Python code. Follow the task instruction and use any provided "
    "artifacts as context. Return only the final code or requested artifact content."
)


def generate_one(model, tokenizer, prompt: str, args) -> str:
    """Generate a single candidate solution from the model."""
    import torch
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(args.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            do_sample=True,
        )
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return extract_code(response)


def extract_code(response: str) -> str:
    """Extract Python code from a response, handling markdown fences."""
    if "```python" in response:
        parts = response.split("```python")
        if len(parts) > 1:
            code = parts[1].split("```")[0]
            return code.strip()
    if "```" in response:
        parts = response.split("```")
        if len(parts) > 2:
            return parts[1].strip()
    return response.strip()


def validate_candidate(code: str, test_harness, task_dir: Path) -> dict:
    """Write candidate to temp file and run test harness against it."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir=str(task_dir)) as f:
        f.write(code)
        f.flush()
        candidate_path = f.name
    try:
        result = test_harness.run_tests(candidate_path)
        return result
    except Exception as e:
        return {"passed": False, "details": [f"Exception: {e}"]}
    finally:
        Path(candidate_path).unlink(missing_ok=True)


def format_example(task: dict, prompt: str, code: str, example_id: str) -> dict:
    """Format a passing solution into chat-SFT-v1 format."""
    meta = task["meta"]
    return {
        "format": "chat-sft-v1",
        "source_schema": "self-play-v1",
        "example_id": example_id,
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
            "source": "self-play",
            "task_id": meta.get("task_id", task["task_dir"].name),
            "task_name": meta.get("task_name", task["task_dir"].name),
        },
    }


def discover_tasks(tasks_dir: Path) -> list[dict]:
    """Find all eval tasks with task.json + tests.py."""
    tasks = []
    for domain_dir in sorted(tasks_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        for task_dir in sorted(domain_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            task = load_task(task_dir)
            if task:
                tasks.append(task)
    return tasks


def main() -> int:
    args = parse_args()
    tasks_dir = Path(args.tasks_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tasks = discover_tasks(tasks_dir)
    print(f"Found {len(tasks)} tasks with test harnesses")

    # Load model
    print(f"Loading model: {args.model_name} on {args.device}...")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(args.model_name, trust_remote_code=True)
    if args.device != "cpu":
        model.to(args.device)
    model.eval()

    import time
    total_generated = 0
    total_passed = 0
    t0 = time.time()

    with open(output_path, "a") as out:  # append mode — safe for restarts
        for ti, task in enumerate(tasks):
            task_name = task["task_dir"].name
            domain = task["meta"].get("domain", "?")
            print(f"\n[{ti+1}/{len(tasks)}] [{domain}/{task_name}] "
                  f"Generating {args.samples_per_task} candidates...")
            sys.stdout.flush()

            test_harness = load_test_harness(task["tests_py"])

            passed_count = 0
            for si in range(args.samples_per_task):
                t_sample = time.time()
                prompt = build_prompt(task, si)
                code = generate_one(model, tokenizer, prompt, args)
                gen_sec = time.time() - t_sample

                total_generated += 1
                result = validate_candidate(code, test_harness, task["task_dir"])
                status = "PASS" if result.get("passed") else "FAIL"

                if result.get("passed"):
                    total_passed += 1
                    passed_count += 1
                    example_id = f"selfplay_{task_name}_{uuid.uuid4().hex[:8]}"
                    example = format_example(task, prompt, code, example_id)
                    out.write(json.dumps(example, ensure_ascii=False) + "\n")
                    out.flush()

                elapsed = time.time() - t0
                print(f"  sample {si+1}/{args.samples_per_task} {status} "
                      f"({gen_sec:.1f}s gen, {total_passed}/{total_generated} total, "
                      f"{elapsed:.0f}s elapsed)")
                sys.stdout.flush()

            pass_rate = passed_count / args.samples_per_task * 100
            print(f"  => {passed_count}/{args.samples_per_task} passed ({pass_rate:.0f}%)")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s. {total_passed}/{total_generated} total passed "
          f"({total_passed/max(total_generated,1)*100:.1f}%)")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
