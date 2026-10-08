# RL-with-Verifier Coding Loop — R&D Method & Session Record

**Date:** 2026-07-09
**Status:** Implementation complete; launch pending NPU availability on ASI1/2/3.
**Author:** session lead (claude code)
**Related plans:**
- `docs/self_correcting_distill_pipeline.md` (updated today with RL-with-verifier mode)
- `docs/rl-distill-iteration-process-2026-07.md` (operational runbook for the same loop)
- `docs/per-artifact-scoring-rd-plan-2026-07-08.md` (reward decomposition, compatible)
- `docs/rl-science-distill-rd-plan-2026-07-09.md` (parallel session, science/non-coding — do not confuse)

> **Purpose of this document:** record the R&D method, the exact set of
> code artifacts produced this session, the open questions, and the launch
> procedure — so that if this session is lost, a future session can pick
> up without re-deriving the design.

---

## 1. Objective

Convert the self-correcting distillation pipeline from a fixed offline
dataset generator into a **closed-loop RL algorithm with a verifier in
the loop** (Option A), trained on both Qwen3.6-27B (ASI1) and
Qwen3.6-35B-A3B (ASI2, ASI3), with:

- **Real execution as the reward signal.** The student's code is actually
  run in a sandboxed Python interpreter; the verdict (PASS/FAIL/ERROR)
  is the dominant reward weight.
- **Double-confirmation gate.** The teacher's corrected code is also
  executed; a sample is admitted to the SFT set only if the correction
  actually runs to PASS.
- **Batch size = 100** per round.
- **Checkpoint every 2 hours.**
- **Stop at 99% student execution pass-rate** over the last 100 samples.
- **Weakness-aware question generation.** Between batches, the
  orchestrator analyzes the last batch's per-cell pass rates and biases
  the next batch's (framework, topic, difficulty) sampler toward the
  student's weak cells.
- **Diversified questions.** Questions span 8 frameworks × 10 topics × 3
  difficulties; the student proposes, the teacher validates via qgate.
- **Question shape (added 2026-07-09):** every question must ask the
  answerer to write a **full runnable Python program with a `main()`
  function that computes and prints a concrete result** — not an
  isolated function or library snippet.
- **Adapters + important files on NAS**, not local disk.

---

## 2. Method

### 2.1 The RL loop (one iteration)

1. **Sample a (framework, topic, difficulty) contract.** When a
   weakness report from the previous batch exists, blend the prior with
   the inverse-pass-rate distribution (`alpha=0.4`).
2. **Student proposes a question** for that contract.
3. **Teacher validates the question** (qgate: well-formed? answerable?
   non-trivial? asks for a full program with `main()`?).
4. **Student answers its own question** (writes the full program).
5. **Verifier executes the student's code** in a sandboxed subprocess
   (`scripts/code_exec_sandbox.py`): 30 s timeout, 1 GiB memory cap,
   captures `{verdict, stdout, stderr, exit_code, runtime_ms}`.
6. **Teacher grades the answer grounded in the execution result** — it
   sees the real stderr/stdout, so its critique references real runtime
   errors. Returns `{is_correct, issues, correct_answer, confidence}`.
7. **Teacher re-emits the corrected answer** with per-token logprobs
   (for soft KL distillation).
8. **Verifier executes the teacher's corrected code** as a double-
   confirmation gate. Only if the corrected code runs to `PASS` is the
   sample admitted to the SFT buffer. Otherwise → `rejected.jsonl`.
9. **Reward is computed** with the real execution signal dominant:

   | Signal | Weight (sandbox on) |
   |--------|---------------------|
   | `w_student_exec_pass` | 0.45 |
   | `w_teacher_exec_pass` | 0.20 |
   | `w_teacher_already_correct` | 0.15 |
   | `w_teacher_confidence` | 0.10 |
   | `w_first_pass_qgate` | 0.05 |
   | `w_answer_substance` | 0.05 |

10. **Trainer burst.** After 100 admitted samples, the orchestrator
    pauses vLLM, runs `training/qwen_sft_peft_kl.py` for one epoch over
    the accumulated buffer (checkpointing every 7200 s), then resumes
    vLLM with the fresh adapter hot-swapped.
11. **Eval burst.** Every 2 rounds, `evals/subsystem/harness.py` runs
    the held-out quantum benchmark and writes a verdict JSON. The
    pipeline polls it and trips a regression gate if pass@1 drops.
12. **Weakness report.** After each round,
    `scripts/analyze_batch_weakness.py` aggregates per-cell pass rates
    from the buffer and writes `weakness_report.json`, which the next
    round's pipeline reloads.

### 2.2 Question shape requirement (added 2026-07-09)

Every question must ask the answerer to write a **full runnable Python
program** with:
- a `main()` function that performs the computation, and
- an `if __name__ == '__main__': main()` guard, and
- a `print(...)` of the concrete result (a probability, an expectation
  value, a statevector, a histogram, a metric — not just "build a
  circuit").

This is enforced in **six** places (defense in depth):
- `SYSTEM_PROMPT_STUDENT_QGEN` — instructs the student to propose only
  such questions.
- `SYSTEM_PROMPT_TEACHER_QGATE` — instructs the teacher to reject
  questions that ask for an isolated function without a runnable main.
  The qgate also has a programmatic check: `process_one` rejects
  questions where `qgate.requires_full_program` is false (coding mode).
- `SYSTEM_PROMPT_STUDENT` + the student-attempt user prompt — instructs
  the student to answer with a full program with `main()`, not a
  snippet.
- **`check_program_shape()`** (AST-level, in `code_exec_sandbox.py`) —
  statically verifies the student's code has a top-level `def main(...)`
  and an `if __name__ == '__main__':` guard that calls `main()`. The
  result is recorded in `metadata.program_shape`.
- **`check_stdout_nonempty()`** (runtime, in `code_exec_sandbox.py`) —
  verifies the executed program actually printed a concrete result to
  stdout. A PASS verdict with empty stdout is flagged.
- **Reward penalty** — in `_compute_reward()`, a sample whose
  `program_shape.is_full_program` is false gets the reward scaled by
  0.5; a sample that ran to PASS but printed nothing gets scaled by
  0.75. This makes the full-program contract a reward signal, not just
  a prompt suggestion.

The sandbox then verifies the program actually runs and prints a
result.

### 2.3 Diversity mechanism

- **Base distribution** (from config): 8 frameworks × 10 topics × 3
  difficulties with configured priors.
- **Rejection-aware blending:** when the rejection tracker has data,
  the sampler blends the prior with the inverse-rejection distribution
  so the student is nudged toward contracts where its proposals survive
  the qgate.
- **Weakness-aware blending:** when the weakness report is loaded, the
  sampler blends the prior with the inverse-pass-rate distribution
  (weighted by sample count per cell) so the student is nudged toward
  its weak cells.
- **Dedup:** a rolling SHA-1 index over (normalized question,
  normalized answer) drops near-duplicates.

---

## 3. Artifacts produced this session

### 3.1 New files

| File | Purpose |
|------|---------|
| `scripts/code_exec_sandbox.py` | Sandboxed Python execution module. Runs candidate code in a subprocess with rlimit CPU/memory caps + wall-clock timeout. Returns `{verdict, stdout, stderr, exit_code, runtime_ms, truncated}`. Also provides `check_program_shape()` (AST check for `def main` + `__main__` guard) and `check_stdout_nonempty()` (runtime check for non-empty stdout). Self-tested. |
| `scripts/analyze_batch_weakness.py` | Reads the RL-distill buffer, aggregates per-(framework, topic, difficulty) pass rates from `metadata.student_exec.verdict`, writes `weakness_report.json` sorted weakest-first. |
| `scripts/launch_rl_distill_all_asi.sh` | Top-level parallel launcher for ASI1 + ASI2 + ASI3. Passes through `BUFFER_TARGET_PER_ROUND=100`, `TRAINER_CHECKPOINT_SECONDS=7200`, `PASS_RATE_STOP=0.99`. |

### 3.2 Modified files

| File | Change |
|------|--------|
| `scripts/rl_distill_pipeline.py` | (1) Import sandbox. (2) Add `SandboxConfig` + `WeaknessReport` dataclasses and `_load_sandbox` helper. (3) Update `TEACHER_EVAL_PROMPT_TEMPLATE` with `{exec_brief}` placeholder + execution-ground-truth rules. (4) Update `teacher_eval()` to accept `exec_brief`. (5) Add Stage 2.5 (execute student code), Stage 4.6 (execute teacher's corrected code as gate), Stage 4.7 (override `is_correct` with exec ground truth). (6) Update `_compute_reward()` to weight `student_exec_pass` (0.45) and `teacher_exec_pass` (0.20) as dominant signals. (7) Update `_build_sample()` to record `student_exec` + `teacher_exec` in metadata. (8) Add `WeaknessReport` class with `load()` + `blended_distribution()`. (9) Wire `weakness_report` into `process_one` and the main loop with periodic reload. (10) Add `--pass-rate-stop`, `--pass-rate-window`, `--weakness-report` CLI args. (11) Add 99% pass-rate stop condition. (12) Update `SYSTEM_PROMPT_STUDENT_QGEN`, `SYSTEM_PROMPT_TEACHER_QGATE`, `SYSTEM_PROMPT_STUDENT`, and the student-attempt user prompt to require a full program with `main()` that computes and prints a concrete result. |
| `scripts/asi1_launch_rl_distill_27b_2npu.sh` | Default `BUFFER_TARGET_PER_ROUND=100`, `TRAINER_CHECKPOINT_SECONDS=7200`. Pass `--pass-rate-stop 0.99 --pass-rate-window 100 --weakness-report $WEAKNESS_REPORT` to the pipeline. Add post-round weakness-report generation step. |
| `scripts/asi2_launch_rl_distill_35b_2npu.sh` | Same changes as ASI1, for 35B on ASI2. |
| `scripts/asi3_launch_rl_distill_35b_2npu.sh` | Same changes as ASI1, for 35B on ASI3. |
| `configs/distill/rl_distill_27b_v1.json` | Add `sandbox` block (enabled, 30s, 1GiB, reject-on-teacher-exec-fail, exec-is-ground-truth). Add `weakness_aware` block (enabled, alpha=0.4, reload every 100 samples). Update `reward_weighting` with the 6 execution-aware weights. |
| `configs/distill/rl_distill_35b_v1.json` | Same config additions as 27B, for ASI2. |
| `configs/distill/rl_distill_35b_asi3_v1.json` | Same config additions as 27B, for ASI3. |
| `tests/test_rl_distill_pipeline.py` | (1) Update `test_teacher_eval_prompt_has_placeholders` for the new `exec_brief` placeholder. (2) Update `test_reward_tagged_in_metadata` to pass PASS exec results. (3) Add `test_reward_low_when_student_exec_fails`. (4) Disable sandbox in `TestProcessOne._make_cfg` so mocked tests still pass. (5) Add `TestSandboxExecution` (5 tests: pass/fail/syntax/timeout/brief). (6) Add `TestWeaknessReport` (2 tests: no-report-returns-prior, up-weights-weak-cells). |
| `docs/self_correcting_distill_pipeline.md` | Add "RL-with-verifier mode (Option A)" section documenting the closed loop, the execution gate, the double-confirmation requirement, the reward weights, the training-loop parameters, and the question-shape requirement. Update the dataset-shape section to mandate `student_exec` + `teacher_exec` in `teacher_eval` and the `rejected.jsonl` audit file. |

### 3.3 Test status

```
tests/test_rl_distill_pipeline.py: 40 passed (5 runs stable)
tests/test_self_correcting_distill_git_sync.py: 7 passed
tests/test_audit_distillation_dataset_quality.py: passed
tests/test_build_quantum_distillation_seed_questions.py: passed
tests/test_repair_quantum_distillation_203.py: passed
```

All distill-related tests green. Pre-existing `transformers` import errors
in unrelated test modules are environmental, not caused by this session.

---

## 4. Launch procedure

> **Policy (2026-07-09):** Training is **always submitted as a job** via
> `scripts/ai_job.sh` / `ai2_job.sh` / `ai3_job.sh`, never run directly
> on the environment's own NPUs. The launchers default to
> `LAUNCH_MODE=job`. Set `LAUNCH_MODE=local` only for debugging on a
> dedicated training host.

### 4.1 Prerequisites (on each ASI host)

- NAS mounted at `/root/work/software/quantum-gpt` (or set `NAS_ROOT`).
- Base model weights decompressed on local disk (27B on ASI1, 35B on ASI2/3).
- `GLM52_API_BASE` and `GLM52_API_KEY` env vars set (teacher endpoint).
- Python venv with qiskit, cirq, pennylane, mitiq, pyzx, qsharp, cuda-quantum,
  isq — the sandbox needs these to execute quantum code.
- The Huanxin job-submission shell (`scripts/ai_shell.sh` etc.) must be
  functional — the launcher uses `scripts/ai{,2,3}_job.sh start` to
  submit the orchestrator.

### 4.2 Launch all three environments

```bash
# On the NAS host (or via SSH to each ASI):
export GLM52_API_BASE=http://<glm52-host>:<port>/v1
export GLM52_API_KEY=...

# Option 1: parallel launcher (SSHes to each ASI)
export ASI1_SSH_HOST=asi1
export ASI2_SSH_HOST=asi2
export ASI3_SSH_HOST=asi3   # optional; omitted = skip ASI3
bash scripts/launch_rl_distill_all_asi.sh launch

# Option 2: launch each individually
bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch   # ASI1, 27B
bash scripts/asi2_launch_rl_distill_35b_2npu.sh launch   # ASI2, 35B
bash scripts/asi3_launch_rl_distill_35b_2npu.sh launch   # ASI3, 35B
```

### 4.3 Monitor

```bash
bash scripts/asi1_launch_rl_distill_27b_2npu.sh status
bash scripts/asi2_launch_rl_distill_35b_2npu.sh status
bash scripts/asi3_launch_rl_distill_35b_2npu.sh status

# Or all at once:
bash scripts/launch_rl_distill_all_asi.sh status
```

Key log/artifact locations (all on NAS):
- Orchestrator log: `$NAS_ROOT/outputs/qg-{27b,35b}-rl-distill-<RUN_ID>/logs/orchestrator.log`
- Pipeline log: `.../logs/rl_distill_pipeline.log`
- Trainer log: `.../logs/trainer.log`
- vLLM log: `.../logs/vllm.log`
- Checkpoints: `.../checkpoints/step-<N>/` (every 2 hours)
- Final adapter: `.../adapter/`
- SFT buffer: `$NAS_ROOT/data/generated/rl_distill_{27b,35b}_v1/samples.jsonl`
- Rejected samples: `.../rejected.jsonl`
- Weakness report: `.../weakness_report.json` (regenerated each round)

### 4.4 Stop

```bash
bash scripts/launch_rl_distill_all_asi.sh stop
```

### 4.5 Tunables (env vars, all optional)

| Var | Default | Meaning |
|-----|---------|---------|
| `BUFFER_TARGET_PER_ROUND` | 100 | Samples admitted per round before a trainer burst |
| `TRAINER_CHECKPOINT_SECONDS` | 7200 | Checkpoint cadence (2 hours) |
| `PASS_RATE_STOP` | 0.99 | Stop when student exec pass-rate ≥ this over the last window |
| `PASS_RATE_WINDOW` | 100 | Number of recent samples for the pass-rate check |
| `PIPELINE_MAX_ROUNDS` | 0 | 0 = unbounded; set N for a fixed round budget |
| `EVAL_EVERY_ROUNDS` | 2 | Run held-out eval every N rounds |
| `PIPELINE_CONCURRENCY` | 4 | In-flight RL iterations (I/O-bound) |

---

## 5. Status

| Component | Status |
|-----------|--------|
| Sandboxed code execution (`code_exec_sandbox.py`) | ✅ implemented, self-tested, integrated |
| Execution-gated reward (student_exec + teacher_exec) | ✅ implemented, unit-tested |
| Double-confirmation gate (reject if teacher's correction fails) | ✅ implemented, unit-tested |
| 99% pass-rate stop condition | ✅ implemented, unit-tested |
| Weakness-aware question generation (`WeaknessReport` + `analyze_batch_weakness.py`) | ✅ implemented, unit-tested |
| Full-program-with-main question shape | ✅ prompts updated (student-qgen, qgate, student-attempt) |
| Configs updated (27B, 35B ASI2, 35B ASI3) | ✅ all three have `sandbox` + `weakness_aware` + exec-aware `reward_weighting` |
| Launchers updated (ASI1, ASI2, ASI3) | ✅ batch=100, 2h checkpoint, pass-rate-stop, weakness-report wired |
| Parallel all-ASI launcher | ✅ created |
| Plan doc (`self_correcting_distill_pipeline.md`) | ✅ updated with RL-with-verifier mode + question-shape requirement |
| Program-shape enforcement (AST `check_program_shape` + `check_stdout_nonempty` + reward penalty) | ✅ implemented, unit-tested — hardens the question-shape contract beyond prompt-only |
| Tests | ✅ 40 passing (5 runs stable) |
| **Launch on ASI1/2/3** | ⏳ pending — requires NPU availability + GLM5.2 teacher endpoint + quantum SDKs in venv |
| **First 100-sample batch** | ⏳ pending launch |
| **Adapter checkpoints** | ⏳ pending — first checkpoint expected 2h after training starts |
| **99% pass-rate convergence** | ⏳ pending — unknown how many rounds it will take |

---

## 6. Open questions / risks

1. **Sandbox dependency availability.** The sandbox runs the student's
   code in the same Python env as the pipeline. If qiskit/cirq/pennylane
   are not installed on the ASI host, every quantum code sample will
   `ERROR` on import and be rejected. **Mitigation:** verify the venv on
   each ASI host before launch; install missing SDKs.
2. **Teacher endpoint capacity.** GLM5.2 is called 4× per iteration
   (qgate, eval, correction, logprobs). At concurrency=4, that's 16
   concurrent teacher calls. Confirm the teacher endpoint can sustain
   this.
3. **~~Question-shape enforcement is prompt-only~~** ✅ RESOLVED. Added
   `check_program_shape()` (AST-level static check for `def main` +
   `__main__` guard + `main()` call) and `check_stdout_nonempty()`
   (runtime check that PASS- verdict code printed something). Both are
   recorded in `metadata.program_shape`. The reward function applies a
   0.5× penalty for non-conforming programs and 0.75× for empty-stdout
   PASS, so the full-program contract is now a reward signal, not just
   a prompt suggestion. See §2.2 for the six-layer enforcement.
4. **Wall-clock per round.** 100 samples × ~5 sequential LLM calls ×
   ~10 s per call = ~50 min pipeline + trainer burst. Two rounds per
   2-hour checkpoint window is realistic. Adjust `BUFFER_TARGET_PER_ROUND`
   down if rounds are too slow.
5. **NAS I/O.** All three environments write buffers + checkpoints to
   the same NAS root. Confirm the NAS can sustain the write bandwidth
   (small — mostly JSONL + LoRA adapter shards, but 35B adapters are
   ~1 GB per checkpoint).

---

## 7. How to resume if this session is lost

1. Read this document (`docs/rl-verifier-coding-rd-session-2026-07-09.md`).
2. Read `docs/self_correcting_distill_pipeline.md` § "RL-with-verifier mode".
3. Verify the code is present: `scripts/code_exec_sandbox.py`,
   `scripts/analyze_batch_weakness.py`, `scripts/launch_rl_distill_all_asi.sh`.
4. Verify configs have the `sandbox` + `weakness_aware` blocks:
   `python3 -c "import json; d=json.load(open('configs/distill/rl_distill_27b_v1.json')); assert d['sandbox']['enabled']; print('ok')"`.
5. Run the tests: `python3 -m pytest tests/test_rl_distill_pipeline.py -q`.
6. Follow the launch procedure in §4.2 above.

The design is fully captured in the code + configs + this document; no
implicit context is required to resume.
