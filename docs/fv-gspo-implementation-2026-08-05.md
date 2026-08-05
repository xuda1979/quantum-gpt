# FV-GSPO Implementation Reference

**Status:** implemented, validated (unit + integration tests), staged for ASI2 launch
**Design source:** [docs/frontier-verifier-gspo-design-2026-08-04.md](frontier-verifier-gspo-design-2026-08-04.md) (proposal) — this document describes what is actually implemented in the code.
**Target models:** Qwen3.6-27B and Qwen3.6-35B-A3B adapters (LoRA), trained on ASI2 NPUs.
**Primary objective:** improve executable quantum-code and software-engineering pass@1 without wasting rollout compute on mastered or currently unlearnable tasks.

---

## 1. What FV-GSPO Is

Frontier-Verifier GSPO is a GRPO-family policy-optimization algorithm that:

1. **Routs training compute by measured learnability** — each task group is probed and classified (frontier RL / partial-repair RL / mastered replay / repair SFT / quarantine) before it can consume an optimizer step;
2. **Trains only on learnable frontier groups with mixed outcomes**, using Dr.GRPO leave-one-out advantages (no per-task standard-deviation normalization);
3. **Applies GSPO sequence-level clipping** with calibrated clip ranges (3e-4/4e-4), which is stable for dense and MoE (expert-routing) adapters;
4. **Routes all-fail tasks into an execution-verified repair lane** — repair SFT/DPO data built from the current adapter's exact failures and executed corrections;
5. **Mixes 50% targeted repairs / 25% neighboring variants / 25% replay** at sampling time;
6. **Keeps held-out eval tasks strictly outside training** (benchmark-file pools, no overlap);
7. **Treats executable tests as authoritative**; the current adapter's self-judgment carries zero reward weight, and a *frozen* comprehensive judge (base model, later older accepted adapters) is calibration-gated to a 0.05 reward cap;
8. **Guards with circuit breakers** on regression, entropy, clipping, frontier yield, and repair conversion;
9. **Preserves capability** with an adaptive KL controller around a fixed anchor policy.

---

## 2. End-to-End Data Flow

```text
evals/tasks/ (training benchmark pool only; held-out pools never enter)
        │  discover_tasks(…) + load_requested_task_ids(benchmark_file)
        ▼
  task sampling (50/25/25 mixture, frontier router state)      [§4.3]
        │
        ▼
  generate G=8 solutions at temp 0.8 (adaptive escalation)     [§4.1]
        │
        ▼
  execute tests.py::run_tests per candidate                    [§4.2]
        │  → syntax / interface / verifier / import / pass signals
        ▼
  probe: p_pass, shaped dispersion → route classification      [§4.3]
        ├── frontier_rl / partial_repair_rl ──► RL update:
        │       leave-one-out advantages (Dr.GRPO)             [§5]
        │       GSPO sequence-clipped objective + KL           [§6]
        ├── mastered_replay (flat) ──► skip step, no escalation
        ├── repair_sft ──► enqueue repair record (best failing  [§7]
        │       candidate + exact failures) → repair stage →
        │       verified SFT/DPO + repair_converted.jsonl
        └── invalid_or_noisy ──► quarantined, never trained
        │
        ▼
  step metrics → circuit breakers (2-window persistence)       [§9]
        │
        ▼
  periodic adapter checkpoints → NAS sync daemon
```

The trainer runs one task group per optimizer step (`grpo_trainer.py`); the router makes the next step's sampling depend on every prior probe.

---

## 3. Code Map

| File | Role |
|---|---|
| `training/grpo_utils.py` | All FV-GSPO primitives: `FrontierRouter`, `build_mixture_weights`, `leave_one_out_advantages`, `stable_gspo_loss(_metrics)`, `completion_entropy`, `RunningMAD`, `CircuitBreakerState`, `AdaptiveKLState`, `blend_comprehensive_reward`, `append_repair_queue_record`, `count_repair_conversions`, record builders |
| `training/grpo_trainer.py` | Training loop: generation, execution scoring, routing, advantages, GSPO loss, repair queue writer, breaker monitor, frozen judge, metrics, checkpointing |
| `scripts/fv_gspo_repair_stage.py` | Off-line repair lane: queue → correction → harness verification → `repair_converted.jsonl` + SFT/DPO JSONL |
| `scripts/calibrate_model_judge.py` | Frozen-judge calibration: AUC / Spearman vs executable anchors → `judge_calibration.json` |
| `scripts/analyze_grpo_metrics.py` | Post-run diagnostics: routes, frontier yield, clip fractions, entropy, breaker trips |
| `scripts/asi2_launch_grpo_27b_selfeval.sh` | ASI2 launcher (launch/status/stop), FV-GSPO flags, NAS checkpoint sync |
| `scripts/submit_asi2_grpo_27b_selfeval_task.sh` | Browser-automation submission; run params baked into the remote script |
| `configs/rl/qwen36_27b_fv_gspo_asi2.json` | Canonical run configuration for the ASI2 launch |
| `tests/test_fv_gspo.py` `test_fv_gspo_repair_stage.py` `test_model_judge.py` | 79 tests covering all components |

---

## 4. Task Probing and Routing

### 4.1 Rollouts

Each sampled task `x` produces `G = group_size` (default 8) solutions at temperature 0.8 (adaptive escalation to max 2.0 after consecutive low-signal skips), `top_p = 0.95`, `max_new_tokens = 1024`.

### 4.2 Executable scoring

Every candidate is written into the task directory and executed against the task's own `tests.py::run_tests` (the same harness used for evaluation). The reward breakdown yields:

- `pass_reward P ∈ {0,1}` — full test pass;
- `syntax_reward S` — AST parse validity;
- `interface_reward I` — required-interface match (signature/name overlap of `candidate.py`);
- `verifier_reward V` — fraction of verifier clauses passed (`1 − failures/detail_budget`, 0 on runtime failure);
- `import_hygiene H` — no invented non-stdlib imports on single-file tasks;
- `brevity` (optional) — smooth decay past a target line count.

The trainer's shaped weight mix (ASI2 launch): pass 0.45, syntax 0.05, interface 0.10, verifier 0.10, import-hygiene 0.05. **Failing candidates never outrank passing ones** (see §8 blend; the plain path keeps the weighted mix with pass weight dominant).

### 4.3 Frontier router

`FrontierRouter` maintains per-task state (probe count, EMA of `p_pass` and shaped dispersion, last probe step, route, coverage need, RL update count) and implements the design's sampling score:

```
w_x = c_x · [ λ_f · L_x  +  λ_n · √( log(1+N) / (1+n_x) )  +  λ_s · S_x ]
```

| symbol | meaning | default |
|---|---|---|
| `L_x` | learnability = max(binary pass variance `4·p(1−p)`, shaped dispersion) | — |
| `c_x` | coverage need from the training-only skill/failure inventory | 1.0 |
| `n_x` | number of probes of task x | — |
| `N` | total probes across tasks | — |
| `S_x` | staleness = min(1, (step − last_probe_step)/50) | — |
| `λ_f, λ_n, λ_s` | frontier / novelty / staleness weights | 1.0 / 0.5 / 0.25 |
| `mastered_replay_scale` | multiplier applied when route = mastered_replay | 0.15 |
| `unprobed_learnability` | learnability assumed before first probe (exploration) | 0.5 |
| `min_weight` | sampling floor | 0.05 |
| `ema_decay` | EMA of p_pass / shaped dispersion (for sampling state) | 0.7 |

**Route classification** (per probe, raw probe stats; thresholds `tau_frontier = 0.10`, `tau_mastered = 0.95`):

| Route | Condition | In-trainer action |
|---|---|---|
| `frontier_rl` | `learnability ≥ 0.10` (mixed outcomes) | RL update |
| `partial_repair_rl` | `p_pass == 0` but shaped dispersion ≥ 0.10 | RL update on shaped verifier reward |
| `mastered_replay` | `p_pass ≥ 0.95` and flat shaped | RL update, but downweighted 0.15×; skipped when flat (`mastered_replay_flat`) |
| `repair_sft` | `p_pass == 0` and flat shaped | enqueue repair (§7), no RL |
| `invalid_or_noisy` | verifier disagreement / flakiness (hook; not emitted in-trainer yet) | quarantine, no RL |

### 4.4 Mixture sampling (50/25/25)

`build_mixture_weights(router, tasks, step, …)` builds per-task sampling weights from three pools each step:

- **targeted** (50% of mass): tasks routed `frontier_rl` / `partial_repair_rl` **plus never-probed tasks** (probing is top priority);
- **neighbor** (25%): tasks sharing the `category` of a recently-selected frontier task (last `neighbor_window = 10` picks) — generalization across nearby variants of the failed skill; falls back to the targeted pool when no neighbors exist;
- **replay** (25%): `mastered_replay` tasks.

Pool masses are split uniformly within each pool, then normalized. Research-method plugins may scale per-task weights afterwards.

---

## 5. Leave-One-Out Advantages (Dr.GRPO)

Per group, the advantage of candidate `i` uses the **mean of the other G−1 rewards** as baseline:

```
A_i = R_i − (1/(G−1)) · Σ_{j≠i} R_j        (leave_one_out_advantages)
```

- **No per-task reward standard-deviation normalization** (the Dr.GRPO correction: std division explodes when groups are near-constant, e.g. binary rewards).
- Optional shared batch scale `--loo-advantage-scale shared_mad`: divides by one fixed running MAD (`RunningMAD`, EMA decay 0.99) shared across tasks — the only permitted batch-level scaling.
- A safety clamp `advantage_clip = 2.5` bounds outliers.
- `--advantage-mode group_std` reproduces the legacy per-group normalization for the ablation baseline.

---

## 6. GSPO Sequence-Level Objective

The trainer already computes completion log-probability per token (sum of completion-token log-probs / completion-token count), i.e. the **sequence-mean log ratio**. The GSPO objective clips that ratio at the sequence level:

```
s_i(θ) = exp( (1/|y_i|) · Σ_t log( π_θ(y_{i,t}|x,y_{i,<t}) / π_old(y_{i,t}|x,y_{i,<t}) ) )

J_FV = (1/B) · Σ_i  min( s_i·A_i ,  clip(s_i; 1−ε_low, 1+ε_high)·A_i )
        − β · D_KL(π_θ ‖ π_anchor)
```

| parameter | default (27B) | note |
|---|---|---|
| `gspo_clip_low` | 3e-4 | paper-verified for Qwen3-30B-A3B (ε_left = 3e-4); 27B sweep range 1e-4..1e-3 |
| `gspo_clip_high` | 4e-4 | 1.3 × low; 35B start 4e-4 |
| `numerical_log_ratio_clip` | 8.0 | wide clamp **only for finite exponentiation**; the proximal objective is controlled by the GSPO clips, not this |
| `kl_coeff` (β) | 0.005 | initial KL penalty (ASI2 launch) |
| optimizer epochs | 1 | one step per fresh rollout batch (stays on-policy; clipping is a guardrail) |

**Why not DAPO's 0.2/0.28:** GSPO ratios are length-normalized sequence ratios and live orders of magnitude closer to 1 than token-level PPO ratios; clipping them at PPO scales would be nearly a no-op. The GSPO paper reports ~3e-4/4e-4 for the 30B-A3B MoE class, and NVIDIA NeMo's Qwen3-30B-A3B example config uses the same magnitude (`ratio_clip_min/max: 3e-4`).

**Legacy loss** (`--loss-mode grpo`): the old unclipped sequence-ratio loss with `ratio_clip_log_delta = 8.0` is retained purely as the ablation baseline; `--loss-mode gspo` (default) is the launch configuration.

**Statistics** returned per step: `ratio_mean`, `ratio_median`, `clip_low_fraction`, `clip_high_fraction`, `clip_total_fraction`, `seq_kl` — recorded into `grpo_step_metrics.jsonl` and fed to the clipping breaker.

---

## 7. Repair Lane (All-Fail → Verified SFT/DPO)

### 7.1 In-trainer queue (grpo_trainer.py)

When a group routes `repair_sft`, the best failing candidate (max verifier reward, then total reward) is appended to `repair_queue.jsonl`:

```json
{"timestamp_utc": …, "step": 7, "task_id": "quantum_…", "domain": "quantum",
 "category": "…", "best_code": "<failing code>", "failures": ["AssertionError: …", …],
 "pass_rate": 0.0, "verifier_rate": 0.12, "code_hash": "…", "dedup_key": "task:hash"}
```

- Deduplicated by `dedup_key` (task id + code hash) so repeated all-fail probes do not flood the queue;
- All-fail groups are **never** fed to the RL loss;
- The `all_fail_without_repair` breaker (§9) reads `repair_converted.jsonl` to confirm the repair stage is actually converting.

### 7.2 Repair stage (scripts/fv_gspo_repair_stage.py)

For each queue record:

1. **Correction** — a trusted teacher CLI (`--teacher-command`, receives the record JSON on stdin, prints corrected code) or, by default, the task's verified reference `candidate.py` (`corrected_by: teacher|reference`);
2. **Execution-grounded verification** — the correction is written inside the task dir and run against the *same* `tests.py::run_tests`; **rejected unless all tests pass**;
3. **Conversion feed** — every attempt (pass or fail) appends to `repair_converted.jsonl` (`converted: true|false`, `failure_category`, `corrected_by`), which `count_repair_conversions()` feeds into the trainer's breaker;
4. **Training data** — verified corrections emit `repair_sft.jsonl` (prompt = task spec + failing program + exact failures, chosen = verified correction) and, when the failing code exists, `repair_dpo.jsonl` (rejected = the exact failing rollout), in the repository's pair schema (`pair_id`, `failure_category` via a `classify_failure` mirror of `evals/subsystem/harness.py`).

Failure categories: `syntax_error`, `import_error`, `timeout`, `runtime_error`, `assertion_failure`, `unknown_failure`.

---

## 8. Frozen Comprehensive Judge (base model / older adapters)

User requirement (2026-08-05): the **base model**, and later **older accepted adapters**, act as an evaluation model giving a comprehensive per-sample score: code correctness, runnable with no error, result correctness, efficiency, etc. **The judge is a separate frozen evaluator, never the current training policy.**

- **Five dimensions** per sample: `correctness`, `runnability`, `result_correctness`, `efficiency`, `quality`;
- **Evidence-anchored, greedy** (temperature 0): the judge prompt includes the executable evidence (test pass/fail, failure details) and must not contradict it;
- CLI: `--model-judge-enabled --judge-model-path <base> [--judge-adapter-path <older adapter>] --judge-device cpu` (default CPU so training NPUs are untouched).

**Reward composition** — two modes (`--reward-mode`, user decision 2026-08-05: the
reward should NOT be executable-dominated):

`p_dominant` (default, FV-GSPO ablation baseline):

```
R = P + (1−P) · [ (1−W)·S  +  W · Σ_d (w_d/Σw)·M_d ]  −  T
W = min( Σ_d w_d , 0.05 )
```

- `P` = full test pass — always dominant: judge mass comes out of the shaped term `S`, never from `P`; a passing candidate always outranks a failing one;
- With all `w_d = 0` (the default until calibration passes), `R = P + (1−P)·S`;
- `T` = bounded truncation/pathological-length penalty.

`comprehensive` (the user's chosen reward — execution is one component, not the
dominator):

```
R = w_P·P  +  w_S·S  +  w_J·J  −  T,        defaults w_P=0.40, w_S=0.35, w_J=0.25
```

- `J` = frozen-judge composite over calibrated dimensions (relative weights);
- Judge mass `w_J` is active only once at least one dimension passes calibration;
  until then the masses renormalize over `P` and `S`;
- A failing candidate CAN outrank a passing one when its shaped/judge scores are
  high enough — the judge is evidence-anchored (its prompt shows the executable
  evidence) and calibration-gated, so it does not contradict the tests;
- Masses configurable: `--reward-pass-mass / --reward-shaped-mass / --reward-judge-mass`.

**Calibration gates** (`scripts/calibrate_model_judge.py`, pure math: Mann-Whitney AUC, Spearman rank ρ):

| dimension | executable anchor | gate |
|---|---|---|
| correctness | full test pass | AUC ≥ 0.85 |
| runnability | syntax + import hygiene | AUC ≥ 0.85 |
| result_correctness | full verifier clause pass | AUC ≥ 0.85 |
| efficiency | measured runtime | Spearman ρ ≤ −0.6 (faster scores higher) |
| quality | no executable anchor | never auto-enabled |

`n ≥ 200` judged samples required; enabled dimensions share the 0.05 cap uniformly. Output `judge_calibration.json` is consumed via `--judge-calibration`. Until a dimension passes, its scores are diagnostics (`model_dim_scores` in step metrics).

---

## 9. Circuit Breakers

`CircuitBreakerState(window_size=10, required_windows=2)` — a rule must persist across **two consecutive evaluation windows** (10 steps each) before it trips; trips are recorded once and halt the run when `stop_on_severe_breaker` (default on; `--no-stop-on-severe-breaker` disables).

| breaker | rule (window mean unless noted) |
|---|---|
| `non_finite` | any non-finite loss/gradient in the window |
| `clip_fraction` | `clip_total_fraction` > 0.50 (GSPO clips far more tokens than PPO — >50% is a guardrail, not normal) |
| `entropy_collapse` | entropy mean < 0.5 × baseline **and** frontier yield < 0.5 × baseline (median of first 20 steps) |
| `all_fail_without_repair` | all-fail step share > 0.40 **and** the repair queue grew **and** `repair_converted` count == 0 |
| `holdout_regression` (external feed) | held-out pass@1 drops > 3 pp across windows |
| `replay_regression` (external feed) | broad replay pass@1 drops > 3 pp across windows |

External feeds: `report_holdout_pass1(value)` / `report_replay_pass1(value)` — used by the monitoring loop / eval gate (the design's eval-side conditions are enforced there; in-trainer breakers are the first four).

Per step, the monitor receives: route, non-finite flag, clip fraction, mean completion entropy (computed from the logits' token distribution over completion tokens), repair-queued flag, repair-converted count, all-fail share. On trip: `circuit_breaker_trip` events are logged and stored; on `should_stop`, training breaks after saving the adapter.

**Monitoring metrics** recorded per step (extended `grpo_step_metrics.jsonl`): route, `all_fail`, `repair_queued`, `frontier_fraction`, `entropy_mean`, `ratio_mean`, `clip_low/high_fraction`, `seq_kl`, `generation_tokens`, `model_dim_scores`, `model_judge_enabled`, `kl_beta`, `breaker_trips`, plus the legacy reward/loss/curriculum fields. `scripts/analyze_grpo_metrics.py` aggregates route counts, frontier yield, all-fail share, clip means, entropy, generation tokens, and breaker trips into `<prefix>.summary.json`.

---

## 10. Adaptive KL Controller

Design §4 ("anchor policy"): β adapts from measured sequence KL each successful step:

```
if seq_kl > 1.5 × kl_target:  β ← min(kl_max, β × kl_up_rate)
if seq_kl < 0.5 × kl_target:  β ← max(kl_min, β × kl_down_rate)
```

| flag | default |
|---|---|
| `--adaptive-kl` | off (fixed β in the first probe) |
| `--kl-target` | 0.05 |
| `--kl-up-rate` / `--kl-down-rate` | 1.2 / 0.9 |
| `--kl-min` / `--kl-max` | 1e-4 / 0.5 |
| `--kl-beta-init` | 0.005 |

Per-step `kl_beta` recorded. The anchor reset half (accepted-checkpoint reference) remains cluster-side: reset the anchor only after a checkpoint passes the held-out regression gates.

---

## 11. CLI Reference (FV-GSPO flags, defaults)

| flag | default | meaning |
|---|---|---|
| `--loss-mode {gspo,grpo}` | gspo | GSPO clipped objective vs legacy unclipped baseline |
| `--gspo-clip-low / --gspo-clip-high` | 3e-4 / 4e-4 | sequence-ratio clip range |
| `--numerical-log-ratio-clip` | 8.0 | wide clamp, finite exponentiation only |
| `--advantage-mode {loo,group_std}` | loo | Dr.GRPO leave-one-out vs legacy normalization |
| `--loo-advantage-scale {none,shared_mad}` | none | optional shared running-MAD batch scale |
| `--advantage-clip` | 2.5 | advantage safety clamp |
| `--frontier-threshold` / `--mastered-threshold` | 0.10 / 0.95 | router τ values |
| `--mix-targeted / --mix-neighbor / --mix-replay` | 0.5 / 0.25 / 0.25 | mixture masses |
| `--neighbor-window` | 10 | recent-frontier window for the neighbor pool |
| `--repair-queue-path` | `<out>/repair_queue.jsonl` | all-fail queue |
| `--repair-converted-jsonl` | — | conversion feed read by the breaker |
| `--coverage-json` | — | training-only coverage map (task_id → need) |
| `--circuit-breaker-window` | 10 | steps per evaluation window |
| `--stop-on-severe-breaker` / `--no-stop-on-severe-breaker` | stop | halt after two-window trip |
| `--model-judge-enabled` | off | frozen comprehensive judge |
| `--judge-model-path` / `--judge-adapter-path` | model path / — | frozen judge base + older adapter |
| `--judge-device` | cpu | judge device (spare NPU allowed) |
| `--model-judge-max-tokens` / `--model-judge-temperature` | 256 / 0.0 | judge generation |
| `--judge-calibration` | — | per-dim weights from calibration |
| `--adaptive-kl` (+ `--kl-*`) | off | adaptive β controller |
| `--top-p` | 0.95 | sampling |
| `--overwrite-output-dir` | off | allow replacing prior step metrics |

---

## 12. ASI2 Launch Configuration

`configs/rl/qwen36_27b_fv_gspo_asi2.json` + `scripts/asi2_launch_grpo_27b_selfeval.sh`:

- Model `/root/work/filestorage/Qwen3.6-27B`, 2–4 NPUs, LoRA rank 16 / α 32 on all q/k/v/o/gate/up/down projections, router/expert gates frozen (`.*\.(mlp\.gate|router)\..*`);
- LR **2e-6** (legacy 1e-5 was aggressive for prolonged verifier RL), KL β **0.005**, temp 0.8, G=8;
- Training pool **only**: `evals/benchmarks/quantum_grpo_training_v1.txt` (13 quantum tasks); held-out pools (`quantum_generalization_holdout_v1/2/3`) never enter training;
- Self-judge disabled (zero reward weight per design); frozen judge off until calibration data exists;
- Repair queue → `$OUT/repair_queue.jsonl`; breakers on (window 10, stop on severe);
- Checkpoints: every 7200 s → NAS `/root/work/filestorage/grpo_checkpoints/qwen36_27b_selfeval` (sync daemon, retain 5);
- **Launch order per the design**: short frontier-yield probe first (`ASI2_GRPO_STEPS=24`, ~2–3 breaker windows) — "do not launch a long run before the router produces a healthy frontier yield"; scale to 500 steps after the probe's routes/clip/entropy diagnostics look right.

---

## 13. Validation

- `tests/test_fv_gspo.py` (25): router classification/weights/staleness/coverage/frontier-fraction, mixture pools + fallback, GSPO loss stats, entropy, running MAD, repair queue dedup/conversions, all breakers (trip, recovery, entropy collapse, all-fail with/without conversion, holdout regression), adaptive KL;
- `tests/test_fv_gspo_repair_stage.py` (3): convert via reference, reject unverified correction, dedup — subprocess end-to-end with a synthetic task harness;
- `tests/test_model_judge.py` (13): blend P-dominance + cap, judge JSON parsing, AUC/Spearman math, calibration gates, calibration script end-to-end;
- plus the pre-existing `test_grpo_utils.py` (34), analyzer tests, and trainer-metrics tests — **82 tests green**; ruff clean (pre-commit hooks enforced, incl. pinned ruff v0.6.9).
- **Paper cross-check:** GSPO ε_left/ε_right = 3e-4/4e-4 for Qwen3-30B-A3B and the length-normalized sequence ratio match the implementation exactly (ar5iv 2507.18071; NVIDIA NeMo `grpo_qwen3_30ba3b_instruct.yaml`).

---

## 14. Ablation Order (as implemented)

1. **Baseline** — `--loss-mode grpo --advantage-mode group_std` with the old curriculum (TaskCurriculum retained);
2. **Router only** — frontier routing + all-fail repair queue with the legacy loss;
3. **Dr advantage** — `--advantage-mode loo`;
4. **FV-GSPO** — `--loss-mode gspo` (default launch config);
5. **Repair loop** — run `fv_gspo_repair_stage.py` on the queue, SFT/DPO on the verified pairs, 50/25/25 mixture;
6. **Adaptive anchor** — `--adaptive-kl` + cluster-side anchor resets after accepted checkpoints;
7. **Judge** — enable `--model-judge-enabled` after `calibrate_model_judge.py` passes gates.

Primary efficiency metric: Δheld-out pass@1 per generated NPU-token-hour.

---

## 15. Known Limitations / Non-Goals

- The trainer processes one task group per optimizer step; multi-group batched updates (design's "batch multiple prompt groups") are a future change — the mixture/router state is structured so K>1 batching can slot in.
- `invalid_or_noisy` routing (flaky-test detection) is a defined route but not emitted in-trainer yet; the router function supports it.
- The in-trainer breakers cover non-finite, clip, entropy, and repair conversion; held-out/replay regression breakers are external feeds used by the monitoring loop.
- The repair stage's default correction source is the task's verified reference; a trusted teacher CLI (`--teacher-command`) is the on-cluster upgrade path.
- The frozen judge defaults to CPU inference (cost: ~256 tokens × G per step); a spare NPU (`--judge-device npu:N`) reduces latency when available.
- Per the design's non-goals: the current adapter is never its own correctness source; self-critique language, long reasoning, or confidence are not rewarded unless they improve executable outcomes; the doubly-robust plugin claims nothing until it wins a controlled ablation.
