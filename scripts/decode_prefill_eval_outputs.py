#!/usr/bin/env python3
"""Decode remote completion token ids locally and score the run."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from transformers import AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast

from evals.runner.candidate_sanitize import sanitize_candidate_text
from training.text_preprocessor_backend import load_text_preprocessor_backend


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--base-model", type=Path, required=True)
    parser.add_argument("--outputs-json", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir.resolve()
    outputs = json.loads(args.outputs_json.read_text(encoding="utf-8"))
    backend = load_text_preprocessor_backend(
        str(args.base_model.resolve()),
        AutoTokenizer,
        AutoProcessor,
        PreTrainedTokenizerFast,
    )
    tokenizer = backend.text_backend
    candidate_map: dict[str, str] = {}
    for record in outputs.get("outputs", []):
        completion_ids = record["completion_ids"]
        candidate_text = sanitize_candidate_text(tokenizer.decode(completion_ids, skip_special_tokens=True))
        candidate_path = run_dir / record["candidate_file"]
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.write_text(candidate_text, encoding="utf-8")
        candidate_map[record["task_id"]] = str(candidate_path.resolve())

    (run_dir / "candidate-map.json").write_text(json.dumps(candidate_map, indent=2), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "runner" / "run_eval.py"), "--candidate-map", str(run_dir / "candidate-map.json")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        return result.returncode
    sys.stdout.write(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
