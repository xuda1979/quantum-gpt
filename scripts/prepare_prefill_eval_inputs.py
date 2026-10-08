#!/usr/bin/env python3
"""Prepare tokenizer-derived prompt tensors for remote eval without remote tokenization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from transformers import AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast

from scripts.run_hf_pass1_eval import render_prompt
from training.text_preprocessor_backend import load_text_preprocessor_backend


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    output_path = args.output.resolve()

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    system_prompt = (run_dir / "SYSTEM_PROMPT.txt").read_text(encoding="utf-8")
    backend = load_text_preprocessor_backend(
        str(args.base_model.resolve()),
        AutoTokenizer,
        AutoProcessor,
        PreTrainedTokenizerFast,
    )
    chat_template_path = args.base_model.resolve() / "chat_template.jinja"
    render_backend = backend.render_backend
    if hasattr(render_backend, "chat_template") and not getattr(render_backend, "chat_template", None) and chat_template_path.exists():
        render_backend.chat_template = chat_template_path.read_text(encoding="utf-8")

    records: list[dict[str, object]] = []
    for task in manifest.get("tasks", []):
        prompt_text = (run_dir / task["prompt_file"]).read_text(encoding="utf-8")
        rendered = render_prompt(backend, system_prompt=system_prompt, user_prompt=prompt_text)
        encoded = backend.text_backend(rendered, return_attention_mask=True)
        records.append(
            {
                "task_id": task["id"],
                "prompt_file": task["prompt_file"],
                "candidate_file": task["candidate_file"],
                "input_ids": list(encoded["input_ids"]),
                "attention_mask": list(encoded["attention_mask"]),
            }
        )

    payload = {
        "run_dir": str(run_dir),
        "base_model": str(args.base_model.resolve()),
        "tokenizer_backend_kind": backend.backend_kind,
        "pad_token_id": getattr(backend.text_backend, "pad_token_id", None),
        "eos_token_id": getattr(backend.text_backend, "eos_token_id", None),
        "records": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output_path), "records": len(records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
