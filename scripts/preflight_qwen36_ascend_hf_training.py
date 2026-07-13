#!/usr/bin/env python3
"""Fail-fast checks for Qwen3.6 training routes on Ascend/HF."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BLOCKED_MODEL_MARKERS = (
    "qwen3.6-35b-a3b-w8a8",
    "qwen36-35b-a3b-w8a8",
)

BLOCKED_MESSAGE = (
    "Qwen3.6-35B-A3B-W8A8 is blocked on the current Ascend + Hugging Face "
    "training path: the MoE W8A8 int8 weights reach aclnnMm, whose fallback "
    "matmul path rejects DT_INT8. Use a non-quantized/BF16 35B checkpoint "
    "or vendor kernels that support W8A8 MoE training."
)


def is_ascend_training_device(device: str) -> bool:
    normalized = device.strip().lower()
    return normalized in {"npu", "ascend", "ascend-npu"}


def is_known_blocked_qwen36_w8a8_model(model_name: str) -> bool:
    normalized = model_name.replace("_", "-").lower()
    return any(marker in normalized for marker in BLOCKED_MODEL_MARKERS)


def read_config_model_markers(model_name: str) -> list[str]:
    path = Path(model_name)
    if not path.is_dir():
        return []
    config_path = path / "config.json"
    if not config_path.is_file():
        return []
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    markers: list[str] = []
    for key in ("model_type", "architectures", "quantization_config", "quant_method"):
        value = config.get(key)
        if value is not None:
            markers.append(json.dumps(value, sort_keys=True).lower())
    return markers


def build_preflight_result(
    model_name: str, device: str, *, allow_known_blocked: bool = False
) -> dict[str, object]:
    blocked_by_name = is_known_blocked_qwen36_w8a8_model(model_name)
    config_markers = read_config_model_markers(model_name)
    config_text = " ".join(config_markers)
    blocked_by_config = "qwen3" in config_text and "moe" in config_text and "w8a8" in config_text
    blocked = is_ascend_training_device(device) and (blocked_by_name or blocked_by_config)

    status = "blocked" if blocked and not allow_known_blocked else "ok"
    return {
        "stage": "qwen36_ascend_hf_training_preflight",
        "status": status,
        "model_name": model_name,
        "device": device,
        "blocked_by_name": blocked_by_name,
        "blocked_by_config": blocked_by_config,
        "message": BLOCKED_MESSAGE if blocked else "",
        "bypass": "ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER=1" if blocked else "",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model-name", required=True, help="Model id or model directory planned for training."
    )
    parser.add_argument("--device", default="npu", help="Training device/backend name.")
    parser.add_argument(
        "--json", action="store_true", help="Emit a machine-readable preflight record."
    )
    parser.add_argument(
        "--allow-known-blocked",
        action="store_true",
        help="Report the blocker but exit successfully for explicit diagnostic reruns.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = build_preflight_result(
        args.model_name,
        args.device,
        allow_known_blocked=args.allow_known_blocked,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result["status"] == "blocked":
        print(result["message"], file=sys.stderr)

    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
