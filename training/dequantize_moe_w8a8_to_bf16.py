#!/usr/bin/env python3
"""Dequantize a compressed-tensors W8A8 checkpoint to bf16 shard-by-shard.

This script avoids `run_compressed=False` compatibility issues by converting
safetensors directly. It dequantizes EVERY int8 weight tensor that has a
sibling ``<name>_scale`` tensor. In Qwen3.6-35B-A3B-W8A8 this covers:
- self-attention projections: q_proj/k_proj/v_proj/o_proj  (scale [out, 1])
- MoE experts: gate_up_proj/down_proj                      (scale [E, N, 1])

Dequantization formula (per-channel scale broadcasts over the input dim):
    W_bf16 = (W_int8.float() * scale_f32).to(torch.bfloat16)

The ``<name>_scale`` tensors are dropped from the output because the resulting
weights are plain bf16. All other tensors are copied as-is.
"""

from __future__ import annotations

import argparse
import glob
import json
import shutil
from pathlib import Path

import torch
from safetensors.torch import load_file, save_file


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--keep-quantization-config", action="store_true")
    return p.parse_args()


def convert_shard(src_path: str, dst_path: str) -> tuple[int, int, int]:
    state = load_file(src_path)
    out: dict[str, torch.Tensor] = {}

    converted = 0
    int8_seen = 0
    dropped_scales = 0

    # Identify scale tensors paired with an int8 weight in this shard.
    scale_keys_to_drop: set[str] = set()
    for k, v in state.items():
        if v.dtype == torch.int8:
            int8_seen += 1
            scale_key = f"{k}_scale"
            if scale_key in state:
                scale_keys_to_drop.add(scale_key)

    for k, v in state.items():
        # Drop scale tensors whose weights we are dequantizing.
        if k in scale_keys_to_drop:
            dropped_scales += 1
            continue

        scale_key = f"{k}_scale"
        if v.dtype == torch.int8 and scale_key in state:
            scale = state[scale_key]
            # Per-channel scale broadcasts over the last (input) dimension:
            #   attn weight [out, in] * scale [out, 1]
            #   expert weight [E, N, M] * scale [E, N, 1]
            deq = (v.float() * scale.float()).to(torch.bfloat16)
            out[k] = deq
            converted += 1
        else:
            out[k] = v

    save_file(out, dst_path)
    return converted, int8_seen, dropped_scales


def main() -> None:
    args = parse_args()

    src = Path(args.input_dir)
    dst = Path(args.output_dir)
    dst.mkdir(parents=True, exist_ok=True)
    done_marker = dst / ".dequant_complete"

    # Ensure stale marker does not survive interrupted runs.
    if done_marker.exists():
        done_marker.unlink()

    shard_paths = sorted(glob.glob(str(src / "*.safetensors")))
    if not shard_paths:
        raise SystemExit("No .safetensors shards found in input dir")

    print(f"[convert] input={src}")
    print(f"[convert] output={dst}")
    print(f"[convert] shards={len(shard_paths)}")

    # Copy non-shard files first (skip the safetensors index; rebuilt below).
    index_name = "model.safetensors.index.json"
    for item in src.iterdir():
        if item.suffix == ".safetensors" or item.name == index_name:
            continue
        target = dst / item.name
        if item.is_file():
            shutil.copy2(item, target)

    total_converted = 0
    total_int8 = 0
    total_dropped = 0

    for i, sp in enumerate(shard_paths, 1):
        dp = str(dst / Path(sp).name)
        converted, int8_seen, dropped = convert_shard(sp, dp)
        total_converted += converted
        total_int8 += int8_seen
        total_dropped += dropped
        print(
            f"[convert] shard {i}/{len(shard_paths)} "
            f"dequantized={converted}/{int8_seen} dropped_scales={dropped}"
        )

    _rebuild_safetensors_index(src, dst, index_name)

    # Remove quantization metadata so loader treats the output as regular bf16 weights.
    cfg_path = dst / "config.json"
    if cfg_path.exists() and not args.keep_quantization_config:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        if "quantization_config" in cfg:
            del cfg["quantization_config"]
        cfg["torch_dtype"] = "bfloat16"
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=True, indent=2), encoding="utf-8")
        print(
            "[convert] updated config.json (removed quantization_config, set torch_dtype=bfloat16)"
        )

    done_marker.write_text("ok\n", encoding="utf-8")
    print(
        f"[convert] done dequantized={total_converted}/{total_int8} "
        f"dropped_scales={total_dropped}"
    )


def _rebuild_safetensors_index(src: Path, dst: Path, index_name: str) -> None:
    """Rebuild the weight_map index so dropped ``_scale`` keys are excluded."""
    src_index = src / index_name
    if not src_index.exists():
        return

    from safetensors import safe_open

    weight_map: dict[str, str] = {}
    total_size = 0
    for shard_path in sorted(glob.glob(str(dst / "*.safetensors"))):
        shard_name = Path(shard_path).name
        with safe_open(shard_path, framework="pt") as f:
            for key in f.keys():
                weight_map[key] = shard_name
                tensor = f.get_slice(key)
                shape = tensor.get_shape()
                numel = 1
                for dim in shape:
                    numel *= dim
                dtype = str(tensor.get_dtype()).lower()
                bytes_per = 2 if ("16" in dtype) else (4 if "32" in dtype else 1)
                total_size += numel * bytes_per

    index = {"metadata": {"total_size": total_size}, "weight_map": weight_map}
    (dst / index_name).write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"[convert] rebuilt {index_name} ({len(weight_map)} tensors)")


if __name__ == "__main__":
    main()
