# Gemma 4 Text-Path Enablement for Quantum R&D

## Claim

Gemma 4 is a promising next-iteration model family, but the current workspace cannot honestly claim Gemma 4 fine-tuning readiness yet. The fastest credible path is:

1. keep the model-source and snapshot pipeline family-generic
2. make LoRA module selection architecture-aware instead of Qwen-only
3. explicitly gate on Gemma 4 runtime support before any Huanxin launch
4. only pursue full Gemma 4 training after a processor-aware conditional-generation backend is validated

## Official Source Facts

- Google announced Gemma 4 on April 2, 2026.
- The official Hugging Face checkpoints `google/gemma-4-E2B-it` and `google/gemma-4-E4B-it` resolve publicly.
- Hugging Face metadata reports both checkpoints as:
  - `model_type: gemma4`
  - `pipeline_tag: any-to-any`
  - architecture `Gemma4ForConditionalGeneration`

Primary sources:

- https://blog.google/technology/developers/gemma-4/
- https://huggingface.co/google/gemma-4-E2B-it
- https://huggingface.co/google/gemma-4-E4B-it

## Local Verification On 2026-04-06

Two local source audits succeeded:

- `python3 training/audit_model_source.py --model-id google/gemma-4-E2B-it --expected-family-substring gemma`
- `python3 training/audit_model_source.py --model-id google/gemma-4-E4B-it --expected-family-substring gemma`

Both returned:

- `status: ok`
- `config_model_type: gemma4`
- `config_architectures: ["Gemma4ForConditionalGeneration"]`

Two local bootstrap smokes then failed honestly:

- `python3 training/huanxin_cpu_smoke.py --model-name google/gemma-4-E2B-it --dataset data/seed/splits-auto-seed/train.jsonl --max-samples 1`
- `python3 training/huanxin_cpu_smoke.py --model-name google/gemma-4-E4B-it --dataset data/seed/splits-auto-seed/train.jsonl --max-samples 1`

Observed blocker:

- local runtime was `transformers 4.49.0`
- AutoConfig could not resolve `model_type=gemma4`
- AutoProcessor was also unavailable for the checkpoint under the current local stack

This means the present local environment is not Gemma 4 capable.

## Engineering Implications

- The existing dataset schema is already generic enough for Gemma-family text work.
- The current SFT and GRPO code were still overfit to Qwen in two places:
  - hard-coded LoRA target module defaults
  - Qwen-family assumptions in snapshot verification/acquisition
- The larger blocker is not just naming debt. Gemma 4 IT checkpoints are advertised as conditional-generation any-to-any models, so even after a Transformers upgrade, the current text-only `AutoModelForCausalLM` path may still be insufficient.

## Decision

Do not fake a Gemma 4 fine-tune launch yet.

Treat Gemma 4 as a gated next target with these prerequisites:

1. local runtime upgraded to a Gemma 4-capable Transformers build
2. processor load verified locally
3. conditional-generation training backend validated locally
4. only then move to Huanxin

## Changes Landed In This Iteration

- LoRA target module selection now auto-discovers common projection suffixes instead of assuming a fixed Qwen list.
- Snapshot verification now supports arbitrary expected model families instead of requiring Qwen metadata.
- Public model acquisition now includes Gemma 4 E2B-it and E4B-it targets for audit/snapshot workflows.
- Smoke/runtime diagnostics now surface family-level upgrade blockers more explicitly.

## Abandon / Continue Guidance

- Abandon immediate remote Gemma 4 training under the current local stack.
- Continue with local backend enablement and runtime validation only.
