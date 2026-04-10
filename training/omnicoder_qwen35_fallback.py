from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping


def extract_omnicoder_text_config(model_config: Mapping[str, Any]) -> dict[str, Any]:
    text_config = dict(model_config.get("text_config") or {})
    rope_parameters = dict(text_config.pop("rope_parameters", {}) or {})

    config = {
        "vocab_size": text_config["vocab_size"],
        "hidden_size": text_config["hidden_size"],
        "intermediate_size": text_config["intermediate_size"],
        "num_hidden_layers": text_config["num_hidden_layers"],
        "num_attention_heads": text_config["num_attention_heads"],
        "num_key_value_heads": text_config["num_key_value_heads"],
        "hidden_act": text_config["hidden_act"],
        "max_position_embeddings": text_config["max_position_embeddings"],
        "initializer_range": text_config["initializer_range"],
        "rms_norm_eps": text_config["rms_norm_eps"],
        "use_cache": text_config["use_cache"],
        "tie_word_embeddings": text_config["tie_word_embeddings"],
        "attention_bias": text_config["attention_bias"],
        "attention_dropout": text_config["attention_dropout"],
        "head_dim": text_config["head_dim"],
        "linear_conv_kernel_dim": text_config["linear_conv_kernel_dim"],
        "linear_key_head_dim": text_config["linear_key_head_dim"],
        "linear_value_head_dim": text_config["linear_value_head_dim"],
        "linear_num_key_heads": text_config["linear_num_key_heads"],
        "linear_num_value_heads": text_config["linear_num_value_heads"],
        "layer_types": list(text_config["layer_types"]),
        "mlp_only_layers": list(text_config.get("mlp_only_layers") or []),
        "partial_rotary_factor": rope_parameters.get(
            "partial_rotary_factor",
            text_config.get("partial_rotary_factor", 0.25),
        ),
        "rope_theta": rope_parameters.get("rope_theta", 10000.0),
        "rope_scaling": None,
        "pad_token_id": text_config.get("pad_token_id"),
        "bos_token_id": text_config.get("bos_token_id"),
        "eos_token_id": text_config.get("eos_token_id"),
        # OmniCoder text_config is dense; keep qwen3_next on its dense path.
        "num_experts": 0,
        "num_experts_per_tok": 0,
        "decoder_sparse_step": 1,
        "moe_intermediate_size": text_config["intermediate_size"],
        "shared_expert_intermediate_size": text_config["intermediate_size"],
        "norm_topk_prob": False,
        "output_router_logits": False,
        "router_aux_loss_coef": 0.0,
    }
    return config


def convert_omnicoder_text_state_dict_to_qwen3_next(
    state_dict: Mapping[str, Any],
    *,
    torch_module: Any,
) -> dict[str, Any]:
    converted: dict[str, Any] = {}
    split_linear_weights: dict[str, dict[str, Any]] = defaultdict(dict)
    text_prefix = "model.language_model."
    linear_prefix = ".linear_attn."

    for key, value in state_dict.items():
        if key == "lm_head.weight":
            converted[key] = value
            continue
        if not key.startswith(text_prefix):
            continue

        stripped = f"model.{key[len(text_prefix):]}"
        if linear_prefix not in stripped:
            converted[stripped] = value
            continue

        if stripped.endswith("in_proj_qkv.weight"):
            split_linear_weights[stripped.rsplit("in_proj_qkv.weight", 1)[0]]["qkv"] = value
            continue
        if stripped.endswith("in_proj_z.weight"):
            split_linear_weights[stripped.rsplit("in_proj_z.weight", 1)[0]]["z"] = value
            continue
        if stripped.endswith("in_proj_b.weight"):
            split_linear_weights[stripped.rsplit("in_proj_b.weight", 1)[0]]["b"] = value
            continue
        if stripped.endswith("in_proj_a.weight"):
            split_linear_weights[stripped.rsplit("in_proj_a.weight", 1)[0]]["a"] = value
            continue

        converted[stripped] = value

    for prefix, parts in split_linear_weights.items():
        missing = {"qkv", "z", "b", "a"} - set(parts)
        if missing:
            missing_keys = [f"in_proj_{name}" for name in sorted(missing)]
            raise KeyError(
                f"Missing OmniCoder linear-attention projection parts for {prefix}: {missing_keys}"
            )
        converted[f"{prefix}in_proj_qkvz.weight"] = torch_module.cat([parts["qkv"], parts["z"]], dim=0)
        converted[f"{prefix}in_proj_ba.weight"] = torch_module.cat([parts["b"], parts["a"]], dim=0)

    return converted
