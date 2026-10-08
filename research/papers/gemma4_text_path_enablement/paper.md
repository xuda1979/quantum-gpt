# Gemma 4 Text-Path Enablement for Quantum R&D

## Claim

Gemma 4 is a promising next-iteration model family, but the current workspace cannot honestly claim Gemma 4 fine-tuning readiness yet. The fastest credible path is:

1. keep the model-source and snapshot pipeline family-generic
2. make LoRA module selection architecture-aware instead of Qwen-only
3. explicitly gate on Gemma 4 trainer/backend preflight before any Huanxin launch
4. only pursue full Gemma 4 training after a processor-aware conditional-generation backend is validated

## Official Source Facts

- Google announced Gemma 4 on April 2, 2026.
- The official Hugging Face checkpoints `google/gemma-4-E2B-it`, `google/gemma-4-E4B-it`, and `google/gemma-4-31B-it` resolve publicly.
- Hugging Face metadata reports these checkpoints as Gemma 4 conditional-generation models:
  - `model_type: gemma4`
  - `pipeline_tag: any-to-any`
  - architecture `Gemma4ForConditionalGeneration`

Primary sources:

- https://blog.google/technology/developers/gemma-4/
- https://huggingface.co/google/gemma-4-E2B-it
- https://huggingface.co/google/gemma-4-E4B-it
- https://huggingface.co/google/gemma-4-31B-it

## Local Verification On 2026-04-07

The local source audit succeeded:

- `python3 training/audit_model_source.py --model-id google/gemma-4-E2B-it --expected-family-substring gemma`

It returned:

- `status: ok`
- `config_model_type: gemma4`
- `config_architectures: ["Gemma4ForConditionalGeneration"]`

The corrected gate-clearing acquisition command is now:

- `python3 training/acquire_public_qwen_snapshot.py --target gemma4-e2b-it --local-dir models/gemma-4-E2B-it`

That acquisition is no longer theoretical. It is in flight and partially materialized locally:

- top-level metadata files are already present under `models/gemma-4-E2B-it`
- the local snapshot directory has grown materially during the live retry
- the remaining blocker is still absence of a fully completed verified weight file, not source discovery

The local bootstrap smoke still fails honestly:

- `python3 training/huanxin_cpu_smoke.py --model-name models/gemma-4-E2B-it --dataset data/seed/splits-auto-seed/train.jsonl --max-samples 1`

Observed blocker:

- local runtime was `transformers 4.49.0`
- AutoConfig could not resolve `model_type=gemma4`
- AutoProcessor was also unavailable for the checkpoint under the current local stack

Separately, ai2/Huanxin shell access was repaired on the exact train-dev route. That means remote access is no longer the primary blocker. The real blocker remains local Gemma runtime and processor-aware conditional-generation backend readiness.

This means the present local environment is still not Gemma 4 capable.

## Direct ai2 31B Download Check On 2026-04-08

The `gemma4-31b-it` target is now wired into the repo control plane and was verified on ai2 itself:

- `training/acquire_public_qwen_snapshot.py` on ai2 contains:
  - `gemma4-31b-it`
  - `google/gemma-4-31B-it`
- live ai2 daemon health on April 8, 2026 reported:
  - `ready: true`
  - `currentUrl: ...#/train-dev/environment/...name=ai2`

I then launched the first honest detached direct-download attempt on ai2:

- `nohup bash -lc 'PYTHONUNBUFFERED=1 python3 training/acquire_public_qwen_snapshot.py --target gemma4-31b-it --local-dir models/gemma-4-31B-it --hf-timeout-seconds 60' > /tmp/gemma4_31b_download.log 2>&1 < /dev/null &`

Observed result:

- remote PID was emitted successfully
- the job exited immediately
- `models/gemma-4-31B-it` was still absent afterward

The exact blocker is now concrete and verified:

- `/tmp/gemma4_31b_download.log` showed:
  - `stage: fetch_model_info`
  - `error_type: URLError`
  - `error: <urlopen error [Errno -2] Name or service not known>`

This was then cross-checked with the repo's remote probe:

- `python3 training/remote_net_probe.py` on ai2 returned `url_error` for:
  - `https://huggingface.co`
  - `https://hf-mirror.com`

So the direct 31B blocker on ai2 is not stale code, wrong model id, or expired Huanxin login. It is remote public DNS resolution from the ai2 host.

## Engineering Implications

- The existing dataset schema is already generic enough for Gemma-family text work.
- The current SFT and GRPO code were still overfit to Qwen in two places:
  - hard-coded LoRA target module defaults
  - Qwen-family assumptions in snapshot verification/acquisition
- The larger blocker is not just naming debt. Gemma 4 IT checkpoints are advertised as conditional-generation any-to-any models, so even after a Transformers upgrade, the current text-only `AutoModelForCausalLM` path may still be insufficient.
- For the 31B checkpoint specifically, there is now an additional transport-layer reality:
  - ai2 cannot currently resolve public model hosts
  - therefore the practical acquisition path is local snapshot or cache acquisition plus S3 relay into ai2, unless the ai2 DNS/network policy is changed
- The autonomous control plane now reports partial 31B acquisition more honestly:
  - indexed total weight bytes from `model.safetensors.index.json`
  - observed downloaded bytes across completed and `.incomplete` shard files
  - a progress percentage
  - whether shard mtimes still indicate recent download activity or a likely stale transfer
- A new shared text forward preflight now exists for the current text path:
  - `training/model_backend.py` exposes a no-grad `run_text_forward_preflight(...)` helper
  - `training/huanxin_cpu_smoke.py` uses it after model load
  - `training/qwen_sft_peft.py` uses it before entering DDP/training
  - this does not claim Gemma conditional-generation training is solved, but it raises the next honest milestone from "batch construction only" to "the current text path can perform one loss-producing forward on a prepared supervised batch"

## Decision

Do not fake a Gemma 4 fine-tune launch yet.

Treat Gemma 4 as a gated next target with these prerequisites:

1. local runtime upgraded to a Gemma 4-capable Transformers build
2. processor load verified locally
3. conditional-generation training backend validated locally
4. a working artifact-delivery path into ai2, either via repaired public DNS or via local-download-plus-S3 relay
5. only then move to Huanxin

## Changes Landed In This Iteration

- LoRA target module selection now auto-discovers common projection suffixes instead of assuming a fixed Qwen list.
- Snapshot verification now supports arbitrary expected model families instead of requiring Qwen metadata.
- Public model acquisition now includes Gemma 4 E2B-it and E4B-it targets for audit/snapshot workflows.
- The local smoke path now fails earlier on an explicit `trainer_backend_preflight` blocker for Gemma 4 conditional-generation checkpoints instead of pretending the text-only `AutoModelForCausalLM` path is ready.
- The autonomous control plane now names the Gemma blocker honestly as a trainer/backend preflight gate rather than a vague runtime-only failure.
- The remote launcher now exits early for `gemma4-*` targets with a concrete preflight blocker instead of pretending ai2 launch readiness.
- The autonomous-cycle command sheet was corrected from a cache-only Gemma acquire step to the gate-clearing local snapshot path: `--local-dir models/gemma-4-E2B-it`.
- The GRPO path now uses the same Gemma trainer/backend preflight and saves the processor-backed artifact path instead of assuming tokenizer-only causal-LM semantics.
- Added `training/model_backend.py` as a shared backend-gating helper so local eval, qualitative comparison, and serving entrypoints all stop at the same Gemma runtime/backend blocker before attempting `AutoModelForCausalLM`.
- Inference-side wording is now explicit too: evaluation and serving paths report a text-only inference blocker, while training paths keep the trainer-specific blocker text.
- The inference entrypoints were then reordered so preflight runs before tokenizer/processor setup; this removed misleading protobuf/processor crashes and replaced them with the honest Gemma runtime/backend blocker in a real `run_base_vs_adapter_eval.py` execution.
- The 31B target is now first-class in the repo control plane:
  - `training/acquire_public_qwen_snapshot.py` exposes `gemma4-31b-it`
  - `scripts/run_autonomous_rd_cycle.py` exposes `gemma4-31b-it` and now defaults to it
  - `scripts/render_timeboxed_scaleup_commands.py` and `scripts/queue_ai2_timeboxed_pipeline.sh` both expose `gemma4-31b-it`
- A fresh 31B control-plane artifact now exists under `reports/autonomous_rd_cycle_gemma4-31b-it_2026-04-08.*`, which keeps the next-action thread anchored on the 31B checkpoint instead of drifting back to smaller Gemma variants.
- `scripts/ai2_sync_from_s3.sh` was hardened too:
  - it now rejects unexpected positional args
  - it now requires a concrete remote completion marker
  - it now checks the combined daemon response instead of trusting only one terminal field
  - this reduces ambiguity about whether ai2 really received the intended code before a remote Gemma retry
- The shared backend path advanced one bounded step further:
  - `training/model_backend.py` now contains `run_text_forward_preflight(...)`
  - `training/huanxin_cpu_smoke.py` now reports `text_forward_preflight` after a successful explicit `--load-model` run
  - `training/qwen_sft_peft.py` now performs the same preflight on the first prepared training batch before entering DDP and the full optimization loop
  - `training/grpo_trainer.py` now performs the same shared preflight before entering distributed RL updates
  - `tests/test_model_family_support.py` now covers the helper with a fake conditional-generation model contract

## Abandon / Continue Guidance

- Abandon immediate remote Gemma 4 training under the current local stack.
- Continue with local backend enablement and runtime validation only.
