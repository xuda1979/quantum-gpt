#!/usr/bin/env python3
"""Repair the 203-row ASI2 distillation dataset for runnable SFT training.

This script performs two conservative repairs:
1. Append the required suffix "写出完整的可运行的代码。" to every user prompt.
2. For Python-like assistant answers that are only bare definitions / helpers,
   append a minimal runnable smoke block so the answer is not just a function
   definition.

The source dataset is left untouched. A repaired version is written to a new
output directory with a manifest describing the changes.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203/all_chatml.jsonl"
)
DEFAULT_OUTPUT_DIR = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_repaired"
)
QUESTION_SUFFIX = "写出完整的可运行的代码。"


@dataclass(frozen=True)
class FunctionParam:
    name: str
    annotation: str | None = None
    has_default: bool = False


@dataclass(frozen=True)
class FunctionSpec:
    name: str
    params: list[FunctionParam]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--suffix", default=QUESTION_SUFFIX)
    return parser.parse_args()


def append_question_suffix(prompt: str, suffix: str) -> str:
    text = str(prompt or "").strip()
    if not text:
        return text
    if suffix in text:
        return text
    if text.endswith(("。", ".", "?", "？", "!", "！")):
        return f"{text} {suffix}"
    return f"{text}\n\n{suffix}"


def _is_python_like_answer(text: str) -> bool:
    lowered = text.lower()
    if "```isq" in lowered or "procedure main" in lowered or re.search(r"^\s*qbit\b", text, re.M):
        return False
    return any(
        token in text
        for token in ("def ", "import ", "from ", "class ", "if __name__", "assert ", "print(")
    )


def _has_entrypoint(text: str) -> bool:
    lowered = text.lower()
    return (
        "if __name__" in lowered
        or re.search(r"^\s*assert\s+", text, re.M) is not None
        or re.search(r"^\s*print\s*\(", text, re.M) is not None
        or "unittest" in lowered
        or "pytest" in lowered
    )


def _extract_function_specs(text: str) -> list[FunctionSpec]:
    specs: list[FunctionSpec] = []
    pattern = re.compile(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*:", re.M)
    for match in pattern.finditer(text):
        name = match.group(1)
        params_src = match.group(2).strip()
        params: list[FunctionParam] = []
        if params_src:
            try:
                fake = ast.parse(f"def _f({params_src}):\n    pass\n")
                args = fake.body[0].args  # type: ignore[assignment]
                all_args = list(args.posonlyargs) + list(args.args)
                defaults = list(args.defaults)
                default_offset = len(all_args) - len(defaults)
                for index, arg in enumerate(all_args):
                    annotation = ast.unparse(arg.annotation) if arg.annotation is not None else None
                    params.append(
                        FunctionParam(
                            name=arg.arg,
                            annotation=annotation,
                            has_default=index >= default_offset,
                        )
                    )
                if args.vararg is not None:
                    params.append(
                        FunctionParam(
                            name=f"*{args.vararg.arg}", annotation=None, has_default=False
                        )
                    )
                for kwarg, default in zip(args.kwonlyargs, args.kw_defaults, strict=False):
                    annotation = (
                        ast.unparse(kwarg.annotation) if kwarg.annotation is not None else None
                    )
                    params.append(
                        FunctionParam(
                            name=kwarg.arg,
                            annotation=annotation,
                            has_default=default is not None,
                        )
                    )
            except Exception:
                # Fallback: split on commas so we can still build a smoke block.
                for raw in params_src.split(","):
                    token = raw.strip()
                    if not token:
                        continue
                    name = token.split(":", 1)[0].split("=", 1)[0].strip()
                    params.append(FunctionParam(name=name))
        specs.append(FunctionSpec(name=name, params=params))
    return specs


def _pick_target_function(specs: list[FunctionSpec]) -> FunctionSpec | None:
    if not specs:
        return None
    for spec in specs:
        if (
            not spec.name.startswith("_")
            and not spec.name.startswith("test_")
            and spec.name not in {"main"}
        ):
            return spec
    return specs[0]


def _placeholder_for_param(param: FunctionParam) -> str:
    name = param.name.lower()
    annotation = (param.annotation or "").lower()

    if name.startswith("*"):
        return ""
    if "circuit" in name or name in {
        "circ",
        "qc",
        "c",
        "eng",
        "backend",
        "device",
        "sim",
        "simulator",
        "graph",
    }:
        return "_SmokeObject()"
    if "rho" in name or "matrix" in name or "hamiltonian" in name:
        return "np.array([[1, 0], [0, 0]], dtype=complex)"
    if "state" in name or "vector" in name:
        return "[1.0, 0.0]"
    if "bitstring" in name:
        return '"01"'
    if "bits" in name:
        return '"01"'
    if "bell" in name:
        return '"phi_plus"'
    if "operation" in name or "gate" in name:
        return '"I"'
    if "edges" in name:
        return "[(0, 1)]"
    if "syndrom" in name:
        return "[(0, 0), (1, 0)]"
    if "ops" in name or "operations" in name:
        return '["H", "X"]'
    if "path" in name:
        return '"candidate.py"'
    if (
        "p" == name
        or "prob" in name
        or "alpha" in name
        or "theta" in name
        or "phi" in name
        or "gamma" in name
        or "beta" in name
        or "dt" in name
        or "time" in name
    ):
        return "0.1"
    if (
        "n_qubits" in name
        or "num_qubits" in name
        or "qubit_count" in name
        or name == "n"
        or name.endswith("_n")
    ):
        return "2"
    if "basis_index" in name or "index" in name or name in {"i", "j", "k"}:
        return "0"
    if annotation in {"int", "builtins.int"}:
        return "2"
    if annotation in {"float", "builtins.float"}:
        return "0.1"
    if annotation in {"str", "builtins.str"}:
        return '"sample"'
    if annotation.startswith("list[") or annotation.startswith("list[") or annotation == "list":
        return "[]"
    if annotation.startswith("tuple[") or annotation == "tuple":
        return "()"
    if annotation.startswith("dict[") or annotation == "dict":
        return "{}"
    if annotation == "bool":
        return "True"
    return "0"


def _build_smoke_block(text: str) -> str:
    specs = _extract_function_specs(text)
    target = _pick_target_function(specs)
    if target is None:
        return ""

    imports = ["import numpy as np"]
    needs_smoke_object = any(
        "circuit" in param.name.lower()
        or param.name.lower()
        in {"circ", "qc", "c", "eng", "backend", "device", "sim", "simulator", "graph"}
        for param in target.params
    )
    smoke_object = ""
    if needs_smoke_object:
        smoke_object = """
class _SmokeObject:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def __getattr__(self, name: str):
        def _method(*args: Any, **kwargs: Any):
            self.calls.append((name, args, kwargs))
            return self

        return _method

    def __call__(self, *args: Any, **kwargs: Any):
        self.calls.append(("__call__", args, kwargs))
        return self

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __repr__(self) -> str:
        return f"<_SmokeObject calls={len(self.calls)}>"
""".strip()

    arg_exprs = []
    for param in target.params:
        expr = _placeholder_for_param(param)
        if expr:
            arg_exprs.append(expr)

    call_expr = f"{target.name}({', '.join(arg_exprs)})"
    harness = f"""
if __name__ == "__main__":
    try:
        _result = {call_expr}
        print(_result)
    except Exception as _exc:
        print(f"{target.name} smoke call failed: {{_exc}}")
""".strip()

    pieces = ["", *imports]
    if smoke_object:
        pieces.append(smoke_object)
    pieces.append(harness)
    return "\n\n".join(pieces)


def repair_answer(text: str) -> tuple[str, bool]:
    original = text or ""
    repaired = original
    changed = False

    if _is_python_like_answer(original) and not _has_entrypoint(original):
        smoke = _build_smoke_block(original)
        if smoke:
            repaired = original.rstrip() + "\n\n" + smoke + "\n"
            changed = True

    return repaired, changed


def repair_row(row: dict[str, Any], suffix: str) -> tuple[dict[str, Any], dict[str, bool]]:
    repaired = json.loads(json.dumps(row))
    changed = {"prompt_suffix": False, "answer_smoke": False}

    messages = repaired.get("messages")
    if not isinstance(messages, list) or len(messages) < 3:
        return repaired, changed

    user = messages[1]
    assistant = messages[2]

    if isinstance(user, dict):
        prompt = str(user.get("content") or "")
        new_prompt = append_question_suffix(prompt, suffix)
        if new_prompt != prompt:
            user["content"] = new_prompt
            changed["prompt_suffix"] = True

    if isinstance(assistant, dict):
        answer = str(assistant.get("content") or "")
        new_answer, answer_changed = repair_answer(answer)
        if answer_changed:
            assistant["content"] = new_answer
            changed["answer_smoke"] = True

    return repaired, changed


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    args = parse_args()
    payload: list[dict[str, Any]] = []
    with args.input_jsonl.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            row = json.loads(text)
            if not isinstance(row, dict):
                raise ValueError(f"{args.input_jsonl}:{line_no}: expected a JSON object")
            payload.append(row)

    repaired_rows: list[dict[str, Any]] = []
    counts = {"prompt_suffix": 0, "answer_smoke": 0}
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("dataset rows must be JSON objects")
        repaired, changed = repair_row(row, args.suffix)
        repaired_rows.append(repaired)
        for key, value in changed.items():
            counts[key] += int(bool(value))

    output_dir = args.output_dir
    train_path = output_dir / "all_chatml.jsonl"
    manifest_path = output_dir / "manifest.json"

    write_jsonl(train_path, repaired_rows)
    manifest = {
        "ok": True,
        "source": str(args.input_jsonl),
        "output_dir": str(output_dir),
        "output_file": str(train_path),
        "total_rows": len(repaired_rows),
        "changed_rows": counts,
        "suffix": args.suffix,
        "repair_policy": {
            "prompt_suffix": "append_once_if_missing",
            "answer_smoke": "append_minimal_python_entrypoint_for_bare_definitions",
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
