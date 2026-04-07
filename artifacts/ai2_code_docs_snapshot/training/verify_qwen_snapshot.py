#!/usr/bin/env python3
"""Verify a local Qwen snapshot directory before Huanxin transfer.

This is intentionally lightweight and offline-first. It does not try to fetch
anything. It answers one narrow question:

- does a provided local directory look like a real Hugging Face model snapshot
  for the expected Qwen target, with enough files present to justify transfer
  and remote smoke testing?

Use it when the project blocker shifts from "no artifact source" to
"someone provided a local path; is it actually the right thing?"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_CONFIG_FILES = [
    "config.json",
]

TOKENIZER_CANDIDATES = [
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",
    "merges.txt",
    "sentencepiece.bpe.model",
    "spiece.model",
]

WEIGHT_CANDIDATES = [
    "model.safetensors",
    "model.safetensors.index.json",
    "pytorch_model.bin",
    "pytorch_model.bin.index.json",
]

PROCESSOR_CANDIDATES = [
    "processor_config.json",
    "preprocessor_config.json",
]

CHAT_TEMPLATE_CANDIDATES = [
    "chat_template.jinja",
    "chat_template.json",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot_dir", type=Path, help="Local snapshot directory to verify")
    parser.add_argument(
        "--expected-substring",
        default="Qwen3.5-1.5B-Instruct",
        help="Substring expected in config metadata, path, or model identifiers",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def find_present(root: Path, names: list[str]) -> list[str]:
    return [name for name in names if (root / name).exists()]


def collect_weight_files(root: Path) -> list[str]:
    found = []
    for pattern in ("*.safetensors", "*.bin"):
        for path in sorted(root.glob(pattern)):
            found.append(path.name)
    index_files = find_present(root, ["model.safetensors.index.json", "pytorch_model.bin.index.json"])
    for name in index_files:
        if name not in found:
            found.append(name)
    return found


def requires_processor_artifacts(config: dict | None) -> bool:
    if not isinstance(config, dict):
        return False
    architectures = [str(item) for item in (config.get("architectures") or [])]
    if any("ConditionalGeneration" in item for item in architectures):
        return True
    if config.get("vision_config") is not None:
        return True
    if config.get("image_token_id") is not None or config.get("video_token_id") is not None:
        return True
    return False


def main() -> int:
    args = parse_args()
    root = args.snapshot_dir.expanduser().resolve()

    summary: dict[str, object] = {
        "snapshot_dir": str(root),
        "expected_substring": args.expected_substring,
    }

    if not root.exists():
        summary.update({"status": "error", "stage": "path_check", "error": "snapshot directory does not exist"})
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1
    if not root.is_dir():
        summary.update({"status": "error", "stage": "path_check", "error": "snapshot path is not a directory"})
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    present_config = find_present(root, REQUIRED_CONFIG_FILES)
    present_tokenizer = find_present(root, TOKENIZER_CANDIDATES)
    present_weights = collect_weight_files(root)
    present_processor = find_present(root, PROCESSOR_CANDIDATES)
    present_chat_template = find_present(root, CHAT_TEMPLATE_CANDIDATES)

    config = load_json(root / "config.json")
    tokenizer_config = load_json(root / "tokenizer_config.json")
    generation_config = load_json(root / "generation_config.json")
    processor_config = load_json(root / "processor_config.json")
    preprocessor_config = load_json(root / "preprocessor_config.json")

    candidate_strings: list[str] = [str(root)]
    for payload in (config, tokenizer_config, generation_config, processor_config, preprocessor_config):
        if isinstance(payload, dict):
            for key in ("_name_or_path", "model_type", "architectures", "tokenizer_class"):
                value = payload.get(key)
                if isinstance(value, str):
                    candidate_strings.append(value)
                elif isinstance(value, list):
                    candidate_strings.extend(str(item) for item in value)

    expected_hit = any(args.expected_substring.lower() in text.lower() for text in candidate_strings)
    config_model_type = config.get("model_type") if isinstance(config, dict) else None
    config_architectures = config.get("architectures") if isinstance(config, dict) else None
    qwen_metadata_hit = False
    if isinstance(config_model_type, str) and "qwen" in config_model_type.lower():
        qwen_metadata_hit = True
    if isinstance(config_architectures, list) and any("qwen" in str(item).lower() for item in config_architectures):
        qwen_metadata_hit = True

    summary["present_config_files"] = present_config
    summary["present_tokenizer_files"] = present_tokenizer
    summary["present_weight_files"] = present_weights
    summary["present_processor_files"] = present_processor
    summary["present_chat_template_files"] = present_chat_template
    summary["accepted_tokenizer_evidence"] = present_tokenizer[:]
    summary["accepted_weight_evidence"] = present_weights[:]
    summary["accepted_processor_evidence"] = present_processor[:]
    summary["accepted_chat_template_evidence"] = present_chat_template[:]
    summary["config_model_type"] = config_model_type
    summary["config_architectures"] = config_architectures
    summary["expected_substring_hit"] = expected_hit
    summary["qwen_metadata_hit"] = qwen_metadata_hit
    summary["directory_file_count"] = sum(1 for _ in root.iterdir())
    summary["requires_processor_artifacts"] = requires_processor_artifacts(config)

    missing_reasons = []
    if not present_config:
        missing_reasons.append("missing config.json")
    if not present_tokenizer:
        missing_reasons.append("missing tokenizer files")
    if not present_weights:
        missing_reasons.append("missing model weight files")
    if summary["requires_processor_artifacts"]:
        if not present_processor:
            missing_reasons.append("missing processor/preprocessor config files for conditional-generation snapshot")
        if not present_chat_template and not (isinstance(tokenizer_config, dict) and tokenizer_config.get("chat_template")):
            missing_reasons.append("missing chat template for conditional-generation snapshot")
    if not expected_hit:
        missing_reasons.append("expected model substring not found in path/config metadata")
    if not qwen_metadata_hit:
        missing_reasons.append("config metadata does not identify a Qwen-family architecture")

    if missing_reasons:
        summary["status"] = "error"
        summary["stage"] = "snapshot_verify"
        summary["error"] = "; ".join(missing_reasons)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    summary["status"] = "ok"
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
