# GLM5.2 Soft-Distillation SFT — R&D Iteration Process

**Date:** 2026-07-06  
**Branch:** `codex/asi2-qwen36-distillation-lora`  
**Environments:** ASI1 (Qwen3.6-27B), ASI2 (Qwen3.6-35B-A3B), ASI3 (Qwen3.6-35B-A3B)  
**Hardware:** Ascend 910B2 NPUs, 60.96 GiB each; 4–8 NPUs per environment

---

## Overview

This document records the complete research and development iteration cycle developed and executed for the GLM5.2 soft-distillation supervised fine-tuning program. The program trains Qwen3.6-27B and Qwen3.6-35B-A3B student models on GLM5.2 teacher completions, targeting quantum computing knowledge and reasoning.

The R&D cycle is composed of seven phases that repeat indefinitely. Each complete iteration takes approximately 1.5 days end-to-end: 2–4 hours for training, 1–2 hours for evaluation, 2–3 hours for diagnosis and dataset creation, 1 hour for quality checking, then training again. The cycle is designed to be self-correcting: each iteration's evaluation output directly drives the next iteration's dataset.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                       R&D Iteration Cycle                      │
│                                                                │
│   Phase 1      Phase 2      Phase 3      Phase 4              │
│   Launch   →  Verify    →  Evaluate  →  Diagnose             │
│   Training    Status        Adapters     Failures             │
│                                              │                 │
│                                              ▼                 │
│   Phase 7      Phase 6      Phase 5      Dataset             │
│   Retrain  ←  3× Quality ← Create       Creation            │
│   (iter N+1)   Check       New Data      (iter N+1)          │
└────────────────────────────────────────────────────────────────┘
```

**Environments and model assignment:**

| Env  | Model                   | NPUs | Parallelism               | Launcher script                                 |
|------|-------------------------|------|---------------------------|-------------------------------------------------|
| ASI1 | Qwen3.6-27B (bf16)      | 8    | single-process, balanced-layers | `scripts/asi1_launch_glm52_distill_sft_27b.sh` |
| ASI2 | Qwen3.6-35B-A3B (→bf16) | 8    | single-process, balanced-layers | `scripts/asi2_launch_glm52_distill_sft_35b.sh` |
| ASI3 | Qwen3.6-35B-A3B (→bf16) | 2    | single-process, balanced-layers | `scripts/asi3_launch_glm52_distill_sft_35b.sh` |

ASI2 uses `NPROC=8` single-process sharding (all 8 NPUs, world_size=1).  
ASI3 uses `NPROC=2` single-process sharding and a different NAS root (`/root/work/quantum-gpt/` vs `/root/work/software/quantum-gpt/`).

---

## Phase 1 — Launch Fine-Tuning

### Goal

Start LoRA SFT training on all three Huanxin environments, confirm processes are alive, and persist run metadata to the NAS.

### Dataset

`data/generated/glm52_soft_distill_sft_100/`  
- 90 training rows / 10 evaluation rows  
- ChatML format: `<|im_start|>user … <|im_end|><|im_start|>assistant … <|im_end|>`  
- Teacher: GLM5.2 (top-20 logprobs preserved in source JSONL for future soft-KL training)  
- Hard SFT mode: student is trained on the teacher's completion text only

### Procedure

1. Verify the dataset files exist and are non-empty:
   ```bash
   wc -l data/generated/glm52_soft_distill_sft_100/train_chatml.jsonl
   wc -l data/generated/glm52_soft_distill_sft_100/eval_chatml.jsonl
   ```

2. Launch each environment:
   ```bash
   # ASI1 — 27B, 8 NPUs
   scripts/asi1_launch_glm52_distill_sft_27b.sh launch

   # ASI2 — 35B, 8 NPUs (dequantizes W8A8 → bf16 first, ~30 min)
   scripts/asi2_launch_glm52_distill_sft_35b.sh launch

   # ASI3 — 35B, 2 NPUs (ASI3_REMOTE_ROOT override required)
   ASI3_REMOTE_ROOT=/root/work/quantum-gpt \
     scripts/asi3_launch_glm52_distill_sft_35b.sh launch
   ```

3. Confirm background PIDs are alive (each launcher prints `__*_LAUNCHED__ pid=…`).

4. Verify `run_config.json` was written to the NAS output directory.

### LoRA Configuration (iteration 1 baseline)

| Parameter             | ASI1 27B         | ASI2/ASI3 35B    |
|-----------------------|------------------|------------------|
| `lora_rank`           | 16               | 16               |
| `lora_alpha`          | 32               | 32               |
| `lora_dropout`        | 0.05             | 0.0              |
| `target_modules`      | q/v/o/gate/up/down proj (no k_proj) | q/k/v/o/gate/up/down proj |
| `learning_rate`       | 1e-4             | 2e-5             |
| `lr_scheduler`        | cosine           | cosine           |
| `warmup_steps`        | 4                | 4                |
| `max_length`          | 768              | 2048             |
| `gradient_checkpointing` | yes           | yes              |
| `train_layernorm`     | no               | yes              |
| `freeze_param_regex`  | none             | `.*\.(mlp\.gate\|router)\..*` |
| `epochs`              | 2                | 2                |
| `effective steps`     | 44               | 44               |

### Key environment variables

```bash
export QWEN_SFT_ATTN_IMPL=eager          # avoids failing flash-attn backward op
export QWEN_SFT_CHUNKED_LOSS=1           # chunked cross-entropy avoids OOM
export QWEN_SFT_LOSS_CHUNK=512           # logits chunk size
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:128
export TOKENIZERS_PARALLELISM=false
```

### Decision gate

- All three launchers must emit `__*_LAUNCHED__` with a live PID.
- `run_config.json` must exist on the NAS output path.
- If any environment fails to launch, diagnose before proceeding (see §Troubleshooting).

---

## Phase 2 — Verify Status

### Goal

Confirm that training is progressing without OOM, hanging, or process death. Catch pod-recycling events early.

### Procedure

Check each environment approximately 15 minutes after launch and again near the expected completion time.

```bash
# ASI1
scripts/asi1_launch_glm52_distill_sft_27b.sh status

# ASI2
scripts/asi2_launch_glm52_distill_sft_35b.sh status

# ASI3 (status reads LOG_PATH and OUTPUT_DIR set by the launcher)
ASI3_REMOTE_ROOT=/root/work/quantum-gpt \
  scripts/asi3_launch_glm52_distill_sft_35b.sh status
```

Each `status` command tails the last 60 lines of the training log and lists checkpoint and adapter directories.

### What to look for in the log

| Pattern | Meaning |
|---------|---------|
| `__STEP__ step=N/44 loss=…` | Normal — note the step number |
| `__CHECKPOINT_SAVED__ step=N` | Checkpoint persisted to NAS |
| `__TRAIN_DONE__` | Training complete |
| `NPU out of memory` | OOM — see §Troubleshooting |
| `Expected all tensors to be on the same device` | Cross-device bug — see §Troubleshooting |
| `aclnnLinalgVectorNorm` | Gradient-norm Ascend kernel crash — see §Troubleshooting |
| `Conv2D` memory failure | Backward-pass OOM on 35B — reduce `max_length` |
| No process, empty log | Pod recycled — reconnect and resume from latest checkpoint |

### Pod-recycle recovery procedure

1. Reconnect the shell terminal:
   ```bash
   node browser-automation/huanxin_open_env.js ASI2 --click-text "Shell终端"
   ```

2. Find the latest checkpoint:
   ```bash
   ls -la $OUTPUT_DIR/checkpoints/
   ```

3. Resume from the checkpoint, computing the remaining steps:
   ```bash
   ADAPTER_INIT="$OUTPUT_DIR/checkpoints/step-33/adapter" \
   MAX_STEPS=11 NUM_EPOCHS=1 LEARNING_RATE=3e-6 \
     scripts/asi2_launch_glm52_distill_sft_35b.sh launch
   ```

### Decision gate

- Training is progressing (step counter advancing, loss decreasing).
- No OOM or crash errors.
- Proceed to Phase 3 once all environments emit `__TRAIN_DONE__`.

---

## Phase 3 — Evaluate Adapters

### Goal

Measure the quality delta between the base model and each fine-tuned adapter on held-out samples. Produce a structured JSON report for diagnosis.

### Procedure

Run the base-vs-adapter evaluation on the NPU:

```bash
# ASI1 — runs on NPU, auto-selects newest adapter
scripts/asi1_eval_base_vs_adapter.sh
```

The script:
1. Auto-picks the newest `adapter_config.json` under `outputs/*/adapter/`.
2. Runs `scripts/eval_base_vs_adapter.py` against the 495 held-out samples in `data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl`.
3. Writes a JSON report to `outputs/eval-base-vs-adapter-<RUN_ID>.json` and logs to `logs/eval-base-vs-adapter-<RUN_ID>.log`.

For different eval files or adapters:
```bash
ADAPTER=/path/to/adapter \
EVAL_FILE=data/generated/glm52_soft_distill_sft_100/eval_chatml.jsonl \
LIMIT=50 \
  scripts/asi1_eval_base_vs_adapter.sh
```

### Metrics to capture

From the eval JSON report, extract:

| Metric | Description |
|--------|-------------|
| `base_accuracy` | Base model pass@1 on eval set |
| `adapter_accuracy` | Adapter pass@1 on eval set |
| `delta` | `adapter_accuracy − base_accuracy` |
| `by_category` | Per-task-category breakdown |
| `failure_samples` | Examples where adapter answered incorrectly |
| `regression_samples` | Examples where base was correct but adapter was wrong |

### Decision gate

- If `delta > 0` on ≥ 70% of categories → iteration is successful; use these adapters as the `ADAPTER_INIT` for the next training run.
- If `delta < 0` on any category → flag for diagnosis; do not regress.
- Iterations with `|delta| < 0.02` on all categories → dataset is likely too small or too narrow; prioritize expanding it in Phase 5.

---

## Phase 4 — Diagnose Failures

### Goal

Identify the root causes of model failures so that the next dataset is targeted at real weaknesses rather than random generation.

### Failure taxonomy

| Category | Description | Likely fix |
|----------|-------------|------------|
| **Knowledge gap** | Model does not know the fact (framework API, gate definition, constant) | Add more factual Q&A pairs to the dataset |
| **Reasoning error** | Model knows the concepts but assembles them incorrectly | Add multi-step reasoning chains with worked examples |
| **Coding error** | Generated code is syntactically or semantically wrong | Add code repair trajectories, add execution-verified examples |
| **Hallucination** | Model fabricates APIs, parameter names, or circuit behavior | Add negative examples; add "I don't know" / citation patterns |
| **Format error** | Answer has correct content but wrong output format | Add few-shot format examples in the training prompt |
| **Regression** | Model previously got this right but now answers incorrectly | Lower learning rate; add replay examples from the previous dataset |

### Procedure

1. Load the eval JSON report.
2. Group `failure_samples` by category (use the `category` field if present; infer from task description if not).
3. Count failures per category. The top-2 categories by failure count drive Phase 5 dataset creation.
4. Inspect 5–10 representative failures per category to characterize the pattern.
5. Write a brief diagnosis note in `docs/` or as comments in the new dataset's `manifest.json`.

### Example diagnosis summary

```
Category failure counts (iter-1):
  knowledge_gap:    18 / 50  (36%)  → top priority
  reasoning_error:  12 / 50  (24%)  → second priority
  coding_error:      8 / 50  (16%)  → third priority
  hallucination:     6 / 50  (12%)
  format_error:      4 / 50   (8%)
  regression:        2 / 50   (4%)

Action: Create iter-2 dataset focused on knowledge gaps (quantum gate
identities, Qiskit transpiler API) and multi-step reasoning chains
(VQE energy surface derivations, QAOA angle optimization).
```

---

## Phase 5 — Create the Next Dataset

### Goal

Build a targeted training dataset that addresses the top failure categories identified in Phase 4.

### Sizing

| Scenario | Train rows | Eval rows | Notes |
|----------|-----------|-----------|-------|
| Minimum viable | 90 | 10 | Same as iter-1; use if time-constrained |
| Standard | 180–450 | 20–50 | 2–5× more diverse |
| Comprehensive | 900–4 500 | 100–500 | Use the 8 000-question pool once repaired |

For each additional 100 training rows with 2048-token max length, expect ~22 additional training steps and ~30 minutes of NPU time on the 35B.

### Generation pipeline

1. **Seed questions** — Write or generate questions targeting the diagnosed weakness categories:
   ```bash
   python3 scripts/build_quantum_distillation_seed_questions.py \
     --categories knowledge_gap reasoning_error \
     --count 200 \
     --out data/generated/iter2_seed_questions.jsonl
   ```

2. **Teacher responses** — Send questions to GLM5.2 and collect completions with logprobs:
   ```bash
   python3 scripts/generate_distillation_teacher_responses.py \
     --questions data/generated/iter2_seed_questions.jsonl \
     --model glm5.2 \
     --out data/generated/iter2_teacher_responses.jsonl \
     --top-logprobs 20
   ```

3. **Format to ChatML SFT split** — Dedup, split 90/10, write train/eval JSONL:
   ```bash
   python3 scripts/prepare_distillation_sft_split.py \
     --teacher-responses data/generated/iter2_teacher_responses.jsonl \
     --out-dir data/generated/glm52_soft_distill_sft_iter2 \
     --train-ratio 0.9 \
     --deduplicate
   ```

4. **Update manifest** — Record provenance in `data/generated/glm52_soft_distill_sft_iter2/manifest.json`.

### Dataset naming convention

```
data/generated/glm52_soft_distill_sft_<iter>_<focus>/
  train_chatml.jsonl    # 90% split
  eval_chatml.jsonl     # 10% split
  manifest.json         # provenance, SHA256, category counts
```

---

## Phase 6 — Dataset Quality Check (3 Rounds)

Run three sequential quality checks before any training begins on the new dataset. Each check can block the pipeline.

### Round 1 — Structural correctness

Verify that every row has the required fields, is parseable, and is formatted correctly.

```bash
python3 - <<'PY'
import json, sys

path = "data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl"
errors = []
for i, line in enumerate(open(path)):
    row = json.loads(line)
    if "messages" not in row:
        errors.append(f"row {i}: missing 'messages'")
        continue
    msgs = row["messages"]
    if not isinstance(msgs, list) or len(msgs) < 2:
        errors.append(f"row {i}: messages must be list of ≥2")
        continue
    roles = [m.get("role") for m in msgs]
    # Allow an optional leading system role (valid ChatML format)
    effective_roles = [r for r in roles if r != "system"]
    if not effective_roles or effective_roles[0] != "user" or effective_roles[-1] != "assistant":
        errors.append(f"row {i}: must have user…assistant turn order; got {roles}")
    for m in msgs:
        if not m.get("content", "").strip():
            errors.append(f"row {i}: empty content in role={m.get('role')}")

if errors:
    print(f"FAIL — {len(errors)} structural errors:")
    for e in errors[:20]: print(" ", e)
    sys.exit(1)
else:
    print("PASS — structural check")
PY
```

**Gate:** Zero structural errors. Fix all before proceeding.

### Round 2 — Content quality

Check that completions are substantive (not refusals, not empty, not stub responses) and that the questions actually target the diagnosed weakness categories.

```bash
python3 - <<'PY'
import json, sys

path = "data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl"
issues = []
MIN_COMPLETION_TOKENS = 50
MIN_QUESTION_TOKENS = 10

for i, line in enumerate(open(path)):
    row = json.loads(line)
    msgs = row["messages"]
    question = next((m["content"] for m in msgs if m["role"] == "user"), "")
    answer   = next((m["content"] for m in msgs if m["role"] == "assistant"), "")
    
    if len(question.split()) < MIN_QUESTION_TOKENS:
        issues.append(f"row {i}: question too short ({len(question.split())} words)")
    if len(answer.split()) < MIN_COMPLETION_TOKENS:
        issues.append(f"row {i}: completion too short ({len(answer.split())} words)")
    
    refusal_phrases = ["I cannot", "I'm sorry", "As an AI", "I don't have access"]
    if any(p.lower() in answer.lower() for p in refusal_phrases):
        issues.append(f"row {i}: possible refusal detected")

print(f"Content check: {len(issues)} issues out of {i+1} rows")
if issues:
    for iss in issues[:20]: print(" ", iss)
    if len(issues) > len(open(path).readlines()) * 0.05:
        print("FAIL — >5% issue rate")
        sys.exit(1)
    else:
        print("WARN — <5% issues; review manually but may proceed")
else:
    print("PASS — content check")
PY
```

**Gate:** Issue rate < 5%. Manually review flagged rows; drop or repair them.

### Round 3 — Fitness for fine-tuning

Verify token-length distribution, detect duplicates, and confirm the dataset is appropriate for the training configuration.

```bash
python3 - <<'PY'
import json, sys

try:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/root/work/filestorage/Qwen3.6-27B", use_fast=True)
except Exception:
    tok = None

path = "data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl"
MAX_LENGTH = 2048
rows = [json.loads(l) for l in open(path)]

lengths, seen = [], set()
dups = 0
for row in rows:
    text = "".join(m["content"] for m in row["messages"])
    if text in seen:
        dups += 1
    seen.add(text)
    if tok:
        lengths.append(len(tok.encode(text)))
    else:
        lengths.append(len(text.split()) * 1.3)  # rough estimate

if lengths:
    import statistics
    p50 = sorted(lengths)[len(lengths)//2]
    p95 = sorted(lengths)[int(len(lengths)*0.95)]
    over = sum(1 for l in lengths if l > MAX_LENGTH)
    print(f"Token length: p50={p50:.0f}  p95={p95:.0f}  max={max(lengths):.0f}")
    print(f"Rows over max_length={MAX_LENGTH}: {over}/{len(lengths)} ({100*over/len(lengths):.1f}%)")
    print(f"Duplicates: {dups}")
    
    if p95 > MAX_LENGTH * 0.9:
        print("WARN — p95 token length is near max_length; consider truncation or max_length increase")
    if over > len(lengths) * 0.1:
        print("FAIL — >10% of rows exceed max_length; truncation will corrupt too many completions")
        sys.exit(1)
    if dups > len(lengths) * 0.05:
        print("FAIL — >5% duplicate rows detected")
        sys.exit(1)
    print("PASS — fitness check")
PY
```

**Gate:** `<10%` rows exceed `max_length`; `<5%` duplicate rows; no p95 warning above `0.9 × max_length` unless `max_length` is explicitly increased.

---

## Phase 7 — Retrain (Next Iteration)

### Goal

Fine-tune the student models on the new dataset, initialized from the previous iteration's adapters to accumulate knowledge across iterations.

### Procedure

Set `ADAPTER_INIT` to the previous iteration's saved adapter path and reduce the learning rate:

```bash
# ASI1 iter-2 from iter-1 adapter
ADAPTER_INIT=/root/work/software/quantum-gpt/outputs/qg-27b-glm52-distill-sft-<iter1-id>/adapter \
DATA=data/generated/glm52_soft_distill_sft_iter2 \
LEARNING_RATE=3e-5 \
  scripts/asi1_launch_glm52_distill_sft_27b.sh launch

# ASI2 iter-2 from iter-1 adapter
ADAPTER_INIT=/root/work/software/quantum-gpt/outputs/qg-35b-glm52-distill-sft-<iter1-id>/adapter \
DATA=data/generated/glm52_soft_distill_sft_iter2 \
LEARNING_RATE=5e-6 \
  scripts/asi2_launch_glm52_distill_sft_35b.sh launch
```

### Learning rate schedule across iterations

| Iteration | 27B LR | 35B LR | Notes |
|-----------|--------|--------|-------|
| 1 (cold)  | 1e-4   | 2e-5   | Full training from base weights |
| 2 (warm)  | 3e-5   | 5e-6   | Resume from iter-1 adapter |
| 3+        | 1e-5   | 2e-6   | Continued warm-start; small targeted corrections |

Lower learning rates on warm restarts prevent catastrophic forgetting of the previous iteration's learning while still updating the adapter for the new patterns.

### Versioning

Each output directory name contains the full timestamp:
```
outputs/qg-27b-glm52-distill-sft-glm52-distill-27b-20260706T080000Z/
```

Record the output path in `artifacts/model-registry/index.json` after each successful iteration:
```json
{
  "run_id": "qg-27b-glm52-distill-sft-iter2-20260706T080000Z",
  "model": "Qwen3.6-27B",
  "adapter": "outputs/qg-27b-glm52-distill-sft-…/adapter",
  "adapter_init": "outputs/qg-27b-glm52-distill-sft-iter1-…/adapter",
  "dataset": "glm52_soft_distill_sft_iter2",
  "iteration": 2,
  "base_accuracy": 0.62,
  "adapter_accuracy": 0.71,
  "delta": 0.09
}
```

---

## Troubleshooting

### OOM during training launch (model loading)

**Symptom:** `RuntimeError: NPU out of memory` in the first few seconds of training.  
**Cause:** DDP (`torchrun --nproc_per_node=N`) forces each rank to load the full model on one NPU. 27B bf16 ≈ 54 GB and 35B bf16 ≈ 70 GB both exceed the 60 GB NPU limit.  
**Fix:** Use `python3` (world_size=1) with `--npu-device-map balanced-layers --npu-max-memory-gib 54`. All launchers in this repo already apply this fix.

### Cross-device tensor error in loss computation

**Symptom:** `RuntimeError: Expected all tensors to be on the same device, but found at least two devices, npu:3 and npu:0!` during forward pass.  
**Cause:** With `balanced-layers` device map, the model's last layer and its output logits land on the last NPU (e.g., npu:3), but the labels tensor was placed on npu:0.  
**Fix:** In `training/qwen_sft_peft.py`, inside the chunked loss loop, add `.to(logits_chunk.device)` when slicing the labels:
```python
labels_chunk = flat_labels[start:end].to(logits_chunk.device)
```

### Ascend `aclnnLinalgVectorNorm` crash during gradient clipping

**Symptom:** `RuntimeError: The Inner error is reported as above. The current working operator name is aclnnLinalgVectorNorm.` during the optimizer step.  
**Cause:** The fused Ascend kernel cannot operate across parameters distributed across multiple NPU devices, as happens with `balanced-layers` sharding and layernorm training enabled.  
**Fix:** Replace `torch.nn.utils.clip_grad_norm_` with a manual per-parameter norm loop that aggregates squared norms as Python floats on CPU, then applies a scalar `mul_` clip. This is already implemented in `training/qwen_sft_peft.py` as of commit `f94d05b`.

### OOM during 35B backward pass (Conv2D)

**Symptom:** `RuntimeError: Failed to apply for memory… op type = Conv2D` during backward on an early step.  
**Cause:** `--max-length 3072` with a 2-NPU or 4-NPU balanced-layers map creates activation tensors too large for the available SRAM on the 35B.  
**Fix:** Reduce `--max-length` from 3072 → 2048. Also add `--freeze-param-regex '.*\.(mlp\.gate|router)\..*'` to freeze the MoE router and reduce gradient memory. Both fixes are already in the ASI2/ASI3 launchers.

### Pod recycled mid-training (error 170022)

**Symptom:** Shell reconnect fails with "获取shell终端信息失败" (error 170022). The training process is gone.  
**Cause:** Huanxin auto-recycles pods that have been idle or running for an extended period.  
**Mitigation:** Use `setsid nohup … </dev/null &` launch pattern (already in all launchers) — this protects background processes from HUP signals but cannot prevent pod-level recycling.  
**Recovery:**
1. Reconnect the shell: `node browser-automation/huanxin_open_env.js ASI2 --click-text "Shell终端"`
2. Find the latest checkpoint: `ls -la $OUTPUT_DIR/checkpoints/`
3. Resume: `ADAPTER_INIT=…/checkpoints/step-N/adapter MAX_STEPS=<remaining> NUM_EPOCHS=1 LEARNING_RATE=<lower> scripts/asi2_…sh launch`
4. The W8A8 → bf16 decompressed cache (`/tmp/qwen35b_decompressed_for_training`) is on the ephemeral disk and will be lost on pod recycle. Expect a ~30-minute re-decompression before training restarts.

---

## Iteration Log

| Iter | Date       | Dataset                      | ASI1 (27B) | ASI2 (35B) | ASI3 (35B) | Notes |
|------|------------|------------------------------|-----------|-----------|-----------|-------|
| 1    | 2026-07-05 | `glm52_soft_distill_sft_100` | ✅ 44/44 steps, adapter saved (312 MB) | ✅ 44/44 steps (resumed from step 33 after pod recycle) | ✅ 44/44 steps, eval loss=0.599, perplexity=1.82 | First run; fixed OOM (balanced-layers), cross-device label bug, clip_grad_norm bug, max_length 3072→2048 |
| 2    | 2026-07-06 | `glm52_soft_distill_sft_iter2` | Staged — max_length fixed 768→1600, warm-start from iter-1 adapter | Staged — warm-start from iter-1 adapter, lr 2e-5→5e-6 | Staged — warm-start from iter-1 adapter, lr 2e-5→5e-6 | Diagnosis: ASI1 94.4% truncation at max_length=768; 5 gap topics (Cirq/PennyLane/ZNE/QML/ISQ) added; dataset: 90→142 train rows, 10→13 eval rows; 3× quality checks all PASS |

---

## File and Path Reference

| Resource | Path |
|----------|------|
| Trainer | `training/qwen_sft_peft.py` |
| NPU modeling patch | `scripts/patch_qwen3_5_npu_modeling.py` |
| W8A8 dequantizer | `training/dequantize_moe_w8a8_to_bf16.py` |
| ASI1 launcher | `scripts/asi1_launch_glm52_distill_sft_27b.sh` |
| ASI2 launcher | `scripts/asi2_launch_glm52_distill_sft_35b.sh` |
| ASI3 launcher | `scripts/asi3_launch_glm52_distill_sft_35b.sh` |
| Eval harness | `scripts/eval_base_vs_adapter.py` |
| Eval launcher | `scripts/asi1_eval_base_vs_adapter.sh` |
| Browser automation | `browser-automation/huanxin_open_env.js` |
| Model registry | `artifacts/model-registry/index.json` |
| Iter-1 dataset | `data/generated/glm52_soft_distill_sft_100/` |
| ASI1/ASI2 NAS root | `/root/work/software/quantum-gpt/` |
| ASI3 NAS root | `/root/work/quantum-gpt/` |
| 27B base model | `/root/work/filestorage/Qwen3.6-27B` |
| 35B base model (W8A8) | `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8` |
| 35B decompressed (ephemeral) | `/tmp/qwen35b_decompressed_for_training` |

---

## Timing Reference

| Phase | Typical duration |
|-------|-----------------|
| Phase 1 — Launch | 5–10 min (excludes W8A8 decompression) |
| W8A8 → bf16 decompression (35B) | 20–35 min |
| Phase 2 — Status check | 5 min per check; repeat every 30 min during training |
| Training: 27B, 90 rows, 2 epochs | ~2–3 hours |
| Training: 35B, 90 rows, 2 epochs | ~3–5 hours |
| Phase 3 — Evaluation | 1–2 hours |
| Phase 4 — Diagnosis | 1–2 hours |
| Phase 5 — Dataset creation | 2–4 hours |
| Phase 6 — Quality checks ×3 | 1 hour |
| **Full iteration** | **~1.5 days** |
