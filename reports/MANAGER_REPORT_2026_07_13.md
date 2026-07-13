# Manager Report — Quantum-Code Adapter R&D
**Date:** 2026-07-13
**Prepared for:** Manager review
**Status:** Reorganization complete; training data ready; awaiting NPU access

---

## Executive summary

We have consolidated **13 scattered R&D lines into 2 production adapters
+ 1 training-time auxiliary**, with all training data generated and
validated locally. The architecture is now deployment-focused: **one
adapter that fixes all quantum-code error categories**, plus an optional
second adapter for quantum-science Q&A. Training is ready to launch the
moment NPU access is restored (currently blocked on Huanxin S3 outage).

## What we deliver

| Deliverable | Description | Ready? |
|-------------|-------------|--------|
| **Adapter A: Quantum-Code** | Primary production adapter. Fixes ImportError, prose-only, TypeError, assertion, traceback, output-mismatch, and circuit-construction errors in one model. 3-stage: SFT → DPO → RL. | Data ✅ / Training ⏳ |
| **Adapter B: Quantum-Science Q&A** | Secondary adapter for non-coding quantum research questions with citation grounding. | Plan ✅ / Training ⏳ |
| **Auxiliary: Quantum-Critic** | Judge model used as RL reward signal (not deployed standalone). Replaces the GLM5.2 teacher dependency. | Data ✅ / Training ⏳ |

## Why this architecture (not 13 adapters)

The original program planned 13 separate LoRA adapters, one per failure
category. This is wrong for deployment:

- An adapter that fixes **only ImportError** is useless if it emits
  **prose-only** output.
- The failure categories are **complementary**, not competing — the model
  must avoid ALL of them simultaneously.
- Serving 13 adapters is operationally infeasible.

So we merge by **role**:
- All "fix this error category" lines → **one unified DPO dataset** → one
  adapter (Adapter A).
- The "judge code correctness" lines (critic + selector) → **one judge
  model** (auxiliary), used two ways.

## Training data — generated and validated

| Dataset | Rows | Source lines | Validation |
|---------|-----:|-------------|------------|
| Unified DPO pairs | 360 | N1+N3+N6+N7+N10 | ✅ all 7 negative types present, ChatML valid |
| Unified SFT curriculum | 22 | N4+N5+N8 | ✅ all rows pass tests.py |
| Critic SFT (auxiliary) | 66 | N2 (58 pos + 8 neg) | ✅ schema-validated |
| Critic eval split | 14 (20%) | held-out | ✅ task-disjoint, stratified |

## Success metrics (measurable)

| Metric | Current baseline | Target |
|--------|-----------------|--------|
| QAOA 5-cycle scorecard | 48/56 tasks pass | ≥ 52/56 |
| Import-error failures | ≥ 3 | 0 |
| Prose-only failures | 1 | 0 |
| TypeError failures | ≥ 1 | 0 |
| General coding holdout | — | < 0.5% regression |
| Critic agreement w/ execution | 50% (random) | ≥ 85% |

## Current blocker

**Huanxin MinIO S3 endpoint is down** (HTTP 500/404). This blocks:
1. Recovery of iter-2 adapter weights (prerequisite for all NPU training).
2. Submission of new training jobs.

**Escalated to:** Huanxin platform team.
**Workaround:** none available locally; all local-only work is complete.

## What happens when S3 recovers

1. Submit critic-LoRA training job (small, fast — ~hours).
2. Submit Adapter A SFT stage (~1 day).
3. Submit Adapter A DPO stage on top of SFT (~hours).
4. Submit Adapter A RL-GRPO stage on top of DPO (~1 day, uses critic).
5. Run full 56-task eval + generalization holdout.
6. Deliver Adapter A to production; Adapter B in parallel.

**Estimated wall-clock from S3 recovery to Adapter A deploy candidate: ~3 days.**

## Files

- Plan: `docs/RD_PLAN_CONSOLIDATED_2026_07_13.md`
- Adapter configs: `configs/adapters/adapter_{a,b}_*.json`, `configs/adapters/aux_quantum_critic_v1.json`
- Training data: `data/generated/rd_lines_2026_07_13/`
- Test suite: 65+ tests passing (unified DPO, critic agreement, all per-line prep scripts)
