#!/usr/bin/env python3
"""Render concrete remote bootstrap commands from an audited Huanxin bundle.

This turns a bundle produced by ``scripts/prepare_huanxin_bootstrap.py`` into a
single durable runbook artifact with:
- exact remote mkdir/cd commands
- exact pip install + smoke commands for the bundled training bootstrap files
- per-file paste stubs tied to manifest paths and hashes

It does not transfer files by itself. The goal is to remove ambiguity at the
moment browser auth becomes usable again.

Important: the default model target is the explicit remote local-path handoff
location under `/root/work/quantum-gpt/models/...`, not an unresolved
public Hugging Face identifier. This avoids generating misleading remote smoke
commands that look runnable before a verified local snapshot has actually been
placed on Huanxin.
"""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "/root/work/quantum-gpt/models/Qwen3.5-1.5B-Instruct"
DEFAULT_DATASET = "data/seed/splits-auto-seed/train.jsonl"
DEFAULT_TRAIN = "data/seed/splits-auto-seed/train.jsonl"
DEFAULT_VAL = "data/seed/splits-auto-seed/val.jsonl"
DEFAULT_REQS = "training/requirements-huanxin-cpu.txt"
GEMMA_REQS = "training/requirements-gemma4-runtime.txt"
DEFAULT_SMOKE = "training/huanxin_cpu_smoke.py"
DEFAULT_TRAINING = "training/qwen_sft_peft.py"
DEFAULT_PREFLIGHT_TARGETS = [
    "training/huanxin_cpu_smoke.py",
    "training/qwen_sft_peft.py",
]
DEFAULT_OUTPUT_DIR = "outputs/qwen35-1p5b-peft-smoke"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bundle",
        type=Path,
        help="Path to a timestamped bundle dir under artifacts/huanxin-bootstrap/",
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL,
        help="Remote model path or identifier to use in smoke/train commands. Defaults to the explicit remote local-path handoff target, not an unresolved HF model id.",
    )
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--train-file", default=DEFAULT_TRAIN)
    parser.add_argument("--eval-file", default=DEFAULT_VAL)
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Remote output dir used by the optional PEFT smoke command",
    )
    parser.add_argument(
        "--output", type=Path, help="Optional explicit output path for the rendered command file"
    )
    return parser.parse_args()


def find_file(files: list[dict], rel_path: str) -> bool:
    return any(item.get("path") == rel_path for item in files)


def existing_preflight(files: list[dict]) -> list[str]:
    return [rel_path for rel_path in DEFAULT_PREFLIGHT_TARGETS if find_file(files, rel_path)]


def resolve_requirements_file(model_name: str) -> str:
    lowered = model_name.lower()
    if "gemma-4" in lowered or "gemma4" in lowered:
        return GEMMA_REQS
    return DEFAULT_REQS


def build_text(
    manifest: dict,
    model_name: str,
    dataset: str,
    train_file: str,
    eval_file: str,
    output_dir: str,
) -> str:
    remote_root = manifest["remote_root"]
    remote_root_q = shlex.quote(remote_root)
    model_name_q = shlex.quote(model_name)
    dataset_q = shlex.quote(dataset)
    train_file_q = shlex.quote(train_file)
    eval_file_q = shlex.quote(eval_file)
    output_dir_q = shlex.quote(output_dir)
    files = manifest["files"]
    requirements_file = resolve_requirements_file(model_name)
    lines: list[str] = []
    lines.append("# Huanxin bootstrap command sheet")
    lines.append(f"# bundle_label: {manifest.get('label', 'unknown')}")
    lines.append(f"# created_at_utc: {manifest.get('created_at_utc', 'unknown')}")
    lines.append(f"# remote_root: {remote_root}")
    lines.append("")
    lines.append("set -euo pipefail")
    lines.append(f"mkdir -p {remote_root_q}")
    lines.append(f"cd {remote_root_q}")
    lines.append("pwd")
    lines.append("python3 --version")
    lines.append("")
    lines.append("# Paste validated files below, preserving exact relative paths.")
    for item in files:
        rel_path = item["path"]
        lines.append(f"# sha256 {item['sha256']}  {rel_path}")
        lines.append(
            f"mkdir -p {shlex.quote(str(Path(rel_path).parent))}"
            if str(Path(rel_path).parent) != "."
            else "# top-level file"
        )
        lines.append(f"cat > {shlex.quote(rel_path)} <<'EOF'")
        lines.append(f"# paste local contents of {rel_path} here")
        lines.append("EOF")
        lines.append("")

    if find_file(files, "evals/runner/run_eval.py"):
        lines.append("# Baseline repo gate if eval runner is part of this bundle.")
        lines.append("python3 evals/runner/run_eval.py")
        lines.append("")

    preflight_targets = existing_preflight(files)
    if preflight_targets:
        lines.append("# Local-file syntax preflight on the remote host before package install.")
        lines.append(
            "python3 -m py_compile " + " ".join(shlex.quote(path) for path in preflight_targets)
        )
        lines.append("")

    if find_file(files, requirements_file):
        lines.append("# Install the minimal CPU bootstrap stack.")
        lines.append("python3 -m pip install --upgrade pip")
        lines.append(f"python3 -m pip install -r {shlex.quote(requirements_file)}")
        lines.append("")
    elif requirements_file == GEMMA_REQS:
        lines.append("# Gemma 4 runtime upgrade file is not present in this bundle.")
        lines.append(f"# Expected requirements file: {GEMMA_REQS}")
        lines.append("")

    if find_file(files, DEFAULT_SMOKE):
        lines.append("# Tokenizer and dataset smoke.")
        lines.append(
            "python3 "
            f"{shlex.quote(DEFAULT_SMOKE)} --model-name {model_name_q} --dataset {dataset_q}"
        )
        lines.append("")
        lines.append("# Optional full model-load smoke.")
        lines.append(
            "python3 "
            f"{shlex.quote(DEFAULT_SMOKE)} --model-name {model_name_q} --dataset {dataset_q} --load-model"
        )
        lines.append("")

    if find_file(files, DEFAULT_TRAINING):
        lines.append("# Optional 1-step PEFT startup smoke after model load succeeds.")
        lines.append(
            "python3 "
            f"{shlex.quote(DEFAULT_TRAINING)} "
            f"--model-name {model_name_q} "
            f"--train-file {train_file_q} "
            f"--eval-file {eval_file_q} "
            f"--output-dir {output_dir_q} "
            "--device cpu --max-steps 1 --per-device-batch-size 1 --gradient-accumulation-steps 1"
        )
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    bundle = args.bundle.resolve()
    manifest_path = bundle / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_path = args.output.resolve() if args.output else bundle / "REMOTE_BOOTSTRAP_COMMANDS.sh"
    output_path.write_text(
        build_text(
            manifest,
            args.model_name,
            args.dataset,
            args.train_file,
            args.eval_file,
            args.output_dir,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"bundle": str(bundle), "output": str(output_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
