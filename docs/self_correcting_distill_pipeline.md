# Self-Correcting Distillation Pipeline

## Overview

This pipeline produces a soft-distillation SFT dataset by having a **student
adapter** attempt quantum-coding questions and a **teacher model (GLM5.2)**
grade + correct the answers. The resulting samples pair the student's
incorrect code with the teacher's critique + corrected answer, and preserve
the teacher's per-token logprobs so a downstream trainer can do logit-level
distillation.

## RL-with-verifier mode (Option A)

The pipeline now runs as a **closed-loop RL algorithm with a verifier in the
loop** rather than a fixed offline dataset generator. The verifier is the
sandboxed Python interpreter in `scripts/code_exec_sandbox.py`. The loop is:

1. **Sample a (framework, topic, difficulty) contract.** When a weakness
   report from the previous batch is available, the sampler biases toward
   the student's weak cells (see `WeaknessReport` in
   `scripts/rl_distill_pipeline.py` and `scripts/analyze_batch_weakness.py`).
2. **Student proposes a question** for that contract; the teacher validates
   it via the qgate.
3. **Student answers its own question** (writes the code).
4. **Verifier executes the student's code** in a sandboxed subprocess and
   records `{verdict, stdout, stderr, exit_code, runtime_ms}`.
5. **Teacher grades the answer grounded in the execution result** (it sees
   the real stderr/stdout, so its critique references real runtime errors).
6. **Teacher produces a corrected answer** with per-token logprobs.
7. **Verifier executes the teacher's corrected code** as a double-
   confirmation gate. Only if the corrected code runs to `PASS` is the
   sample admitted to the SFT buffer. Otherwise the row is written to
   `rejected.jsonl` with both execution logs for auditability.
8. The scalar reward is computed with the **real execution signal as the
   dominant weight** (`w_student_exec_pass=0.45`, `w_teacher_exec_pass=0.20`
   when the sandbox is enabled; the teacher-judgment and confidence weights
   shrink accordingly). This is the verifier-in-the-loop reward that GRPO
   or reward-weighted SFT optimizes against.

**Training loop parameters (per the user's spec):**
- Batch size: **100 samples per round** (`--target-buffer-size 100`).
- Checkpoint cadence: **every 2 hours** (`--checkpoint-interval-seconds 7200`
  on the trainer).
- Stop condition: **student execution pass-rate ≥ 99%** over the last 100
  samples (`--pass-rate-stop 0.99 --pass-rate-window 100`).
- Environments: **ASI1 (Qwen3.6-27B), ASI2 + ASI3 (Qwen3.6-35B-A3B)** all
  run in parallel.
- Adapters + important files: written to **NAS** (`$NAS_ROOT/outputs/...`),
  not local disk.

**Question diversity + weakness-aware generation:**
- The base distribution spans 8 frameworks × 10 topics × 3 difficulties.
- Between batches, the orchestrator runs
  `scripts/analyze_batch_weakness.py` to emit a per-cell pass-rate report.
- The next batch's pipeline reloads the report and blends the prior with
  the inverse-pass-rate distribution (`alpha=0.4`), so the student is
  nudged toward its weakest cells without losing coverage.
- Questions are still **proposed by the student first, then corrected by
  the teacher** (the student is the question proposer; the teacher is the
  answerer/corrector), exactly as requested.

## Dataset shape

For each question in the pool:

1. The student adapter is asked to write code for the question.
2. **The student's code is actually executed** before any teacher judgment.
   The runner writes the code to a temp file and runs it in a sandboxed
   Python environment (timeout: 30 s, memory: 1 GiB). The execution
   produces one of:
   - `PASS` — the code ran to completion with exit code 0 and, when a
     test harness is available, the harness assertions all passed.
   - `FAIL: <stderr tail>` — the code raised an exception, failed an
     assertion, or returned a wrong value. The full traceback is
     captured.
   - `ERROR: <reason>` — the code could not be executed at all (syntax
     error, missing dependency, timeout, OOM). The reason is captured.
   The raw `stdout`, `stderr`, `exit_code`, and `runtime_ms` are stored
   alongside the verdict. This execution evidence is **mandatory** and
   is the ground truth that gates every downstream decision.
3. The teacher (GLM5.2) is then asked to evaluate correctness. The
   teacher is **given the execution result** (verdict + stderr/stdout
   excerpt) so its judgment is grounded in real runtime behavior, not
   text-only inspection. The teacher returns a structured JSON response.
4. If the student's code is judged **correct (100%) AND the execution
   verdict is `PASS`**, the pipeline moves on to the next question. The
   teacher is still asked to confirm the answer with logprobs so the
   student can distill the teacher's confidence.
5. If the student's code is **not correct** (teacher-judged incorrect,
   or execution verdict != `PASS`), the teacher is asked again
   (with `logprobs=True`) to provide:
   - a one-paragraph critique of where the student's answer is wrong
     (referencing the execution error when present), and
   - a corrected, complete answer in a single ```python``` block.
6. **The teacher's corrected code is then executed in the same sandbox**
   as a double-confirmation gate. Only if this second execution returns
   `PASS` is the corrected sample admitted into the SFT set. If the
   teacher's correction also fails to run, the sample is marked
   `rejected` and written to `rejected.jsonl` with both the student and
   teacher execution logs, so the failure is auditable and the row is
   not silently dropped. A sample is never admitted on the teacher's
   text judgment alone.
7. The final SFT sample is:
   - **system**: the teacher's system prompt
   - **user**: `Question:\n{question}\n\nStudent code:\n\`\`\`python\n{student_code}\n\`\`\`\n\nDo you think the code is correct?`
   - **assistant**: the teacher's critique + corrected answer
   - **teacher_logits**: per-token `{token, logprob, top_logprobs:[{token, logprob}]}` for the assistant target (used for soft distillation)
   - **status**: `accepted`, `corrected`, or `rejected`
   - **teacher_eval**: the structured JSON evaluation. **Must** include:
     - `is_correct` (bool): teacher's judgment
     - `issues` (list[str]): diagnosed problems, each referencing the
       execution evidence when present (e.g. `"NameError on line 12:
       'qc' is not defined (see student_exec.stderr)"`)
     - `correct_answer` (str): the teacher's corrected code block
     - `confidence` (float in [0,1]): teacher's confidence
     - `student_exec` (obj, **mandatory**): `{verdict: "PASS"|"FAIL"|"ERROR", stdout: str, stderr: str, exit_code: int, runtime_ms: int}` — the real execution result of the student's code
     - `teacher_exec` (obj, **mandatory when status=="corrected"**): same shape as `student_exec`, the real execution result of the teacher's corrected code. Must be `PASS` for the sample to be admitted; otherwise `status="rejected"`.
   - **harness_result**: the test-harness result, if a harness was available (kept for backward compatibility; superseded by `teacher_eval.student_exec` / `teacher_eval.teacher_exec`)

## Layout

```
configs/distill/
  self_correcting_distill_27b_v1.json   # 27B student config
  self_correcting_distill_35b_v1.json   # 35B student config
scripts/
  build_self_correcting_questions.py    # builds the 8000-question pool
  self_correcting_distill.py            # the pipeline
  run_self_correcting_distill_27b.py    # one-shot runner (27B)
  run_self_correcting_distill_35b.py    # one-shot runner (35B)
data/generated/self_correcting_distill/
  questions_pool.jsonl                  # 8000 unique questions
  questions_pool_manifest.json
data/generated/self_correcting_distill_{27b,35b}_v1/
  student_answers.jsonl                 # raw student responses
  teacher_evals.jsonl                   # structured teacher evals (incl. student_exec + teacher_exec)
  train_chatml_with_logits.jsonl        # admitted SFT samples with teacher logits (status in {accepted, corrected})
  rejected.jsonl                        # rows where teacher's correction also failed execution (status=rejected)
  pipeline_report.json                  # progress / acceptance / rejection counters
```

## Running

### Prerequisites

- A serving endpoint for the student adapter (OpenAI-compatible). Defaults:
  - 27B: `http://127.0.0.1:8007/v1`
  - 35B: `http://127.0.0.1:8008/v1`
- A serving endpoint for GLM5.2 (the teacher), exposed via `GLM52_API_BASE`
  and `GLM52_API_KEY`.

### Build the question pool (one-time)

```bash
python3 scripts/build_self_correcting_questions.py
```

This dedupes and normalizes questions from
`data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl`,
`data/seed/quantum_rag_seed_questions.jsonl`,
`data/seed/quantum_llm_plan_seed.jsonl`, and `evals/tasks/quantum`, then
writes 8000 unique questions to
`data/generated/self_correcting_distill/questions_pool.jsonl`.

### Run the pipeline (27B)

```bash
export STUDENT_27B_API_KEY=dummy
export GLM52_API_BASE=http://127.0.0.1:8009/v1
export GLM52_API_KEY=...
python3 scripts/run_self_correcting_distill_27b.py
```

### Run the pipeline (35B)

```bash
export STUDENT_35B_API_KEY=dummy
export GLM52_API_BASE=http://127.0.0.1:8009/v1
export GLM52_API_KEY=...
python3 scripts/run_self_correcting_distill_35b.py
```

### Runner env vars

| Var | Default | Meaning |
|-----|---------|---------|
| `WORKERS` | `4` | Concurrent student+teacher calls |
| `START_INDEX` | `0` | Inclusive start index into the pool |
| `END_INDEX` | `8000` | Exclusive end index into the pool |
| `LIMIT` | unset | Process at most N questions (debug) |
| `GIT_SYNC_INTERVAL` | `100` | Commit every N processed questions |
| `NO_GIT_PUSH` | unset | Set to `1` to commit without pushing |
| `NO_GIT_SYNC` | unset | Set to `1` to disable git checkpoints |

## Git checkpointing

To avoid losing partial progress, the pipeline commits and pushes the
output directory at three points:

1. **Periodic** — every `GIT_SYNC_INTERVAL` (default 100) processed
   questions, the pipeline flushes `pipeline_report.json` and runs
   `git add -A <output_dir> && git commit && git push`.
2. **Final** — when the loop completes normally.
3. **Danger** — if the process receives `SIGTERM` or `SIGINT`, the
   pipeline stops submitting new questions, finishes the in-flight batch,
   then runs a `phase=danger` sync before exiting.

Commit messages are structured:

```
[distill:periodic] sync checkpoint: processed=100 accepted=42 corrected=55 skipped=0 errors=3

phase=periodic
output_dir=/path/to/data/generated/self_correcting_distill_27b_v1
branch=codex/asi2-qwen36-distillation-lora
Co-Authored-By: distill-bot <distill-bot@local>
```

To inspect the timeline of checkpoints:

```bash
git log --grep='^\[distill:' --oneline
```

## Resumability

`--resume` is on by default in the runners. The pipeline reads
`student_answers.jsonl` to determine which `question_id`s are already
done, and skips them. Append-only writes mean a crash mid-run never
corrupts a partial record.

## Soft distillation

`train_chatml_with_logits.jsonl` is the SFT file. Each record carries
`teacher_logits` as a list of per-token entries. A downstream trainer can
use these to do KL-divergence soft distillation against the teacher's
distribution, in addition to (or instead of) the hard token-level NLL on
the assistant target.

To convert to a plain ChatML SFT file (dropping logits) for a trainer
that doesn't yet support logit distillation:

```bash
python3 - <<'PY'
import json, sys
with open(sys.argv[1]) as f:
    for line in f:
        r = json.loads(line)
        out = {"messages": r["messages"]}
        print(json.dumps(out, ensure_ascii=False))
PY data/generated/self_correcting_distill_27b_v1/train_chatml_with_logits.jsonl \
    > data/generated/self_correcting_distill_27b_v1/train_chatml.jsonl
```
