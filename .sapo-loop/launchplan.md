# LAUNCHPLAN — NEXT SAPO LAUNCH (RUN-14 expected) — deploy-integrity + launch-preparer lane
Prepared: 2026-08-31 22:15 CST · Channel: DOWN (deploy NOT performed; this is the pre-launch gate artifact)
Bundles: r21 `tmp/sapo-relaunch-r21.tgz` (sha 05e6698e…) RE-AUDITED → **r22** `tmp/sapo-relaunch-r22.tgz` REBUILT + VERIFIED (FINAL v4: 349 members, sha `b5e0adbc…`).

---

## 1. BUNDLE INTEGRITY VERDICT (re-audit of r21 + build of r22)

### 1a. r21 re-audit (the "current bundle" at task start)
| check | result |
|---|---|
| tree == `tmp/sapo-relaunch-r21.sha256` (180 members) | **PASS** — 0 missing, 0 mismatch |
| embedded `MANIFEST.sha256.json` vs tgz contents (180 members) | **PASS** — 0 missing, 0 mismatch |
| tgz sha256 vs stated `05e6698e66e3f22a905ff0864119f9e512bb9f8816e7db76e020c17bb36f8dde` | **PASS** — identical |
| tgz member count (180 + MANIFEST, no hidden files) | **PASS** — 181 entries |

Verdict: r21 was internally consistent at build time, BUT it is NOT launch-ready for the mandated next-launch config (see §1b F1).

### 1b. Why r21 was NOT launch-ready (the rebuild trigger)
1. **F1 — v9 launch assets absent from r21 (BLOCKER).** The mandate's next-launch benchmark is `evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt` (v9, 12 jsonl-derived tasks). r21 contains ZERO v9 references: the manifest, its 12 task dirs, and the source jsonl are all absent. The box-side launcher would hard-fail at preflight (`required launch file missing`).
2. **F2 — launcher `required_files` gate needs files never in the bundle lineage.** `asi3_launch_grpo_direct.sh` fails closed if any of these are missing at `$NAS_ROOT` on the box: 4 promotion holdout benchmarks (quantum_generalization_holdout_v1/v2_hard/v3_multi_framework, qwen36_27b_quantum_holdout_v1), `scripts/sapo_ensure_repair_sidecar.sh`, `training/sidecar_liveness.py`. Channel is down → cannot verify box state → bundle must be SELF-CONTAINED for the launcher's file gate.
3. **F3 — tree drift after r21 build (19:29).** Post-19:29 launch-path changes: v9 manifest + builder (19:38), capability-sentinel rule contract + test (22:03), vLLM Lane-A client/tests/server/lifecycle (17:22–22:07), trainer updates (ImportError guard 22:06, entropy-floor-weight 0.01→0.03 default, min-group-size flag), launcher-readiness test v9 pin, gate_alias_normalization tests, `evals/benchmarks/` etc.
4. **browser-automation/huanxin_browser_launch.js (resolver-pin, 21:45) — checked, NOT added.** Browser automation has never been in the bundle lineage (r20/r21 contain zero `browser-automation/` members); it is Mac-side tooling for the Huanxin console, not box-side code. The two bundled scripts that mention it (`submit_asi2_grpo_27b_selfeval_task.sh`, dry-run spec in `asi2_launch_grpo_27b_selfeval.sh`) are only used by the browser-submit path, which is not used for the AI/ASI3 direct launch (STATUS #173: "ASI3/AI direct path only"). Resolver-pin lives in the Mac-side launch flow. **Decision: do not bundle.**

### 1c. r22 build + verification (FINAL v4 2026-09-01: 349 members — see deploywatch.md FINAL v4)
- Member list: canonical lineage (`tmp/r18_members.txt` superset + holdout task dirs = 235 members, the concurrent build) **merged with 12 launch-critical files** = **247 members + embedded MANIFEST.sha256.json**. The 235-member build alone was NOT launch-ready: it lacked `quantum_rl_questions_v2.jsonl` (launcher source-lineage hard-fail for v9) and the launcher `required_files` set.
- Delta list vs r21 (55): v9 manifest + 12× v9 task dirs (36 files, exactly the manifest's task set; WIP dir `quantum_rl_v2_teleport_rz_ry` excluded), frozen-holdout task dirs (braket_bell_state, circuit_depth_optimization, cirq_qaoa_line, qiskit_stabilizer_5qubit_code, trotterized_hamiltonian_evolution — the box eval loop's 18-task holdout needs them box-side).
- Merged additions (12): `quantum_rl_questions_v2.jsonl` (repo-root member → `$NAS_ROOT/` box-side), `scripts/build_grpo_v9_manifest.py`, capability-sentinel rules + test, `vllm_lifecycle.py` + test, launcher `required_files` set (4 promotion holdouts + `sapo_ensure_repair_sidecar.sh` + `sidecar_liveness.py`). (vLLM client + test + server launcher were already in the 235 lineage.)

| check | result |
|---|---|
| tree == `tmp/sapo-relaunch-r22.sha256` (349 members, FINAL v4) | **PASS** — 0 missing, 0 mismatch |
| embedded `MANIFEST.sha256.json` vs tgz (349 members) | **PASS** — 0 missing, 0 mismatch |
| outer/inner key sets identical | **PASS** |
| **tgz sha256 (FINAL)** | **b5e0adbc8a3e505dd1338846369270ef22c515f7cc93ac0a7446670c7d6295e1** |
| launcher manifest-gate simulation vs bundle (as the box runs it, root=extracted bundle) | **PASS** — imports [], exec-verified true, semantic=0, source sha match, task_contract `97809aef…` MATCH, contamination clean vs all 5 holdouts, all required_files present |
| v9 contract hash recomputed on tree | **PASS** — header `97809aeff45c…` == computed |
| py_compile of bundled trainer + tests | **PASS** |

**INTEGRITY VERDICT: r22 (349 members, sha `b5e0adbc…`) is the launch bundle. Do not launch with r21.**

> NOTE (concurrent-lane coordination): the tree was live-edited during this audit (trainer + vLLM Lane A + sentinel rules landed 22:03–22:11). The final r22 freeze (22:15) captured the current tree; if any launch-path file is edited after this freeze, rebuild r22 by re-running `python3 tmp/build_r22_bundle.py` (it reads the current tree; lineage = current `tmp/sapo-relaunch-r22.sha256` + the 12-file merge list) and re-verify before deploy.

---

## 2. CONFIG AUDIT — env overrides the NEXT launch MUST set

Launcher truth: `scripts/asi3_launch_grpo_direct.sh` (read-only, not modified). Canonical entry: `scripts/ai_launch_sapo_direct.sh` (wrapper; `AI_SAPO_*` aliases → `ASI3_SAPO_*`). NOTE: `configs/rl/qwen36_27b_fv_gspo_asi2.json` is documentation-only (trainer never reads it — audit F2); launcher env/CLI is the sole source of truth.

| knob | launcher default | next launch MUST override | rationale |
|---|---|---|---|
| `ASI3_SAPO_LR` / `AI_SAPO_LR` | `2e-4` | **`5e-5`** | RUN-13 capability-erosion fix (STANDUP #232/#233): lr 2e-4 → entropy explosion 0.055→1.59, 16 trust-region violation windows, uniform rubric losses. 5e-5 confirmed in RUN-13 launch_config. |
| `ASI3_SAPO_BENCHMARK_FILE` / `AI_SAPO_BENCHMARK_FILE` | `evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt` | **`evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt`** | **v9 ALONE (recommended, not v8∪v9 union).** Justification: (1) the union does not exist as a file — building it needs a new manifest with a recomputed 32-task contract hash AND a launcher-verifiable `# source=` lineage; no builder exists and the launcher rejects unverifiable lineage — v9 alone is the audit lane's documented choice too; (2) v9 is the fresh first-wave jsonl curriculum covering exactly the frozen-holdout competence classes (partial trace/entropy, Shor, Trotter, depolarizing, VQE, QAOA, Bell, QFT, stabilizers, error-correcting codes) on disjoint instances; (3) verified disjoint: v9 ∩ v8 = ∅, v9 ∩ all 5 promotion holdouts = ∅ (contamination gate clean); (4) v9 manifest passes every launcher preflight (verified locally, §1c). |
| `ASI3_SAPO_ADAPTER_INIT` / `AI_SAPO_ADAPTER_INIT` | empty (base-init) | **newest RUN-13 step_*_adapter checkpoint** (see §3 for the find command) | Warm continuation of RUN-13's learned weights (RUN-13 = `sapo-27b-ai-20260831T083524Z`, adapter_init step_000037, lr 5e-5). The trainer refuses a mismatched r/alpha adapter (must be 16/64) and refuses RESUME_* without ADAPTER_INIT. |
| `ASI3_SAPO_ROOT` / `AI_SAPO_ROOT` | `/root/software/quantum-gpt` | **`/root/work/software/quantum-gpt`** | Box tree is at `/root/work/software/quantum-gpt` (RUN-4 launch env, STATUS:255; asi2_loop_eval.sh REMOTE_ROOT default). Launcher default points at the nonexistent `/root/software` tree. |
| `ASI3_SAPO_MODEL_PATH` / `AI_SAPO_MODEL_PATH` | `$NAS_ROOT/models/Qwen3.6-27B` | **`/root/work/filestorage/Qwen3.6-27B`** | Box model location (STATUS:255). Verify at launch. |
| `ASI3_SAPO_STEPS` / `AI_SAPO_STEPS` | asi3: `500`; wrapper: **`100`** | **`500`** (pin explicitly) | Wrapper default (100) differs from asi3 default (500) — MUST pin `ASI3_SAPO_STEPS=500` so the wrapper doesn't silently shrink the run (F3-class knob). |
| `ASI3_SAPO_REWARD_MODE` / `AI_SAPO_REWARD_MODE` | `p_dominant` | **`comprehensive`** | Approved R20/R21 stack (verified argv: `--reward-mode comprehensive`). |
| `ASI3_SAPO_REWARD_NORMALIZATION` / `AI_SAPO_REWARD_NORMALIZATION` | `none` (inert) | **`minmax`** | Approved stack; judge batch-normalization across group. |
| `ASI3_SAPO_MIN_GROUP_SIZE` / `AI_SAPO_MIN_GROUP_SIZE` | `1` (inert) | **`8`** | r19 user binding: every round rolls out ≥8 candidates (hard floor overrides router adaptive-4). |
| `ASI3_SAPO_BATCH_COMPARATIVE_JUDGE` / `AI_SAPO_BATCH_COMPARATIVE_JUDGE` | `0` (inert) | **`1`** | dp4 batch-comparative judge enabled (r19 binding). |
| `ASI3_SAPO_JUDGE_DP4_ENDPOINT` / `AI_SAPO_JUDGE_DP4_ENDPOINT` | empty | **`http://127.0.0.1:56237`** | Box-local dp4 bridge port (also `JUDGE_BRIDGE_PORT=56237`). |
| `ASI3_SAPO_JUDGE_DP4_MODEL` / `AI_SAPO_JUDGE_DP4_MODEL` | `dp4` | `dp4` (default fine) | — |
| `ASI3_SAPO_JUDGE_DP4_MAX_TOKENS` / `AI_SAPO_JUDGE_DP4_MAX_TOKENS` | `4096` | `4096` (default fine) | R21 verified argv. |
| EVAL (frozen holdout) | `EVAL_BENCHMARK` default = `sapo_promotion_holdout_v1_18.txt` (18-task FROZEN holdout) in `asi2_loop_eval.sh:78`; `EVAL_BENCHMARK_BOX` = same relative path | **already correct — no override needed** | The eval loop runs Mac-side, executes the evaluator box-side via the daemon; holdout file + evaluator + runner are in r22. |

Confirmed "correct by default" (no override, documented for completeness): GROUP_SIZE 4, MAX_ADAPTIVE_GROUP 4, KL_COEFF 0.01, INNER_EPOCHS 1, LORA 16/64, MAX_NEW_TOKENS 2048, MAX_ADAPTIVE_NEW_TOKENS 2048, MAX_SEQ_LENGTH 3072, TRAIN_PASS_MAX_SEQ_LENGTH 2048, LOGIT_CLIP 50, CHECKPOINT_INTERVAL_SECONDS 1800, LOSS_MODE sapo, SAPO_TAU_POS 1.0 / TAU_NEG 1.05, GSPO_CLIP 0.1/0.2, ADVANTAGE_MODE loo, LOO_ADVANTAGE_SCALE shared_mad, GREEDY_ROLLOUT_FRACTION 0.4, ENTROPY_FLOOR 1.5, ENTROPY_TOKEN_CAP 256, TRUST_REGION scale_lr / max_seq_kl 0.25 / max_clip_fraction 0.90, REWARD masses 0.50/0.40/0.10, curriculum knobs (EMA 0.9 / min 0.05), adaptive-temp max 1.3, SELF_REPAIR_ROUNDS 0.

> NOTE — `ENTROPY_FLOOR_WEIGHT` (asi3 default 0.01) vs trainer CLI default now 0.03 (2026-08-31 research audit T1c strengthening). Launcher passes the env explicitly, so the launch uses 0.01 unless overridden. No directive received to change → keep 0.01 (launcher pin) unless manager decides otherwise; flag for manager.

---

## 3. COMPLETE NEXT-LAUNCH COMMAND (fill ADAPTER_INIT when the channel opens)

### 3a. Find the newest RUN-13 adapter checkpoint (box-side, when channel opens)
```bash
# On the box (NAS_ROOT=/root/work/software/quantum-gpt), newest RUN-13 step adapter:
ls -dt /root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260831T083524Z/step_*_adapter | head -1
# Fallback (checkpoint root also mirrors step adapters):
ls -dt /root/work/software/quantum-gpt/outputs/checkpoints/qwen36_27b_sapo_ai/*/step_*_adapter 2>/dev/null | head -1
# Adapter dir must contain adapter_config.json (launcher validates r=16/alpha=64).
```

### 3b. Launch command (execute in the Huanxin webshell on the box; channel open required)
```bash
AI_SAPO_ROOT=/root/work/software/quantum-gpt \
AI_SAPO_MODEL_PATH=/root/work/filestorage/Qwen3.6-27B \
AI_SAPO_ADAPTER_INIT=/root/work/software/quantum-gpt/outputs/sapo-27b-ai-20260831T083524Z/step_000NNN_adapter \
AI_SAPO_LR=5e-5 \
AI_SAPO_STEPS=500 \
AI_SAPO_BENCHMARK_FILE=evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt \
AI_SAPO_REWARD_MODE=comprehensive \
AI_SAPO_REWARD_NORMALIZATION=minmax \
AI_SAPO_MIN_GROUP_SIZE=8 \
AI_SAPO_BATCH_COMPARATIVE_JUDGE=1 \
AI_SAPO_JUDGE_DP4_ENDPOINT=http://127.0.0.1:56237 \
AI_SAPO_JUDGE_DP4_MODEL=dp4 \
AI_SAPO_JUDGE_DP4_MAX_TOKENS=4096 \
AI_SAPO_GREEDY_ROLLOUT_FRACTION=0.4 \
AI_SAPO_ENTROPY_FLOOR_WEIGHT=0.01 \
bash scripts/ai_launch_sapo_direct.sh launch
```
(ASI3_SAPO_* names work identically; AI_SAPO_* is the canonical wrapper alias. `step_000NNN_adapter` = output of the §3a find command.)

Pre-launch deploy steps (when channel opens — DO NOT launch before):
1. Upload `tmp/sapo-relaunch-r22.tgz` (sha b5e0adbc8a3e505dd1338846369270ef22c515f7cc93ac0a7446670c7d6295e1) to the S3 bundle key; sync via `scripts/asi3_secure_sync_sapo.py --bundle-key … --bundle-sha256 c7f9f658…` (rclone + sha256sum -c + tar -xzf into $NAS_ROOT).
2. On-box spot-check critical shas vs `tmp/sapo-relaunch-r22.sha256` (at minimum: training/grpo_trainer.py, training/generation.py, scripts/asi2_loop_eval.sh, evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt, quantum_rl_questions_v2.jsonl).
3. Confirm the box has `qiskit`/`cirq`/`pennylane`/`stim`/`scipy` (v9 `required_import_roots` is empty, but task runtime must exist — box already has them per audit).
4. Confirm the trainer is NOT already running (`pgrep -f 'training/[g]rpo_trainer.py'` empty; no stale `$LOGDIR/grpo_27b_selfeval.pid`).
5. Run §3a to resolve ADAPTER_INIT; verify `adapter_config.json` r=16/alpha=64.

---

## 4. BOOT-VERIFY CHECKLIST (post-launch, from the train log + eval loop)

### 4a. Train-log boot contract (trainer log: `$NAS_ROOT/logs/sapo_27b_ai/grpo_train_*.log`; launcher echoes before trainer start)
| # | item | what to confirm | where |
|---|---|---|---|
| 1 | lr echo | `LR=5e-5` in the `[asi3]` boot echo AND `"lr": 0.00005` in `launch_config.json` (written at trainer boot, `stage: launch_config_written`) | log head / `outputs/sapo-27b-ai-<RUN_ID>/launch_config.json` |
| 2 | benchmark name | `BENCHMARK=evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt` in boot echo AND `"benchmark_file": …v9…` in launch_config.json | log head / launch_config.json |
| 3 | adapter_init | `ADAPTER_INIT=<resolved step_*_adapter path>` in boot echo AND `"adapter_init"` in launch_config.json (must be ≠ "None"; must match §3a resolution) | log head / launch_config.json |
| 4 | reward/judge stack | `REWARD_MODE=comprehensive`, `REWARD_NORMALIZATION=minmax`, `MIN_GROUP_SIZE=8`, `BATCH_COMPARATIVE_JUDGE=1` in boot echo (line `[asi3] R19_REWARD …`) | log head |
| 5 | step_begin | `stage: zero_change_snapshot` line (lora_b_params_tracked > 0) then step 1 begins (`quantum_rl_v2_*` task sampling — 50/25/25 mix lines); trainer PID matches launcher child | log |
| 6 | zero_change_snapshot | marker present with `lora_b_params_tracked: N`; after step 1, `max\|Δlora_B\|` vs snapshot > 0 (zero_change_alarm must NOT fire) | log after step 1 |
| 7 | repair sidecar alive | boot guard `[asi3] ensuring repair sidecar alive` then trainer step records flag `sidecar_alive: true` (alarm 8) | log |
| 8 | sentinel | `capability_sentinel.py` watching the ACTIVE log (entropy/trust-region/NaN/ERR99999 rules; rules mirrored in bundled `scripts/sapo_capability_sentinel_rules.py`) | box-side process list |

### 4b. Eval loop (box-side evaluator + frozen holdout)
- **Box repo has the holdout + evaluator** — TRUE for r22: `sapo_promotion_holdout_v1_18.txt` (frozen 18-task) + `scripts/run_asi2_base_adapter_rubric_eval.py` + `evals/runner/*` are bundle members; the box already runs the perpetual box-side eval loop (STANDUP #232) which auto-evaluates every new `step_[0-9]{6}_adapter` checkpoint.
- Confirm after launch: `EVAL_BENCHMARK` default = `sapo_promotion_holdout_v1_18.txt` (frozen; do NOT point it at v8/v9 training benchmarks — the loop's `--limit 0` + frozen-holdout contract is the beats-base instrument).
- First eval target: newest RUN-14 checkpoint; verdict lands in `outputs/reeval_latest_<ts>.json` on the box; Mac-side ledger `reports/.asi2_eval_state.json` + `logs/` poll.
- Poke the loop: `bash scripts/asi2_loop_eval.sh --dry-run` from the Mac (needs the daemon /exec transport healthy).

---

## 5. RULES COMPLIANCE
- NOTHING deployed (channel down; bundle staged locally, no S3 upload performed).
- `training/grpo_trainer.py`, `scripts/asi3_launch_grpo_direct.sh`, `scripts/ai_launch_sapo_direct.sh` NOT modified.
- Build artifact: `tmp/build_r22_bundle.py` (member lineage = r21 sha256 list + deltas; embeds MANIFEST; writes `tmp/sapo-relaunch-r22.sha256`).
- SHA references: r22 tgz b5e0adbc8a3e505dd1338846369270ef22c515f7cc93ac0a7446670c7d6295e1 · per-file `tmp/sapo-relaunch-r22.sha256` (247 members) · r21 tgz `05e6698e…` (superseded).
- Rebuild tool: `tmp/build_r22_bundle.py` (lineage = current r22 sha256 + 12-file merge list; embeds MANIFEST; writes `tmp/sapo-relaunch-r22.sha256`).
