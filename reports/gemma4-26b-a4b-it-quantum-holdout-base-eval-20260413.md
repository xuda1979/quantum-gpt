# Gemma 4 26B-A4B-it — Quantum Holdout Base Evaluation Report

**Date**: 2026-04-13
**Model**: `models/gemma-4-26B-A4B-it` (25.8B params, MoE 128 experts, top-k=8)
**Eval**: quantum generalization holdout v1, pass@1, temperature=0.0, max_new_tokens=512
**Device**: CPU (Apple Silicon 16GB, bfloat16 with swap)

## Results

### Strict Override (Holdout) Tasks — 4/4 PASSED (100%)

| Task | Result | Notes |
|------|--------|-------|
| `quantum_gate_alias_normalization` | ✅ PASS | Clean dict-based mapping, proper casing/whitespace handling |
| `quantum_phase_estimation_circuit` | ✅ PASS | Correct round-based QPE simulation with boundary clamping |
| `quantum_qaoa_maxcut` | ✅ PASS | Full QAOA cost function + classical sim |
| `quantum_superdense_coding` | ✅ PASS | All message round-trips correct |

### Full Scorecard — 38/38 PASSED (100%)

- Quantum domain: 25/25
- Software domain: 13/13

## Comparison: Gemma 4 26B vs OmniCoder 9B Base

| Metric | Gemma 4 26B-A4B-it (base) | OmniCoder 9B (base) |
|--------|---------------------------|---------------------|
| Override tasks | **4/4 (100%)** | 3/4 (75%) |
| Full scorecard | **38/38 (100%)** | 25/26 (96%) |
| Failed tasks | — | `quantum_gate_alias_normalization` |
| Model size | 25.8B (active 4B MoE) | 9B (dense) |

**Key insight**: Gemma 4 26B base already achieves ceiling performance on the quantum
holdout benchmark without any finetuning. It passes the `quantum_gate_alias_normalization`
task that OmniCoder 9B base fails. The model produces clean, correct Python code
with proper interface contracts.

## Finetuning Pipeline Validation

SFT training was successfully initiated with the following verified pipeline:

- **LoRA targets**: 205 `nn.Linear` modules in `model.language_model` text backbone
  (explicit full-path discovery avoids `Gemma4ClippableLinear` in vision tower)
- **Trainable params**: 18,585,600 / 25.8B = 0.072%
- **LoRA config**: rank=16, alpha=32, dropout=0.05, CAUSAL_LM
- **mm_token_type_ids**: All-zero tensor injected for text-only training
  (required by Gemma 4's causal mask during `model.train()` mode)
- **Forward preflight loss**: 5.316 (full sequence) / 0.536 (completions-only)
- **Research methods**: verifier_guided_repair_curriculum, ast_anchor_interface_grounding

### Code changes required for Gemma 4 support

1. `training/qwen_sft_peft.py` — Full-path LoRA target module discovery (`_resolve_lora_targets_full_path`)
2. `training/text_preprocessor_backend.py` — `add_mm_token_type_ids` in batch collator
3. `training/grpo_trainer.py` — `add_mm_token_type_ids` in `compute_completion_log_prob`
4. `training/model_family_preflight.py` — Gemma 4 blocker removed
5. `scripts/queue_ai2_timeboxed_pipeline.sh` — Remote launch blocker removed
6. `training/requirements-gemma4-runtime.txt` — peft >= 0.18.1 (was 0.14.0)

## Generation Timing (CPU, 26B model)

| Task | Time (sec) | Output chars |
|------|-----------|--------------|
| gate_alias_normalization | ~2795 | 600 |
| phase_estimation_circuit | ~4415 | 1017 |
| qaoa_maxcut | ~5547 | 1279 |
| superdense_coding | ~2540 | 775 |
| **Total** | **~15,297 (4.25h)** | **3,671** |

## Next Steps

1. Complete SFT training (20 steps, ~6-8h on CPU) → evaluate finetuned model
2. Deploy to ai2 8-NPU for production-speed training (standard profile: 40 SFT + 8 GRPO steps)
3. GRPO reinforcement stage after SFT
4. Extend holdout benchmark with harder quantum tasks to differentiate finetuned from base
