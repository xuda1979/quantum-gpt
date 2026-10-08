# RL + Soft-Distillation for Quantum-Computing **Science** (non-coding) — R&D Plan

**Date:** 2026-07-09
**Status:** Active. Implementation kickoff; RL launches on ASI1/2/3 (2 NPUs each) once build + smoke tests pass.
**Author:** parallel session (Track S)
**Sibling doc:** `docs/rl-distill-iteration-process-2026-07.md` (the Stage-1 *coding* loop this plan clones).

---

## 1. Why this document exists

The repo already has a working RL + soft-distillation loop for **quantum coding**:
student proposes a coding question → teacher (GLM5.2) qgates it → student
answers with Python → sandbox executes the code → teacher grades + corrects →
teacher re-emits the corrected answer with `top_logprobs` for soft KL distillation.
The buffer is consumed by a periodic LoRA SFT trainer (`training/qwen_sft_peft_kl.py`)
that interleaves NLL on the corrected answer with KL to the teacher's
distribution. Orchestrator launchers (`scripts/asi{1,2,3}_launch_rl_distill_*_2npu.sh`)
run this on 2 NPUs per host with a vLLM server + pipeline + trainer + eval loop.

This plan **clones** that exact algorithm but swaps the *task domain* from
quantum **coding** to quantum-computing **science** (conceptual / theoretical /
paper-grounded reasoning). No code execution sandbox is involved; the teacher
grades the answer against a scientific rubric and provides a corrected answer.
Everything else — orchestrator, vLLM, trainer, KL distillation, per-artifact
scoring, eval gate, guardrails, dedup, git-sync — is reused verbatim.

This is the **Stage-2 RL** track from `docs/two-stage-training-roadmap-2026-06-30.md`,
executed in parallel with the Stage-1 coding RL loop, sharing the same teacher
and the same hardware allocation policy (2 NPUs per host) but with a disjoint
buffer, disjoint adapter init, and disjoint output directory.

## 2. Mission & success metrics

**Mission.** Improve Qwen3.6-27B (ASI1) and Qwen3.6-35B-A3B (ASI2, ASI3) on
quantum-computing *science* QA: concept explanation, math derivation, algorithm
walk-through, limitation analysis, cross-paper comparison — the L0–L6 levels
defined in `docs/stage2-science-corpus-manifest-schema-2026-07-07.md`.

**Primary success metrics (held-out eval, paper-disjoint from any training source):**

| Metric | Target | Source |
|---|---|---|
| `pass@1` on `quantum_science_holdout_v1` (teacher-judged correctness) | ≥ +0.10 absolute over the SFT-distill iter-2 adapter | new eval task set |
| Teacher-judged `citation_grounding` rate | ≥ +0.15 absolute | rubric metadata |
| Hallucination rate (teacher flags `fabricated_claim`) | ≤ −0.10 absolute | rubric metadata |
| Stage-1 coding `pass@1` regression | ≤ −0.03 absolute | `evals/tasks/quantum/*` |

**Stop conditions.** Either (a) held-out pass@1 improves by ≥0.10 with ≤0.03
coding regression for two consecutive eval rounds, or (b) wall-clock budget hit
(see §7), or (c) guardrail trips (§9) and cannot be recovered within one round.

## 3. What is reused verbatim from the coding loop

| Component | Reused from | Modifications |
|---|---|---|
| Orchestrator loop (vLLM serve → pipeline → pause → trainer → eval → resume) | `scripts/asi{1,2,3}_launch_rl_distill_{27b,35b,35b_asi3}_2npu.sh` | clone + change `CONFIG`, `BUFFER_DIR`, `OUT`, port, served-name |
| Soft-KL LoRA SFT trainer | `training/qwen_sft_peft_kl.py` | none (it is task-agnostic; it consumes `messages` + `teacher_logits.logprobs`) |
| Per-artifact scoring | `training/artifact_scoring.py` | extend `rule_v1` classifier with science-rubric issue categories (see §5) |
| Buffer writer, dedup index, rejection tracker, guardrails, eval-gate hook, git-sync | `scripts/rl_distill_pipeline.py` | none (the CLI surface is reused) |
| Eval subsystem harness | `evals/subsystem/harness.py` | add a `quantum_science` task family |
| Huanxin + S3 ops | `skills/huanxin-s3-ops/SKILL.md` | none |
| Doubly-robust GRPO plugin (optional, future) | `training/grpo_trainer.py` + `training/research_plugins.py` | not wired in v1; can be added once SFT-distill baseline is stable |

## 4. What is new

### 4.1 Pipeline mode flag

A new top-level config key `task_domain: "science"` (default `"coding"`) switches
the pipeline between the two domains. When `task_domain == "science"`:

1. **Student question-generation prompt** asks for a science QA question
   (concept / derivation / walk-through / limitation / comparison), not a
   single-file Python coding task.
2. **Teacher qgate** validates the question is well-formed, scientifically
   answerable without writing code, and non-trivial.
3. **Student answer prompt** asks for a structured prose + math answer (LaTeX
   inline allowed), no code block required.
4. **Sandbox execution is skipped** (`SandboxConfig.enabled = False` forced).
   `exec_brief` in the teacher eval prompt becomes a fixed string
   `"(science mode: no code execution; grade the answer on scientific correctness and grounding)"`.
5. **Teacher correction logprobs prompt** is unchanged in shape but refers to
   "corrected answer" not "corrected code".
6. **Reward** drops the `w_exec_pass` / `w_teacher_exec_pass` terms (they are
   zero in science mode) and the normalisation is recomputed. The remaining
   terms are `w_teacher_already_correct`, `w_teacher_confidence`,
   `w_first_pass_qgate`, `w_answer_substance`, plus a new
   `w_citation_grounding` term sourced from the teacher rubric.

### 4.2 Science question-generation contract

`question_generation` gains a new sub-block used only in science mode:

```json
"question_generation": {
  "task_domain": "science",
  "science_levels": ["L0", "L1", "L2", "L3", "L5", "L6"],
  "science_level_distribution": {
    "L0": 0.05, "L1": 0.25, "L2": 0.20, "L3": 0.20, "L5": 0.20, "L6": 0.10
  },
  "science_fields": [
    "vqe", "qaoa", "qpe", "grover", "qec", "error_mitigation",
    "hamiltonian_simulation", "quantum_ml", "quantum_comm",
    "variational_theory", "compilation", "tomography"
  ],
  "science_field_distribution": { "vqe": 0.14, "qaoa": 0.12, ... },
  "frameworks": [],          // ignored in science mode
  "topics": [],              // ignored in science mode
  ...
}
```

`L4` (Implementation — "write a Qiskit function") is **excluded** from science
mode by design; that level belongs to the coding loop. The student sampler draws
`(level, field, difficulty)` from the science distributions and passes them as
hints to the qgen prompt exactly as the coding loop passes `(framework, topic, difficulty)`.

### 4.3 Science teacher rubric

The teacher eval JSON schema gains two optional fields:

```json
{
  "is_correct": true | false,
  "issues": ["..."],
  "correct_answer": "...",
  "confidence": 0.0..1.0,
  "citation_grounding": 0.0..1.0,   // NEW: 1.0 = every claim is grounded
  "fabricated_claim": true | false, // NEW: teacher suspects a fabricated result
  "artifact_scores": { ... }        // populated by per_artifact_scoring
}
```

`citation_grounding` defaults to 0.5 when the teacher omits it. The pipeline
extracts it and feeds it into `_compute_reward`. `fabricated_claim` is recorded
in metadata and used by the guardrail (§9) to detect hallucination drift.

### 4.4 Science reward weighting (default)

```json
"reward_weighting": {
  "w_teacher_already_correct": 0.35,
  "w_teacher_confidence": 0.20,
  "w_first_pass_qgate": 0.15,
  "w_answer_substance": 0.10,
  "w_citation_grounding": 0.20
}
```

Compared to the coding loop's no-sandbox fallback (which is what this most
resembles), the science loop **adds `w_citation_grounding`** and **raises
`w_teacher_already_correct`** because there is no execution ground truth to lean
on. The teacher's verdict is the primary signal, so we weight it heavily and
guard against its noise with the per-artifact KL gate (§5).

### 4.5 Per-artifact scoring extension

`training/artifact_scoring.py` `rule_v1` classifier currently maps coding-issue
strings onto a fixed category set. For science mode we add a parallel classifier
`rule_science_v1` with categories:

| Category | Trigger keywords (lowercase substring) |
|---|---|
| `incorrect_math` | "equation", "derivation", "missing term", "wrong sign", "normalization" |
| `unsupported_claim` | "unsupported", "no citation", "fabricated", "not in source", "invented" |
| `conceptual_error` | "misunderstands", "confuses", "wrong definition", "category error" |
| `incomplete` | "incomplete", "missing step", "hand-waves", "glosses over" |
| `ungrounded_comparison` | "comparison", "compares to", "threshold", "vs.", "relative to" |
| `notation` | "notation", "ambiguous symbol", "inconsistent convention" |
| `other` | (fallback) |

The classifier is selected by `per_artifact_scoring.issue_classifier =
"rule_science_v1"` in the science config. The trainer side is unchanged: it
consumes `metadata.artifact_scores.<category>` for reward-weighted NLL and the
per-artifact KL gate.

### 4.6 Science eval task family

A new eval task family `quantum_science` lives at `evals/tasks/quantum_science/`.
Each task is a directory with:

- `task.json` — `{ "id", "name", "domain": "quantum_science", "category": "concept|derivation|walkthrough|limitation|comparison", "candidate_file": "candidate.py", "test_file": "tests.py" }`
- `candidate.py` — empty stub; the eval harness fills it with the model's answer
- `tests.py` — a **teacher-judge** test that sends the question + the model's
  answer to GLM5.2 and asserts the teacher's `is_correct == true` and
  `citation_grounding >= 0.7`. This mirrors the coding eval's "run the code and
  check stdout" pattern but substitutes the teacher for the interpreter.

An initial set of **20 held-out science tasks** is authored manually, covering
the 6 science levels × the 12 fields, paper-disjoint from any future Stage-2
corpus. These are the `quantum_science_holdout_v1` benchmark.

### 4.7 Adapter init

Science RL starts from the **same** GLM5.2-distill iter-2 LoRA adapters the
coding loop uses (paths in `outputs/qg-{27b,35b,35b-asi3}-glm52-distill-sft-iter2/adapter`
on the NAS). Rationale: the iter-2 adapter already has quantum vocabulary and
basic reasoning; we don't want to start from the raw base. We accept the small
risk that the coding adapter biases question generation toward code-flavored
science questions — the qgate and the `task_domain=science` prompt framing
should counter this, and we will measure it in the first eval round.

If the first eval round shows coding-flavored question drift, the fallback is to
re-init from the base Qwen3.6 model with a fresh LoRA. This is a one-line
`adapter_init_path` change in the config.

## 5. Per-artifact reward-weighted distillation (science)

The coding loop's per-artifact scoring R&D plan
(`docs/per-artifact-scoring-rd-plan-2026-07-08.md`) applies directly. In science
mode we use the **`E_full` ablation preset** from day one (reward-weighted NLL +
per-artifact KL gate + partial-credit upweight 0.5), because the teacher is the
only ground truth and we want the trainer to down-weight KL on artifacts where
the teacher is uncertain. The coding loop defaults to `A_legacy` because it has
execution ground truth; the science loop has no such luxury.

Concretely, the science launchers pass `--reward-weighted-nll
--per-artifact-kl-gate --partial-credit-upweight 0.5` to
`training/qwen_sft_peft_kl.py` (the `E_full` preset mapping in the launcher).

## 6. Architecture per host (2 NPUs)

Identical to the coding loop:

```
NPU 0,1  -> vLLM student server (Qwen3.6-{27B,35B-A3B} + LoRA adapter, science port)
CPU      -> rl_distill_pipeline.py --config configs/distill/rl_distill_science_*_v1.json
NPU 0,1  -> qwen_sft_peft_kl.py (trainer, paused vLLM, soft-KL LoRA SFT)
NPU 0,1  -> evals/subsystem/harness.py --tasks quantum_science (every 2 rounds)
```

**Port + served-name allocation (science):**

| Host | Model | vLLM port | Served name | Output dir | Buffer dir |
|---|---|---|---|---|---|
| ASI1 | Qwen3.6-27B | 8017 | qwen36-27b-rl-distill-science | `outputs/qg-27b-rl-distill-science-<RUN_ID>` | `data/generated/rl_distill_science_27b_v1` |
| ASI2 | Qwen3.6-35B-A3B | 8018 | qwen36-35b-rl-distill-science | `outputs/qg-35b-rl-distill-science-<RUN_ID>` | `data/generated/rl_distill_science_35b_v1` |
| ASI3 | Qwen3.6-35B-A3B | 8019 | qwen36-35b-asi3-rl-distill-science | `outputs/qg-35b-asi3-rl-distill-science-<RUN_ID>` | `data/generated/rl_distill_science_35b_asi3_v1` |

Ports 8017/8018/8019 are chosen to avoid colliding with the coding loop's
8007/8008/8009 if both loops ever run on the same host simultaneously (they
won't in v1, but the separation makes the two loops independently restartable).

## 7. Budget & schedule

| Item | Budget | Owner |
|---|---|---|
| Build (pipeline mode flag, prompts, rubric, classifiers, configs, launchers, eval tasks) | 1 local session | Track S |
| Local smoke test (CPU, no NPU, mock teacher) | 1 local session | Track S |
| First RL round on ASI1 (27B, 2 NPUs) | 1 hour wall-clock | ASI1 |
| First RL round on ASI2 + ASI3 (35B, 2 NPUs each) | 1 hour wall-clock each | ASI2, ASI3 |
| First eval round (every 2 RL rounds) | ~15 min per host | per host |
| Iter-1 budget cap | 24 hours wall-clock per host, or 20 RL rounds, whichever first | per host |
| Iter-2 decision point | after iter-1 eval report | Track S + lead |

**Parallelism with Stage-1 coding loop.** The coding RL loop and the science RL
loop are intended to run **concurrently** on different hosts if hardware allows.
In v1, if only one host is available at a time, the science loop yields to the
coding loop (coding has the stricter Stage-1 stability gate). The launchers are
independent; neither blocks the other.

## 8. Configuration files to create

```
configs/distill/rl_distill_science_27b_v1.json
configs/distill/rl_distill_science_35b_v1.json
configs/distill/rl_distill_science_35b_asi3_v1.json
```

Each is a clone of the corresponding `rl_distill_*_v1.json` with:
- `name` → `rl_distill_science_*_v1`
- `student_model.serving.api_base` → `http://127.0.0.1:{8017|8018|8019}/v1`
- `student_model.serving.model` → `rl_distill_science_latest`
- `student_model.adapter_init_path` → unchanged (iter-2 SFT adapter)
- `output_dir` → `data/generated/rl_distill_science_*_v1`
- `pipeline.task_domain` → `"science"`
- `pipeline.run_harness_when_available` → `false` (no sandbox)
- `pipeline.teacher_judge_when_no_harness` → `true`
- `question_generation` → science sub-block (§4.2)
- `reward_weighting` → science weights (§4.4)
- `per_artifact_scoring.issue_classifier` → `"rule_science_v1"`
- `per_artifact_scoring.trainer` → `{ "reward_weighted_nll": true, "per_artifact_kl_gate": true, "partial_credit_upweight": 0.5 }`
- `eval.tasks` → `"quantum_science"`
- `eval.every_rounds` → `2`
- `guardrail` → add `max_fabricated_claim_rate: 0.20` and `min_citation_grounding: 0.4`

## 9. Guardrails (science-specific, additive)

Inherited from the coding loop:
- `max_consecutive_teacher_rejections: 12`
- `max_teacher_qgate_rejection_rate: 0.85`
- `min_teacher_confidence: 0.3`
- `min_corrected_answer_chars: 40`
- `rolling_window: 32`

New for science:
- `max_fabricated_claim_rate: 0.20` — if >20% of the last 32 samples have
  `fabricated_claim == true`, trip the guardrail and exit cleanly so the
  orchestrator runs a trainer + eval burst early. This catches hallucination
  drift where the student learns to make up citations/results.
- `min_citation_grounding: 0.4` — if the rolling mean `citation_grounding`
  drops below 0.4, trip. This catches the student drifting into ungrounded
  speculation.

Both are checked in `BufferWriter.append` (or its science equivalent) and emit a
manifest entry with `guardrail_trip: true` and the offending metric, matching
the existing guardrail pattern.

## 10. Implementation order

1. **Pipeline mode flag + science prompts.** Edit
   `scripts/rl_distill_pipeline.py`:
   - Add `task_domain` to `PipelineConfig` (default `"coding"`).
   - Add `SCIENCE_*` prompt constants parallel to the coding ones.
   - In `process_one`, branch on `cfg.task_domain` to pick prompts and skip
     sandbox.
   - In `_compute_reward`, branch on `cfg.task_domain` to use science weights
     (drop exec terms, add `w_citation_grounding`).
   - Add science-specific guardrail checks.
2. **Science per-artifact classifier.** Edit
   `training/artifact_scoring.py`: add `rule_science_v1` classifier function
   alongside `rule_v1`, selected by `issue_classifier` config key.
3. **Configs.** Create the three `rl_distill_science_*_v1.json` files.
4. **Launchers.** Create
   `scripts/asi{1,2,3}_launch_rl_distill_science_{27b,35b}_2npu.sh` by cloning
   the coding launchers and changing `CONFIG`, `BUFFER_DIR`, `OUT`, ports,
   served-name, and the `ABLATION_PRESET` default to `E_full`.
5. **Eval tasks.** Create `evals/tasks/quantum_science/` with 20 held-out
   teacher-judge tasks. Create
   `evals/benchmarks/quantum_science_holdout_v1.txt` listing their ids.
6. **Local smoke test.** Run the pipeline on CPU with a mock teacher (return a
   canned JSON) for ~4 samples, confirm the buffer JSONL has the science
   schema, confirm `_compute_reward` returns values in [0,1] with no exec
   terms. Confirm the trainer can load the buffer and do 2 steps without
   crashing (CPU, tiny model stub if needed).
7. **Sync to NAS + S3.** Use `skills/huanxin-s3-ops` to push the new configs,
   launchers, pipeline, classifier, and eval tasks to each host.
8. **Launch on ASI1.** `bash scripts/asi1_launch_rl_distill_science_27b_2npu.sh`
   via `scripts/ai_shell.sh`. Watch the orchestrator log for the first pipeline
   round to confirm science prompts are used and no sandbox process spawns.
9. **Launch on ASI2 + ASI3.** Same pattern, 35B launchers.
10. **First eval round.** After 2 RL rounds on each host, inspect
    `outputs/qg-*-rl-distill-science-*/evals/round-2/eval-2.json`. Compare
    against the iter-2 SFT adapter baseline on the same holdout.
11. **Iter-1 report.** After 24h or 20 rounds, write
    `docs/rl-science-distill-iter1-report-<date>.md` with pass@1 delta,
    citation_grounding delta, hallucination rate, coding-regression check, and
    a go/no-go for iter-2.

## 11. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Teacher (GLM5.2) is weaker at science grading than at code grading | `E_full` per-artifact KL gate down-weights distillation where teacher confidence < 0.5; raise `min_teacher_confidence` guardrail if noise is high |
| Student drifts into coding-flavored questions (because adapter init is from coding SFT) | qgate rejects questions that require code; measure `% questions rejected for "requires code"` in round 1; if >30%, fall back to base-model adapter init |
| Hallucination reward hacking (student makes up citations) | `max_fabricated_claim_rate` guardrail + `w_citation_grounding` reward term + teacher prompt explicitly asks for `fabricated_claim` flag |
| Eval task leakage into training buffer | science holdout is paper-disjoint and authored before the pipeline runs; dedup index checks question normalized-hash against holdout ids at buffer-append time |
| Both loops (coding + science) compete for the same host | v1 runs them on different hosts; if forced to share, science yields (config flag `priority: lower` in orchestrator — future work) |
| KL distillation NaNs on long science answers (avg answer length > coding answers) | `trainer_max_length` raised to 3072 for science; `KL_COEFF` lowered to 0.4 from 0.5; `--min-teacher-logprob-tokens` filter at 8 |

## 12. Out of scope for this track

- Ingesting the 1000-paper corpus (still owned by the Stage-2 corpus track;
  this RL loop's questions are *student-generated*, not paper-grounded, to keep
  the loop self-contained and avoid the corpus-ingestion critical path).
- Wiring the doubly-robust GRPO plugin (deferred to iter-2 once the SFT-distill
  baseline is stable, same sequencing as the coding loop).
- Multi-host distributed training (each host runs an independent 2-NPU loop;
  no FSDP across hosts in v1).
- Modifying the base model or the tokenizer.
- Modifying the coding loop (the two loops share no mutable state).

## 13. Handoff to the next session

When iter-1 completes, the next session should:
1. Read `outputs/qg-{27b,35b,35b-asi3}-rl-distill-science-*/evals/round-*/eval-*.json`
   and compute the deltas vs the iter-2 SFT baseline.
2. Decide go/no-go for iter-2:
   - **Go** if pass@1 ≥ +0.10 and coding regression ≤ 0.03 and
     hallucination rate ≤ baseline − 0.05.
   - **No-go** if any guardrail tripped and could not be recovered; write a
     failure-mode analysis and propose a config change (likely:
     `w_citation_grounding` up, `min_teacher_confidence` up, or fall back to
     base-model adapter init).
3. If go: bump `LEARNING_RATE` down to 2e-6, raise `EVAL_EVERY_ROUNDS` to 3,
   and relaunch for iter-2 (another 24h / 20 rounds).
4. Update `docs/STATE.md` with the iter-1 outcome and the iter-2 plan.
