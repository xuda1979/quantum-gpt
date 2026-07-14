# R&D Blocker Status — 2026-07-14

## RESOLVED ✅

**Root cause:** The Huanxin environments (ASI1/ASI2/ASI3) were **stopped/stale**,
not experiencing a platform outage. Starting them from the Huanxin UI resolved
the error 170022 immediately.

**Lesson learned:** Before classifying error 170022 as a platform outage,
always try starting the environments from the Huanxin UI first. See
`skills/huanxin-browser/SKILL.md` for updated guidance.

## Training Status (2026-07-14 12:08 UTC)

- **ASI1**: Qwen3.6-27B LoRA SFT on 1K dedup dataset — **RUNNING** (step 31/250, loss ~0.14)
- **ASI2**: Qwen3.6-27B LoRA SFT on 1K dedup dataset — **RUNNING** (step 13/250, loss ~0.07)
- **ASI3**: Qwen3.6-35B-A3B LoRA SFT — **FAILED** (device mapping issue with MoE model, not critical)

## Environment Setup

Fresh containers need package installation. Run `scripts/setup_asi_training_env.sh`
on each NPU box after restart. This installs peft, accelerate, transformers 5.6.0,
huggingface_hub 1.22.0 from local wheels/py_deps, and applies the NPU modeling patch.

**After installing packages, save the environment image from the Huanxin UI.**

## Key Fixes Applied

1. `asi1_launch_1k_sft_4npu.sh`: Use `NPROC` env var (was hardcoded 4), use
   `MAX_LENGTH` env var (was hardcoded 512). Single-NPU boxes need NPROC=1
   and MAX_LENGTH=256.
2. Do NOT set `ASCEND_RT_VISIBLE_DEVICES` — let torch_npu auto-detect.
3. Use unique `MASTER_PORT` for each concurrent run.

---

## Original Post-Mortem (superseded by resolution above)

The user requested: **deliver an adapter with >50% pass rate on nontrivial
quantum coding problems ASAP** and **submit training tasks ASAP**.

### Initial misdiagnosis: Classified as "platform outage"

**Error 170022 "获取shell终端信息失败"** was observed on ASI1/ASI2/ASI3.
I incorrectly classified this as a Huanxin platform-side outage that could
not be fixed locally. In reality, the environments were simply stopped/stale
and needed to be started from the Huanxin UI.

**What I should have done:**
1. Recognized that error 170022 means "shell terminal unavailable" — which
   can mean either a platform outage OR stopped environments.
2. Checked the Huanxin UI to see if the environments were running.
3. Tried starting the environments from the UI before concluding it was
   a platform outage.
4. Asked the user to check the UI sooner, rather than waiting 4 days.

### What IS working

- ✅ **S3 (MinIO) endpoint is UP** — `https://iner.aihuanxin.cn` returns HTTP 200,
  bucket listing works, file upload/download works. (The 2026-07-13 S3 blocker
  has resolved.)
- ✅ **All training data is staged on S3** — uploaded today:
  - `data/generated/adapter_a_sft_combined_v1/` (164 rows, combined curriculum)
  - `data/generated/qwen36_quantum_finetune_10k_split_9500_500_v1/` (10K rows)
  - `data/generated/rd_lines_2026_07_13/` (DPO pairs, critic SFT, per-line data)
  - `configs/adapters/` (all 3 adapter configs)
- ✅ **Local data preparation complete** — combined SFT, DPO pairs, critic SFT
  all ready.

### What we need to submit training

The Huanxin shell terminal service must recover. Once it does:
1. Submit Adapter A SFT (use 10K verified dataset for maximum signal)
2. Submit Adapter A DPO on top of SFT
3. Submit Adapter A RL-GRPO on top of DPO
4. Submit Aux critic SFT (66 rows, quick)

### Estimated timeline once shell recovers
- SFT (10K rows, 4 NPU, ~3 epochs): ~6-12 hours
- DPO (361 pairs): ~2-4 hours
- RL-GRPO: ~1 day
- **Total to Adapter A deploy candidate: ~2 days from shell recovery**

## Action items for user

1. **Escalate Huanxin platform outage** — error 170022 "获取shell终端信息失败"
   is blocking all training. This has been down since 2026-07-10 (4 days).
   The platform team needs to fix the shell terminal URL service.
2. **Alternative:** If there's a Huanxin REST API for training job submission
   (not browser/shell based), please point us to it — all our current paths
   go through the shell terminal.
