"""Regression: SAPO adapters must ACTUALLY merge into the eval base model.

2026-08-24 bug (manager-confirmed): the SAPO trainer wraps the text-only
Qwen3_5ForCausalLM class, so its LoRA keys are
``base_model.model.model.layers.*`` — but the promotion-eval runner loads the
FULL multimodal Qwen3_5ForConditionalGeneration whose language layers live at
``base_model.model.model.language_model.layers.*``. peft silently skips every
mismatched key (UserWarning only), leaving zero-init LoRA -> generated
candidates byte-identical to base. All three RL arms (run-1 s2, run-1 s7,
run-2 s4) md5-matched the base leg for 18/18 tasks; the warm adapter carried
the ``language_model`` prefix so it loaded correctly (0/18 identical).

These tests lock the fix: a nonzero SAPO-style adapter merged through the
runner's exact code path MUST change probe output versus base, and the load
must FAIL CLOSED (never silently fall back to base) when the adapter cannot
be applied.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

try:
    import torch  # noqa: F401
    import transformers  # noqa: F401
    from peft import LoraConfig, TaskType, get_peft_model
    from safetensors import safe_open
    from safetensors.torch import save_file
except Exception:  # pragma: no cover - plain-python3 suite host
    transformers = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(
    transformers is None,
    reason="requires torch/transformers/peft/safetensors",
)

# ─────────────────────────────────────────────────────────────────────────────
# Pure logic (no model load) — the key-namespace remap
# ─────────────────────────────────────────────────────────────────────────────


def test_sapo_key_remap_inserts_language_model_segment() -> None:
    """SAPO text-only keys must be remapped into the full-model namespace."""
    from scripts.run_hf_pass1_eval import _remap_sapo_keys

    keys = [
        "base_model.model.model.layers.0.mlp.gate_proj.lora_A.weight",
        "base_model.model.model.layers.3.self_attn.q_proj.lora_B.weight",
        "base_model.model.model.embed_tokens.weight",  # non-LoRA, leave alone
    ]
    remapped = _remap_sapo_keys(keys)
    assert "base_model.model.model.language_model.layers.0.mlp.gate_proj.lora_A.weight" in remapped
    assert (
        "base_model.model.model.language_model.layers.3.self_attn.q_proj.lora_B.weight" in remapped
    )
    # warm-namespace keys (already contain language_model) are untouched
    warm = ["base_model.model.model.language_model.layers.5.mlp.up_proj.lora_A.weight"]
    assert _remap_sapo_keys(warm) == warm
    # 2026-08-24 QA: EVERY text-only-namespace key needs the language_model
    # segment — the full multimodal model keeps all language weights under
    # model.model.language_model.*; a leftover non-layer key (embed/lm_head)
    # is silently dropped by peft again -> partial merge. Remap it too.
    assert "base_model.model.model.language_model.embed_tokens.weight" in remapped


def test_adapter_effectively_zero_detects_silent_skip() -> None:
    """A PeftModel whose lora_B is all zero must be flagged as not applied."""
    from scripts.run_hf_pass1_eval import _adapter_effectively_zero, _state_has_nonzero_b

    zero_state = {
        "base_model.model.model.language_model.layers.0.mlp.gate_proj.lora_B.default.weight": torch.zeros(
            4, 8
        )
    }
    nonzero_state = {
        "base_model.model.model.language_model.layers.0.mlp.gate_proj.lora_B.default.weight": torch.ones(
            4, 8
        )
        * 0.5
    }
    assert not _state_has_nonzero_b(zero_state)
    assert _state_has_nonzero_b(nonzero_state)

    class FakePeft(torch.nn.Module):  # pragma: no cover - exercised below
        pass

    # _adapter_effectively_zero inspects lora_B params of the merged model.
    model = torch.nn.Module()
    layer = torch.nn.Module()
    layer.register_parameter("lora_B_default", torch.nn.Parameter(torch.zeros(4, 8)))
    layer.lora_B_default.requires_grad = False
    model.lora = layer
    assert _adapter_effectively_zero(model)
    layer.lora_B_default.data.fill_(0.25)
    assert not _adapter_effectively_zero(model)


def test_adapter_effectively_zero_not_fooled_by_in_place_peft_mutation() -> None:
    """PeftModel.from_pretrained/get_peft_model inject LoRA modules INTO the
    base object in place: the zero-check must use a pre-mutation id snapshot,
    or it skips every live delta as "base" and fails closed on genuinely live
    adapters (2026-08-25 aliasing regression that aborted all three legs)."""
    from scripts.run_hf_pass1_eval import _adapter_effectively_zero

    base = _tiny_multimodal_base()
    base.eval()
    base_param_ids = {id(param) for param in base.parameters()}
    lora = get_peft_model(
        base,
        LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=4,
            lora_alpha=8,
            target_modules=["q_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        ),
    )
    with torch.no_grad():
        for name, p in lora.named_parameters():
            if "lora_B" in name:
                p.data.normal_(0.0, 0.4)
    # Hazard documented: the naive id set (computed from the mutated base)
    # includes the adapter's own tensors, so the live delta looks like base.
    assert _adapter_effectively_zero(lora, base) is True
    # Fixed: the pre-mutation snapshot makes the live delta visible.
    assert _adapter_effectively_zero(lora, base, base_param_ids) is False


# ─────────────────────────────────────────────────────────────────────────────
# Hermetic tiny-model test — reproduces the production failure shape
# ─────────────────────────────────────────────────────────────────────────────


def _tiny_multimodal_base():
    """A small image-text-conditional model with model.language_model.layers."""
    from transformers import Qwen2VLConfig, Qwen2VLForConditionalGeneration

    cfg = Qwen2VLConfig(
        hidden_size=64,
        intermediate_size=128,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        vocab_size=256,
        max_position_embeddings=64,
        vision_config={
            "hidden_size": 32,
            "intermediate_size": 64,
            "num_hidden_layers": 1,
            "num_attention_heads": 4,
            "image_size": 32,
            "patch_size": 8,
            "num_channels": 3,
        },
        rope_scaling={"type": "mrope", "mrope_section": [2, 3, 3], "rope_type": "default"},
    )
    return Qwen2VLForConditionalGeneration(cfg)


def test_tiny_multimodal_sapo_adapter_changes_probe_output(tmp_path: Path) -> None:
    """SAPO-namespace adapter loaded via the runner path must differ from base.

    Red before the fix: peft silently skips the mismatched keys and the probe
    output equals base. Green after: remap + fail-closed load apply the delta.
    """
    from scripts.run_hf_pass1_eval import _apply_adapter_checked, _probe_differs

    base = _tiny_multimodal_base()
    base.eval()

    # Build a genuinely nonzero LoRA adapter on the full model, then rewrite
    # its keys into the SAPO text-only namespace (drop the language_model
    # segment) exactly as the SAPO trainer's save does.
    lora = get_peft_model(
        base,
        LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=4,
            lora_alpha=8,
            target_modules=["q_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        ),
    )
    with torch.no_grad():
        for name, p in lora.named_parameters():
            if "lora_B" in name:
                p.data.normal_(0.0, 0.4)
    adapter_dir = tmp_path / "sapo_adapter"
    lora.save_pretrained(str(adapter_dir))

    # Rewrite safetensors keys to the SAPO (text-only) namespace.
    src = adapter_dir / "adapter_model.safetensors"
    tensors = {}
    with safe_open(str(src), framework="pt", device="cpu") as h:
        for k in h.keys():
            new_k = k.replace(
                "base_model.model.model.language_model.layers.",
                "base_model.model.model.layers.",
            )
            tensors[new_k] = h.get_tensor(k)
    save_file(tensors, str(src))

    # Runner path: fresh full base + adapter via the checked loader.
    fresh = _tiny_multimodal_base()
    fresh.eval()
    merged = _apply_adapter_checked(fresh, adapter_dir)

    probe = "def solve():"
    assert _probe_differs(
        fresh, merged, probe, max_new_tokens=8
    ), "SAPO adapter produced base-identical output — silent merge fallback"


def test_apply_adapter_fails_closed_on_truly_empty_adapter(tmp_path: Path) -> None:
    """An adapter with zero B must raise, not silently run base."""
    from scripts.run_hf_pass1_eval import _apply_adapter_checked

    base = _tiny_multimodal_base()
    base.eval()
    lora = get_peft_model(
        base,
        LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=4,
            lora_alpha=8,
            target_modules=["q_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        ),
    )
    adapter_dir = tmp_path / "zero_adapter"
    lora.save_pretrained(str(adapter_dir))
    fresh = _tiny_multimodal_base()
    fresh.eval()
    with pytest.raises(SystemExit):
        _apply_adapter_checked(fresh, adapter_dir)


# ─────────────────────────────────────────────────────────────────────────────
# Real-adapter integration (runs on the box; skipped elsewhere)
# ─────────────────────────────────────────────────────────────────────────────

REAL_BASE = Path("/root/work/filestorage/Qwen3.6-27B")
REAL_ADAPTERS = [
    Path("/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260824T031524/step_000002_adapter"),
    Path("/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260824T031524/step_000007_adapter"),
    Path("/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260824T075223/step_000004_adapter"),
]


@pytest.mark.parametrize("adapter_dir", REAL_ADAPTERS, ids=lambda p: p.parent.name + "/" + p.name)
@pytest.mark.skipif(
    not REAL_BASE.is_dir() or not all(a.is_dir() for a in REAL_ADAPTERS),
    reason="real model/adapter not present on this host",
)
def test_real_sapo_adapter_probe_differs_base(adapter_dir: Path) -> None:
    """All THREE REAL SAPO adapters (run-1 s2/s7, run-2 s4) must change
    probe output vs base once applied.

    CPU-precheck merged-deltas: s2 max_abs_diff=9.77e-4, s7=9.92e-4 (the
    strongest drift ever seen, at/above the ACTIVE bar), s4=6.1e-5 (small
    but nonzero — at fp32 first-step-logit equality it still probe-differs;
    measured live on the box 2026-08-25). A probe-identical result for any of
    them means the loader failed — not a weak delta.

    Loads on NPU with the production config (balanced-layers/54 GiB) — the
    same path the promotion legs use, and fast enough to gate every leg.
    """
    from scripts.run_hf_pass1_eval import _apply_adapter_checked, _probe_differs, load_model

    base = load_model(
        REAL_BASE,
        "npu",
        device_map="balanced-layers",
        npu_max_memory_gib=54,
    )
    merged = _apply_adapter_checked(base, adapter_dir)
    probe = "Write a Python function that applies a phase flip on the third qubit."
    assert _probe_differs(
        base, merged, probe, max_new_tokens=2
    ), f"{adapter_dir} merged to base-identical output (silent skip)"
