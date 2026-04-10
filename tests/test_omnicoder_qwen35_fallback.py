from __future__ import annotations

import torch

from training.omnicoder_qwen35_fallback import (
    convert_omnicoder_text_state_dict_to_qwen3_next,
    extract_omnicoder_text_config,
)


def test_extract_omnicoder_text_config_maps_expected_fields() -> None:
    model_config = {
        "text_config": {
            "vocab_size": 248320,
            "hidden_size": 4096,
            "intermediate_size": 12288,
            "num_hidden_layers": 32,
            "num_attention_heads": 16,
            "num_key_value_heads": 4,
            "hidden_act": "silu",
            "max_position_embeddings": 262144,
            "initializer_range": 0.02,
            "rms_norm_eps": 1e-6,
            "use_cache": True,
            "tie_word_embeddings": False,
            "attention_bias": False,
            "attention_dropout": 0.0,
            "head_dim": 256,
            "linear_conv_kernel_dim": 4,
            "linear_key_head_dim": 128,
            "linear_value_head_dim": 128,
            "linear_num_key_heads": 16,
            "linear_num_value_heads": 32,
            "layer_types": ["linear_attention", "full_attention"],
            "mlp_only_layers": [],
            "bos_token_id": None,
            "eos_token_id": 248044,
            "pad_token_id": None,
            "partial_rotary_factor": 0.25,
            "rope_parameters": {
                "partial_rotary_factor": 0.25,
                "rope_theta": 10_000_000,
                "rope_type": "default",
            },
        }
    }

    config = extract_omnicoder_text_config(model_config)

    assert config["hidden_size"] == 4096
    assert config["rope_theta"] == 10_000_000
    assert config["partial_rotary_factor"] == 0.25
    assert config["layer_types"] == ["linear_attention", "full_attention"]
    assert config["num_experts"] == 0
    assert config["moe_intermediate_size"] == 12288


def test_convert_omnicoder_text_state_dict_to_qwen3_next_merges_linear_projections() -> None:
    state_dict = {
        "lm_head.weight": torch.arange(6, dtype=torch.float32).reshape(3, 2),
        "model.language_model.embed_tokens.weight": torch.arange(8, dtype=torch.float32).reshape(4, 2),
        "model.language_model.layers.0.linear_attn.in_proj_qkv.weight": torch.full((2, 2), 1.0),
        "model.language_model.layers.0.linear_attn.in_proj_z.weight": torch.full((3, 2), 2.0),
        "model.language_model.layers.0.linear_attn.in_proj_b.weight": torch.full((4, 2), 3.0),
        "model.language_model.layers.0.linear_attn.in_proj_a.weight": torch.full((5, 2), 4.0),
        "model.language_model.layers.0.linear_attn.dt_bias": torch.arange(4, dtype=torch.float32),
        "model.language_model.layers.0.mlp.gate_proj.weight": torch.full((2, 2), 5.0),
        "model.language_model.layers.1.self_attn.q_proj.weight": torch.full((2, 2), 6.0),
    }

    converted = convert_omnicoder_text_state_dict_to_qwen3_next(state_dict, torch_module=torch)

    assert torch.equal(converted["lm_head.weight"], state_dict["lm_head.weight"])
    assert torch.equal(
        converted["model.embed_tokens.weight"],
        state_dict["model.language_model.embed_tokens.weight"],
    )
    assert torch.equal(
        converted["model.layers.0.linear_attn.in_proj_qkvz.weight"],
        torch.cat(
            [
                state_dict["model.language_model.layers.0.linear_attn.in_proj_qkv.weight"],
                state_dict["model.language_model.layers.0.linear_attn.in_proj_z.weight"],
            ],
            dim=0,
        ),
    )
    assert torch.equal(
        converted["model.layers.0.linear_attn.in_proj_ba.weight"],
        torch.cat(
            [
                state_dict["model.language_model.layers.0.linear_attn.in_proj_b.weight"],
                state_dict["model.language_model.layers.0.linear_attn.in_proj_a.weight"],
            ],
            dim=0,
        ),
    )
    assert torch.equal(
        converted["model.layers.0.linear_attn.dt_bias"],
        state_dict["model.language_model.layers.0.linear_attn.dt_bias"],
    )
    assert torch.equal(
        converted["model.layers.0.mlp.gate_proj.weight"],
        state_dict["model.language_model.layers.0.mlp.gate_proj.weight"],
    )
    assert torch.equal(
        converted["model.layers.1.self_attn.q_proj.weight"],
        state_dict["model.language_model.layers.1.self_attn.q_proj.weight"],
    )


def test_convert_omnicoder_text_state_dict_to_qwen3_next_requires_all_split_weights() -> None:
    state_dict = {
        "model.language_model.layers.0.linear_attn.in_proj_qkv.weight": torch.zeros(2, 2),
        "model.language_model.layers.0.linear_attn.in_proj_z.weight": torch.zeros(2, 2),
        "model.language_model.layers.0.linear_attn.in_proj_b.weight": torch.zeros(2, 2),
    }

    try:
        convert_omnicoder_text_state_dict_to_qwen3_next(state_dict, torch_module=torch)
    except KeyError as exc:
        assert "in_proj_a" in str(exc)
    else:
        raise AssertionError("expected KeyError for incomplete split linear-attention weights")
