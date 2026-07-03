# Self-Correcting Distillation Pipeline

## Overview

This pipeline produces a soft-distillation SFT dataset by having a **student
adapter** attempt quantum-coding questions and a **teacher model (GLM5.2)**
grade + correct the answers. The resulting samples pair the student's
incorrect code with the teacher's critique + corrected answer, and preserve
the teacher's per-token logprobs so a downstream trainer can do logit-level
distillation.

## Dataset shape

For each question in the pool:

1. The student adapter is asked to write code for the question.
2. The teacher (GLM5.2) is asked to evaluate correctness:
   - If a test harness is available, the harness is run first and its result
     is treated as ground truth. If the harness says the code is correct,
     the sample is `accepted`.
   - Otherwise (or when no harness exists), the teacher judges correctness
     via a structured JSON response.
3. If the student's code is judged **correct (100%)**, the pipeline moves on
   to the next question. The teacher is still asked to confirm the answer
   with logprobs so the student can distill the teacher's confidence.
4. If the student's code is **incorrect**, the teacher is asked again
   (with `logprobs=True`) to provide:
   - a one-paragraph critique of where the student's answer is wrong, and
   - a corrected, complete answer in a single ```python``` block.
5. The final SFT sample is:
   - **system**: the teacher's system prompt
   - **user**: `Question:\n{question}\n\nStudent code:\n\`\`\`python\n{student_code}\n\`\`\`\n\nDo you think the code is correct?`
   - **assistant**: the teacher's critique + corrected answer
   - **teacher_logits**: per-token `{token, logprob, top_logprobs:[{token, logprob}]}` for the assistant target (used for soft distillation)
   - **status**: `accepted` or `corrected`
   - **teacher_eval**: the structured JSON evaluation (`is_correct`, `issues`, `correct_answer`, `confidence`)
   - **harness_result**: the test-harness result, if a harness was available

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
  teacher_evals.jsonl                   # structured teacher evals
  train_chatml_with_logits.jsonl        # the SFT samples with teacher logits
  pipeline_report.json                  # progress / acceptance counters
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
