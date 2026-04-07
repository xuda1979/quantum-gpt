from __future__ import annotations

from training.acquire_public_qwen_snapshot import PUBLIC_MODELS
from training.huanxin_cpu_smoke import runtime_autoconfig_requires_upgrade
from training.qwen_sft_peft import resolve_lora_target_modules
from training.verify_qwen_snapshot import metadata_family_hit


class _FakeModel:
    def named_modules(self):
        return iter(
            [
                ("", object()),
                ("model.layers.0.self_attn.q_proj", object()),
                ("model.layers.0.self_attn.k_proj", object()),
                ("model.layers.0.self_attn.v_proj", object()),
                ("model.layers.0.self_attn.o_proj", object()),
                ("model.layers.0.mlp.gate_proj", object()),
                ("model.layers.0.mlp.up_proj", object()),
                ("model.layers.0.mlp.down_proj", object()),
            ]
        )


def test_resolve_lora_target_modules_auto_discovers_common_projection_names() -> None:
    resolved = resolve_lora_target_modules(None, _FakeModel())
    assert resolved == ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def test_resolve_lora_target_modules_keeps_explicit_override() -> None:
    resolved = resolve_lora_target_modules(["attention_proj", "mlp_proj"], _FakeModel())
    assert resolved == ["attention_proj", "mlp_proj"]


def test_metadata_family_hit_is_generic_not_qwen_only() -> None:
    assert metadata_family_hit("gemma4", ["Gemma4ForConditionalGeneration"], "gemma") is True
    assert metadata_family_hit("qwen3_5", ["Qwen3_5ForConditionalGeneration"], "gemma") is False


def test_runtime_upgrade_detection_matches_gemma4_unrecognized_architecture() -> None:
    exc = ValueError("Transformers does not recognize this architecture yet")
    assert runtime_autoconfig_requires_upgrade("gemma4", exc) is True


def test_public_models_exposes_gemma4_targets() -> None:
    assert PUBLIC_MODELS["gemma4-e2b-it"]["model_id"] == "google/gemma-4-E2B-it"
    assert PUBLIC_MODELS["gemma4-e4b-it"]["expected_family_substring"] == "gemma"
