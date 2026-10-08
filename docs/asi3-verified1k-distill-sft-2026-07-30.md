# ASI3 Verified-1k Distillation SFT — 2026-07-30

**Goal:** Run plain cross-entropy LoRA SFT on Qwen3.6-35B-A3B (ASI3) using the
1,000-row GLM5.2 soft-distillation set, **filtered to strict-verified-PASS rows
only** (no teacher logits), to avoid training on unverified code.

## Dataset

- **Source:** `data/generated/quantum_dedup_1k_glm52_soft_distill_v3/`
  - 1,000 question/code samples (GLM5.2 teacher, Qwen3.6 chat-sft-v1 format).
  - Strict runnable verification: **94.75% PASS** (937 unique PASS / 63 FAIL)
  across `verify_*_strict.json` files.
- **Filtered (used for this run):**
  `data/generated/quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit/`
  - 937 strict-PASS rows, `teacher_logits` dropped (plain SFT, no soft-KL).
  - Deterministic 900 train / 37 eval split (seed 20260730, sorted by example_id).
  - `manifest.json` records the filter + framework distribution.
- Framework mix (kept): qiskit 464, cirq 122, pennylane 88, dwave_ocean 70,
  stim 34, openqasm3 32, qutip 29, unknown 24, pytket 23, qsharp 22, braket 16,
  qulacs 13.

## Student / Trainer

- **Student:** Qwen3.6-35B-A3B (W8A8 → bf16 decompressed on ephemeral disk).
- **Trainer:** `training/qwen_sft_peft.py` (plain cross-entropy SFT,
  `--train-on-completions-only`, LoRA rank 16 / alpha 32, lr 2e-5, cosine,
  2 epochs, max-length 2048, grad-accum 4, gradient-checkpointing, train-layernorm).
- **Launcher:** `scripts/asi3_launch_verified1k_distill_sft_35b.sh`
  (thin wrapper that sets `DATA` + `RUN_ID` and delegates to
  `scripts/asi3_launch_glm52_distill_sft_35b.sh`).

## Run lifecycle

1. Build verified-only no-logit dataset (local) — done 2026-07-30.
2. Refresh Huanxin auth via Safari SSO bridge (daemon was 401) — done.
3. Part-upload dataset tarball to ASI3 + extract — done (SHA-verified).
4. Upload launcher wrapper to ASI3 — done (SHA-verified).
5. Preflight NPU: 8 × 910B2, all OK, idle — done.
6. **Launch SFT** via `scripts/huanxin_training_job.sh --env ASI3 start ...` — in progress.
7. Monitor via `status` / `logs` subcommands every ~30 min.
8. After training, pull adapter + eval.

## Notes / guardrails

- W8A8 → bf16 decompression is cached at
  `/tmp/qwen35b_decompressed_for_training_asi3/.dequant_complete`.
  Ephemeral disk → may need ~30 min re-decompression if pod recycled.
- Output dir is forced under `/root/work/*` (persistent NAS) by the launcher's
  durability guardrail.
- Adapter checkpoints mirrored to NAS every 900 s.
- **Parallelism:** ASI3 exposes 8 × 910B2 NPUs (64 GB each). The 35B-A3B model
  is ~67 GB in bf16 → too large for one-NPU DDP, so the launcher uses
  single-process `balanced-layers` sharding (pipeline-parallel across all 8
  NPUs). The pipeline bubble leaves ~35 GB free per NPU, so the lever for
  throughput is `per_device_batch_size`, not NPU count.

## Throughput tuning (2026-07-30)

| Config | per_device_batch | grad_accum | max_length | step time | 2-epoch ETA |
|--------|------------------|------------|------------|-----------|-------------|
| v1 (initial) | 1 | 4 | 2048 | ~90 s/step | ~11 h |
| v2 (current) | **4** | **1** | **1536** | **~28 s/step** | **~3.5 h** |

- v2 uses the same effective batch (4 samples/step) but 4× the optimizer steps
  per epoch, filling the pipeline bubble. NPU memory 27–39 GB / 65 GB (safe).
- 98.2% of samples are < 1024 tokens; max_length 1536 covers 99.4%. The 0.6%
  tail is truncated, which is acceptable for SFT.
- Job id: `asi3-verified1k-distill-sft-35b-batch4-20260730T095003Z`.
- If more speed is needed: batch=8 (~45 GB/NPU) is the next ceiling, but risks
  OOM on the 2560-token tail; consider sorting by length or capping at 2048.

## Iteration log entry

| Iter | Date       | Dataset                                  | ASI3 (35B) | Notes |
|------|------------|------------------------------------------|-----------|-------|
| v3-verified | 2026-07-30 | `quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit` (900 train / 37 eval) | running (batch4 config) | plain SFT, strict-PASS only, no logits, ~3.5 h ETA |
