# GLM5.2 Soft-Distillation SFT — Evaluation Summary

**Date:** 2026-07-06  
**Author:** Claude Code  
**Last updated:** 2026-07-06T13:30Z (iter-2 adapter evals complete for ASI3/35B)

---

## 1. Background and Scope

This report covers the evaluation of LoRA adapters trained via **GLM5.2 soft-distillation SFT** across two iterations on the `glm52_soft_distill_sft_iter2` 100-row dataset (90 train / 10 eval). Three training runs were completed across three environments:

| Run | Model | Env | Adapter | Training Loss (final eval) |
|:----|:------|:----|:--------|:--------------------------|
| `qg-27b-glm52-distill-sft-…-20260705T125328Z` | Qwen3.6-27B | ASI1 | r=16, α=32 | loss=0.622, ppl=1.863 |
| `qg-35b-glm52-distill-sft-…-20260705T133302Z` | Qwen3.6-35B (MoE) | ASI3 | r=16, α=32 | loss=0.599, ppl=1.820 |
| `qg-35b-glm52-distill-sft-…-asi2-resume-20260706T041403Z` | Qwen3.6-35B (MoE) | ASI2 | r=16, α=32 | loss=0.597, ppl=1.817 |

The **ASI2-resume** adapter is a warm-started continuation (9-11 more steps) of the ASI3 33-step adapter.

Evaluation harness: `scripts/run_asi2_35b_pass1_eval.py` — 12-task pass@1 (8 quantum + 4 software), greedy decoding, max 768 new tokens.

---

## 2. Completed Results: ASI3 35B 33-step Adapter

**Date run:** 2026-07-06, completed ~05:55 UTC  
**Base model:** `/root/work/filestorage/qwen35b_decompressed_for_training`  
**Adapter:** `outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260705T133302Z/adapter`  
**Output JSON:** `/root/work/quantum-gpt/outputs/eval-35b-glm52-distill-pass1-12task-20260706T055500Z.json`

### 2.1 Summary

| Model | Pass@1 | Rate | Quantum (8 tasks) | Software (4 tasks) |
|:------|:-------|:-----|:------------------|:-------------------|
| Base (35B) | 10/12 | **83.3%** | 6/8 (75.0%) | 4/4 (100%) |
| Adapter (35B GLM5.2 iter-1) | 11/12 | **91.7%** | 7/8 (87.5%) | 4/4 (100%) |
| **Delta** | **+1/12** | **+8.3pp** | **+1/8 (+12.5pp)** | **0/4 (0pp)** |

### 2.2 Per-Task Breakdown

| Task | Domain | Base | Adapter | Change |
|:-----|:-------|:-----|:--------|:-------|
| quantum_gate_alias_normalization | quantum | ✅ PASS | ✅ PASS | — |
| quantum_phase_estimation_circuit | quantum | ✅ PASS | ✅ PASS | — |
| quantum_qaoa_maxcut | quantum | ✅ PASS | ✅ PASS | — |
| quantum_superdense_coding | quantum | ✅ PASS | ✅ PASS | — |
| quantum_grover_oracle_diffusion | quantum | ❌ FAIL | ✅ **PASS** | **FIXED** |
| quantum_density_matrix_partial_trace | quantum | ✅ PASS | ✅ PASS | — |
| quantum_channel_depolarizing | quantum | ❌ FAIL | ❌ FAIL | still failing |
| quantum_ghz_state_witness | quantum | ✅ PASS | ✅ PASS | — |
| software_docstring_contract | software | ✅ PASS | ✅ PASS | — |
| software_duplicate_logic_refactor | software | ✅ PASS | ✅ PASS | — |
| software_off_by_one_bugfix | software | ✅ PASS | ✅ PASS | — |
| software_retry_decorator | software | ✅ PASS | ✅ PASS | — |

**Key finding:** The GLM5.2 distillation adapter fixed `quantum_grover_oracle_diffusion` (Grover's search oracle + diffusion operator), which the base 35B model consistently failed. The `quantum_channel_depolarizing` task remains unsolved by both base and adapter.

---

## 3. Completed Results: ASI3 35B Iter-2 Adapter

**Date run:** 2026-07-06T12:00Z–13:26Z (duration: 82 min)  
**Base model:** `/tmp/qwen35b_decompressed_for_training_asi3`  
**Adapter:** `outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/adapter`  
**Output JSON:** `/root/work/quantum-gpt/outputs/eval-35b-glm52-distill-iter2-adapteronly-20260706T120000Z.json`

### 3.1 Summary

| Model | Pass@1 | Rate | Quantum (8 tasks) | Software (4 tasks) |
|:------|:-------|:-----|:------------------|:-------------------|
| Adapter (35B GLM5.2 iter-2) | 11/12 | **91.7%** | 7/8 (87.5%) | 4/4 (100%) |

### 3.2 Per-Task Breakdown

| Task | Domain | Adapter iter-2 | vs iter-1 |
|:-----|:-------|:---------------|:----------|
| quantum_gate_alias_normalization | quantum | ✅ PASS | same |
| quantum_phase_estimation_circuit | quantum | ✅ PASS | same |
| quantum_qaoa_maxcut | quantum | ✅ PASS | same |
| quantum_superdense_coding | quantum | ✅ PASS | same |
| quantum_grover_oracle_diffusion | quantum | ✅ PASS | same |
| quantum_density_matrix_partial_trace | quantum | ✅ PASS | same |
| quantum_channel_depolarizing | quantum | ❌ FAIL | still failing |
| quantum_ghz_state_witness | quantum | ✅ PASS | same |
| software_docstring_contract | software | ✅ PASS | same |
| software_duplicate_logic_refactor | software | ✅ PASS | same |
| software_off_by_one_bugfix | software | ✅ PASS | same |
| software_retry_decorator | software | ✅ PASS | same |

**Key finding:** Iter-2 adapter (35B) matches iter-1 exactly at 11/12. The `quantum_channel_depolarizing` task remains the single stubborn failure for both iter-1 and iter-2 35B adapters. This task needs targeted dataset curation for iter-3.

---

## 4. In-Progress Results: ASI1 27B Iter-2 Adapter

**Date run:** 2026-07-06, started ~14:00 UTC (PID 387151)  
**Base model:** `/root/work/filestorage/Qwen3.6-27B`  
**Adapter:** `outputs/qg-27b-glm52-distill-sft-glm52-distill-27b-20260706T083156Z/adapter`  
**Log:** `/root/work/software/quantum-gpt/logs/eval-27b-glm52-distill-iter2-adapteronly-20260706T140000Z.log`  
**Output:** `outputs/eval-27b-glm52-distill-iter2-adapteronly-20260706T140000Z.json`

**Status:** Evaluating adapter-only (base already scored 11/12, 91.7%). Expected completion: ~15:00–15:30 UTC.

*Results will be added to Section 4.1 when available.*

---

## 5. Blocked Results: ASI2 35B Iter-3 Adapter

**Blocker:** All 4 ASI2 NPUs (davinci3-6) are occupied by the iter-3 training run (`qg-35b-glm52-distill-sft-…-20260706T075349Z`, PID 5165). ETA: ~14:37 UTC.

**Plan:** Kill coordinator (`eval_all_adapters.py`), restore `harness.py`, evaluate when training completes.

---

## 6. Comparison Summary

### 6.1 Cross-Iteration: 35B GLM5.2 Distill (ASI3)

| Iter | Adapter | Base | Adapter | Delta | Date |
|:-----|:--------|:-----|:--------|:------|:-----|
| iter-1 | `qg-35b-…-20260705T133302Z` | 10/12 (83.3%) | 11/12 (91.7%) | +8.3pp | 2026-07-06 ✅ |
| **iter-2** | **`qg-35b-…-20260706T081105Z`** | *(base from iter-1)* | **11/12 (91.7%)** | — | **2026-07-06** ✅ |

**Finding:** Iter-2 35B adapter matches iter-1 exactly. No regression, no improvement. `quantum_channel_depolarizing` is the persistent failure target.

### 6.2 Cross-Model (27B vs 35B)

| Model | Version | Base | Adapter | Failing Task(s) |
|:------|:--------|:-----|:--------|:----------------|
| 27B | iter-1 (base scored) | 11/12 (91.7%) | 5/12 partial (stopped) | channel_depolarizing |
| 27B | iter-2 | 11/12 (91.7%) | **in progress** | TBD |
| 35B | iter-1 | 10/12 (83.3%) | 11/12 (91.7%) | channel_depolarizing |
| 35B | iter-2 | *(same base)* | 11/12 (91.7%) | channel_depolarizing |

### 6.3 vs Prior Baselines

| Model | Eval Set | Base | Adapter | Delta | Date |
|:------|:---------|:-----|:--------|:------|:-----|
| 27B fallback (dedup-1k LoRA) | 12-task | 8/12 | 8/12 | 0 | 2026-06-11 |
| 35B dedup-1k LoRA (W8A8) | 12-task | 0/12 | 0/12 | 0 | 2026-06-11 (INVALID) |
| **35B GLM5.2 distill iter-1** | **12-task** | **10/12** | **11/12** | **+8.3pp** | **2026-07-06** ✅ |
| **35B GLM5.2 distill iter-2** | **12-task** | *(same base)* | **11/12** | **0pp vs iter-1** | **2026-07-06** ✅ |
| 27B GLM5.2 distill iter-2 | 12-task | 11/12 | in progress | TBD | 2026-07-06 |

**Notes:**
- The dedup-1k W8A8 `0/12` result is invalid (audit: candidate code was token soup, not model generation).
- The 35B GLM5.2 distill iter-1 is the **first valid 35B 12-task result** confirming model quality improvement.
- Training loss metrics (final eval loss=0.597–0.622, ppl=1.820–1.863) are consistent across all three runs.
- The 27B base outperforms 35B base on this holdout (11/12 vs 10/12) — 27B passes `quantum_grover_oracle_diffusion` which 35B base fails.

---

## 7. Adapter Configuration Summary

All three iter-1 adapters share the same LoRA hyperparameters:

| Parameter | Value |
|:----------|:------|
| LoRA rank | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.0 |
| Target modules (35B) | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Target modules (27B) | q_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Frozen | mlp.gate, router |
| Train layernorm | Yes |
| Train-on-completions-only | Yes |
| Dataset | glm52_soft_distill_sft 100 rows (90 train, 10 eval) |
| Max length | 2048 (35B) / 1600 (27B) |

---

## 8. Open Items

1. **[HIGH, IN PROGRESS]** Collect ASI1 27B iter-2 adapter results (~15:00–15:30 UTC) → add to Section 4.1
2. **[HIGH]** Evaluate ASI2 35B iter-3 adapter after training completes (~14:37 UTC):
   - Kill `eval_all_adapters.py`, restore harness.py, launch `--models adapter`
3. **[HIGH]** After all iter-2 evals complete: run `evals/subsystem/analyzer.py compare` + `dataset_gap.py recommend` to generate iter-3 curation guidance
4. **[MED]** Target `quantum_channel_depolarizing` in iter-3 dataset — all models fail this task; failure category: `syntax` (likely complex noise channel API)
5. **[MED]** Run CE loss/perplexity eval on all adapters using `run_asi2_35b_heldout_loss_eval.py`
6. **[LOW]** 495-holdout pass@1 evals (long-running, deprioritized)

