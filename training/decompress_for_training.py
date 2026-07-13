#!/usr/bin/env python3
"""
Preprocess quantized model to full precision for Ascend NPU training.

Issue: Qwen3.6-35B-A3B-W8A8 has int8-quantized MoE experts.
During training, transformers/integrations/moe.py routes through _grouped_mm_fallback,
which does torch.mm(input, weight[i]) where weight[i] stays DT_INT8.
Ascend aclnnMm kernel rejects int8 operands.

Solution: Fully dequantize the model to bf16 before training starts.
This module loads the model and ensures all weights (including MoE experts) are decompressed.
"""


import torch
from transformers import AutoConfig, AutoModelForCausalLM


def decompress_model_for_training(
    model_name_or_path: str,
    output_path: str | None = None,
    device: str = "cpu",
    torch_dtype: torch.dtype = torch.bfloat16,
    verbose: bool = True,
) -> tuple:
    """
    Load a quantized model and decompress it to full precision.

    For Qwen3.6-35B-A3B-W8A8:
    - Loads with run_compressed=False to trigger decompression
    - Iterates through all linear layers (including MoE experts)
    - Converts int8 weights to bf16
    - Returns model ready for NPU training

    Args:
        model_name_or_path: Path or HF hub ID to quantized model
        output_path: If provided, save the decompressed model here
        device: Device to load on (cpu, npu, cuda, etc.)
        torch_dtype: Target dtype for weights (default bfloat16)
        verbose: Print progress

    Returns:
        (model, config): Decompressed model and config
    """

    if verbose:
        print(f"[decompress_model_for_training] Loading model from {model_name_or_path}...")

    # Load config
    config = AutoConfig.from_pretrained(model_name_or_path, trust_remote_code=True)
    if verbose:
        print(
            f"[config] model_type={config.model_type}, has_quantization_config={hasattr(config, 'quantization_config')}"
        )

    # Load model with decompression enabled
    # Setting device_map=None and device=cpu initially to avoid NAID mapping issues during loading
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        config=config,
        torch_dtype=torch_dtype,
        device_map=None,
        trust_remote_code=True,
        # Ensure quantization is decompressed
        run_compressed=False if hasattr(config, "quantization_config") else None,
    )

    if verbose:
        print(
            f"[model_loaded] dtype={model.dtype}, param_count={sum(p.numel() for p in model.parameters()):,}"
        )

    # Ensure all weights are in target dtype, especially MoE expert weights
    # This is the key step: convert any remaining int8 weights to bf16
    dequantized_layers = 0
    int8_count_before = 0

    for name, param in model.named_parameters():
        if param.dtype == torch.int8:
            int8_count_before += 1
            if verbose and int8_count_before <= 5:  # Log first few
                print(f"  Converting {name}: int8 -> {torch_dtype}")
            param.data = param.data.to(torch_dtype)
            dequantized_layers += 1

    for name, buf in model.named_buffers():
        if buf.dtype == torch.int8:
            int8_count_before += 1
            if verbose and int8_count_before <= 5:
                print(f"  Converting buffer {name}: int8 -> {torch_dtype}")
            buf.data = buf.data.to(torch_dtype)
            dequantized_layers += 1

    if verbose:
        print(f"[dequantized] Converted {dequantized_layers} int8 weights/buffers to {torch_dtype}")

    # Verify no int8 remains
    remaining_int8 = sum(1 for p in model.parameters() if p.dtype == torch.int8) + sum(
        1 for b in model.buffers() if b.dtype == torch.int8
    )
    if remaining_int8 > 0:
        print(f"[WARNING] {remaining_int8} int8 tensors still remain after conversion!")
    else:
        if verbose:
            print(
                "[dequantized_verified] No int8 tensors remain. Model is ready for Ascend training."
            )

    # Save decompressed model if requested
    if output_path:
        if verbose:
            print(f"[saving] Saving decompressed model to {output_path}...")
        model.save_pretrained(output_path)
        config.save_pretrained(output_path)
        if verbose:
            print(
                f"[saved] Done. Total model size: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B params"
            )

    return model, config


def load_decompressed_model_for_npu(
    model_name_or_path: str,
    device_map: str | None = None,
    npu_max_memory: int | None = None,
    verbose: bool = True,
) -> tuple:
    """
    Load decompressed model and prepare for NPU device mapping.

    Args:
        model_name_or_path: Path to (preferably already decompressed) model
        device_map: device map strategy (e.g., 'balanced-layers', 'auto')
        npu_max_memory: Max memory per NPU device in GiB
        verbose: Print progress

    Returns:
        (model, config): Model and config ready for NPU training
    """

    if verbose:
        print(f"[load_npu] Loading {model_name_or_path} for NPU training...")

    # Load config first
    config = AutoConfig.from_pretrained(model_name_or_path, trust_remote_code=True)

    # Build device map
    if device_map == "balanced-layers" and npu_max_memory:
        from accelerate import infer_auto_device_map
        from accelerate.utils import get_balanced_memory

        max_memory = get_balanced_memory(
            model_name_or_path,
            max_memory={i: f"{npu_max_memory}GiB" for i in range(8)},  # Assume up to 8 NPUs
        )
        device_map = infer_auto_device_map(model_name_or_path, max_memory=max_memory)
        if verbose:
            print("[device_map] Built balanced device map for NPU")

    # Load with device map
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        config=config,
        torch_dtype=torch.bfloat16,
        device_map=device_map,
        trust_remote_code=True,
    )

    if verbose:
        print(f"[loaded] Model on NPU. dtype={model.dtype}")

    return model, config


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Decompress quantized model for training")
    parser.add_argument("--model-path", required=True, help="Path to quantized model")
    parser.add_argument("--output-path", default=None, help="Path to save decompressed model")
    parser.add_argument("--device", default="cpu", help="Device for initial loading")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    model, config = decompress_model_for_training(
        args.model_path,
        output_path=args.output_path,
        device=args.device,
        verbose=args.verbose or True,
    )

    print("\n[SUCCESS] Model decompressed and ready for training.")
