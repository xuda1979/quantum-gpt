# Per-Artifact Scoring R&D Plan

**Date:** 2026-07-08
**Status:** Active. Implementation in progress.
**Scope:** Extends the RL + soft-distillation loop (`scripts/rl_distill_pipeline.py`
+ `training/qwen_sft_peft_kl.py`) with per-artifact reward decomposition and
reward-weighted distillation. Additive: the legacy single-reward path remains
the default; the new path is opt-in via config so the two can be A/B-ed.

## 1. Problem with the current loop

The existing RL+distill pipeline computes **one scalar reward per sample**
(`metadata.reward` in `[0, 1]`), a weighted blend of:

- `w_teacher_already_correct` — was the student's first attempt already correct?
- `w_teacher_confidence` — GLM5.2's stated confidence in its correction.
- `w_first_pass_qgate` — did the question pass the gate without resampling?
- `w_answer_substance` — length of the corrected answer (anti-cop-out).

The trainer (`qwen_sft_peft_kl.py`) uses this scalar only as a **filter**
(`--reward-floor 0.20` drops samples below the floor). It does **not** weight
the loss by reward, and it does **not** distinguish *why* a sample scored well
or poorly. A sample where the student's code was 80% correct (one API misuse)
gets the same loss signal as a sample where the student's code was totally
wrong, as long as both are above the floor.

The reward rubric (`configs/rl/reward_rubric_v1.json`) already defines seven
decomposed components (R_pass, R_partial, R_runnable, R_api_correct, R_style,
R_length_penalty, R_hallucination_penalty), but it is marked "Spec only. No
trainer changes in this track." None of these components are currently
captured by the pipeline or consumed by the trainer.

## 2. Research hypothesis

**H1:** Distilling more heavily from samples where the student is *close*
(high partial credit, one or two issues) accelerates learning more than
distilling uniformly from all above-floor samples, because the gradient
on the "fix the last API misuse" signal is exactly what the student needs.

**H2 (anti):** Distilling too heavily from near-misses and ignoring total
failures loses coverage of the question space and makes the student brittle
on unfamiliar topics. (This is the failure mode the single-reward path guards
against by keeping all above-floor samples.)

**H3:** Per-artifact decomposition lets us **down-weight** the KL term on
artifacts where the teacher itself is uncertain (low confidence, many issues)
and **up-weight** NLL on artifacts where the teacher is confident. This
targets distillation signal where it is most reliable, addressing the
"teacher noise" failure mode.

## 3. Design

### 3.1 Per-artifact score vector (pipeline side)

For each RL+distill sample, the pipeline will additionally capture a
**score vector** `metadata.artifact_scores` with the following fields,
all in `[0, 1]`:

| Field | Source | Already available? |
|-------|--------|--------------------|
| `r_pass` | `teacher_eval_result.is_correct` | yes (as `teacher_is_correct`) |
| `r_partial` | derived from `teacher_issues` count + severity | no — new |
| `r_runnable` | `teacher_issues` contains no "syntax error" / "import error" / "NameError" class | no — new |
| `r_api_correct` | `teacher_issues` contains no "deprecated API" / "wrong API" / "hallucinated import" class | no — new |
| `r_style` | `teacher_issues` contains no "style" / "pyflakes" class | no — new |
| `r_length_penalty` | `len(correct_answer)` piecewise-linear per rubric | no — new |
| `r_hallucination_penalty` | `teacher_issues` contains "hallucinated import" class | no — new |
| `r_teacher_confidence` | `teacher_eval_result.confidence` | yes |
| `r_first_pass` | `resample_attempts <= 1` | yes |

The `r_partial`, `r_runnable`, `r_api_correct`, `r_style`, and
`r_hallucination_penalty` fields are derived by **classifying each string in
`teacher_issues`** into one of the rubric's issue categories via a keyword
table (see §3.2). This is rule-based, not a separate reward model — it reuses
the teacher signal we already pay for.

### 3.2 Issue classifier (rule-based)

A new module `training/artifact_scoring.py` will export:

```python
def classify_issue(issue: str) -> str
    # Returns one of:
    #   "syntax"        -> affects r_runnable
    #   "import_error"  -> affects r_runnable
    #   "name_error"    -> affects r_runnable
    #   "deprecated_api"-> affects r_api_correct
    #   "wrong_api"     -> affects r_api_correct
    #   "hallucinated_import" -> affects r_api_correct + r_hallucination_penalty
    #   "style"         -> affects r_style
    #   "logic"         -> affects r_partial (catch-all for correctness issues)
    #   "other"         -> ignored

def score_artifact(teacher_eval_result: dict, correct_answer: str,
                   resample_attempts: int) -> dict[str, float]
    # Returns the full score vector above.
```

The keyword table is intentionally conservative: if a string doesn't match
any keyword, it falls into `"logic"` (affects `r_partial`) rather than
`"other"`, so unrecognised teacher criticism still hurts partial credit.

### 3.3 Reward-weighted distillation loss (trainer side)

The trainer gains three new args (all default-off for back-compat):

- `--reward-weighted-nll` (bool): multiply the NLL term by
  `w = (reward - reward_floor) / (1 - reward_floor)` clamped to `[0, 1]`.
  Samples below the floor are still dropped. Samples at the floor get
  `w=0` (no NLL gradient); samples at reward=1 get `w=1` (full gradient).
- `--per-artifact-kl-gate` (bool): scale the KL term by
  `r_teacher_confidence`. When the teacher is uncertain (low confidence),
  the KL target is down-weighted (we trust the teacher's distribution less).
- `--partial-credit-upweight` (float, default 0.0): add an extra NLL weight
  `+ partial_credit_upweight * r_partial` to up-weight near-miss samples.
  This is the knob for testing H1. At 0.0 the trainer behaves exactly as
  today.

The combined loss becomes:

```
w_sample = clamp((reward - reward_floor) / (1 - reward_floor), 0, 1)
if per_artifact_kl_gate:
    kl_weight_this_sample = kl_coeff * r_teacher_confidence
else:
    kl_weight_this_sample = kl_coeff
w_nll = nll_coeff * (w_sample + partial_credit_upweight * r_partial)
loss = w_nll * nll_loss + kl_weight_this_sample * kl_loss
```

When all three new args are off / zero, `loss` reduces to the current
`nll_coeff * nll_loss + kl_coeff * kl_loss` exactly.

### 3.4 Config wiring

A new section in `configs/distill/rl_distill_*.json`:

```json
"per_artifact_scoring": {
  "enabled": true,
  "issue_classifier": "rule_v1",
  "trainer": {
    "reward_weighted_nll": true,
    "per_artifact_kl_gate": true,
    "partial_credit_upweight": 0.5
  }
}
```

When `enabled: false` (or the section absent), the pipeline writes only the
existing `metadata.reward` and the trainer uses the legacy loss. This makes
the two paths A/B-able by flipping one config flag.

### 3.5 Ablation matrix

The ablation presets from `reward_rubric_v1.json` extend naturally:

| Preset | `reward_weighted_nll` | `per_artifact_kl_gate` | `partial_credit_upweight` | Tests |
|--------|----------------------|------------------------|---------------------------|-------|
| A (legacy) | off | off | 0.0 | baseline, current behaviour |
| B (rw-nll) | on | off | 0.0 | H1 minimal: reward-weighted NLL only |
| C (kl-gate) | off | on | 0.0 | H3: confidence-gated KL only |
| D (partial-up) | off | off | 0.5 | H1 direct: up-weight near-misses |
| E (full) | on | on | 0.5 | combined: B+C+D |
| F (full, no up) | on | on | 0.0 | combined without partial upweight |

Each preset runs as an independent RL+distill loop (separate buffer, separate
adapter checkpoint lineage). The eval subsystem's `pass@1` on the quantum
holdout is the primary metric.

## 4. Implementation phases

### Phase 1 — Per-artifact scoring module + tests (CPU, no NPU)
- `training/artifact_scoring.py`: issue classifier + `score_artifact()`.
- `tests/test_artifact_scoring.py`: unit tests for the keyword table, edge
  cases (empty issues, unknown issue strings, confidence clamping), and
  the score-vector range contracts.
- **Done when:** all unit tests pass and `score_artifact()` produces the
  full vector for a sample of real `teacher_eval_result` JSONs from
  `data/generated/rl_distill_*_v1/rl_distill_samples.jsonl`.

### Phase 2 — Pipeline integration (CPU, no NPU)
- `scripts/rl_distill_pipeline.py`: call `score_artifact()` in
  `_build_sample()`, write `metadata.artifact_scores` alongside the
  existing `metadata.reward`.
- `configs/distill/rl_distill_*.json`: add `per_artifact_scoring` section
  (default `enabled: true` so new samples carry the vector; the trainer
  still ignores it until Phase 3).
- **Done when:** a short pipeline run produces samples whose JSON has the
  new `metadata.artifact_scores` field with all 9 fields populated, and the
  existing `metadata.reward` is unchanged (back-compat).

### Phase 3 — Trainer reward-weighted loss (NPU)
- `training/qwen_sft_peft_kl.py`: add the three new args, read
  `metadata.artifact_scores` from the dataset, compute `w_sample` and
  `kl_weight_this_sample`, modify the loss. When args are off, loss is
  bit-identical to today.
- `tests/test_qwen_sft_peft_kl_loss.py`: unit test the loss function with
  mock logits + teacher logprobs + score vectors, asserting:
  - legacy path (all off) == current formula.
  - `reward_weighted_nll` scales NLL by `w_sample`.
  - `per_artifact_kl_gate` scales KL by `r_teacher_confidence`.
  - `partial_credit_upweight` adds `r_partial`-weighted NLL.
- **Done when:** loss unit tests pass and a 2-step trainer smoke run on
  NPU with `--reward-weighted-nll --per-artifact-kl-gate` produces a
  non-NaN loss curve and a valid adapter checkpoint.

### Phase 4 — Orchestrator + config A/B wiring (NPU) ✅ launcher wiring done
- Orchestrator launchers: pass the new trainer args through from the
  config's `per_artifact_scoring.trainer` section.
- Add an `ABLATION_PRESET` env var to the launchers that maps the preset
  name (A–F) to the three trainer args, so a single `ABLATION_PRESET=B
  bash scripts/asi1_launch_rl_distill_27b_2npu.sh` run selects the full
  configuration.
- **Done when:** each preset can be launched with one env var, and the
  run config JSON records which preset was used.

  **Status (2026-07-09):** Launcher wiring is complete across all three
  student launchers — `scripts/asi1_launch_rl_distill_27b_2npu.sh`,
  `scripts/asi2_launch_rl_distill_35b_2npu.sh`, and
  `scripts/asi3_launch_rl_distill_35b_2npu.sh`. Each accepts
  `ABLATION_PRESET={A_legacy|B_rw_nll|C_kl_gate|D_partial_up|E_full|F_full_no_up}`,
  expands it to the three trainer flags (`--reward-weighted-nll`,
  `--per-artifact-kl-gate`, `--partial-credit-upweight <w>`), passes them to
  `training/qwen_sft_peft_kl.py`, and records the preset + per-flag booleans +
  upweight in `run_config.json`. All three scripts pass `bash -n`; a render
  test of all 6 presets produces the expected JSON + trainer-arg combos.
  Phase 5 (NPU ablation runs) is unblocked. The trainer already supports all
  three flags (see `qwen_sft_peft_kl.py` arg defs).

### Phase 5 — Eval + decision (NPU)
- Run presets A, B, D, E on ASI1 (27B) for ~20 rounds each (≈17 hours
  wall-clock per preset at 55 min/round).
- Compare `pass@1` on the quantum holdout at rounds 5, 10, 15, 20.
- **Decision rule:** adopt the preset with the highest `pass@1` at round 20
  that does not regress `pass@1` by more than 1pp at any earlier checkpoint
  (monotonic-improvement guard). If no preset beats A, keep the legacy
  path and write up the negative result.

  **Launch commands (hands-off, 20-round budget each).** All three
  launchers now support `PIPELINE_MAX_ROUNDS` (auto-stops after N rounds)
  and `ABLATION_PRESET`. Per the 2026-07-10 training-execution policy
  (see `MEMORY.md`), **all training runs must be submitted as ASI1 jobs
  via `scripts/submit_asi1_shell_task.sh`, never run directly on the
  environment's own NPU.** Run one preset at a time (the 2-NPU launcher is
  not multi-tenant), in this order so the legacy baseline is captured first:

  ```bash
  # Preset A (legacy baseline) — must complete first as the control.
  ASI1_SHELL_REMOTE_COMMAND="ABLATION_PRESET=A_legacy PIPELINE_MAX_ROUNDS=20 \
    bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch" \
    bash scripts/submit_asi1_shell_task.sh --submit

  # Preset B (reward-weighted NLL only).
  ASI1_SHELL_REMOTE_COMMAND="ABLATION_PRESET=B_rw_nll PIPELINE_MAX_ROUNDS=20 \
    RUN_ID=ablation-B-\$(date -u +%Y%m%dT%H%M%SZ) \
    bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch" \
    bash scripts/submit_asi1_shell_task.sh --submit

  # Preset D (partial-credit upweight 0.5 only).
  ASI1_SHELL_REMOTE_COMMAND="ABLATION_PRESET=D_partial_up PIPELINE_MAX_ROUNDS=20 \
    RUN_ID=ablation-D-\$(date -u +%Y%m%dT%H%M%SZ) \
    bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch" \
    bash scripts/submit_asi1_shell_task.sh --submit

  # Preset E (all three on; the "full" treatment).
  ASI1_SHELL_REMOTE_COMMAND="ABLATION_PRESET=E_full PIPELINE_MAX_ROUNDS=20 \
    RUN_ID=ablation-E-\$(date -u +%Y%m%dT%H%M%SZ) \
    bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch" \
    bash scripts/submit_asi1_shell_task.sh --submit
  ```

  Use `--dry-run` first to inspect the rendered launch spec before
  `--submit`. Each submitted job writes its preset + per-flag booleans to
  `outputs/.../run_config.json` on the NAS and auto-stops after round 20.
  Monitor the submitted job's orchestrator via
  `bash scripts/asi1_launch_rl_distill_27b_2npu.sh status` (on the host,
  read-only); stop early with `... stop`. Per-round eval JSON lands in
  `outputs/.../evals/round-N/`. The eval harness
  (`evals/subsystem/harness.py`) runs every `EVAL_EVERY_ROUNDS=2` rounds
  by default (i.e. rounds 2, 4, 6, …, 20), giving 10 checkpoint
  comparisons per preset. Use round-20 `pass@1` as the primary decision
  point and the round-2…18 trajectory for the monotonic-improvement guard.

## 5. Risk register

| Risk | Mitigation |
|------|------------|
| Issue classifier mis-categorises teacher strings → noisy `r_partial` | Conservative fallback to `"logic"`; keyword table tuned on 200 real `teacher_issues` samples before Phase 3. |
| `partial_credit_upweight` too aggressive → student overfits to near-miss patterns | Phase 5 ablation compares D vs A; if D regresses early `pass@1`, lower the weight or drop it. |
| `per_artifact_kl_gate` with low-confidence teacher → KL term vanishes → no distillation signal | Floor `r_teacher_confidence` at 0.3 inside the gate so KL never goes fully to zero. |
| Score vector inflates sample metadata → buffer grows | 9 floats ≈ 72 bytes/sample; negligible vs. the teacher logits payload (KBs/sample). |
| New loss path has a bug that silently degrades training | Phase 3 unit tests assert bit-identical legacy path; Phase 5 monotonic-improvement guard catches regressions early. |

## 6. Out of scope

- Training a separate neural reward model (we use rule-based + teacher signals).
- Changing the GRPO trainer (`training/agentic_grpo_trainer.py`) — this plan
  only touches the soft-KL distillation trainer. GRPO changes are a separate
  R&D track.
- Per-token credit assignment within the corrected answer (we weight at the
  sample level; per-token is future work if sample-level wins).

## 7. Success metric

Primary: `pass@1` on `evals/benchmarks/quantum_paper_science_holdout_v1.json`
(or the agentic coding holdout, whichever is the current Stage-1 benchmark)
at RL+distill round 20, for the best preset vs. legacy preset A.

Secondary: convergence speed (rounds to reach 90% of the final `pass@1`).

Tertiary: robustness — `pass@1` variance across 3 eval seeds at round 20.

The plan succeeds if at least one preset beats A on the primary metric
without regressing on the tertiary metric.
