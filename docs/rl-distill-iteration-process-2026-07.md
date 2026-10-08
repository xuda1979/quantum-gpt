# RL + Soft-Distillation Iteration Process (GLM5.2 teacher)

**Date:** 2026-07-06 (updated 2026-07-07)
**Branch:** `codex/asi2-qwen36-distillation-lora`
**Students:** Qwen3.6-27B (ASI1, 2 NPUs) and Qwen3.6-35B-A3B (ASI2 + ASI3, 2 NPUs each)
**Teacher:** GLM5.2 (remote HTTP endpoint)
**Hardware:** Ascend 910B2 NPUs, 60.96 GiB each; 2 NPUs per environment

> **2026-07-07 update.** The loop is now **fully closed**: eval (Stage 9)
> runs automatically inside the orchestrator, the pipeline is **concurrent**
> (4 in-flight iterations by default), and a **rejection-aware distribution**,
> **reward-weighted sampling**, **deduplication**, and **guardrails** have
> been added so the loop can run for days without producing a degenerate
> buffer. ASI3 (a second 35B-A3B node) is now supported as a parallel
> independent loop. See §“Fully automated operation” and §“What was added
> in the 2026-07-07 hardening” for the diff.
Us per student

---

## Overview

This document describes a mixed **reinforcement-learning + soft-distillation**
loop that complements the existing SFT iteration process
(`docs/glm52-distillation-rd-iteration-process-2026-07.md`).

The student model is both:
- an **actor** that proposes new quantum-coding questions and attempts to
  answer them (RL exploration), and
- a **learner** that is fine-tuned on the teacher's corrections with a
  combination of token-level NLL and KL-divergence against the teacher's
  top-k logprob distribution (soft distillation).

GLM5.2 acts as a fixed teacher that (a) gates question quality, (b) grades
and corrects the student's code answers, and (c) provides per-token top-k
logprobs on the corrected answer for the KL term.

The loop runs continuously. Every hour a checkpoint is saved and the
accumulated high-quality samples are folded back into the student via a
short soft-KL SFT burst. **Every 2 rounds** (configurable), the eval
subsystem runs `pass@k` against `evals/tasks/quantum/` on the latest
adapter, appends a row to the iteration log, and updates the markdown
summary — without human intervention.

### Environments

| Env   | Model            | NPUs | vLLM port | Config                                   | Launcher                                    |
|-------|------------------|------|-----------|------------------------------------------|---------------------------------------------|
| ASI1  | Qwen3.6-27B      | 0,1  | 8007      | `configs/distill/rl_distill_27b_v1.json` | `scripts/asi1_launch_rl_distill_27b_2npu.sh`  |
| ASI2  | Qwen3.6-35B-A3B  | 0,1  | 8008      | `configs/distill/rl_distill_35b_v1.json` | `scripts/asi2_launch_rl_distill_35b_2npu.sh`  |
| ASI3  | Qwen3.6-35B-A3B  | 0,1  | 8009      | `configs/distill/rl_distill_35b_asi3_v1.json` | `scripts/asi3_launch_rl_distill_35b_2npu.sh` |

ASI2 and ASI3 run **independent** loops (separate buffers, separate adapter
checkpoints, separate eval runs). They share the same teacher endpoint and
the same task suite. This gives two 35B replicas exploring different parts
of the question space in parallel; the better adapter across the two at any
round can be promoted to the canonical SFT iter for the next cold-start.

---

## Architecture

```
+------------------+
|  Student server  |  NPU 0,1  (vLLM, TP=2)
|  Qwen3.6-27B/35B |  port 8007 (27B) / 8008 (35B ASI2) / 8009 (35B ASI3)
|  + LoRA adapter  |
+---------+--------+
          | OpenAI-compatible /v1/chat/completions
          v
+-------------------+        +--------------------------+
| rl_distill_       | <----> | GLM5.2 teacher (remote)  |
| pipeline.py       |        | via GLM52_API_BASE/KEY   |
| (CPU, no NPU)     |        +--------------------------+
+---------+---------+
          | appends (question, correction, teacher_logits, reward) tuples
          v
+-------------------+
| Rolling JSONL     |  data/generated/rl_distill_{27b,35b,35b_asi3}_v1/
| buffer            |  rl_distill_samples.jsonl
+---------+---------+
          | every ~55 min, vLLM is paused
          v
+-------------------+
| qwen_sft_peft_kl  |  NPU 0,1  (LoRA SFT + KL, reward-floor filtered)
| hourly burst      |  -> checkpoints/round-N/adapter
+---------+---------+
          | every EVAL_EVERY_ROUNDS: eval subsystem runs pass@k
          v
+-------------------+
| evals/subsystem/  |  NPU 0,1  (balanced-layers, same as trainer)
| harness.py        |  -> evals/round-N/eval-N.json + eval_summary.md
+---------+---------+
          | latest adapter reloaded by vLLM
          v
   (loop continues)
```

### Process roles

| Process | CPU/NPU | Role |
|---------|---------|------|
| vLLM student server | NPU 0,1 | Serves the student + latest LoRA adapter for question generation and code attempts (tensor-parallel size 2) |
| `rl_distill_pipeline.py` | CPU only | Generates questions, gets teacher corrections + logits, appends to buffer |
| `qwen_sft_peft_kl.py` | NPU 0,1 | Hourly soft-KL SFT burst on the accumulated buffer; single-process sharded across both NPUs via `--npu-device-map balanced-layers`; saves checkpoint |
| Orchestrator (`orchestrator.sh`) | CPU | Alternates pipeline ↔ trainer, pauses vLLM during trainer bursts |

> **Why single-process sharding, not DDP?** A 27B bf16 model is ~54 GB and
> a 35B-A3B bf16 model is ~70 GB. Each Ascend 910B2 NPU has 60.96 GiB, so
> loading the full model onto one NPU (which DDP requires) OOMs at weight
> materialization time. The trainer therefore uses single-process
> `device_map="balanced-layers"` sharding — the model is split across
> both NPUs by transformer layer index, and a single training process
> drives both. vLLM, by contrast, uses tensor-parallel size 2 to serve
> the model with both NPUs cooperating on each forward pass.

---

## Pipeline stages (per iteration)

### Stage 1 — Student proposes a question (RL explore)

The student is prompted with a sampled `(framework, topic, difficulty)`
contract and asked to produce ONE new, original quantum-coding question
that a peer could answer in a single Python file.

Frameworks, topics, and difficulties are sampled from the distributions
in `configs/distill/rl_distill_{27b,35b}_v1.json` (e.g. qiskit 30%,
pennylane 16%, cirq 12%, etc.).

### Stage 2 — Teacher validates the question (gate)

GLM5.2 reviews the proposed question and returns strict JSON:

```json
{
  "is_valid": true,
  "is_answerable": true,
  "is_non_trivial": true,
  "issues": ["..."],
  "confidence": 0.0,
  "improved_question": "..."
}
```

A question is accepted only if all three of `is_valid`,
`is_answerable`, and `is_non_trivial` are `true`. Up to
`max_resamples_per_question` (default 3) attempts are made per contract;
rejected proposals are logged to `rl_distill_rejected.jsonl` for offline
analysis.

If `improved_question` is non-empty and the question is mostly good, the
improved version replaces the original.

### Stage 3 — Student attempts the validated question (RL roll-out)

The student is asked to answer its own validated question with a single
self-contained Python code block. Output is parsed to extract the
```` ```python ... ``` ```` block.

### Stage 4 — Teacher grades and corrects

GLM5.2 receives the question and the student's code, and returns strict
JSON:

```json
{
  "is_correct": false,
  "issues": ["..."],
  "correct_answer": "<corrected code and/or precise explanation>",
  "confidence": 0.85
}
```

The `correct_answer` field becomes the assistant target for SFT.

### Stage 5 — Teacher re-emits the corrected answer with top-k logprobs

To capture a soft target distribution, GLM5.2 is asked to re-emit the
corrected answer verbatim with `logprobs=True, top_logprobs=20`. The
response contains, for each generated token:

```json
{
  "token": "def",
  "logprob": -0.42,
  "top_logprobs": [
    {"token": "def", "logprob": -0.42},
    {"token": "class", "logprob": -3.1},
    ...
  ]
}
```

These per-token top-k distributions are stored alongside the sample and
used by the soft-KL trainer.

### Stage 6 — Buffer append

The sample is appended to the rolling JSONL buffer:

```
data/generated/rl_distill_27b_v1/rl_distill_samples.jsonl
```

Each line is a JSON object with:

| Field | Description |
|-------|-------------|
| `example_id` | `rl_distill_{sha8(question)}_{sha8(answer)}` |
| `messages` | ChatML `[system, user, assistant]` with the corrected answer as the assistant target |
| `teacher_logits.content` | The teacher's re-emitted corrected answer |
| `teacher_logits.logprobs` | Per-token top-k logprob entries |
| `metadata.framework`, `.topic`, `.difficulty` | The sampled contract |
| `metadata.teacher_is_correct`, `.teacher_confidence` | Teacher's grading verdict |
| `metadata.qgate_*` | Teacher's question-gate verdict |
| `student_attempt` | The student's original (pre-correction) code |

A manifest is written periodically:

```
data/generated/rl_distill_27b_v1/rl_distill_manifest.json
```

### Stage 7 — Hourly soft-KL SFT burst

Every ~55 minutes the orchestrator pauses vLLM, then runs
`training/qwen_sft_peft_kl.py` on the accumulated buffer:

```bash
python3 training/qwen_sft_peft_kl.py \
  --model-name /root/work/filestorage/Qwen3.6-27B \
  --train-file data/generated/rl_distill_27b_v1/rl_distill_samples.jsonl \
  --output-dir outputs/qg-27b-rl-distill-.../checkpoints/round-N \
  --device npu --npu-device-map balanced-layers --npu-max-memory-gib 58 \
  --kl-coeff 0.5 --nll-coeff 0.5 --temperature 1.0 \
  --max-length 2048 --max-steps 200 \
  --checkpoint-interval-seconds 3600 \
  --learning-rate 3e-5 \
  --lora-rank 16 --lora-alpha 32 \
  --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only --gradient-checkpointing \
  --adapter-init <previous-round-adapter>
```

The trainer computes, for each assistant token:

```
Loss = nll_coeff * NLL(student, target_token)
     + kl_coeff * KL(student_topk || teacher_topk)
```

where the KL is computed over the union of the teacher's top-k token ids
(plus the argmax token). This avoids materializing the full ~150k vocab
— only the ~21 ids the teacher scored are gathered from the student
logits at each position, which fits comfortably on a 61 GiB Ascend NPU.

The trainer saves a checkpoint to
`outputs/qg-27b-rl-distill-.../checkpoints/round-N/adapter` and (if the
burst runs longer than an hour) periodic sub-checkpoints to
`checkpoints/step-M/adapter`.

### Stage 8 — Adapter reload

After the trainer burst, vLLM is resumed with the latest adapter. There
are two resume modes, selected by the `VLLM_PAUSE_MODE` env var:

- **`sleep` (default, fast):** the orchestrator keeps the vLLM process
  alive across the trainer burst. Before training it calls
  `POST /v1/sleep {"level": 1}` to free NPU memory while keeping the
  base weights in host pinned memory. After training it calls
  `POST /v1/wake_up` to reload weights onto the NPU (seconds, not
  minutes), then `POST /v1/load_lora_adapter` to hot-swap the new
  LoRA adapter without restarting the process. This avoids re-loading
  the 27B/35B base weights from disk on every round.
- **`kill` (legacy, slow):** the orchestrator SIGTERM/SIGKILLs vLLM
  before training and relaunches `vllm serve` with
  `--enable-lora --lora-modules rl_distill_latest=<adapter>` after.

Sleep mode auto-falls back to kill mode if the running vLLM does not
expose `/v1/sleep` or `/v1/load_lora_adapter` (detected via
`scripts/vllm_lifecycle.py`). Set `VLLM_PAUSE_MODE=kill` to force the
legacy path (useful for vLLM versions < 0.6 or when debugging NPU
memory accounting issues).

### Stage 9 — Auto-eval (closed loop, new 2026-07-07)

Every `EVAL_EVERY_ROUNDS` rounds (default 2), the orchestrator runs the
eval subsystem on the latest adapter **before** vLLM is resumed:

```bash
python3 evals/subsystem/harness.py \
  --base-model "$MODEL" \
  --adapter  "$OUT/checkpoints/round-$ROUND/adapter" \
  --output   "$OUT/evals/round-$ROUND/eval-$ROUND.json" \
  --device npu --npu-max-memory-gib 58 \
  --max-new-tokens 1024 --k 1 --tasks quantum
```

The harness loads the adapter with `device_map="balanced-layers"` on the
two NPUs (same sharding strategy as the trainer), runs `pass@k` over the
task suite in `evals/tasks/quantum/`, and writes a schema-v2 JSON. The
analyzer and reporter then run to produce a delta report and update
`$OUT/eval_summary.md`.

The eval result is **not** used to gate the next training round in the
current implementation — the loop continues regardless. The result is
recorded for trend analysis and to trigger manual intervention if
`pass@1` degrades monotonically across 3 consecutive evals (see
§“When to intervene”).

> **Why eval before vLLM resume?** vLLM is paused for the trainer burst
> and the NPUs are free. Running eval in this window avoids a second
> vLLM pause later and keeps the GPU-resident adapter warm.

---

## Launch

### ASI1 — Qwen3.6-27B, 2 NPUs

```bash
export GLM52_API_BASE=https://<glm52-endpoint>/v1
export GLM52_API_KEY=...
export STUDENT_27B_API_KEY=dummy  # any non-empty string
export ASCEND_RT_VISIBLE_DEVICES=0,1
# Optional: warm-start from the iter-2 SFT adapter
export ADAPTER_INIT=outputs/qg-27b-glm52-distill-sft-iter2/adapter

bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch
```

### ASI2 — Qwen3.6-35B-A3B, 2 NPUs

```bash
export GLM52_API_BASE=https://<glm52-endpoint>/v1
export GLM52_API_KEY=...
export STUDENT_35B_API_KEY=dummy
export ASCEND_RT_VISIBLE_DEVICES=0,1
export ADAPTER_INIT=outputs/qg-35b-glm52-distill-sft-iter2/adapter

bash scripts/asi2_launch_rl_distill_35b_2npu.sh launch
```

### ASI3 — Qwen3.6-35B-A3B, 2 NPUs (parallel independent loop)

```bash
export GLM52_API_BASE=https://<glm52-endpoint>/v1
export GLM52_API_KEY=...
export STUDENT_35B_API_KEY=dummy
export ASCEND_RT_VISIBLE_DEVICES=0,1
export ADAPTER_INIT=outputs/qg-35b-asi3-glm52-distill-sft-iter2/adapter

bash scripts/asi3_launch_rl_distill_35b_2npu.sh launch
```

ASI3 runs its own buffer (`data/generated/rl_distill_35b_asi3_v1/`) and
its own adapter checkpoints (`outputs/qg-35b-asi3-rl-distill-*/`).
Compare ASI2 vs ASI3 eval trends periodically and promote the better
adapter to the next SFT cold-start.

### Status

```bash
bash scripts/asi1_launch_rl_distill_27b_2npu.sh status
bash scripts/asi2_launch_rl_distill_35b_2npu.sh status
bash scripts/asi3_launch_rl_distill_35b_2npu.sh status
```

### Stop

```bash
bash scripts/asi1_launch_rl_distill_27b_2npu.sh stop
bash scripts/asi2_launch_rl_distill_35b_2npu.sh stop
bash scripts/asi3_launch_rl_distill_35b_2npu.sh stop
```

---

## Checkpoint cadence

| Event | Frequency | Location |
|-------|-----------|----------|
| Buffer manifest update | every 8 appended samples | `data/generated/rl_distill_{27b,35b}_v1/rl_distill_manifest.json` |
| Trainer checkpoint | every 3600 s during a training burst | `outputs/qg-{27b,35b}-rl-distill-.../checkpoints/step-N/adapter` |
| Round checkpoint | end of each ~55-minute round | `outputs/qg-{27b,35b}-rl-distill-.../checkpoints/round-N/adapter` |

The round-N checkpoint is the one reloaded by vLLM for the next round.
The step-N checkpoints inside a round are recovery points in case a
burst is interrupted.

---

## Configuration knobs

The pipeline is configured via `configs/distill/rl_distill_{27b,35b}_v1.json`.
Important knobs:

| Knob | Default | Effect |
|------|---------|--------|
| `question_generation.max_resamples_per_question` | 3 | How many times the student may re-propose a question before the contract is abandoned |
| `question_generation.framework_distribution` | qiskit 30%, pennylane 16%, ... | Sampling distribution over quantum SDKs |
| `pipeline.target_buffer_size_per_round` | 256 | Number of accepted samples to accumulate per round before triggering a trainer burst |
| `pipeline.trainer_max_length` | 2048 | Max sequence length for the trainer |
| `teacher_model.top_logprobs` | 20 | Top-k width for teacher logprobs (drives KL width) |
| `student_model.serving.temperature` | 0.7 | Student sampling temperature for question generation and code attempts |

Trainer knobs (env vars on the launcher):

| Env var | Default | Effect |
|---------|---------|--------|
| `KL_COEFF` | 0.5 | Weight on the KL loss term |
| `NLL_COEFF` | 0.5 | Weight on the NLL loss term |
| `TEMPERATURE` | 1.0 | Softmax temperature applied to both student and teacher distributions before KL |
| `LEARNING_RATE` | 27B 3e-5 / 35B 5e-6 | LoRA learning rate |
| `TRAINER_MAX_STEPS_PER_ROUND` | 27B 200 / 35B 150 | Max optimizer steps per hourly burst |
| `TRAINER_CHECKPOINT_SECONDS` | 3600 | Sub-checkpoint interval within a burst |
| `PIPELINE_MAX_WALLCLOCK_SECONDS` | 3300 | ~55 min pipeline phase per round |

---

## Acceptance criteria for a sample

A sample is appended to the buffer only if **all** of the following hold:

1. The student proposed a non-empty question (≥ 40 chars).
2. The teacher's question gate returned `is_valid && is_answerable && is_non_trivial`.
3. The student produced a non-empty code answer.
4. The teacher returned a non-empty `correct_answer` of at least
   `guardrail.min_corrected_answer_chars` chars (default 40).
5. The teacher's `confidence` is at least `guardrail.min_teacher_confidence`
   (default 0.30). Low-confidence corrections are dropped.
6. The teacher's logprobs re-emission returned ≥ 4 scored tokens.
7. The `(question, correct_answer)` pair is not a near-duplicate of a
   recent sample (rolling 20k-entry LRU set, normalized text + sha1).

Samples that fail any stage are logged to `rl_distill_rejected.jsonl`
with the failure reason. Each accepted sample is tagged with a scalar
`metadata.reward ∈ [0, 1]` (see §“Reward weighting”). Samples below
`eval.reward_floor_for_train` (default 0.20) are filtered out at trainer
load time via `--reward-floor`.

---

## What was added in the 2026-07-07 hardening

The original loop was serial (one sample at a time), had no eval step,
and would happily produce a degenerate buffer if the teacher started
rejecting everything or the student collapsed to a narrow topic. The
following changes make it safe to run unattended for days:

### 1. Pipeline concurrency (`concurrency`)

The pipeline now runs `concurrency` (default 4) RL+distill iterations
in flight simultaneously via a `ThreadPoolExecutor`. Each iteration is
5 sequential LLM calls (student qgen → teacher gate → student attempt →
teacher eval → teacher re-emit), so this is I/O-bound and safe to
parallelize against a single vLLM student + remote teacher. Effective
sample throughput rises ~3–4× on a 2-NPU node.

Stat updates are protected by a module-level `_STATS_LOCK` and the
buffer writer is already thread-safe (append-only JSONL with a
`threading.Lock`).

### 2. Rejection-aware distribution (`RejectionTracker`)

The `(framework, topic, difficulty)` contract is no longer sampled
from the static prior. Instead, a `RejectionTracker` blends the prior
with the inverse-rejection distribution:

```
w(k) = (1 - low_pass) * prior(k) + low_pass * accept_rate(k)
```

with `low_pass=0.25` and `smoothing=4` pseudo-counts. This gently
nudges the student toward contracts where its proposals survive the
teacher gate, while never fully abandoning hard contracts. The tracker
is updated on every accept/reject.

### 3. Reward weighting (`reward_weighting`)

Every accepted sample is tagged with `metadata.reward ∈ [0, 1]`:

```
reward = (w_correct * already_correct
        + w_conf    * teacher_confidence
        + w_first   * first_pass_qgate
        + w_subst   * answer_substance) / sum(weights)
```

Default weights: `w_correct=0.40, w_conf=0.25, w_first=0.20, w_subst=0.15`.
The trainer drops samples below `--reward-floor` (default 0.20). A
future enhancement can scale the per-row loss by `(reward - floor) /
(1 - floor)` for true reward-weighted regression.

### 4. Deduplication (`dedup`)

A 20k-entry LRU set of `sha1(normalized_question || normalized_answer)`
prevents the same (q, a) pair from entering the buffer twice. This is
especially important when the student's temperature is low and it
re-proposes similar questions.

### 5. Guardrails (`guardrail`)

Two hard stops protect against degenerate rounds:

- **`max_consecutive_teacher_rejections=12`**: if the teacher rejects
  12 questions in a row, the pipeline writes a `rl_distill_guardrail_trip`
  log line and exits the round early. The orchestrator then runs the
  trainer + eval burst on whatever samples accumulated.
- **`max_teacher_qgate_rejection_rate=0.85`**: if the rejection rate
  over the last `rolling_window=32` samples exceeds 85%, same trip.

Both are configurable in the JSON config or via CLI override
(`--guardrail-max-consecutive-rejections`).

### 6. Auto-eval (Stage 9)

See Stage 9 above. The orchestrator runs the eval subsystem every
`EVAL_EVERY_ROUNDS` rounds (default 2) on the latest adapter, in the
vLLM-paused window between trainer burst and vLLM resume.

---

## Parameters to tune at each stage

This is the single most important section for an operator. Each stage
has a small set of knobs that actually matter; everything else is
best left at defaults.

### Stage 1 — Student question generation

| Parameter | Where | Default | When to change |
|-----------|-------|---------|----------------|
| `student_model.serving.temperature` | config | 0.7 | Raise to 0.85 if the student keeps proposing the same question (low diversity). Lower to 0.5 if >30% of qgate rejections are "is_non_trivial=false". |
| `question_gen.framework_distribution` | config | qiskit 0.30, pennylane 0.16, ... | Don't tune manually — the `RejectionTracker` adjusts this automatically. Only override if you want to force-exclude a framework (set weight to 0). |
| `question_gen.topic_distribution` | config | circuits 0.18, algorithms 0.18, ... | Same — auto-adjusted. Audit monthly by reading `rl_distill_rejected.jsonl` to see which topics the student is weakest at. |
| `question_gen.max_resamples_per_question` | config | 3 | Raise to 5 if the student is strong and you want fewer wasted contracts. Lower to 2 if the teacher is rejecting >60% (avoid burning teacher quota). |

### Stage 2 — Teacher question gate

| Parameter | Where | Default | When to change |
|-----------|-------|---------|----------------|
| `teacher_model.temperature` | config | 0.0 | Keep at 0.0 (deterministic grading). Only raise to 0.2 if the teacher is too harsh on borderline questions. |
| `teacher_model.max_tokens` | config | 4096 | Raise if the teacher's `improved_question` is getting truncated. |
| `guardrail.max_consecutive_teacher_rejections` | config | 12 | Lower to 8 if the teacher is brittle; raise to 20 if you want the loop to push through hard contracts. |

### Stage 3 — Student code attempt

| Parameter | Where | Default | When to change |
|-----------|-------|---------|----------------|
| `student_model.serving.temperature` | config | 0.7 | Same knob as Stage 1 — affects both qgen and attempt. If you want them separate, you'd need to refactor the pipeline (not currently supported). |
| `student_model.serving.max_tokens` | config | 3072 (35B) / 4096 (27B) | Raise if the student's code is getting cut off mid-function. Lower to 2048 if the student is rambling. |
| `pipeline.execution_timeout_seconds` | config | 30 | Currently unused (no execution verifier in the loop). Reserved for future harness integration. |

### Stage 4 — Teacher grade + correct

| Parameter | Where | Default | When to change |
|-----------|-------|---------|----------------|
| `guardrail.min_teacher_confidence` | config | 0.30 | Raise to 0.50 if you see low-quality corrections entering the buffer. Lower to 0.20 if the teacher is conservative and you're starving the buffer. |
| `guardrail.min_corrected_answer_chars` | config | 40 | Raise to 80 if the teacher is producing one-line cop-outs. |

### Stage 5 — Teacher logprobs re-emission

| Parameter | Where | Default | When to change |
|-----------|-------|---------|----------------|
| `teacher_model.top_logprobs` | config | 20 | Keep at 20 — this is the K for the KL loss. Lowering to 10 saves memory but loses distribution information. Raising above 20 has diminishing returns. |
| `--min-teacher-logprob-tokens` | trainer CLI | 4 | Raise to 8 if the KL loss is noisy on short answers. |

### Stage 7 — Soft-KL SFT burst

| Parameter | Where | 27B default | 35B default | When to change |
|-----------|-------|-------------|-------------|----------------|
| `KL_COEFF` | launcher env | 0.5 | 0.5 | Lower to 0.3 if KL loss is NaN/exploding. Raise to 0.7 if the student is drifting from the teacher's style. |
| `NLL_COEFF` | launcher env | 0.5 | 0.5 | Keep `KL_COEFF + NLL_COEFF = 1.0`. |
| `TEMPERATURE` | launcher env | 1.0 | 1.0 | Lower to 0.7 if the teacher distribution is too peaked (KL unstable). Raise to 1.3 if the student is too uniform. |
| `LEARNING_RATE` | launcher env | 3e-5 | 5e-6 | **27B vs 35B differ.** For the continuous RL+distill loop, use 1/2 the cold-start SFT LR. If loss oscillates, halve it. If too slow, double it (cap at 5e-5 for 27B, 1e-5 for 35B). |
| `LORA_RANK` | launcher env | 16 | 16 | Raise to 32 if the student has plateaued and you want more capacity. Lower to 8 if you're memory-constrained. |
| `MAX_LENGTH` | launcher env | 2048 | 2048 | 27B iter-1 used 768 (too short — 94% truncation). 2048 is the sweet spot for quantum-coding samples with framework boilerplate. Raise to 3072 only if you see >20% truncation in the trainer log. |
| `TRAINER_MAX_STEPS_PER_ROUND` | launcher env | 200 | 150 | 35B uses fewer steps (slower per step). Raise to 300 if the buffer is large (>512 rows) and loss is still decreasing. |
| `TRAINER_CHECKPOINT_SECONDS` | launcher env | 3600 | 3600 | Keep at 3600 (1 hour) — matches the round cadence. |
| `--reward-floor` | trainer CLI | 0.20 | 0.20 | Raise to 0.35 if the buffer is large and you want to train only on the best samples. Set to 0.0 to disable reward filtering. |
| `--gradient-accumulation-steps` | trainer CLI | 4 | 4 | Raise to 8 if OOM during backward; lower to 2 if you want faster steps and have memory headroom. |

### Stage 9 — Auto-eval

| Parameter | Where | Default | When to change |
|-----------|-------|---------|----------------|
| `EVAL_EVERY_ROUNDS` | launcher env | 2 | Set to 0 to disable eval entirely. Raise to 3 if eval is eating too much of the round budget. Lower to 1 if you want tight feedback (costs ~15 min/round). |
| `EVAL_TASKS` | launcher env | `quantum` | The task suite to eval against. Use `standard12` for a quick smoke or `quantum` for the full holdout. |
| `EVAL_K` | launcher env | 1 | pass@1 (greedy). Raise to 4 only if you have the wall-clock budget for sampling. |
| `EVAL_MAX_NEW_TOKENS` | launcher env | 1024 | Raise to 2048 if eval samples are getting truncated (check the harness log). |
| `EVAL_NPU_MAX_MEMORY_GIB` | launcher env | 58 | Lower to 54 if eval OOMs (35B is tight on 61 GiB NPUs). |
| `VLLM_PAUSE_MODE` | launcher env | `sleep` | `sleep` keeps vLLM alive across trainer bursts via `/v1/sleep`+`/v1/wake_up`+`/v1/load_lora_adapter` (fast; no base-weight reload). `kill` forces the legacy SIGTERM/relaunch path. Sleep auto-falls back to kill if the vLLM build lacks the endpoints. |
| `VLLM_WAKE_TIMEOUT_SECONDS` | launcher env | 300 | Seconds to wait for `/v1/wake_up` to bring `/v1/models` back healthy. Raise to 600 on slow NPU memory reload paths. |
| `VLLM_LORA_ADAPTER_NAME` | launcher env | `rl_distill_latest` | The served name vLLM registers the hot-swapped LoRA under. The pipeline config's `student_model.serving.model` should match this name so requests hit the adapted model. |

### Cross-stage: concurrency

| Parameter | Where | Default | When to change |
|-----------|-------|---------|----------------|
| `concurrency` | config / `--concurrency` | 4 | Raise to 6 if the teacher endpoint has spare capacity (watch teacher p95 latency). Lower to 2 if vLLM is returning 429s or the teacher is rate-limiting. |

---

## Fully automated operation

With the defaults above, the loop runs unattended:

```
round 1:  pipeline 55 min → trainer 5 min → eval 10 min → vLLM resume
round 2:  pipeline 55 min → trainer 5 min → (skip eval)  → vLLM resume
round 3:  pipeline 55 min → trainer 5 min → eval 10 min → vLLM resume
...
```

- Each round produces ~256 samples (concurrency-4 × ~55 min × ~1 sample/min/worker).
- Every 2 rounds, `eval-<round>.json` + `eval_summary.md` are updated in
  `$OUT/evals/`.
- The adapter checkpoint at `$OUT/checkpoints/round-N/adapter` is always
  the latest student state.
- The orchestrator logs to `$OUT/logs/orchestrator.log` with one line
  per stage transition.

The only things that require manual action are listed in the next
section.

---

## When to intervene

The loop is designed to run for days without human input, but the
following conditions warrant a look:

1. **`pass@1` degrades monotonically across 3 consecutive evals.**
   Check `$OUT/evals/round-*/eval-*.json` and look at the
   `summary.pass_at_k` trend. If it's going down, the student is
   overfitting to the teacher's idiosyncrasies. Lower `KL_COEFF` to
   0.3 and raise `--reward-floor` to 0.35 to train only on
   high-quality samples.

2. **`guardrail_trips` > 0 in the pipeline log.** The teacher is
   rejecting too much. Inspect `rl_distill_rejected.jsonl` — if the
   rejections cluster on one framework, that framework's API may have
   drifted. Either fix the teacher's system prompt or temporarily
   set that framework's weight to 0 in `framework_distribution`.

3. **`duplicates_dropped` > 20% of `samples_appended`.** The student
   has collapsed to a narrow mode. Raise `student_model.serving.temperature`
   to 0.85 and/or raise `question_gen.max_resamples_per_question` to 5.

4. **KL loss is NaN or > 5.0.** See §“KL loss is NaN or exploding”
   in Troubleshooting.

5. **The buffer is not growing.** Check the pipeline log for
   `teacher_logprobs_empty` — if the teacher's logprobs re-emission
   is failing, the loop produces no usable samples. Verify the
   teacher endpoint is up and supports `logprobs=True, top_logprobs=20`.

6. **vLLM fails to come up after a trainer burst.** See
   §“vLLM fails to come up after a trainer burst” in Troubleshooting.

7. **Promoting an RL-distill checkpoint to a new SFT cold-start.**
   When an RL-distill adapter achieves a clearly better `pass@1`
   than the previous SFT iter (e.g. +5pp on the full quantum holdout),
   copy it to `outputs/qg-{27b,35b}-glm52-distill-sft-iter<N+1>/adapter`
   and use it as `ADAPTER_INIT` for the next SFT round. This is the
   only way the RL+distill loop feeds back into the SFT lineage.

---

## Monitoring

### Live stats

```bash
tail -f outputs/qg-27b-rl-distill-*/logs/orchestrator.log
tail -f outputs/qg-27b-rl-distill-*/logs/rl_distill_pipeline.log
tail -f outputs/qg-27b-rl-distill-*/logs/trainer.log
```

### Buffer growth

```bash
watch -n 60 'wc -l data/generated/rl_distill_27b_v1/rl_distill_samples.jsonl
             cat data/generated/rl_distill_27b_v1/rl_distill_manifest.json'
```

### Trainer loss curve

```bash
grep '"stage": "train_step"' outputs/qg-27b-rl-distill-*/logs/trainer.log | tail -50
```

Each log line includes `nll`, `kl`, and `loss` so the KL/NLL balance
can be monitored.

---

## Iteration log

After each round, append a row to the iteration log section:

```
| Date | Round | Student | Buffer rows | Train rows | NLL | KL | Notes |
|------|-------|---------|-------------|-----------|-----|----|-------|
| 2026-07-06 | 1 | 27B | 256 | 256 | 1.42 | 0.87 | first round; KL high (teacher distribution far from student) |
| 2026-07-06 | 1 | 35B | 256 | 256 | 1.18 | 0.65 | 35B starts closer to teacher |
```

Track the KL trend across rounds — a decreasing KL indicates the
student is converging toward the teacher's distribution on the
corrected-answer distribution.

---

## Relationship to the SFT iteration process

This RL+distill loop is **complementary** to the existing SFT iteration
process documented in
`docs/glm52-distillation-rd-iteration-process-2026-07.md`:

| Aspect | SFT iteration | RL+distill iteration |
|--------|---------------|----------------------|
| Data source | Static seed pool + RAG-grounded questions | Student-generated questions, teacher-gated |
| Target | Teacher's hard answer | Teacher's correction + soft logits |
| Loss | NLL only | NLL + KL(teacher top-k), reward-floor filtered |
| Cadence | Manual, ~1.5 days per iteration | Continuous, hourly checkpoints; auto-eval every 2 rounds |
| Adapter init | Previous SFT iter adapter | Previous RL-distill round adapter (or SFT iter adapter for round 1) |
| Gate | 3-round dataset quality check | Teacher question gate + teacher correction + guardrails |
| Eval | Manual harness run | Automatic, every 2 rounds, into `eval_summary.md` |
| Concurrency | 1 (serial) | 4 in-flight iterations (ThreadPool) |
| Distribution | Fixed per config | Rejection-aware, auto-adjusted per (framework, topic, difficulty) |

Recommended workflow: run the SFT iteration for 1–2 iters to get a
strong base adapter, then start the RL+distill loop warm-started from
the best SFT adapter. The RL+distill loop runs indefinitely and
self-evaluates; promote an RL-distill checkpoint to a new SFT
cold-start only when it shows a clear `pass@1` win on the full quantum
holdout (see §“When to intervene” §7).

---

## Troubleshooting

### vLLM fails to come up after a trainer burst

- Check `outputs/qg-.../logs/vllm.log` for OOM or port-in-use errors.
- With the default `VLLM_PAUSE_MODE=sleep`, the orchestrator does NOT
  kill vLLM; it calls `/v1/sleep` then `/v1/wake_up`. If wake-up fails
  (rc != 0 in the orchestrator log), the orchestrator automatically
  falls back to killing and relaunching vLLM. If NPU memory is still
  not released after the fallback, run
  `bash scripts/asi1_launch_rl_distill_27b_2npu.sh stop` and wait 30 s
  before re-launching.
- To force the legacy kill/restart path (e.g. when debugging
  `/v1/sleep` NPU-memory accounting issues), set `VLLM_PAUSE_MODE=kill`.

### Trainer OOM on 35B

- Reduce `MAX_LENGTH` to 1536.
- Reduce `TRAINER_MAX_STEPS_PER_ROUND` to 100.
- Set `--gradient-accumulation-steps 8` to reduce peak memory.

### Pipeline producing too many rejections

- Inspect `data/generated/rl_distill_27b_v1/rl_distill_rejected.jsonl`
  for the most common `issues` strings from the teacher gate.
- Tune `question_generation.topic_distribution` to down-weight topics
  where the student's proposals are most often rejected.
- Raise `student_model.serving.temperature` slightly (e.g. 0.7 → 0.85)
  to encourage more diverse proposals.

### KL loss is NaN or exploding

- Lower `TEMPERATURE` (e.g. 1.0 → 0.7) so the teacher distribution is
  less peaked.
- Lower `KL_COEFF` (e.g. 0.5 → 0.2) and raise `NLL_COEFF` accordingly.
- Check that the teacher's `top_logprobs` field is not empty for the
  failing samples (filter via `--min-teacher-logprob-tokens`).
