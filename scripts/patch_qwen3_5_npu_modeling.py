#!/usr/bin/env python3
"""Idempotently patch the installed transformers Qwen3.5 modeling file so LoRA
SFT can train on Ascend NPU.

Two Ascend operators fail in the hybrid Qwen3.5 backward pass:

1. aclnnFlashAttentionScoreGrad  - the flash-attention backward used by the
   softmax-attention layers. Avoided by forcing eager attention at model load
   time (QWEN_SFT_ATTN_IMPL=eager handling in training/qwen_sft_peft.py), so no
   source patch is required for that one.

2. Conv2DBackpropInput           - the backward of the grouped depthwise
   nn.Conv1d short-conv inside the gated-delta-rule (linear-attention) layers.
   When the CUDA causal_conv1d kernel is unavailable (always true on NPU) the
   model falls back to nn.Conv1d, whose backward is unsupported on Ascend. We
   replace that single fallback line with a mathematically identical manual
   causal depthwise conv built from pad/slice/mul/add, all of which have working
   Ascend backward kernels.

Safe to run repeatedly. Meant to run once at the start of every training launch
because the in-container transformers install is ephemeral.
"""

import sys

OLD = "                mixed_qkv = F.silu(self.conv1d(mixed_qkv)[:, :, :seq_len])\n"
NEW = (
    "                # NPU fix: Ascend Conv2DBackpropInput (grouped depthwise\n"
    "                # conv1d backward) is unsupported. Equivalent manual causal\n"
    "                # depthwise conv via pad/slice/mul/add, which all have\n"
    "                # supported backward kernels on Ascend.\n"
    "                _cw = self.conv1d.weight.squeeze(1)\n"
    "                _xp = F.pad(mixed_qkv, (self.conv_kernel_size - 1, 0))\n"
    "                _acc = (\n"
    "                    self.conv1d.bias.view(1, -1, 1).to(mixed_qkv.dtype)\n"
    "                    if self.conv1d.bias is not None\n"
    "                    else None\n"
    "                )\n"
    "                for _k in range(self.conv_kernel_size):\n"
    "                    _term = _xp[:, :, _k:_k + seq_len] * _cw[:, _k].view(1, -1, 1)\n"
    "                    _acc = _term if _acc is None else _acc + _term\n"
    "                mixed_qkv = F.silu(_acc)\n"
)
MARKER = "# NPU fix: Ascend Conv2DBackpropInput"


def find_modeling_path():
    import os

    import transformers

    path = os.path.join(
        os.path.dirname(transformers.__file__),
        "models",
        "qwen3_5",
        "modeling_qwen3_5.py",
    )
    if not os.path.exists(path):
        raise SystemExit("modeling file not found at %s" % path)
    return path


def main():
    path = find_modeling_path()
    src = open(path, encoding="utf-8").read()
    if MARKER in src:
        print("ALREADY_PATCHED %s" % path)
        return 0
    if OLD not in src:
        print("ANCHOR_NOT_FOUND in %s -- modeling source differs; not patched" % path)
        return 2
    src = src.replace(OLD, NEW, 1)
    open(path, "w", encoding="utf-8").write(src)
    import ast

    ast.parse(open(path, encoding="utf-8").read())
    print("PATCHED_OK %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
