# Evaluation Subsystem

Comprehensive, multi-dimensional evaluation infrastructure for quantum-gpt adapter R&D iteration.

## Architecture

```
evals/subsystem/
├── harness.py       NPU-resident pass@k harness (runs on Huanxin; replaces run_asi2_35b_pass1_eval.py)
├── analyzer.py      Offline analysis & comparison of eval JSON outputs (runs locally)
├── reporter.py      Markdown/HTML report generation (runs locally)
├── dataset_gap.py   Failure analysis → dataset gap recommendations (runs locally)
├── tracker.py       Training-aware eval tracker (runs on Huanxin; auto-launches eval on completion)
└── README.md        This file
```

## Quickstart

### 1. Evaluate an adapter on Huanxin (NPU)

```bash
# Standard 12-task pass@1 (fastest, ~30-60 min on ASI3 8-NPU):
TS=$(date +%Y%m%dT%H%M%SZ)
nohup python3 evals/subsystem/harness.py \
    --base-model /tmp/qwen35b_decompressed_for_training_asi3 \
    --adapter outputs/<run_name>/adapter \
    --output outputs/eval-${TS}.json \
    --device npu \
    --npu-max-memory-gib 50 \
    --tasks standard12 \
    > logs/eval-${TS}.log 2>&1 &

# Full 44-task coverage:
python3 evals/subsystem/harness.py --tasks all ...

# pass@5 (5 samples per task, temperature=0.8):
python3 evals/subsystem/harness.py --k 5 --temperature 0.8 ...

# With CE-loss on held-out JSONL:
python3 evals/subsystem/harness.py \
    --eval-file data/generated/.../eval_chatml.jsonl ...
```

### 2. Analyze results locally

```bash
# Base vs adapter comparison:
python3 evals/subsystem/analyzer.py compare \
    --eval outputs/eval-35b-glm52-distill-iter2-pass1.json

# Failure details:
python3 evals/subsystem/analyzer.py failures \
    --eval outputs/eval-35b-iter2.json --model adapter

# Multi-run trend (across iterations):
python3 evals/subsystem/analyzer.py trend \
    outputs/eval-iter1.json outputs/eval-iter2.json outputs/eval-iter3.json

# Machine-readable diff:
python3 evals/subsystem/analyzer.py json-diff \
    --eval outputs/eval-iter2.json
```

### 3. Generate reports

```bash
# Markdown report for a single eval:
python3 evals/subsystem/reporter.py single \
    --eval outputs/eval-35b-iter2.json \
    --label "35B GLM5.2 iter-2 (ASI3)" \
    --out reports/eval_35b_iter2.md

# Multi-run trend table:
python3 evals/subsystem/reporter.py multi \
    --evals outputs/eval-iter1.json outputs/eval-iter2.json \
    --out reports/trend_$(date +%Y%m%d).md

# Update the canonical eval summary:
python3 evals/subsystem/reporter.py update-summary \
    --eval outputs/eval-35b-iter2.json \
    --run-label "35B iter-2" \
    --summary-file reports/glm52_distillation_eval_summary_2026-07-06.md
```

### 4. Get dataset gap recommendations

```bash
# What to add to training data to fix failing tasks:
python3 evals/subsystem/dataset_gap.py recommend \
    --eval outputs/eval-35b-iter2.json \
    --model adapter \
    --top-k 10 \
    --json-out reports/iter3_dataset_gaps.json

# Coverage analysis (what's passing/failing by domain/category):
python3 evals/subsystem/dataset_gap.py coverage \
    --eval outputs/eval-35b-iter2.json

# Audit training dataset balance:
python3 evals/subsystem/dataset_gap.py audit \
    --dataset data/generated/glm52_soft_distill_sft_iter2/train_chatml.jsonl
```

### 5. Auto-eval when training finishes (tracker)

```bash
# On the NPU machine: watch a training run and auto-eval:
python3 evals/subsystem/tracker.py watch \
    --output-dir /root/work/quantum-gpt/outputs/qg-35b-glm52-distill-sft-...-20260706T081105Z \
    --base-model /tmp/qwen35b_decompressed_for_training_asi3 \
    --eval-output-dir /root/work/quantum-gpt/outputs/ \
    --device npu \
    --npu-max-memory-gib 50

# Print the harness command for a specific training output dir:
python3 evals/subsystem/tracker.py print-eval-cmd \
    --output-dir /root/work/quantum-gpt/outputs/qg-35b-glm52-distill-sft-... \
    --base-model /tmp/qwen35b_decompressed_for_training_asi3 \
    --device npu

# Show status of all recent training output dirs:
python3 evals/subsystem/tracker.py status \
    --outputs-root /root/work/quantum-gpt/outputs
```

## Output Format (schema_version=2)

The harness writes JSON with this top-level structure:
```json
{
  "schema_version": 2,
  "created_at_utc": "2026-07-06T09:00:00Z",
  "base_model": "/path/to/base",
  "adapter": "/path/to/adapter",
  "task_ids": [...],
  "k": 1,
  "results": {
    "base":    {"summary": {...}, "records": [...], "heldout_loss": {...}},
    "adapter": {"summary": {...}, "records": [...], "heldout_loss": {...}}
  },
  "delta": {
    "pass_at_1": 0.0833,
    "base_pass_at_1": 0.8333,
    "adapter_pass_at_1": 0.9167,
    "fixed_tasks": ["quantum_grover_oracle_diffusion"],
    "broken_tasks": []
  }
}
```

The `records` list contains per-task entries with:
- `task_id`, `domain`, `category`, `name`
- `n_samples`, `n_pass`, `pass_at_1` (+ `pass_at_2`, `pass_at_5`, `pass_at_10` if k>1)
- `samples`: list of `{passed, failure_category, details, code_head, raw_head}`
- `gen_sec`: generation time in seconds

## Backward Compatibility

`analyzer.py`, `reporter.py`, and `dataset_gap.py` all handle both:
- **schema_version=2** (new harness output)
- **schema_version=1 / legacy** (old `run_asi2_35b_pass1_eval.py` output)

Existing eval JSON files produced during the R&D cycle remain valid inputs.

## R&D Loop Integration

```
Training finishes → adapter/ written
        ↓
tracker.py watch OR manual harness.py launch
        ↓
eval-*.json output (schema_version=2)
        ↓
analyzer.py compare/trend  ──────────────→  Delta report
        ↓
dataset_gap.py recommend   ──────────────→  iter-N+1 dataset gaps
        ↓
reporter.py update-summary ──────────────→  Markdown summary updated
        ↓
Next training iteration
```
