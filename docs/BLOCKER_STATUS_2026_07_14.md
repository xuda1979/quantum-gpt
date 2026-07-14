# R&D Blocker Status — 2026-07-14

## Summary

The user requested: **deliver an adapter with >50% pass rate on nontrivial
quantum coding problems ASAP** and **submit training tasks ASAP**.

### Blocker: Huanxin shell terminal service is DOWN (platform-wide outage)

**All NPU training job submissions require the Huanxin shell terminal service**,
which routes through a browser daemon → `aihuanxin.cn/kunlun/web/develop/v1/getShellVisitUrl`.

**Error:** HTTP 170022 — "获取shell终端信息失败" (Failed to get shell terminal info)
**Affected:** ASI1, ASI2, ASI3 (all environments)
**WebSocket:** `wss://aihuanxin.cn/kunlun/null` → 404
**First observed:** 2026-07-10 (per docs/huanxin-adapter-recovery-2026-07-11.md)
**Still down as of:** 2026-07-14 17:15 CST

This is a **Huanxin platform-side outage**, not a local issue. We cannot fix it
from our side. The browser daemon connects fine, but the platform's shell
terminal URL service returns error 170022 for all pod IDs.

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
