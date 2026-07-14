# STATE.md — Current R&D Snapshot

**Last updated:** 2026-07-14 (S3 recovered; Huanxin shell terminal still down — platform outage)
**Purpose:** One-page index. Read this first, then drill into PLAN.md / docs/ for depth.
**Refresh rule:** Update whenever an iteration boundary changes (eval result lands,
new adapter trained, blocker moves). Keep ≤100 lines.

---

## ⚠️ Critical Blocker (2026-07-14)

**Huanxin shell terminal service is DOWN (platform-wide outage).**
Error 170022 "获取shell终端信息失败" on ASI1/ASI2/ASI3. Blocks ALL NPU
training job submissions. Down since 2026-07-10 (4 days). See
`docs/BLOCKER_STATUS_2026_07_14.md`.

**S3 (MinIO) is UP** — all training data staged on S3. Ready to submit
the moment shell terminal recovers.

---

## Where We Are

**Stage 1 (code ability) — active.** GLM5.2 → Qwen3.6 soft-distillation LoRA SFT loop.
Iter-2 adapters trained on ASI1 (27B) and ASI3 (35B); iter-2 eval in progress.
Iter-3 dataset scaffold ready, waiting on iter-2 gap report before filling rows.

**Stage 2 (quantum science) — spec only.** 1000-paper corpus manifest schema +
verification scripts ready. No training until Stage 1 adapter is stable.

## Current Iteration Status

| Item | Status | Location |
|------|--------|----------|
| Iter-2 LoRA SFT (27B, ASI3 r21) | **LOCATED & CONFIG-VERIFIED 2026-07-12** — adapter weights (628 MB `.bin`) on NAS, `adapter_config.json` fetched & decoded locally. Qwen3.6-27B base, r=64, α=128. Weight materialization pending. | NAS `outputs/qnt-sft-27b-asi3-r21-20260706T143739Z/adapter/`; local config `models/iter2-27b-asi3-r21/adapter_config.verified.json` |
| Iter-2 LoRA SFT (35B, ASI3) | **LOCATED & CONFIG-VERIFIED 2026-07-12** — adapter weights (5.3 GB safetensors) on NAS, `adapter_config.json` fetched & decoded locally. r=16, α=32. Weight materialization pending (large-file path needed). | NAS `outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/adapter/`; local config `models/iter2-35b-asi3/adapter_config.verified.json` |e; 11/12 claim not reproducible from local disk** | NAS `/root/work/.../outputs/` (not mirrored to S3) |
| Iter-2 held-out eval | in progress | `evals/runs/` + `evals/subsystem/harness.py` |
| Iter-3 dataset | scaffold only | `scripts/prepare_iter3_distill_sft.py` |
| RL + soft-distill pipeline | designed, gate hook added | `scripts/rl_distill_pipeline.py` |
| Per-artifact scoring | Phase 1-4 done (50 loss-path unit tests pass; launchers wired); **Phase 5 runlist prepared 2026-07-11** (not submitted; awaiting Huanxin transport) | `training/artifact_scoring.py`, `docs/per-artifact-scoring-phase5-runlist-2026-07-11.md` |
| DR-GRPO iteration | psi warmup + variance-correction analyzer done 2026-07-11 (23 DR tests + 4 analyzer tests pass) | `research/papers/doubly_robust_quantum_grpo/`, `scripts/analyze_grpo_metrics.py` |
| Iter-2 eval gap report | **manual draft written 2026-07-11**; machine recs pending dataset_gap.py run + iter2-pull re-pull | `docs/iter2-eval-gap-report-2026-07-11.md` |
| Reward rubric v1 | spec only | `configs/rl/reward_rubric_v1.json` |

## Key Decisions (locked)

- **Students:** Qwen3.6-27B (ASI1), Qwen3.6-35B-A3B (ASI2/ASI3). **Teacher:** GLM5.2.
- **Hardware:** Ascend 910B2, 2 NPUs per environment. Single-process `device_map="balanced-layers"` sharding (not DDP — 27B/35B bf16 don't fit on one NPU).
- **Persistence:** Training outputs → NAS `/root/work/*` (launch scripts refuse `/workspace`). S3 mirror every 5 min via rclone. **Never** trust ephemeral `/workspace` for anything durable.
- **Data philosophy:** LIMA-style, quality over quantity (100 → 1000 curated rows, not 100k noisy).
- **Eval discipline:** Frozen held-out benchmark, identical harness + seed, base-vs-adapter comparison. Two consecutive regressions = hard stop.

## Active Blockers / Risks

- **Iter-2 eval gap report** not yet written — blocks iter-3 dataset fill.
- **Adapter weights missing locally (2026-07-10 finding → 2026-07-12 UPDATE: LOCATED on NAS).** Both iter-2 adapters (27B + 35B) have been located on NAS and their `adapter_config.json` files fetched & verified locally (see `docs/huanxin-adapter-recovery-2026-07-11.md` UPDATE section). Weight materialization (628 MB 27B / 5.3 GB 35B) is the remaining step before the iter-2 eval can be re-run. The "11/12" claim is still unverified pending that re-run.producible from this machine.** This is the #1 blocker.
- **S3 mirror gap → 2026-07-12 UPDATE: Huanxin shell transport RECOVERED.** Daemon connects cleanly to env `AI` (use `scripts/ai_shell.sh "<cmd>"`). The July `qg-27b-*` / `qg-35b-*` output dirs are still NOT in the S3 mirror, but NAS access via Huanxin shell is working again. Adapter dirs located: `outputs/qnt-sft-27b-asi3-r21-20260706T143739Z/` (27B) and `outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/` (35B).
- **W8A8 decompression** takes ~hours before each SFT launch (known cost).
- **Huanxin session keepalive** — browser automation can drift; see `skills/huanxin-s3-ops`.
- **`transformers==4.57.1` Gemma runtime** — still fails on `gemma4` recognition (legacy issue, not on critical path).

## Tooling Status (as of 2026-07-10)

- ✅ `pyproject.toml` (ruff + pytest config) — new
- ✅ `requirements-cpu-eval.txt` (pinned local eval stack) — new
- ✅ `.pre-commit-config.yaml` (ruff + smoke pytest) — new
- ✅ `skills/quantum-eval-verifier/` (eval + gate skill) — new
- ✅ RL eval-gate hook in `scripts/rl_distill_pipeline.py` — new
- ✅ Ablation preset wiring (`ABLATION_PRESET` A–F) + round-cap (`PIPELINE_MAX_ROUNDS`) in all three student launchers (ASI1/2/3) — new 2026-07-10
- ✅ `main()`-program question contract machine-enforced via `requires_full_program` gate field (coding domain) — new 2026-07-10
- ✅ `ruff 0.15.21` installed; `pytest 9.1.1` present
- ✅ `pre-commit 4.6.0` installed (`uv tool install pre-commit`); git hook installed via `pre-commit install` — new 2026-07-10. Ruff hook needs network to fetch `ruff-pre-commit`; run `ruff check` directly when offline.
- ✅ DR-GRPO psi warmup schedule (`dr_psi_warmup_steps`, linear 0→psi_init) wired into `compute_dr_variance_correction` + plugin + 3 new tests — new 2026-07-11
- ✅ `scripts/analyze_grpo_metrics.py` (per-step CSV + DR variance correction summary, `dr_variance_correction` column) + 4 tests — new 2026-07-11
- ✅ `qiskit 2.5.0`, `pennylane 0.45.1`, `qiskit-algorithms`, `qiskit-optimization` installed locally
- ⚠️ `cirq` NOT installable on local py3.14 (needs 3.11-3.13) — cirq tasks run on NAS-side py3.9 verifier only
- ✅ Reference QAOA 5-cycle solution verified locally: cut=4 (optimum)
- ✅ N1/N6/N2 full-scale training data generated + validated (`data/generated/rd_lines_2026_07_13/`) — new 2026-07-13 iter-2
- ✅ `scripts/eval_critic_agreement.py` (N2 ≥85% agreement harness, task-disjoint stratified split, oracle + mock + real-critic modes) + 4 tests — new 2026-07-13 iter-2
- ✅ N2 critic-LoRA seam in `rl_distill_pipeline.py` (`TeacherConfig.critic_mode` + `_critic_lora_eval`) + 3 tests — new 2026-07-13 iter-2
- ✅ 704 tests pass / 13 fail / 11 collection errors (full suite, 2026-07-11). The 13 failures are pre-existing and unrelated to the DR-GRPO changes: 7 are `braket`/`cirq`/`pennylane` module-not-installed in `test_grpo_pipeline_fast`, 1 is a stale default-target assertion in `test_autonomous_rd_cycle`, 1 is an `isq_sft` launcher flag drift, 1 is a runtime-overlay image-loader check, 3 are reference-candidate reward checks depending on missing optional deps. The 11 collection errors are all `ModuleNotFoundError: No module named 'transformers'` (transformers not installable on local py3.14). Focused suites: 23 DR-GRPO + 4 GRPO-metrics-analyzer + 40 artifact-scoring + 14 KL-loss + 30 trust-eval = 111 pass clean.

## Verified Result (2026-07-09, QAOA Max-Cut 5-cycle)

Fresh eval today on the gold-standard full-program task (`quantum_qaoa_maxcut_5cycle`,
56-task scorecard, 3 models). This is the only GLM5.2-era result reproducible from local disk:

| Model | Role | QAOA 5-cycle | Overall 56-task | Failure mode |
|-------|------|:---:|:---:|---|
| `glm5.2` | teacher/base | ✅ PASS (cut=4, optimum) | 49/56 | — |
| `deepseek-v4-pro` | base | ❌ FAIL | 48/56 | `ImportError`: `MinimumEigenOptimizer` from wrong module |
| `qwen3.6-27b-rag` | RAG service (no LoRA) | ❌ FAIL | 48/56 | output is doc prose, not code |

**No trained LoRA adapter was available for this eval.** Source: `evals/runs/qaoa-maxcut-5cycle-20260709/SUMMARY.md`.

## Immediate Next Steps

1. **Materialize 27B adapter weights (628 MB)** from NAS via Huanxin chunked-base64 fetch — build reusable helper, reassemble locally, verify SHA256. ✅ config already verified 2026-07-12.
2. **Materialize 35B adapter weights (5.3 GB)** — too large for base64-over-xterm; use S3 sync or tarball-via-HTTP fallback. ✅ config already verified 2026-07-12.
3. **Re-run iter-2 12-task eval** with materialized adapters to verify the "11/12" claim.
4. ~~Fill iter-3 dataset rows~~ ✅ DONE 2026-07-13 — all 16/16 gap rows in `scripts/iter3_reference_solutions.py` now have reference solutions (9 Qiskit A-rows authored this session + 7 B/C rows from prior). Syntax 16/16 clean; 98 regression tests pass. Build gate still waits on iter-2 eval (item #3) per `scripts/prepare_iter3_distill_sft.py` line 400.
5. ~~Wire `eval_gate` block into active RL config (`configs/rl/*.json`)~~ ✅ DONE 2026-07-13 — both `qwen36_35b_a3b_grpo_rlvr_asi1.json` and `qwen36_35b_a3b_grpo_rlvr_yx_qite.json` have the `eval_gate` block; 13/13 `test_eval_gate_logic.py` pass.
6. Run first RL + soft-distill round with eval gate armed (set `enabled=true` + `verdict_path` when ready)

## Drill-Down

| Topic | Doc |
|-------|-----|
| Two-stage roadmap | `docs/two-stage-training-roadmap-2026-06-30.md` |
| RL + distill iteration process | `docs/rl-distill-iteration-process-2026-07.md` |
| GLM5.2 distillation iteration | `docs/glm52-distillation-rd-iteration-process-2026-07.md` |
| Per-artifact scoring plan | `docs/per-artifact-scoring-rd-plan-2026-07-08.md` |
| Ablation wiring + `main()` contract (2026-07-10) | `docs/ablation-wiring-and-main-program-contract-2026-07-10.md` |
| Reward rubric v1 | `docs/quantum-coding-reward-rubric-2026-07-07.md` |
| Iter-3 dataset spec | `docs/iter3-dataset-spec-2026-07-07.md` |
| Task design conventions | `docs/task-design-conventions.md` |
| Session journal (today) | `journal/2026-07-10.md` |
| Eval subsystem | `evals/subsystem/README.md` |
| Eval verifier skill | `skills/quantum-eval-verifier/SKILL.md` |
| Huanxin + S3 ops | `skills/huanxin-s3-ops/SKILL.md` |
| Frontier infra practices | `docs/frontier_llm_rd_infrastructure_practices_2026-05-26.md` |
| **Consolidated R&D plan (2026-07-13)** | |
| Master plan (replaces 10 line docs) | `docs/RD_PLAN_CONSOLIDATED_2026_07_13.md` |
| Manager report | `reports/MANAGER_REPORT_2026_07_13.md` |
| Adapter A config (quantum-code, primary) | `configs/adapters/adapter_a_quantum_code_v1.json` |
| Adapter B config (quantum-science Q&A) | `configs/adapters/adapter_b_quantum_science_v1.json` |
| Auxiliary critic config (training-time) | `configs/adapters/aux_quantum_critic_v1.json` |
| Archived per-line docs (10) | `docs/archive/rd-lines-2026-07-13/` |
